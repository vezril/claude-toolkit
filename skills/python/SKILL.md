---
name: python
description: Writing idiomatic, modern, effective Python (3.x), distilled from Slatkin's *Effective Python*, Ramalho's *Fluent Python*, and Sweigart's *Automate the Boring Stuff*. Covers Pythonic philosophy (PEP 8 / the Zen of Python, readability), the high-leverage best practices (comprehensions & generators, unpacking, default-arg pitfalls, EAFP, prefer exceptions, dataclasses, f-strings, pathlib, context managers, the walrus and match), the data model and "dunder"/special methods that make objects feel native, first-class functions/closures/decorators, iterators/generators, concurrency (the GIL, threads vs multiprocessing vs asyncio), type hints, the standard library, practical automation/scripting, and tooling (venv, pip, ruff/black, mypy, pytest, packaging). Use whenever writing, reviewing, or refactoring Python — choosing an idiom, designing a class/API, handling errors, writing comprehensions/generators, adding type hints, doing concurrency/async, scripting automation, or setting up Python tooling. Comprehensive with a Scala/FP comparison lens; complements clean-code, software-design, and tdd.
---

# Python

How to write **idiomatic, modern, effective Python (3.x)** — "Pythonic" code that's readable, correct, and leverages what the language actually offers. Distilled from **Effective Python** (best-practice items), **Fluent Python** (the deep data model / idioms), and **Automate the Boring Stuff** (practical scripting). Comprehensive, with a **Scala/FP comparison lens** since that's the toolkit's home stack.

