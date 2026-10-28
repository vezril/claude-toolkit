# Upstream

Imported from [mattpocock/skills](https://github.com/mattpocock/skills) at commit
`59db609eb1e18aaf59b63284d0e52255aff0c63c` (2026-10-27), path `skills/engineering/wizard/`, under the MIT license below.

## Changes from upstream

- `template.sh` line 114: `$e[Enter keeps current]` → `${e}[Enter keeps current]`. Upstream, `shellcheck -S error` reports SC1087 on that line (it reads `$e[` as an array index). The line works either way, but the skill's own step 4 says to run shellcheck, so every wizard built from the unchanged library fails its own verification. Measured: v2 failed **valid** 6/6 on both models; v3 with this one change passed.
- `SKILL.md`, step 1, the migration bullet: one added sentence. The repo's own scripts, README and runbooks usually name the exact command and the objects it touches; use those, and never ask the human for something the repo already states. Measured: with upstream's wording Haiku twice invented the table name or demanded a migration command the README gives; with the sentence, 46/48 over two samples (95.8%), up from 45/48.

Built eval-first: the suite, the iteration log and every measured run are in `evals/wizard/`.

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
