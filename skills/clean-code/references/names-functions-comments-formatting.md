# Names, functions, comments, formatting

*Clean Code* (Martin, 2008), Chapters 2–5. Principles stated language-agnostically; Scala/FP notes and critique inline.

## Meaningful names (Ch. 2)

- **Use intention-revealing names** — the name should answer why it exists, what it does, how it's used. `int d` → `int elapsedTimeInDays`. If a name needs a comment to explain it, it's the wrong name.
- **Avoid disinformation** — don't use names with established meanings for other things (`accountList` that isn't a List); avoid names that vary in tiny ways.
- **Make meaningful distinctions** — no noise words (`ProductData` vs `ProductInfo`, `a1`/`a2`); distinguish by meaning, not by satisfying the compiler.
- **Use pronounceable, searchable names** — single letters and magic numbers can't be grepped; reserve single letters for tiny local scopes.
- **Avoid encodings** — no Hungarian notation, no type/scope prefixes (`m_`, `strName`); interfaces/implementations shouldn't be encoded (`IShapeFactory`).
- **Class names are nouns** (`Customer`, `WikiPage`), **method names are verbs** (`postPayment`, `deletePage`); use `get/set/is` per convention. **Pick one word per concept** (`fetch` vs `retrieve` vs `get` — choose one) and **don't pun** (don't reuse one word for two ideas).
- **Add meaningful context** (a `state` field makes more sense inside an `Address`); **don't add gratuitous context** (prefixing every class with the app name).

**Scala/FP:** the same rules apply to `val`/`def`/type names; ADT case names should read in the Ubiquitous Language ([[domain-driven-design]]). Type-driven naming lets you drop encodings entirely (the type *is* the documentation).

## Functions (Ch. 3)

- **Small.** Functions should be small, then smaller. Blocks inside `if/else/while` should be one line — usually a function call with a good name. *(Critique: "2–4 lines" is aspirational; extract to clarify a concept or remove duplication, not to hit a count — over-extraction harms locality and readability.)*
- **Do one thing**, at **one level of abstraction**. A function does one thing if its statements are all one level below its name. Mixing high-level policy and low-level detail in one function is the most common smell.
- **The Stepdown Rule** (newspaper metaphor): code reads top-to-bottom, each function followed by those one level lower — like a narrative.
- **`switch`/`if-else` chains** tend to do N things; bury an unavoidable `switch` in a factory (create polymorphic objects once) rather than repeating it. *(Critique: a single `switch`/`match` over a closed set/ADT is often the cleanest option — see [[design-patterns]] expression problem; don't replace it with polymorphism reflexively.)*
- **Arguments:** fewer is better — 0 (niladic) ideal, 1–2 fine, 3+ needs justification; wrap related args in an object. **Flag (boolean) arguments are bad** — the function does two things; split it. **Output arguments** are confusing — return the value (or new state) instead.
- **No side effects** — a function that promises one thing but secretly changes state (a hidden init, a static) lies. **Command-Query Separation:** a function either changes state *or* returns information, not both.
- **Prefer exceptions to error codes** (codes force the caller to check inline and breed nesting); **extract try/catch bodies** into their own functions (error handling is "one thing").
- **DRY** — duplication is the root of much evil; extract it. **Structured programming** (single exit) matters less in small functions — early returns are fine when they read clearly.

**Scala/FP:** "no side effects" + CQS = **purity** ([[functional-programming]]); "one level of abstraction" = composing small total functions; replace output args with returned immutable values / `Either`.

## Comments (Ch. 4)

"Comments are, at best, a necessary evil." Prefer to **explain yourself in code** (extract a well-named function/variable) rather than write a comment.

- **Good comments:** legal/license; informative (rarely); **explanation of intent / rationale** (the *why*); clarification of opaque external code you can't change; warning of consequences; `TODO`; amplification of importance; Javadoc/public-API docs.
- **Bad comments:** mumbling; redundant (restating the code); misleading; mandated (a comment on every function/var); journal/changelog comments (use VCS); noise; **commented-out code** (delete it — VCS remembers); position markers; closing-brace comments; attributions; HTML in comments; nonlocal info; too much info; function headers on small well-named functions.

**Critique:** the book's stance is best read as "don't comment *what* the code already says." *Why*-comments — design rationale, trade-offs, non-obvious constraints, links to a ticket/spec — are genuinely valuable and can't live in the code itself. Don't treat all comments as failures.

## Formatting (Ch. 5)

- **Purpose:** formatting is communication; consistency matters more than any particular style. **Agree on team rules and let a tool enforce them** (e.g. scalafmt/spotless).
- **Vertical:** the newspaper metaphor — high-level at top, detail below. Blank lines separate concepts; related lines stay dense. **Vertical distance:** keep related things close — variables near their use, dependent functions near each other (caller above callee), similar functions grouped. Instance variables at the top of the class.
- **Horizontal:** keep lines short enough to read without scrolling; use whitespace to associate/disassociate; **don't horizontally align** columns of declarations (it draws the eye wrong and rots). Indentation reflects scope — don't collapse short `if`/`while` bodies onto one line.

These are conventions; the value is a codebase that looks like it was written by one mind.
