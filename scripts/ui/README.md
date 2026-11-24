# Workflow UI

A local, read-only diagram of both workflows — `delivery-flow` and `sdlc` — with per-node
detail, certification state and run statistics.

```bash
python3 scripts/ui/serve-ui.py --repo /path/to/delivery/repo
```

Opens `http://127.0.0.1:8787/`. Pass `--repo` once per delivery repo to read run statistics
from; omit it and the structure still renders, with statistics reported as unavailable and the
reason stated.

## What it shows

- **The diagram** — each profile as a row of step cards, in routing order. Click a card.
- **Per node** — artifact, kind, model tier, agent, prompt, whether it is in the Stage 4
  certified chain, and any declared edge check.
- **Certification** — from `check-certification.py` itself, never from the registry's
  `certified:` field. delivery-flow's certified steps do not carry that field; their
  certification is the evidence clearing the gate. Reading the flag reported delivery-flow as
  having nothing certified, which is the opposite of true.
- **Three distinct states** — certified, uncertified, and *no prompt to certify* (a script or
  adapter). Collapsing the last two reports every deterministic step as a failure.
- **Statistics** — traced calls, API-equivalent cost and output tokens per step, plus a
  cost-by-step comparison. A step with no trace records says so explicitly: absent is not
  zero.

## Security posture

This opens a listening socket, so the choices are deliberate and tested
(`tests/ui/test_serve_ui.py`):

- **Bound to `127.0.0.1`**, not configurable. The only reason to make it configurable would be
  to expose it.
- **Read-only.** No write handler exists.
- **No file serving.** The page is one path resolved at import; nothing in a request reaches
  the filesystem, so there is no traversal surface.
- **No ticket prose.** `item.json` bodies, briefs, triage rationale and PR text are not
  exposed. The delivery repos point at a client's tracker (`tracker.external: true`), and this
  plugin's rule keeps client content out of the public repo — so it never reaches a socket.
- **No secrets.** Nothing reads the environment.

Changing any of that is a security decision and belongs to a human.

## Why it lives here and not in `scripts/workflow/`

That directory is the substrate, and `tests/workflow/test_substrate_shims.py` enforces that
nothing in it names a specific workflow. This UI reads both workflows and calls
`check-certification.py` and `delivery-report.py`, which still live under
`scripts/delivery-flow/`. It is neither substrate nor one workflow's own.
