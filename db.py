import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path("leetcode.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    tags TEXT,
    created_at TEXT NOT NULL,
    ef REAL NOT NULL DEFAULT 2.5,
    reps INTEGER NOT NULL DEFAULT 0,
    interval_days INTEGER NOT NULL DEFAULT 0,
    next_review TEXT NOT NULL,
    last_attempt_at TEXT,
    last_q INTEGER,
    time_spent_min INTEGER,
    hints_used INTEGER
);
""")
    cur.execute("""
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    attempted_at TEXT NOT NULL,
    q INTEGER NOT NULL,
    time_spent_min INTEGER,
    hints_used INTEGER,
    notes TEXT,
    FOREIGN KEY(problem_id) REFERENCES problems(id) ON DELETE CASCADE
);
""")
    conn.commit()
    conn.close()

def add_problem(title: str, url: str, tags: Optional[str] = None):
    now = datetime.utcnow().isoformat(timespec="seconds")
    today = date.today().isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO problems (title, url, tags, created_at, next_review) VALUES (?, ?, ?, ?, ?)",
        (title.strip(), url.strip(), (tags or "").strip(), now, today)
    )
    conn.commit()
    conn.close()

def list_due_problems(today: Optional[date] = None):
    if today is None:
        today = date.today()
    today_iso = today.isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
SELECT * FROM problems
WHERE date(next_review) <= date(?)
ORDER BY date(next_review) ASC, id ASC
""", (today_iso,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_problem(problem_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_problem_after_attempt(problem_id: int, *, ef: float, reps: int, interval_days: int, next_review: date, q: int, time_spent_min: Optional[int], hints_used: Optional[int]):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat(timespec="seconds")
    cur.execute("""
UPDATE problems
SET ef=?, reps=?, interval_days=?, next_review=?, last_attempt_at=?, last_q=?, time_spent_min=?, hints_used=?
WHERE id=?
""", (ef, reps, interval_days, next_review.isoformat(), now, q, time_spent_min, hints_used, problem_id))
    conn.commit()
    conn.close()

def add_attempt(problem_id: int, q: int, time_spent_min: Optional[int], hints_used: Optional[int], notes: Optional[str] = None):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat(timespec="seconds")
    cur.execute("""
INSERT INTO attempts (problem_id, attempted_at, q, time_spent_min, hints_used, notes)
VALUES (?, ?, ?, ?, ?, ?)
""", (problem_id, now, q, time_spent_min, hints_used, notes))
    conn.commit()
    conn.close()

# ----- History / Dashboard helpers -----

def get_today_attempts(today: Optional[date] = None):
    if today is None:
        today = date.today()
    today_iso = today.isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
SELECT a.id, a.problem_id, a.attempted_at, a.q, a.time_spent_min, a.hints_used,
       p.title, p.url
FROM attempts a
JOIN problems p ON p.id = a.problem_id
WHERE date(a.attempted_at) = date(?)
ORDER BY a.attempted_at DESC
""", (today_iso,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_today_summary(today: Optional[date] = None) -> Dict[str, Any]:
    if today is None:
        today = date.today()
    today_iso = today.isoformat()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
SELECT COUNT(*) as cnt,
       AVG(q) as avg_q,
       SUM(COALESCE(time_spent_min,0)) as sum_time,
       SUM(COALESCE(hints_used,0)) as sum_hints
FROM attempts
WHERE date(attempted_at) = date(?)
""", (today_iso,))
    att = cur.fetchone()

    cur.execute("""
SELECT COUNT(*) as new_cnt
FROM problems
WHERE date(created_at) = date(?)
""", (today_iso,))
    newp = cur.fetchone()

    conn.close()
    return {
        "attempts_today": att["cnt"] or 0,
        "avg_q_today": float(att["avg_q"]) if att["avg_q"] is not None else None,
        "time_today": att["sum_time"] or 0,
        "hints_today": att["sum_hints"] or 0,
        "new_problems_today": newp["new_cnt"] or 0,
    }

def get_global_summary(today: Optional[date] = None) -> Dict[str, Any]:
    if today is None:
        today = date.today()
    today_iso = today.isoformat()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS problems_total FROM problems")
    p = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS attempts_total, AVG(q) AS avg_q_global FROM attempts")
    a = cur.fetchone()

    cur.execute("""
SELECT COUNT(*) AS due_today
FROM problems
WHERE date(next_review) <= date(?)
""", (today_iso,))
    d = cur.fetchone()

    conn.close()
    return {
        "problems_total": p["problems_total"] or 0,
        "attempts_total": a["attempts_total"] or 0,
        "avg_q_global": float(a["avg_q_global"]) if a["avg_q_global"] is not None else None,
        "due_today": d["due_today"] or 0,
    }

def list_all_problems_with_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
SELECT
  p.id, p.title, p.url, p.tags, p.next_review, p.ef, p.reps, p.last_q, p.last_attempt_at,
  COALESCE(s.avg_q, 0.0) AS avg_q,
  COALESCE(s.attempts, 0) AS attempts,
  s.last_attempt_at AS last_attempt
FROM problems p
LEFT JOIN (
  SELECT
    problem_id,
    AVG(q) AS avg_q,
    COUNT(*) AS attempts,
    MAX(attempted_at) AS last_attempt_at
  FROM attempts
  GROUP BY problem_id
) s ON s.problem_id = p.id
ORDER BY date(p.next_review) ASC, p.id ASC
""")
    rows = cur.fetchall()
    conn.close()
    return rows
