"""
curriculum.py — the 30-day CodeQuest curriculum.

Each day has:
- title: short name
- goal: what the learner achieves
- concept: the core CS/AI concept
- task: the specific coding task
- challenge: optional bonus challenge

The full data lives in curriculum_data.py (imported here for convenience).
"""

from curriculum_data import CURRICULUM


def get_day(n):
    """Return the curriculum entry for day n (1-30)."""
    if n < 1 or n > 30:
        raise ValueError(f"Day must be 1-30, got {n}")
    return CURRICULUM[n - 1]


def get_all_days():
    """Return the full 30-day curriculum list."""
    return list(CURRICULUM)


def get_days_by_goal(goal):
    """Filter curriculum days by goal string."""
    return [d for d in CURRICULUM if d["goal"].lower() == goal.lower()]


def search_curriculum(query):
    """Simple text search across title, goal, concept, and task."""
    q = query.lower()
    results = []
    for d in CURRICULUM:
        haystack = " ".join([d["title"], d["goal"], d["concept"], d["task"]]).lower()
        if q in haystack:
            results.append(d)
    return results


if __name__ == "__main__":
    print(f"CodeQuest 2 — {len(CURRICULUM)} days")
    print("=" * 50)
    for day in CURRICULUM:
        print(f"  Day {day['n']:>2}: {day['title']}  [{day['concept']}]")
