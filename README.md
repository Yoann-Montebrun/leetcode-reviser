# LeetCode Reviser (SM-2 powered)

A tiny, clean Python/Flask app to **schedule and grade your LeetCode reviews** using a lightweight adaptation of the **SM‑2 spaced-repetition algorithm**.

## Features (v1)
- **Add problems** (title + URL + optional tags) from a simple UI.
- **Daily review queue**: see what’s due today, and grade each attempt (**0–5**) to update the next review date automatically.
- Stores data locally in a tiny **SQLite** database (`leetcode.db`).

> Scheduling logic is based on SM‑2:
> - Initialize `ease_factor (EF)=2.5`, `reps=0`, `interval_days=0`.
> - After each attempt:
>   - If `q < 3`: `reps=0`, `interval=1 day`.
>   - If `q ≥ 3`:
>     - `reps += 1`
>     - If `reps == 1`: `interval=1 day`
>     - If `reps == 2`: `interval=6 days`
>     - Else: `interval = round(prev_interval * EF)`
>   - Update EF:  
>     `EF = max(1.3, EF + (0.1 - (5-q) * (0.08 + (5-q)*0.02)))`
>
> This gives short, then expanding intervals, and shrinks them after failure.

## Quickstart

```bash
# 1) Clone your repo, then inside it:
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
export FLASK_APP=app.py
export FLASK_ENV=development   # optional
flask run
# App runs on http://127.0.0.1:5000
```

## UI
- **Today**: shows due problems as tidy cards. For each, set `q` (0–5), optionally time (mins) and hints used, then **Submit**.
- **Add**: add a problem by **title**, **URL**, and optional **tags** (comma-separated).

## Data model
- Table **problems**:
  - `id`, `title`, `url`, `tags`, `created_at`
  - `ef` (ease factor), `reps`, `interval_days`, `next_review` (DATE)
  - `last_attempt_at`, `last_q`, `time_spent_min`, `hints_used`
- Table **attempts**:
  - `id`, `problem_id`, `attempted_at`, `q`, `time_spent_min`, `hints_used`, `notes`

The database is auto-created on first run.

## Grading rubric (q)
- `5`: <20 min, no help, optimal solution + correct complexity
- `4`: ≤30 min, small hint or tiny bug fixed quickly
- `3`: ≤45 min, multiple hints/hiccups but solved alone
- `2`: failed until reading the idea; solved after reading
- `1`: partial understanding even after reading
- `0`: total miss/abandon

Use whatever granularity feels right. The algorithm only requires **q ∈ [0..5]**.

## Roadmap (next)
- Tag-based interleaving and custom filters.
- Horizon-aware interval compression (e.g., 8–10 week interview prep).
- Import/export (CSV/JSON).
- Dark mode & keyboard-driven grading.

---

Made for focused, honest practice: **attempt → grade → schedule**. Happy grinding!
