"""The rules as pure functions: no HTTP, no repository, no clock."""

from datetime import date

import pytest

from library.lending.domain import rules
from library.lending.domain.model import (
    CopyNotFound,
    CopyOnLoan,
    FeesOutstanding,
    LoanLimitReached,
    Member,
)
from library.lending.domain.policy import load_policy

STANDARD = load_policy()["standard"]
PREMIUM = load_policy()["premium"]


def _member(fees: int = 0) -> Member:
    return Member(member_id="m", name="Ada", tier="standard", outstanding_fees_cents=fees)


@pytest.mark.rule("LEND-R1")
def test_an_unknown_copy_or_one_already_on_loan_cannot_be_borrowed() -> None:
    with pytest.raises(CopyNotFound):
        rules.check_can_borrow(
            _member(), STANDARD, copy_known=False, copy_on_loan=False, active_loans=0
        )
    with pytest.raises(CopyOnLoan):
        rules.check_can_borrow(
            _member(), STANDARD, copy_known=True, copy_on_loan=True, active_loans=0
        )


@pytest.mark.rule("LEND-R2")
def test_the_tier_caps_active_loans() -> None:
    rules.check_can_borrow(_member(), STANDARD, copy_known=True, copy_on_loan=False, active_loans=2)
    with pytest.raises(LoanLimitReached):
        rules.check_can_borrow(
            _member(), STANDARD, copy_known=True, copy_on_loan=False, active_loans=3
        )
    rules.check_can_borrow(_member(), PREMIUM, copy_known=True, copy_on_loan=False, active_loans=5)


@pytest.mark.rule("LEND-R3")
def test_a_loan_is_due_loan_days_after_it_is_borrowed() -> None:
    assert rules.due_on(STANDARD, date(2026, 3, 2)) == date(2026, 3, 16)
    assert rules.due_on(PREMIUM, date(2026, 3, 2)) == date(2026, 3, 30)


@pytest.mark.rule("LEND-R4")
def test_outstanding_fees_block_borrowing_before_the_limit_is_even_looked_at() -> None:
    with pytest.raises(FeesOutstanding):
        rules.check_can_borrow(
            _member(fees=25), STANDARD, copy_known=True, copy_on_loan=False, active_loans=3
        )


@pytest.mark.rule("LEND-R5")
@pytest.mark.parametrize(
    ("returned", "fee"),
    [
        (date(2026, 3, 15), 0),  # early
        (date(2026, 3, 16), 0),  # on the due date
        (date(2026, 3, 17), 25),  # one day late
        (date(2026, 3, 20), 100),  # four days
        (date(2026, 6, 1), 1000),  # capped
    ],
)
def test_the_late_fee_is_per_day_and_capped(returned: date, fee: int) -> None:
    assert rules.late_fee_cents(STANDARD, date(2026, 3, 16), returned) == fee