Cross-links: [[clean-code]] / [[software-design]] (readability & design apply everywhere), [[tdd]] (pytest), [[functional-programming]] (Python's functional features and where they differ), [[secure-coding]] (input/deserialization safety), [[information-theory]]/[[operating-systems]] (Python as the lingua franca for tooling/scripts).

## Pythonic philosophy

- **Readability counts** (the Zen of Python, `import this`): explicit over implicit, simple over complex, flat over nested, "there should be one obvious way to do it." Follow **PEP 8** (style) and **PEP 257** (docstrings); let a formatter/linter enforce it.
- **EAFP over LBYL** — "easier to ask forgiveness than permission": try the operation and catch the exception, rather than pre-checking (`try: d[k] except KeyError:` over `if k in d:`). Idiomatic and often faster; ties to "prefer exceptions to error codes."
- **Duck typing & protocols** — code to behavior, not concrete types ("if it quacks like a duck…"); the data model (`__len__`, `__iter__`, …) lets your objects work with built-in functions and syntax. Modern Python adds **structural typing** via `typing.Protocol`.
- **Batteries included** — reach for the rich standard library before third-party deps.

## Highest-impact best practices (apply by default)

1. **Comprehensions & generators over manual loops** for building collections; use **generator expressions / `yield`** for large/streaming data (lazy, memory-efficient) — but don't nest comprehensions past readability.
2. **Unpacking** (`a, b = b, a`; `first, *rest = seq`; star-args) and **f-strings** for formatting — never `%`/`.format` for new code.
3. **Avoid mutable default arguments** (`def f(x, items=[])` is a classic bug — the default is shared across calls; use `None` + create inside). Likewise beware late-binding closures over loop variables.
4. **Prefer exceptions to returning `None`/sentinels** for errors; raise specific exception types; use `try/except/else/finally` precisely and never bare `except:`.
5. **Use `dataclasses`** (or `attrs`/`pydantic`) for data-holding classes instead of hand-written `__init__`/`__repr__`/`__eq__`; reach for `enum.Enum` for closed sets, `namedtuple`/`NamedTuple` for lightweight records.
6. **`pathlib.Path`** for filesystem paths (not `os.path` string-mangling); **context managers (`with`)** for resources (files, locks, connections) — write your own with `contextlib.contextmanager`.
7. **Type hints everywhere** (PEP 484+): annotate function signatures and key data; check with **mypy/pyright**. Hints are documentation + tooling, not runtime enforcement.
8. **Iterate idiomatically** — `enumerate`, `zip`, `items()`, `itertools`; never `for i in range(len(x))`. Prefer the built-ins (`any`, `all`, `sorted`, `sum`, `map`/`filter` — though comprehensions usually read better).
9. **Know the modern syntax**: the **walrus** `:=` (assignment expressions), **structural pattern matching** `match/case` (3.10+), keyword-only/positional-only params, `functools` (`lru_cache`, `partial`, `singledispatch`).
10. **Virtual environments always** (`venv`); pin dependencies; never `pip install` into the system Python.

## Modern Python (postdates Effective Python 1st ed — use these)

f-strings, `dataclasses`, `pathlib`, the walrus operator, `match`/`case` structural pattern matching, `asyncio`/`async`-`await`, modern type hints (`list[int]`/`X | None` syntax, `Protocol`, `TypedDict`, generics), `functools.cached_property`, `tomllib`, and `pyproject.toml`-based packaging. (Effective Python's 1st-ed items remain sound; these are the additions.)

## Scala / FP comparison lens

Python and Scala/FP overlap and diverge in instructive ways:
- **First-class functions, closures, comprehensions, generators, decorators** map cleanly to FP ideas; `functools.reduce`/`map`/`filter` exist, but Python favors comprehensions and is **not** expression-oriented or lazy by default.
- **Immutability is opt-in, not the default** — Python objects are mutable; use tuples, `frozenset`, frozen dataclasses (`@dataclass(frozen=True)`), and discipline to get the [[functional-programming]] benefits. The "no mutable default arg" trap is the cost of mutable-by-default.
- **Errors as values vs exceptions** — Python is exception-first (EAFP); there's no built-in `Either`/`Option` (use exceptions, or `Optional[T]` + `None`, or a result library). Contrast [[functional-programming]]/[[scala]] errors-as-values.
- **Types are gradual & structural** (`Protocol`) vs Scala's nominal+structural static system; Python hints don't make illegal states unrepresentable the way Scala ADTs do — use `Enum`/dataclasses/`Literal` to approximate.
- **Pattern matching** (`match`) is newer and less exhaustive-checked than Scala's; pair with types.

## Anti-patterns (flag in review)

- Mutable default arguments; bare `except:`; catching `Exception` and swallowing it; using exceptions for normal control flow gratuitously.
- `for i in range(len(x)): x[i]` instead of iterating/`enumerate`; building a list with `.append` in a loop where a comprehension fits; manual string concatenation in loops.
- `%`/`.format` over f-strings; `os.path` string mangling over `pathlib`; not using `with` for resources.
- Hand-rolled `__init__/__repr__/__eq__` where a `dataclass` fits; `from module import *`; mutable global state.
- No virtualenv / unpinned deps; no type hints on public APIs; threads for CPU-bound work (the GIL — use multiprocessing); blocking calls inside `asyncio`.
- `eval`/`pickle` on untrusted input ([[secure-coding]]); `assert` for runtime validation (stripped under `-O`).

## How to use this skill

- **`references/effective-python.md`** — the *Effective Python* best-practice items grouped (Pythonic thinking, functions, classes & inheritance, metaclasses/attributes, concurrency & the GIL, robustness, collaboration/production), plus the modern additions.
- **`references/data-model-and-fluency.md`** — *Fluent Python*: the data model & special (dunder) methods, sequences/dicts/sets, first-class functions/closures/**decorators**, **iterators & generators**, context managers, **concurrency & asyncio**, and type hints in depth.
- **`references/automation-and-stdlib.md`** — *Automate the Boring Stuff* + the standard library: files/`pathlib`, regex, CSV/JSON/Excel/PDF, web scraping (`requests`/`BeautifulSoup`), scheduling/automation, and the tooling stack (venv, pip, ruff/black, mypy, pytest, packaging).

## Always-apply defaults

1. **Pythonic, readable, PEP 8-clean** ([[clean-code]]); let **ruff/black** format and lint, **mypy/pyright** type-check.
2. **Type-hint public APIs**; use **dataclasses/enums** to model data; prefer comprehensions/generators and the standard library.
3. **EAFP + specific exceptions**; resources via `with`; paths via `pathlib`.
4. **venv + pinned deps + `pyproject.toml`**; test with **pytest** ([[tdd]]).
5. Match concurrency to the workload: **asyncio** for IO-bound concurrency, **multiprocessing** for CPU-bound (the GIL serializes threads); threads only for blocking-IO simplicity.

## Related

- [[clean-code]] / [[software-design]] — readability and design principles applied to Python.
- [[tdd]] — pytest-based test-first development.
- [[functional-programming]] / [[scala]] — the comparison lens (immutability, errors-as-values, types).
- [[secure-coding]] — safe input handling, no `eval`/`pickle` on untrusted data.
- Sources: *Effective Python* (Brett Slatkin), *Fluent Python* (Luciano Ramalho), *Automate the Boring Stuff with Python* (Al Sweigart); PEP 8 / PEP 20 / typing PEPs.
