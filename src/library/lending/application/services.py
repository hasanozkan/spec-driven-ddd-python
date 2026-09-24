"""Lending use cases: load, apply the domain rules, save, publish."""

import uuid
from collections.abc import Callable
from datetime import date

from library.contracts.events import CopyRegistered, LoanClosed, LoanOpened
from library.lending.domain import rules
from library.lending.domain.model import (
    Loan,
    LoanAlreadyReturned,
    LoanNotFound,
    Member,
    MemberNotFound,
)
from library.lending.domain.policy import Tier
from library.lending.domain.repository import LendingRepository
from library.shared.errors import DomainError
from library.shared.events import EventBus

Clock = Callable[[], date]


class UnknownTier(DomainError):
    code = "unknown_tier"


class LendingService:
    def __init__(
        self, repo: LendingRepository, policy: dict[str, Tier], bus: EventBus, clock: Clock
    ) -> None:
        self._repo = repo
        self._policy = policy
        self._bus = bus
        self._today = clock
        # Lending's own projection of the catalog: which copies exist (ADR-0002).
        bus.subscribe(CopyRegistered, lambda e: repo.remember_copy(e.copy_id))

    def register_member(self, name: str, tier: str) -> Member:
        if tier not in self._policy:
            raise UnknownTier(tier)
        member = Member(member_id=f"m_{uuid.uuid4().hex[:10]}", name=name, tier=tier)
        self._repo.add_member(member)
        return member

    def borrow(self, member_id: str, copy_id: str) -> Loan:
        member = self._member(member_id)
        tier = self._policy[member.tier]
        rules.check_can_borrow(
            member,
            tier,
            copy_known=self._repo.knows_copy(copy_id),
            copy_on_loan=self._repo.active_loan_of_copy(copy_id) is not None,
            active_loans=len(self._repo.active_loans_of(member_id)),
        )
        today = self._today()
        loan = Loan(
            loan_id=f"l_{uuid.uuid4().hex[:10]}",
            copy_id=copy_id,
            member_id=member_id,
            borrowed_on=today,
            due_on=rules.due_on(tier, today),
        )
        self._repo.add_loan(loan)
        self._bus.publish(LoanOpened(loan.loan_id, loan.copy_id, loan.member_id, loan.due_on))
        return loan

    def return_copy(self, loan_id: str) -> Loan:
        loan = self._repo.get_loan(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)
        if not loan.active:
            raise LoanAlreadyReturned(loan_id)  # LEND-R7
        member = self._member(loan.member_id)
        today = self._today()
        loan.returned_on = today
        loan.late_fee_cents = rules.late_fee_cents(self._policy[member.tier], loan.due_on, today)
        member.outstanding_fees_cents += loan.late_fee_cents  # LEND-R6
        self._bus.publish(
            LoanClosed(loan.loan_id, loan.copy_id, loan.member_id, loan.late_fee_cents)
        )
        return loan

    def pay_fees(self, member_id: str) -> Member:
        member = self._member(member_id)
        member.outstanding_fees_cents = 0  # LEND-R6
        return member

    def member(self, member_id: str) -> Member:
        return self._member(member_id)

    def _member(self, member_id: str) -> Member:
        member = self._repo.get_member(member_id)
        if member is None:
            raise MemberNotFound(member_id)
        return member
