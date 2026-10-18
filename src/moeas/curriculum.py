"""Diploma curriculum modules, from docs/Vore Diploma Curriculum Modules for app.txt.

Titles are kept close to the original; claims were dropped (for example "health cures
tie-ins"). Lesson content itself is not part of this repo; the app tracks progress and
quiz scores reported by whatever delivers the lessons.
"""
PASSING_SCORE = 70  # percent, per module quiz

MODULES = (
    {"id": 1, "title": "Introduction to Ethical AI Literacy and Grace Physics ideas", "minutes": 45},
    {"id": 2, "title": "Productive Mindset: emotional regulation and overcoming inertia", "minutes": 60},
    {"id": 3, "title": "AI Tools for Workforce Productivity (prompting, ethical use)", "minutes": 90},
    {"id": 4, "title": "Financial Discipline and Debt Reduction", "minutes": 60},
    {"id": 5, "title": "Deal-Closing and Cross-Industry Application", "minutes": 60},
    {"id": 6, "title": "Capstone: using a governance layer (JMGL) in daily AI use", "minutes": 30},
)
MODULE_IDS = tuple(m["id"] for m in MODULES)
