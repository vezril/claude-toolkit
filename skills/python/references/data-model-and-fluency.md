# Fluent Python — the data model & idioms

From Luciano Ramalho's *Fluent Python* (2nd ed., modern Python 3.10+). The book's thesis: **lean on Python's data model** (the special/"dunder" methods) so your objects integrate with the language's syntax and built-ins, and use the rich functional and concurrency features deliberately.

## The Python data model (special / "dunder" methods)

The interpreter calls `__dunder__` methods to implement syntax. Implement them so your objects behave like built-ins:
- **Object representation**: `__repr__` (unambiguous, for developers — always implement), `__str__` (readable, for users), `__format__`, `__bytes__`.
- **Collections / sequences**: `__len__`, `__getitem__` (enables indexing, slicing, iteration, and `in` for free), `__setitem__`, `__contains__`, `__iter__`.
- **Numeric / operators**: `__add__`, `__mul__`, `__eq__`, `__hash__` (define together — objects equal must hash equal; needed for dict/set keys), `__lt__` et al. (or `functools.total_ordering`).
- **Callable**: `__call__` makes an instance behave like a function. **Context manager**: `__enter__`/`__exit__`.
- **Attribute access**: `__getattr__`/`__setattr__`/`__getattribute__`, descriptors (`__get__`/`__set__`).

Key lesson: a "Pythonic" object is one that uses the data model rather than ad-hoc methods (`obj.size()` → `len(obj)`; `obj.get(i)` → `obj[i]`).

## Data structures

- **Sequences**: list vs tuple (tuple as immutable record *and* as immutable list); **slicing** semantics; `+`/`*`; `list.sort` (in place) vs `sorted` (new); `bisect` for ordered inserts; **`array`/`memoryview`/`collections.deque`** when lists aren't ideal.
- **Unpacking**: `*` in assignments and calls; nested unpacking; in `match` patterns.
- **Dicts & sets**: dict comprehensions; `dict.setdefault`, **`collections.defaultdict`**, `__missing__`; **`collections.Counter`**, `ChainMap`; views; dicts are **insertion-ordered** (3.7+); sets & frozensets and set algebra. Understand hashability.
- **Text vs bytes**: `str` (Unicode) vs `bytes`; always **encode/decode at the boundaries**; be explicit about encodings (default to UTF-8).

## First-class functions

- Functions are objects: pass them, return them, store them. **Higher-order functions**; `map`/`filter`/`reduce` (but comprehensions/generators usually read better); `sorted(key=...)`.
- **`lambda`** for tiny anonymous functions only. The nine flavors of callable (functions, methods, classes, instances with `__call__`, generators, …).
- **`functools`**: `partial` (freeze args), `reduce`, **`lru_cache`/`cache`** (memoize), **`singledispatch`** (function overloading on first-arg type), `wraps`.
- **Closures & `nonlocal`**: free variables captured by reference; the classic averager/counter example; why you need `nonlocal` to rebind.

## Decorators

- A decorator is a callable that takes a function and returns a (usually wrapping) function; applied with `@`. Run **at import time**.
- Use **`functools.wraps`** to preserve metadata. **Parameterized decorators** = a factory returning a decorator. **Stacked** decorators apply bottom-up.
- Stdlib decorators worth knowing: `@property`, `@classmethod`/`@staticmethod`, `@functools.lru_cache`, `@singledispatch`, `@dataclass`, `@contextmanager`.

## Object-oriented idioms

- **`dataclasses`** (`@dataclass`, `field`, `frozen=True`), `typing.NamedTuple`, and `collections.namedtuple` — three ways to build record classes; prefer them over bare tuples/dicts. `attrs`/`pydantic` for richer needs.
- **`@property`** and **descriptors** for managed attributes; `__slots__` for memory. Interfaces via **ABCs** (`abc`) *or* **`typing.Protocol`** (structural / static duck typing — usually preferred for new code).
- Inheritance pitfalls: prefer composition; understand the **MRO** and cooperative `super()`; avoid subclassing built-ins directly (subclass `collections.UserDict`/`UserList` instead).

## Iterators, generators & lazy evaluation

- The **Iterator pattern is built in**: `iter()` → `__iter__`/`__next__`; `StopIteration` ends iteration. Make classes iterable via `__iter__` returning a fresh iterator each time.
- **Generators** (`yield`) produce values lazily; **generator expressions** `(x for x in …)`; `yield from` delegates to a sub-iterator. Generators are the idiomatic way to build lazy pipelines.
- **`itertools`** is the toolbox: `count`/`cycle`/`repeat`, `chain`, `islice`, `takewhile`/`dropwhile`, `groupby`, `tee`, `product`/`permutations`/`combinations`, `accumulate`. Compose them into memory-efficient pipelines (closest Python gets to lazy FP streams — cf. [[functional-programming]]).

## Context managers & `with`

- `with` guarantees setup/teardown via `__enter__`/`__exit__` (files, locks, transactions, temporarily patching state). Write your own with **`contextlib.contextmanager`** (a generator with one `yield`), `closing`, `suppress`, `ExitStack`.

## Concurrency & parallelism

- **The GIL**: one thread executes Python bytecode at a time. So:
  - **CPU-bound** → **`multiprocessing`** / `concurrent.futures.ProcessPoolExecutor` (true parallelism across processes) or native extensions that release the GIL.
  - **IO-bound** → **threads** (`ThreadPoolExecutor`) *or* **`asyncio`** (single-threaded cooperative concurrency).
- **`concurrent.futures`** gives a uniform `Executor.map`/`submit` + `Future` API over threads and processes.
- **`asyncio`**: `async def` coroutines, `await`, the event loop, `asyncio.gather`/`TaskGroup`, async generators/iterators/context managers (`async for`, `async with`). **Never block the loop** — wrap blocking/CPU work in `run_in_executor`. Use async libraries (httpx, asyncpg) not blocking ones inside async code.

## Type hints in depth

- Gradual typing: hints are optional, checked statically (**mypy**/**pyright**), ignored at runtime. Modern syntax: `list[int]`, `dict[str, int]`, `X | None` (3.10+), `tuple[int, ...]`.
- `typing` tools: `Optional`/`Union`, `Any`, **`Protocol`** (structural typing), `TypeVar`/`Generic`, `Callable`, `Literal`, `TypedDict`, `Final`, `cast`, `@overload`, `Annotated`, `Self`. Variance and the "consistent-with" relation.
- Hints make APIs self-documenting and enable refactoring/IDE support; they **don't** give you Scala-grade exhaustiveness — approximate "make illegal states unrepresentable" with `Enum`, frozen dataclasses, `Literal`, and `NewType` (cf. [[scala]]/[[functional-programming]]).
