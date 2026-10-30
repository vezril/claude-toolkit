# Upstream

The **Merge danger** section (one-way or two-way door, then blast radius) is adapted from the `pr`
skill in [mattpocock/skills](https://github.com/mattpocock/skills) at commit
`59db609eb1e18aaf59b63284d0e52255aff0c63c` (2026-10-27), path `skills/engineering/pr/`, under the MIT
license below. The rest of `SKILL.md` is this toolkit's own.

## Changes from upstream

- Taken: the door call and the blast radius, as two labelled lines under their own heading.
- Added: a definition of a one-way door (a revert wouldn't undo it: dropped or rewritten data, a
  removed public contract consumers use, a published release), so the call comes from the diff.
- Left out: upstream's Evidence section (before/after screenshots or test runs), because this
  skill's fidelity rule bans results the diff doesn't show; and its visual summary, which would
  compete with the Changes list.

Built eval-first: v6 in `evals/pr-description/` (iteration log, load-bearing map, every run).

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
