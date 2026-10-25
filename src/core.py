"""
core.py — shared game-loop state, scoring, and persistence for CodeQuest.

No external dependencies (stdlib only). Works on Windows, macOS, and Linux.
"""

import json
import os
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(os.path.expanduser("~"), ".codequest")
SAVE_PATH = os.path.join(SAVE_DIR, "save.json")


def _ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
DEFAULT_STATE = {
    "day": 1,
    "score": 0,
    "streak": 0,
    "xp": 0,
    "completed_days": [],
    "settings": {
        "theme": "dark",
        "sound": True,
        "auto_save": True,
    },
}


def load_state():
    """Load player state from disk (or return defaults)."""
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new fields don't crash old saves
        merged = dict(DEFAULT_STATE)
        merged.update(data)
        return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_STATE)


def save_state(state):
    """Persist player state to disk."""
    _ensure_save_dir()
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def complete_day(state, day_number, score=100):
    """Mark a day as completed and update stats."""
    if day_number not in state["completed_days"]:
        state["completed_days"].append(day_number)
    state["day"] = day_number + 1
    state["score"] += score
    state["xp"] += score
    state["streak"] += 1
    return state


def reset_state():
    """Wipe saved progress and return a fresh state."""
    state = dict(DEFAULT_STATE)
    save_state(state)
    return state


def get_progress_percent(state):
    """Return completion percentage (out of 30 days)."""
    total_days = 30
    completed = len(state["completed_days"])
    return round((completed / total_days) * 100, 1)


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------
def score_answer(correct, time_spent_s, difficulty=1):
    """Compute a score for a single answer.
    
    correct: bool
    time_spent_s: seconds the player took
    difficulty: 1-3 multiplier
    """
    if not correct:
        return 0
    
    base = 100
    # Time bonus: faster = more points (cap at 50% bonus)
    time_bonus = max(0, int(50 - (time_spent_s / 60)))
    return int((base + time_bonus) * difficulty)


# ---------------------------------------------------------------------------
# Logging / audit
# ---------------------------------------------------------------------------
def log_action(action, details=None):
    """Append an action to a simple log file (for debugging)."""
    log_path = os.path.join(SAVE_DIR, "actions.log")
    _ensure_save_dir()
    ts = datetime.now().isoformat()
    line = f"[{ts}] {action}"
    if details:
        line += f" | {json.dumps(details, default=str)}"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
