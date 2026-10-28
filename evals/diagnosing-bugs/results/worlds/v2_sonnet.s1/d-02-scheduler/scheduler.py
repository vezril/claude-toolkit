"""Pick meeting slots."""

SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "13:00", "13:30", "14:00", "14:30", "15:00"]


def free_slots(busy):
    return set(SLOTS) - set(busy)


def next_slot(busy):
    """The earliest free slot of the day, or None when the day is full."""
    free = free_slots(busy)
    if not free:
        return None
    return min(free)


def book(busy, slot):
    if slot in busy:
        raise ValueError(f"{slot} is already booked")
    return sorted(set(busy) | {slot})
