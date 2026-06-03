# Effective Python — best-practice items (grouped)

From Brett Slatkin's *Effective Python* (1st ed., "59 ways"; durable items), with **modern additions** noted where the 1st ed predates them. Grouped by the book's chapters.

## Pythonic thinking

- Know which **Python version** you target (3.x; 2 is dead); follow **PEP 8** and let a tool enforce it.
- Prefer **f-strings** for interpolation (modern; over `%` and `str.format`).
- Write **helper functions** instead of complex one-line expressions; complex expressions hurt readability.
- **Unpack** rather than index (`x, y = pair`; `first, *rest = seq`); prefer multiple-assignment unpacking over slicing/indexing.
- Prefer **`enumerate`** over `range(len(...))`; use **`zip`** to iterate multiple sequences in parallel (and `itertools.zip_longest` for uneven lengths).
- Avoid `else` blocks after `for`/`while` (confusing); know how `try/except/else/finally` compose.
- Modern: use the **walrus `:=`** to avoid repeating sub-expressions, and prefer **slicing**/`itertools` over manual loops.

## Functions

- **Prefer raising exceptions to returning `None`** (callers forget to check `None`; it's error-prone).
- **Closures capture variables by reference** and see enclosing scope read-only by default; use `nonlocal` deliberately (or, better, a small class) — don't get clever with closures over loop variables.
- Use **`*args`** and **keyword arguments** for clear, flexible signatures; provide optional behavior via keyword args with good defaults; consider **keyword-only** (and positional-only) parameters to force clarity.
- **Never use a mutable default argument** (`def f(x=[])`) — the default is created once and shared; use `None` and create inside.
- Use **`functools.wraps`** when writing decorators (preserve name/docstring/metadata).

## Comprehensions & generators

- Use **list/dict/set comprehensions** instead of `map`/`filter`+`lambda` for clarity; but **avoid more than two expressions/conditions** in one comprehension (split it).
- Prefer **generators / generator expressions** for large inputs (lazy, low memory) over building lists; `yield from` to delegate.
- Be wary that **iterators/generators are single-pass** — passing one to multiple consumers exhausts it; take a defensive copy or accept an iterable + re-create.

## Classes & inheritance

- Prefer **helper classes / `dataclasses` / `namedtuple`** over deeply nested dicts/tuples for structured data.
- Accept **functions** for simple interfaces (Python has first-class functions — you rarely need a one-method class/Strategy object; cf. [[design-patterns]]).
- Use **`@classmethod` polymorphism** to construct objects generically; use **`super().__init__`** and understand the **MRO** for multiple inheritance; prefer **composition / mix-ins** over deep inheritance.
- Make interfaces clear with **public vs `_private`** by convention (no real privacy); use **`@property`** for computed/validated attributes instead of getter/setter methods.

## Metaclasses & attributes

- Use **`@property`** and **descriptors** for reusable attribute behavior; prefer `property` over `__getattr__`/`__setattr__` unless you need dynamic attributes.
- Use **`__init_subclass__`** / class decorators for validation/registration; reach for **metaclasses** only when nothing simpler works (they're powerful and confusing — last resort).
- Use **`__slots__`** to save memory for many small instances (trade-off: no dynamic attributes).

## Concurrency & parallelism

- **Understand the GIL**: only one thread runs Python bytecode at a time, so **threads don't speed up CPU-bound** work — use **`multiprocessing`** (or C extensions) for CPU parallelism. Threads are fine for **blocking I/O**.
- Use **`concurrent.futures`** (`ThreadPoolExecutor`/`ProcessPoolExecutor`) for simple parallelism; use **`queue.Queue`** to coordinate worker threads (pipeline).
- Modern: **`asyncio`** with `async`/`await` for high-concurrency **IO-bound** code (thousands of sockets) without threads; never call blocking code directly in the event loop (offload to an executor).

## Robustness, collaboration & production

- Write **docstrings** (PEP 257) for modules/classes/functions; use **packages** to organize and define clear public APIs (`__all__`).
- Define a **root exception** for your module so callers can catch your errors precisely (and you can evolve internals).
- Know how to **break circular imports** and use **`warnings`** for migration.
- **Test** with `pytest`/`unittest` ([[tdd]]); use **`unittest.mock`** sparingly; prefer dependency injection so code is testable without mocks.
- Use **`pdb`/breakpoints** for debugging, **`cProfile`** for profiling (don't optimize on intuition), **`tracemalloc`** for memory.
- Use **`venv`** for isolated dependencies; ship reproducible environments.

## Modern additions (post-1st-ed)

`dataclasses`, **type hints** + `mypy`/`pyright`, f-strings, `pathlib`, the walrus `:=`, **`match`/`case`** pattern matching, `functools.lru_cache`/`cached_property`/`singledispatch`, `asyncio` maturity, `pyproject.toml` packaging, and modern tooling (**ruff**, **black**). (*Effective Python* 2nd ed. expands to 90 items covering many of these — the principles above still hold.)
