# Automation, the standard library & tooling

From Al Sweigart's *Automate the Boring Stuff with Python* (practical scripting for non-engineers and engineers alike) plus the standard-library and tooling stack every Python project needs.

## Practical scripting patterns (Automate the Boring Stuff)

The book's value is a catalogue of "glue" tasks — wiring stdlib + a few packages to automate real chores. The Pythonic versions:

- **Files & folders** — use **`pathlib.Path`** (`Path.home()`, `/` operator, `.glob`/`.rglob`, `.read_text`/`.write_text`, `.exists`, `.mkdir(parents=True, exist_ok=True)`). Use **`shutil`** for copy/move/rmtree, **`zipfile`** for archives, **`os`/`os.walk`** only when `pathlib` doesn't cover it. Use **`tempfile`** for scratch files.
- **Reading/writing data** — **`csv`** (use `DictReader`/`DictWriter`), **`json`** (`load`/`dump`, `indent=2`), **`tomllib`** (read TOML config, 3.11+), `configparser` for INI. For Excel use **`openpyxl`**; PDFs use **`pypdf`**; Word uses **`python-docx`**.
- **Regular expressions** — **`re`**: `compile`, `search`/`match`/`fullmatch`, `findall`/`finditer`, groups (named `(?P<name>...)`), `sub`. Use **raw strings** `r"..."`; prefer `re.VERBOSE` for complex patterns; don't parse HTML with regex (use a parser).
- **Web** — **`requests`** for HTTP (or stdlib `urllib`), **`BeautifulSoup`** (`bs4`) for HTML parsing, browser automation via Selenium/Playwright when JS rendering is required. Respect robots/rate limits ([[secure-coding]] — validate/escape anything you act on).
- **Sending output** — email via `smtplib`/`email` (or an API); spreadsheets/PDFs as above; logging via the **`logging`** module (not `print`) with levels and handlers.
- **Time & scheduling** — **`datetime`**/`time`/`zoneinfo`; `time.sleep` for simple pauses; for recurring jobs prefer the OS scheduler (cron / Task Scheduler / launchd) or a library (`APScheduler`) over a long-running sleep loop.
- **CLI scripts** — parse args with **`argparse`** (or `click`/`typer`); read input/secrets from **env vars** / a config file, never hard-code; use `sys.exit(code)` and exit codes; guard entry points with `if __name__ == "__main__":`.
- **Robustness for automation** — wrap fragile IO in `try/except` with specific exceptions; log failures; make scripts **idempotent** and safe to re-run; back up before destructive operations; dry-run flags.

## Standard library worth knowing (beyond the above)

- **`collections`** — `defaultdict`, `Counter`, `deque`, `namedtuple`, `ChainMap`, `OrderedDict`.
- **`itertools`** & **`functools`** — lazy iteration toolkit and function utilities (see data-model reference).
- **`dataclasses`**, **`enum`**, **`typing`** — modeling.
- **`contextlib`** — `contextmanager`, `suppress`, `closing`, `ExitStack`.
- **`subprocess`** — run external commands (`subprocess.run(..., check=True, capture_output=True)`; pass a list, avoid `shell=True` with untrusted input — [[secure-coding]]).
- **`concurrent.futures`**, **`asyncio`**, **`multiprocessing`**, **`threading`**, **`queue`** — concurrency.
- **`unittest`/`unittest.mock`**, **`doctest`** — testing; **`logging`**, **`argparse`**, **`os`/`sys`**, **`math`/`statistics`/`random`/`decimal`/`fractions`**, **`hashlib`/`secrets`** (use `secrets`, not `random`, for tokens — [[cryptography]]).

## Tooling stack (set this up for any project)

- **Environments**: **`venv`** (`python -m venv .venv && source .venv/bin/activate`); install with **`pip`** and pin in `requirements.txt` or, better, a **`pyproject.toml`** with a lock (uv / Poetry / PDM). Never install into system Python. **`uv`** is the modern fast resolver/installer worth adopting.
- **Formatting & linting**: **`black`** (or `ruff format`) for formatting; **`ruff`** for linting (fast, replaces flake8/isort/pyupgrade and more). Run in CI and pre-commit.
- **Type checking**: **`mypy`** or **`pyright`** on annotated code; treat type errors like build errors.
- **Testing**: **`pytest`** (fixtures, parametrize, `assert` rewriting) — see [[tdd]]; coverage via `pytest-cov`; property-based testing via `hypothesis`.
- **Pre-commit**: the **`pre-commit`** framework to run ruff/black/mypy/tests on commit.
- **Packaging & distribution**: **`pyproject.toml`** ([PEP 621] metadata) + a build backend (hatchling/setuptools/flit); build with `python -m build`, publish with `twine`/`uv publish`. Use semantic versioning.
- **Project layout**: prefer the **`src/` layout** (`src/package/...`, `tests/`, `pyproject.toml`); a clear public API; `__init__.py` exports.

## Quick checklist for a new Python project

1. `python -m venv .venv` + activate; create `pyproject.toml`.
2. Add **ruff + black + mypy + pytest** (and `pre-commit`).
3. `src/` layout, type-hinted public API, docstrings.
4. EAFP error handling, `pathlib`, `logging` (not print), `argparse`/`typer` for CLIs.
5. Tests first ([[tdd]]); pin/lock deps; CI runs format-check + lint + types + tests.
