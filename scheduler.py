from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta

MIN_EF = 1.3

def update_ease_factor(ef: float, q: int) -> float:
    """
    SM-2 EF update.
    q in [0..5]
    """
    if q < 0: q = 0
    if q > 5: q = 5
    new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    return max(MIN_EF, new_ef)

@dataclass
class ReviewState:
    ef: float
    reps: int
    interval_days: int  # previous interval
    next_review: date

def schedule_after_attempt(state: ReviewState, q: int, today: date | None = None) -> ReviewState:
    """
    Apply SM-2 style update based on quality q and return new state.
    """
    if today is None:
        today = date.today()

    ef = update_ease_factor(state.ef, q)

    if q < 3:
        reps = 0
        interval = 1
    else:
        reps = state.reps + 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = max(1, round(state.interval_days * ef))

    next_review = today + timedelta(days=interval)
    return ReviewState(ef=ef, reps=reps, interval_days=interval, next_review=next_review)
