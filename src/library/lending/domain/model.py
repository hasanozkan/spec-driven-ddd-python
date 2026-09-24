from dataclasses import dataclass
from datetime import date

from library.shared.errors import Conflict, NotFound


@dataclass(slots=True)
class Member:
    member_id: str
    name: str
    tier: str
    outstanding_fees_cents: int = 0


@dataclass(slots=True)
class Loan:
    loan_id: str
    copy_id: str
    member_id: str
    borrowed_on: date
    due_on: date
    returned_on: date | None = None
    late_fee_cents: int = 0

    @property
    def active(self) -> bool:
        return self.returned_on is None


class MemberNotFound(NotFound):
    code = "member_not_found"


class CopyNotFound(NotFound):
    code = "copy_not_found"


class LoanNotFound(NotFound):
    code = "loan_not_found"


class CopyOnLoan(Conflict):
    code = "copy_on_loan"


class LoanLimitReached(Conflict):
    code = "loan_limit_reached"


class FeesOutstanding(Conflict):
    code = "fees_outstanding"


class LoanAlreadyReturned(Conflict):
    code = "loan_already_returned"
