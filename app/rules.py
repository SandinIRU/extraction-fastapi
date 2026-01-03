from __future__ import annotations

from typing import List
from app.schemas import Itinerary


def validate_business_rules(it: Itinerary) -> List[str]:
    errors: List[str] = []

    # days length must equal duration_days
    if len(it.days) != it.duration_days:
        errors.append(f"days length ({len(it.days)}) must equal duration_days ({it.duration_days}).")

    # day_number must be 1..duration_days in order
    expected = list(range(1, it.duration_days + 1))
    actual = [d.day_number for d in it.days]
    if actual != expected:
        errors.append(f"day_number must be exactly {expected} in order; got {actual}.")

    # currency should look like a short code
    if not it.currency or len(it.currency) not in (3, 4):
        errors.append("currency must be a short code like LKR or USD.")

    return errors
