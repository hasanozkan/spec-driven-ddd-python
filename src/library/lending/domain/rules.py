"""The lending rules as plain functions — each one names the spec rule it
implements, and each is testable without a repository, a clock or HTTP."""

from datetime import date, timedelta

from library.lending.domain.model import (
    CopyNotFound,
    CopyOnLoan,
    FeesOutstanding,
    LoanLimitReached,
    Member,
)
from library.lending.domain.policy import Tier


def check_can_borrow(
    member: Member, tier: Tier, *, copy_known: bool, copy_on_loan: bool, active_loans: int
) -> None:
    """Refuses with the FIRST rule that fails, in the order the spec lists them."""
    if not copy_known:
        raise CopyNotFound()  # LEND-R1
    if copy_on_loan:
        raise CopyOnLoan()  # LEND-R1
    if member.outstanding_fees_cents > 0:
        raise FeesOutstanding()  # LEND-R4
    if active_loans >= tier.max_active_loans:
        raise LoanLimitReached()  # LEND-R2


def due_on(tier: Tier, borrowed_on: date) -> date:
    """LEND-R3."""
    return borrowed_on + timedelta(days=tier.loan_days)


def late_fee_cents(tier: Tier, due: date, returned_on: date) -> int:
    """LEND-R5: per day late, capped; nothing on or before the due date."""
    days_late = (returned_on - due).days
    if days_late <= 0:
        return 0
    return min(days_late * tier.late_fee_per_day_cents, tier.max_late_fee_cents)
