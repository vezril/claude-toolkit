# Memory safety (prevention & hardening)

Defensive reference. Describes memory-corruption weakness *classes* and how to prevent/harden against them — not how to exploit them. References: CERT C/C++ Secure Coding, CWE-119/120/787/416/190, OWASP.

## The weakness classes (what to prevent)

- **Buffer overflow / out-of-bounds write (CWE-120/787)** — writing past the end (or before the start) of a stack or heap buffer because a length wasn't checked. Corrupts adjacent memory and is the classic memory-safety failure.
- **Out-of-bounds read (CWE-125)** — reading past a buffer (info disclosure, e.g. over-long reads).
- **Use-after-free / double-free (CWE-416/415)** — using or freeing memory after it's been freed; dangling pointers.
- **Integer overflow/wraparound (CWE-190)** — arithmetic that wraps and then feeds a size/length/index, producing an undersized allocation or a bad bounds check.
- **Format-string issues (CWE-134)** — passing untrusted data as a format string (covered in the injection reference) can read/write memory.

## Prevention — by far the most effective controls

- **Use a memory-safe language where you can.** Rust, Java/Scala, Go, etc. eliminate most of these by construction (bounds checks, GC/ownership, no raw pointer arithmetic). For the JVM/Scala stack this class is largely a non-issue except at JNI / `sun.misc.Unsafe` / native boundaries — keep those minimal and bounded.
- **Never use unbounded string/buffer APIs.** In C/C++: avoid `gets`, `strcpy`, `strcat`, `sprintf`, unbounded `scanf("%s")`; prefer bounded equivalents (`snprintf`, `strlcpy`/`strlcat`, `memcpy` with a *checked* length), and always size against the destination. Prefer `std::string`/`std::vector`/`std::span` over raw arrays; use `.at()` (checked) at trust boundaries.
- **Check all length/size arithmetic for overflow before using it** for allocation or indexing (e.g. verify `count <= MAX/elemSize` before `count*elemSize`); use checked-arithmetic helpers/builtins (`__builtin_mul_overflow`, `<stdckdint.h>`), and use `size_t` for sizes (avoid signed/unsigned mix-ups).
- **Validate indices and lengths against the actual buffer size**, not against attacker-supplied length fields.
- **Manage lifetimes with ownership, not discipline.** C++: RAII, smart pointers (`unique_ptr`/`shared_ptr`), no manual `new`/`delete`; null out / don't reuse freed pointers. Rust's borrow checker enforces this.
- **Parse, don't trust.** Turn raw bytes into a validated, sized representation once at the edge (a length-prefixed/framed parser that rejects malformed input) rather than scattering ad-hoc pointer math.

## Compiler & OS hardening (defense in depth)

Enable these so that even a latent bug is much harder to turn into a compromise (none replace fixing the bug):

- **Stack canaries** — `-fstack-protector-strong` (GCC/Clang) detects stack buffer overwrites before return.
- **FORTIFY_SOURCE** — `-D_FORTIFY_SOURCE=2 -O2` adds compile/runtime bounds checks to libc functions.
- **NX / DEP** (non-executable stack/heap) — default on modern toolchains; don't disable. Mark the stack non-executable.
- **ASLR / PIE** — build position-independent (`-fPIE -pie`) so memory layout is randomized.
- **RELRO** — `-Wl,-z,relro,-z,now` makes the GOT read-only.
- **Control-Flow Integrity / safe-stack** (`-fsanitize=cfi`, `-fsanitize=safe-stack`) where available.
- **Sanitizers in CI/testing** — AddressSanitizer (`-fsanitize=address`), UBSan, MemorySanitizer, plus **fuzzing** (libFuzzer/AFL++) of parsers/byte-handling to *find* these bugs before shipping.
- **Stay patched** — keep the toolchain, libc, and dependencies current.

## Review checklist

- Every buffer write bounded by the destination size? Every length/size from untrusted input validated and overflow-checked before use as a size/index?
- Any banned unbounded API (`strcpy`/`gets`/`sprintf`/unchecked `memcpy`)?
- Pointer lifetimes clear (no use-after-free/double-free)? Ownership expressed via RAII/smart pointers?
- Native/JNI/`Unsafe` boundaries minimized and bounds-checked?
- Hardening flags and sanitizers enabled in the build/CI? Fuzzing for byte-level parsers?

For the JVM/Scala stack, the highest-leverage version of this is: keep `unsafe`/JNI surfaces tiny, validate all framed/binary input with a strict parser, and rely on the platform's memory safety for the rest.
