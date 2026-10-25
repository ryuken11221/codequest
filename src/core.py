"""
core.py — game state, save/load, XP, levels, and quest progression.
Zero dependencies.
"""
import os
import json
import time

SAVE_FILE = os.path.expanduser("~/.codequest2/save.json")


def _default_state():
    return {
        "xp": 0,
        "level": 1,
        "day": 1,
        "quests_done": [],
        "badges": [],
        "streak_days": 0,
        "last_play": None,
        "total_rounds": 0,
        "settings": {
            "sound": True,
            "auto_save": True,
        },
    }


def load_state():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return _default_state()


def save_state(state):
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def add_xp(state, amount):
    state["xp"] += amount
    # level = floor(sqrt(xp/50)) + 1, so each level costs ~50*level^2 total
    target = int((state["xp"] / 50) ** 0.5) + 1
    leveled_up = False
    while state["level"] < target:
        state["level"] += 1
        leveled_up = True
    return leveled_up


def complete_quest(state, quest_id, xp_reward):
    if quest_id not in state["quests_done"]:
        state["quests_done"].append(quest_id)
    leveled = add_xp(state, xp_reward)
    state["last_play"] = time.time()
    return leveled


def xp_for_level(level):
    """Total XP required to reach a given level."""
    return int(50 * (level - 1) ** 2)


def progress_in_level(state):
    lo = xp_for_level(state["level"])
    hi = xp_for_level(state["level"] + 1)
    cur = state["xp"]
    if hi <= lo:
        return 1.0
    return max(0.0, min(1.0, (cur - lo) / (hi - lo)))
