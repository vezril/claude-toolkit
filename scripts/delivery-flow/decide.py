#!/usr/bin/env python3
"""Resolve a punch-out, or authorize a deploy. Humans only.

Usage:
    decide.py <ITEM-KEY> <punch-out-N|deploy> --choose proceed|stop|redirect
              [--note "..."] [--repo <path>] [--key ~/.ssh/id_ed25519_sk]

The decision is signed with a key whose every use requires your presence — a hardware key's
touch, or Touch ID through a Secure Enclave agent. That signature, not a terminal check, is
what an agent cannot forge: an agent can fake a TTY with `script` or a pty, but it cannot
produce your fingerprint.

The signature covers the decision's fields including the sha256 of the file being decided,
so editing the punch-out afterwards invalidates it.

Exit codes: 0 written, 1 refused (prerequisite missing, signing failed), 2 usage error.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (SIGN_NAMESPACE, _payload_for_signing, artifact_root, is_delivery_repo, load_config,  # noqa: E402
                    load_json, repo_root, sha256, verify_decision)


def sign(payload: bytes, key: Path) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "decision.json"
        data.write_bytes(payload)
        r = subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(key), "-n", SIGN_NAMESPACE, str(data)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or "ssh-keygen sign failed")
        return (data.with_suffix(".json.sig")).read_text()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("subject", help="punch-out-N, or 'deploy'")
    ap.add_argument("--choose", required=True, choices=["proceed", "stop", "redirect"])
    ap.add_argument("--note", default="")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--key", default=os.environ.get("DELIVERY_FLOW_SIGNING_KEY", "~/.ssh/id_ed25519_sk"))
    ap.add_argument("--decider", default=os.environ.get("DELIVERY_FLOW_SIGNER", ""))
    ap.add_argument("--yes", action="store_true", help="skip the typed confirmation (scripted setup only)")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo", file=sys.stderr)
        return 2
    item_dir = artifact_root(repo) / args.item
    cfg = load_config(repo)
    decisions = cfg.get("decisions") or {}
    decider = args.decider or decisions.get("signer") or os.environ.get("USER", "")
    allowed = Path(str(decisions.get("allowed_signers") or "~/.config/delivery-flow/allowed_signers")).expanduser()

    if args.subject == "deploy":
        target = item_dir / "verify.json"
        if not target.exists():
            print("refusing: deploy is decided against verify.json, which does not exist", file=sys.stderr)
            return 1
        trigger = "deploy"
    else:
        target = item_dir / f"{args.subject}.md"
        if not target.exists():
            print(f"refusing: no such punch-out: {target}", file=sys.stderr)
            return 1
        trigger = target.stem

    if not args.yes and sys.stdin.isatty():
        print(target.read_text())
        typed = input(f"Type the item key to confirm '{args.choose}' ({args.item}): ").strip()
        if typed != args.item:
            print("refused: the typed key did not match", file=sys.stderr)
            return 1

    decision = {"id": args.subject, "item": args.item, "trigger": trigger,
                "artifact": target.name, "sha256": sha256(target), "choice": args.choose,
                "note": args.note, "decider": decider,
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        decision["signature"] = sign(_payload_for_signing(decision), Path(args.key).expanduser())
    except (RuntimeError, OSError) as e:
        print(f"refusing: could not sign the decision ({e}).\n"
              f"Signing needs a key that asks for your presence on every use — a hardware key, "
              f"or a Secure Enclave key through an agent such as Secretive.", file=sys.stderr)
        return 1

    ok, reason = verify_decision(decision, allowed)
    if not ok:
        print(f"refusing: the decision signed, but does not verify against {allowed} ({reason}).\n"
              f"Add this key's public half to that file as: <decider> <public key>", file=sys.stderr)
        return 1

    out_dir = item_dir / "decisions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{args.subject}.json"
    out.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n")
    print(f"decided: {args.subject} -> {args.choose} ({reason}); wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
