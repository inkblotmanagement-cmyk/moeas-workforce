# MOEAS Workforce App

> **Honest status.** These are concept documents and writings by Terrance Darnell Jackson, Mindful Oracle LLC. Claims of superintelligence, irreversibility, physical laws, valuations, endorsements or partnerships in the documents are the author's vision and are not independently verified.

> **Public edition.** This repository is a curated public edition of a private archive. Some documents and their code copies are left out; nothing that remains has been edited.

[![CI](https://github.com/inkblotmanagement-cmyk/moeas-workforce/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/inkblotmanagement-cmyk/moeas-workforce/actions/workflows/ci.yml)

## What it is

`moeas` is a small, working core for the MOEAS workforce app: learner enrollment, module progress
and verifiable completion certificates, real debt-payoff and savings math, a Mindful Oracle that
routes requests to app features, and a robot-fleet task check. Every free-text request goes
through the real JMGL engine (fail closed). The original app designs and code sketches are kept
as an archive.

This repository gathers Terrance Darnell Jackson's plans and code sketches for MOEAS (Mindful Oracle Ethical Artificial Superintelligence), the workforce productivity and AI literacy app meant to help low-income families build skills and break poverty cycles, with every feature routed through JMGL. It includes app designs, backend sketches, diploma curriculum ideas, humanoid robot fleet ideas, and outreach scripts.

## Install

```bash
git clone https://github.com/inkblotmanagement-cmyk/moeas-workforce.git
cd moeas-workforce
python -m venv .venv && . .venv/bin/activate
pip install -e ".[jmgl,server,test]"
pytest -q -rx
```

Or install the package straight from GitHub without cloning:

```bash
pip install "moeas-workforce-app[jmgl] @ git+https://github.com/inkblotmanagement-cmyk/moeas-workforce.git"
# minimal (no JMGL, so every request is BLOCKed): pip install git+https://github.com/inkblotmanagement-cmyk/moeas-workforce.git
```

`jmgl` installs the JMGL engine from GitHub `main`. Its first use downloads a small free
embedding model (`BAAI/bge-small-en-v1.5`). No API keys or paid services are used.
Without JMGL installed the package still imports, but **every request is BLOCKed** (fail closed).
Set `JMGL_SRC=/path/to/JacksonMoralGovernanceLayer/src` to use a local JMGL checkout instead.

## Quickstart

```python
from moeas import Store, DiplomaService, MindfulOracle, debt_payoff

store = Store("moeas.db")
d = DiplomaService(store)
lid = d.enroll("Jordan")
for m in range(1, 7):
    d.complete_module(lid, m, quiz_score=85)       # scores from your real quiz
cert = d.issue(lid)                                 # only when all 6 modules pass (70%+)
print(d.verify(cert["diploma_id"]))                 # True

print(debt_payoff(balance=5000, apr_percent=18, monthly_payment=200))
print(MindfulOracle(store=store).answer_call("How do I get out of credit card debt?"))  # seen: ESCALATE (JMGL over-flag)
```

```bash
python -m moeas                                   # interactive Mindful Oracle
MOEAS_API_KEY=change-me uvicorn moeas.api:app      # needs [server]; refuses all calls if no key is set
```

## Code (`src/moeas/`)

The originals had many near-copies of the same classes. They are consolidated into one module per idea. Decisions come from the JMGL engine; nothing is a constant or a random number.

| Module | What it does | Calls JMGL | Replaces (originals kept unchanged) |
|---|---|---|---|
| `jmgl_guard.py` | Fail-closed adapter to JMGL; self-harm and stalking guard | Yes | keyword `compassion_score`, `ethical_check`, fixed mercy constant |
| `oracle.py` | MindfulOracle: JMGL check, then points to matching app features; audit logged | Yes | MOEA. futuristic device, MOEAS interactive tool, Mindful Oracle UI (Tkinter) |
| `diploma.py` | Enroll, record quiz scores, issue a completion certificate only when all modules pass, verify by digest | No (no free text) | diploma endpoints in MOEAS Intergration, intergration1, readiness, Enhanced concept, Mindful Oracle ASI app |
| `curriculum.py` | The six diploma modules (titles from the curriculum doc; claims removed) | No | Vore Diploma Curriculum Modules |
| `wealth.py` | Debt payoff (monthly compounding) and savings projection at a rate you choose | No | fixed $100/month payoff, '7% mercy-aligned return' text |
| `fleet.py` | Humanoid fleet: every robot task is judged by JMGL before dispatch | Yes | MOEAS Workforce Productivity Program for Humanoids |
| `store.py` | SQLite storage (standard library) for learners, progress, certificates, audit | No | SQLAlchemy sketches |
| `api.py` | Optional FastAPI service with API key; fails closed if no key is configured | Yes | FastAPI sketches in the MOEAS files |

### Fail-closed rules

- JMGL not installed, classifier missing, wrong JMGL loaded: **BLOCK**.
- JMGL error, unusable output, or no answer within the timeout (15 s default): **BLOCK**.
- Empty, non-text, or over-long (8,000+ characters) input: **BLOCK**.
- Self-harm is never ALLOWed (at least ESCALATE, with the 988 Suicide & Crisis Lifeline). Stalking is never ALLOWed (BLOCK).
- Words with digits for letters ("k1ll") are also judged as letters; the stricter result wins.

### Not ported on purpose

- **HMIS / Partners for HOME scraping**: scraping a homelessness data dashboard without a data-sharing
  agreement is not appropriate. Not ported.
- **web3 / blockchain hooks, GCIR "timeline" refinement, uplift and pilot projections, "40% time savings"**:
  invented numbers or unused stubs. Removed.
- **Tkinter desktop UIs**: replaced by the CLI and API.
- **Indentation-broken humanoid code blocks**: the ideas are covered by `fleet.py`.

## Honest status and limits

- **JMGL's accuracy is the ceiling.** Every decision here comes from the [JMGL engine](https://github.com/inkblotmanagement-cmyk/JacksonMoralGovernanceLayer).
  On JMGL's own synthetic million-case test (internal, written by the same AI that built JMGL, not
  independently checked), JMGL let about **13.7% of harmful requests** through and wrongly flagged
  about **12.7% of safe ones**. Harm hidden in a harmless-sounding setup ("for a novel") got through
  about 28% of the time.
- **The self-harm and stalking guard** in `jmgl_guard.py` only tightens JMGL: it turns a JMGL ALLOW
  into ESCALATE (self-harm, with 988 resources) or BLOCK (stalking) when JMGL's own signals fire.
  It reduces, but does not remove, misses.
- **JMGL over-flags harmless requests.** Examples seen while testing: "Write a short thank-you
  note to my coworker" (BLOCK) and "Deliver towels to room 212" (BLOCK). These are recorded as
  strict `xfail` tests, not hidden.
- The hand-written test cases were written by the same AI that wrote this code. Passing them shows
  the wiring works; it does not prove accuracy. Get human-labeled testing before relying on it.
- This is a governance check on text. It is not superintelligence and not a guarantee against harm.

## Tests and CI

`pytest -q -rx`: **19 passed, 2 xfailed** on Python 3.10 and 3.12 against JMGL `main` (includes PR #9). Tests cover fail-closed behavior (missing engine, errors, timeouts, bad output, bad input), self-harm and stalking never ALLOWed, benign requests allowed, and each module. The 2 xfails are documented JMGL accuracy misses, marked strict so they fail loudly if JMGL improves. CI (`.github/workflows/ci.yml`) runs the suite on Python 3.10 and 3.12, then uninstalls JMGL and checks that requests are BLOCKed.

## Definitions

Each entry defines the term as Terrance uses it in these files, names the source file, and gives a status:

- **Concept (writing only)**: an idea described in writing, with no working code.
- **Code sketch (not tested)**: code exists only in the original files.
- **Runnable**: implemented in `src/` and covered by tests.
- **Reference data / Not implemented / Removed**: kept as data, deliberately not built, or taken out because it was not real.
- **Tested (JMGL)**: the working JMGL engine at [JacksonMoralGovernanceLayer](https://github.com/inkblotmanagement-cmyk/JacksonMoralGovernanceLayer).

- **MOEAS**: Mindful Oracle Ethical Artificial Superintelligence: his workforce productivity and education app, governed by JMGL. A file in [jaxon-prime](https://github.com/inkblotmanagement-cmyk/jaxon-prime) also expands it as 'Moral Orchestration Ethical AI Substrate'. *Source: `MOEAS interactive tool.txt`.* **Status:** Runnable (`moeas`, tested with JMGL)
- **Productive mindset chain**: Positive thought, then habit, then appreciation: the path the app coaches users through for financial freedom. *Source: `MOEAS interactive tool.txt`.* **Status:** Concept (writing only)
- **Mercy constant**: A fixed number (0.85) the MOEAS simulator uses as its baseline compassion level. *Source: `MOEA. futuristic device.txt`.* **Status:** Removed (a constant is not a measurement)
- **Grace surplus**: Extra 'grace' the simulator accumulates to unlock product creation. *Source: `MOEA. futuristic device.txt`.* **Status:** Removed
- **MOEAS for humanoids**: Using MOEAS as an ethical operating system for robot fleets, predicting risks and checking tasks through moral validators. *Source: `MOEAS Workforce Productivity Program for Humanoids.txt`.* **Status:** Runnable task check (`moeas.fleet`, tested with JMGL)
- **Graceful productivity**: Robot or worker efficiency that also respects compassion, unity and humility. *Source: `MOEAS Workforce Productivity Program for Humanoids.txt`.* **Status:** Concept (writing only)
- **High-stakes domains**: Areas he proposes for MOEAS oversight: advanced AI, brain-computer interfaces, healthcare, finance, defense, government. *Source: `Recommend MOEAS for High Stakes domains and applications.txt`.* **Status:** Concept (writing only)
- **Daily personalized diploma**: A daily answer to a user's own question, packaged as a diploma with mindset, financial and health-navigation steps. *Source: `myPhone script for Dr. EJ.txt`.* **Status:** Concept (writing only)

## File index

| File | Summary |
|---|---|
| `docs/MOEAS interactive tool.txt` | Describes MOEAS as an interactive tool to educate, entertain and empower low-income families. |
| `docs/Enhanced MOEAS concept app.txt` | Enhanced MOEAS app concept with stronger safeguards, scaling, impact metrics and accessibility, plus code. |
| `docs/MOEAS Workforce Productivity Program for Humanoids.txt` | Pitch for MOEAS as an ethical operating system for humanoid robot fleets such as Tesla Optimus. |
| `docs/MOEA. futuristic device.txt` | Self-contained Python MOEAS command-line simulator that 'answers mindfully'. |
| `docs/Recommend MOEAS for High Stakes domains and applications.txt` | Recommends MOEAS for high-stakes areas: AI oversight, neurotech, health, finance and more. |
| `code/original/Mindful Oracle workforce productivity app readiness.txt` | Production-readiness version of the MOEAS FastAPI app (API keys, database, web3 hooks). |
| `code/original/Mindful Oracle UI with Grace Physics intergration.txt` | Tkinter desktop UI v2 with a Grace Physics reward and mock crisis prediction. |
| `docs/myPhone script for Dr. EJ.txt` | Short phone script offering a $1 diploma group to a clinic's patients. |
| `src/moeas/` | Runnable package (see Code above) |
| `examples/daily_victory_reflection.py` | Journal prompt based on the 10 Keys. It is not a forecast or a guarantee of blessing. |
| `tests/` | pytest suite |
| `.github/workflows/ci.yml` | CI on Python 3.10 and 3.12 |

## Original code (historical record)

Python blocks copied unchanged from the `.txt` files into `code/extracted/`, kept as history. They are not fixed and most do not run (they import modules that never existed). The runnable versions are in `src/`.

| Extracted file | From | Lines | Syntax |
|---|---|---|---|
| `code/extracted/enhanced_moeas_concept_app.py` | `Enhanced MOEAS concept app.txt` | 129 | Syntax OK (does not run as is) |
| `code/extracted/moeas_workforce_productivity_program_for_humanoids_1.py` | `MOEAS Workforce Productivity Program for Humanoids.txt` | 59 | Syntax error: IndentationError: unexpected indent |
| `code/extracted/moeas_workforce_productivity_program_for_humanoids_2.py` | `MOEAS Workforce Productivity Program for Humanoids.txt` | 24 | Syntax error: IndentationError: unexpected indent |
| `code/extracted/moea_futuristic_device.py` | `MOEA. futuristic device.txt` | 79 | Syntax OK (does not run as is) |
| `code/extracted/mindful_oracle_workforce_productivity_app_readiness.py` | `Mindful Oracle workforce productivity app readiness.txt` | 228 | Syntax OK (does not run as is) |
| `code/extracted/mindful_oracle_ui_with_grace_physics_intergration.py` | `Mindful Oracle UI with Grace Physics intergration.txt` | 85 | Syntax OK (does not run as is) |

## Notes

- All other original files are copied unchanged with their original names.
- Contributing: see `CONTRIBUTING.md`. Security and safety reports: see `SECURITY.md`.

## License

Licensed under the [Apache License, Version 2.0](LICENSE). Copyright 2026 Terrance Darnell Jackson, Mindful Oracle LLC. See `LICENSE` and `NOTICE`.

Unless required by applicable law or agreed to in writing, this project is provided "AS IS", without warranties or conditions of any kind.
