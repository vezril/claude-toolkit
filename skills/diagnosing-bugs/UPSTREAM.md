# Upstream

Imported from [mattpocock/skills](https://github.com/mattpocock/skills) at commit
`59db609eb1e18aaf59b63284d0e52255aff0c63c` (2026-10-27), path `skills/engineering/diagnosing-bugs/`,
under the MIT license below.

## Changes from upstream

- `SKILL.md`, Phase 5, step 1: one added sentence. The regression test must go red on every run
  against the buggy code; for a non-deterministic bug, pin the source of the nondeterminism inside
  the test (seed, iteration order, clock); an existing test that fails only some of the time is the
  symptom, not the regression test. Measured: with the upstream skill, both models skipped the
  regression test on the flaky case in every sample, calling the half-failing existing test "already
  a good regression test"; with the sentence, 5 of 6 samples wrote one that fails reliably.
- `scripts/hitl-loop.template.sh` is upstream byte for byte.

Built eval-first: the suite, the iteration log and every measured run are in `evals/diagnosing-bugs/`.

## Upstream license

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
