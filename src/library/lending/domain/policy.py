"""Tier policy, loaded from the vendored copy of `specs/policy.yaml` (ADR-0003)."""

from dataclasses import dataclass
from functools import cache
from pathlib import Path

import yaml

POLICY_FILE = Path(__file__).with_name("policy.yaml")


@dataclass(frozen=True, slots=True)
class Tier:
    name: str
    max_active_loans: int
    loan_days: int
    late_fee_per_day_cents: int
    max_late_fee_cents: int


@cache
def load_policy() -> dict[str, Tier]:
    doc = yaml.safe_load(POLICY_FILE.read_text(encoding="utf-8"))
    return {name: Tier(name=name, **values) for name, values in doc["tiers"].items()}
