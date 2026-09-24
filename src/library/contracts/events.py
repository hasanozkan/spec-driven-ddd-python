"""Integration events: the ONLY thing contexts share (ADR-0002).

Changing a field here is a contract change between contexts — treat it like
an API change.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class CopyRegistered:
    copy_id: str
    isbn: str


@dataclass(frozen=True, slots=True)
class LoanOpened:
    loan_id: str
    copy_id: str
    member_id: str
    due_on: date


@dataclass(frozen=True, slots=True)
class LoanClosed:
    loan_id: str
    copy_id: str
    member_id: str
    late_fee_cents: int
