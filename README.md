# LeetCode Reviser (SM-2 powered)

A tiny, clean Python/Flask app to **schedule and grade your LeetCode reviews** using a lightweight adaptation of the **SM-2** spaced-repetition algorithm.

## Features (v1)
- **Add problems** (title + URL + optional tags) from a simple UI.
- **Daily review queue**: see what’s due today, and grade each attempt (**0–5**) to update the next review date automatically.
- **History / Dashboard** page:
  - Today summary (attempts, avg q, time, hints, new problems)
  - Today activity (each attempt card)
  - Global KPIs (total problems, due today, attempts, avg q)
  - Full table: next review, last q, avg q, attempts, EF, reps, last attempt
- Stores data locally in **SQLite** (`leetcode.db`).

## Scheduling (SM-2)
- If `q < 3`: `reps=0`, `interval=1 day`
- If `q ≥ 3`:
  - `reps += 1`
  - `reps==1 → 1 day`, `reps==2 → 6 days`, else `interval = round(prev_interval * EF)`
- `EF = max(1.3, EF + (0.1 - (5-q)*(0.08 + (5-q)*0.02)))`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
# http://127.0.0.1:5000
```
