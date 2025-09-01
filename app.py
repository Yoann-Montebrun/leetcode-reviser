from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from db import init_db, add_problem, list_due_problems, get_problem, update_problem_after_attempt, add_attempt
from scheduler import ReviewState, schedule_after_attempt

app = Flask(__name__)
app.secret_key = "dev-secret"  # replace for production

# Ensure DB exists
init_db()

@app.template_filter("none_to_dash")
def none_to_dash(value):
    return "-" if value in (None, "", 0) else value

@app.route("/")
def home():
    today = date.today()
    due = list_due_problems(today)
    return render_template("index.html", problems=due, today=today)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        url = (request.form.get("url") or "").strip()
        tags = (request.form.get("tags") or "").strip()
        if not title or not url:
            flash("Title and URL are required.", "error")
            return redirect(url_for("add"))
        try:
            add_problem(title, url, tags)
            flash("Problem added.", "success")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("add"))
    return render_template("add.html")

@app.route("/grade/<int:problem_id>", methods=["POST"])
def grade(problem_id: int):
    # Get current state
    row = get_problem(problem_id)
    if not row:
        flash("Problem not found.", "error")
        return redirect(url_for("home"))

    try:
        q = int(request.form.get("q", ""))
    except ValueError:
        q = 0

    # Optional metrics
    ts = request.form.get("time_spent_min", "").strip()
    hints = request.form.get("hints_used", "").strip()
    time_spent_min = int(ts) if ts.isdigit() else None
    hints_used = int(hints) if hints.isdigit() else None

    # Build state and schedule
    state = ReviewState(
        ef=float(row["ef"]),
        reps=int(row["reps"]),
        interval_days=int(row["interval_days"]),
        next_review=date.fromisoformat(row["next_review"])
    )
    new_state = schedule_after_attempt(state, q, today=date.today())

    # Persist
    update_problem_after_attempt(
        problem_id,
        ef=new_state.ef,
        reps=new_state.reps,
        interval_days=new_state.interval_days,
        next_review=new_state.next_review,
        q=q,
        time_spent_min=time_spent_min,
        hints_used=hints_used
    )
    add_attempt(problem_id, q, time_spent_min, hints_used)
    flash(f"Saved. Next review on {new_state.next_review.isoformat()}", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
