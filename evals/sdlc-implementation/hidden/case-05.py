"""Running balance."""


def apply_entry(balance: float, entry: dict) -> float:
    kind = entry.get("kind")
    if kind not in ("credit", "debit"):
        raise ValueError(f"entry has no usable kind: {kind!r}")
    amount = entry["amount"]
    if amount == 0.0:
        return balance
    return balance + amount if kind == "credit" else balance - amount
