# Contributing

Thank you for your interest. This repository belongs to Terrance Darnell Jackson, Mindful
Oracle LLC. It is licensed under the Apache License, Version 2.0 (see
`LICENSE` and `NOTICE`). By submitting a contribution you agree it is licensed under
Apache-2.0 as well (section 5 of the License). Contributions are welcome by
invitation; open an issue first to discuss a change.

## Ground rules

- **Keep the original writings unchanged.** Files in `docs/`, `code/original/` and
  `code/extracted/` are the historical record. Fixes go in `src/`.
- **Decisions come from real input.** Any score or decision must be computed from the
  actual request (through the JMGL engine). No constants, random numbers or invented
  metrics presented as results. If something is a simulation, say so in the name and output.
- **Fail closed.** If the JMGL engine is missing, errors, times out or returns something
  unusable, the answer is BLOCK.
- **Self-harm and stalking are never ALLOWed.** Self-harm responses include the 988
  Suicide & Crisis Lifeline (US). Changes may only make these checks stricter.
- **No self-training that drifts toward approval.** Learning components may only learn from
  human-labeled data and may only tighten a decision.
- **Honest claims.** Do not add claims of superintelligence, guaranteed safety, medical
  effects, endorsements, partnerships or valuations that are not backed by evidence.

## Running the tests

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[jmgl,server,test]"
pytest -q -rx
```

Tests use the real JMGL engine (installed from GitHub `main`). Cases JMGL is known to get
wrong are marked `xfail(strict=True)` with the reason, instead of being special-cased in
code. If JMGL improves and one starts passing, remove the marker.

## Style

Plain language in docs. Python 3.10+. Keep heavy dependencies (torch, web servers)
optional.
