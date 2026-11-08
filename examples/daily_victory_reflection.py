"""Daily Victory Reflection

A journal prompt drawn from Terrance Darnell Jackson's 10 Keys
in "Get Rich and Grow Wealth: 10 Keys to Being an Effective Leader
in a Global Economy" (created 2005).

This is not a forecast, a score, or a guarantee of blessing.
Intensity is your own 1-to-10 rating of how hard today feels.
"""

from datetime import date


PRACTICES = [
    {
        "key": 1,
        "name": "Invest in people",
        "hints": ("alone", "lonely", "people", "relationship", "conflict", "unseen"),
        "question": "Who can I help, thank, or treat fairly today?",
        "step": "Send one honest note, or do one small kindness.",
    },
    {
        "key": 4,
        "name": "Use time for something of value",
        "hints": ("time", "delay", "confused", "stuck", "procrastinate", "waste"),
        "question": "What is the one useful thing I can finish today?",
        "step": "Give that task a start time and 25 focused minutes.",
    },
    {
        "key": 5,
        "name": "Care for body and stress",
        "hints": (
            "anger",
            "stress",
            "panic",
            "exhausted",
            "tired",
            "hungry",
            "pain",
        ),
        "question": "What does my body need right now: food, water, rest, or a walk?",
        "step": "Do one physical reset before you decide anything big.",
    },
    {
        "key": 6,
        "name": "Faith for perseverance",
        "hints": ("afraid", "fear", "faith", "wait", "doubt", "hope"),
        "question": "What would faithfulness look like for the next hour?",
        "step": "Take the next honest step, then rest if you need to.",
        "faith_note": (
            "Greater is He that is in you than he that is in the world. "
            "(1 John 4:4)"
        ),
    },
    {
        "key": 7,
        "name": "Conserve energy",
        "hints": ("empty", "overwhelmed", "too much", "spread thin", "burnout"),
        "question": "What can I stop, simplify, or save today?",
        "step": "Cut one drain that does not serve you or anyone else.",
    },
    {
        "key": 8,
        "name": "Master emotions and learn from the mistake",
        "hints": ("shame", "mistake", "regret", "sad", "upset", "emotion"),
        "question": (
            "What is this feeling asking me to notice, "
            "without letting it run me?"
        ),
        "step": "Name the feeling, then choose one calm action.",
    },
]


def _pick_practice(trial: str, intensity: int) -> dict:
    text = trial.lower()
    for practice in PRACTICES:
        if any(hint in text for hint in practice["hints"]):
            return practice
    if intensity >= 8:
        return next(p for p in PRACTICES if p["key"] == 5)
    if intensity >= 6:
        return next(p for p in PRACTICES if p["key"] == 8)
    return next(p for p in PRACTICES if p["key"] == 4)


def daily_victory_reflection(trial: str, intensity: int = 5) -> dict:
    """Return a reflection for today's trial. Not a prediction."""
    if not trial or not str(trial).strip():
        raise ValueError("Describe today's trial in a short sentence.")
    if not isinstance(intensity, int) or not 1 <= intensity <= 10:
        raise ValueError("intensity must be a whole number from 1 to 10.")

    practice = _pick_practice(trial, intensity)
    result = {
        "date": date.today().isoformat(),
        "kind": "reflection prompt, not a prediction",
        "trial": trial.strip(),
        "self_rated_intensity": intensity,
        "practice_today": f"Key {practice['key']}: {practice['name']}",
        "question": practice["question"],
        "next_step": practice["step"],
        "motto": "Morality first, rich second.",
    }
    if "faith_note" in practice:
        result["faith_note"] = practice["faith_note"]
    return result


if __name__ == "__main__":
    hard_day = daily_victory_reflection(
        "I feel exhausted and under a lot of stress", intensity=9
    )
    quiet_day = daily_victory_reflection(
        "A slow week of waiting and doubt", intensity=3
    )
    print(hard_day)
    print(quiet_day)
