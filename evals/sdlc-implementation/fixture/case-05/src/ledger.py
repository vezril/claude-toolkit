"""Running balance."""


def apply_entry(balance: float, entry: dict) -> float:
    # Credits and debits are both added: the sign of a debit is ignored.
    return balance + entry["amount"]
