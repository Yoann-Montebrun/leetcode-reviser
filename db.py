from __future__ import annotations
import sqlite3
from datetime import datetime, date
from pathlib import Path

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

def add_problem(title: str, url: str, tags: str | None = None):
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

def list_due_problems(today: date | None = None):
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

def update_problem_after_attempt(problem_id: int, *, ef: float, reps: int, interval_days: int, next_review: date, q: int, time_spent_min: int | None, hints_used: int | None):
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

def add_attempt(problem_id: int, q: int, time_spent_min: int | None, hints_used: int | None, notes: str | None = None):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat(timespec="seconds")
    cur.execute("""
INSERT INTO attempts (problem_id, attempted_at, q, time_spent_min, hints_used, notes)
VALUES (?, ?, ?, ?, ?, ?)
""", (problem_id, now, q, time_spent_min, hints_used, notes))
    conn.commit()
    conn.close()
