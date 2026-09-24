from datetime import date
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from library.lending.application.services import LendingService
from library.lending.domain.model import Loan, Member


class RegisterMember(BaseModel):
    name: str = Field(min_length=1)
    tier: Literal["standard", "premium"] = "standard"


class MemberOut(BaseModel):
    member_id: str
    name: str
    tier: str
    outstanding_fees_cents: int


class Borrow(BaseModel):
    member_id: str
    copy_id: str


class LoanOut(BaseModel):
    loan_id: str
    copy_id: str
    member_id: str
    borrowed_on: date
    due_on: date
    returned_on: date | None
    late_fee_cents: int


def _member(m: Member) -> MemberOut:
    return MemberOut(
        member_id=m.member_id,
        name=m.name,
        tier=m.tier,
        outstanding_fees_cents=m.outstanding_fees_cents,
    )


def _loan(x: Loan) -> LoanOut:
    return LoanOut(
        loan_id=x.loan_id,
        copy_id=x.copy_id,
        member_id=x.member_id,
        borrowed_on=x.borrowed_on,
        due_on=x.due_on,
        returned_on=x.returned_on,
        late_fee_cents=x.late_fee_cents,
    )


def build_router(service: LendingService) -> APIRouter:
    router = APIRouter(prefix="/lending", tags=["lending"])

    @router.post("/members", status_code=201)
    def register_member(body: RegisterMember) -> MemberOut:
        return _member(service.register_member(body.name, body.tier))

    @router.get("/members/{member_id}")
    def get_member(member_id: str) -> MemberOut:
        return _member(service.member(member_id))

    @router.post("/members/{member_id}/payments")
    def pay(member_id: str) -> MemberOut:
        return _member(service.pay_fees(member_id))

    @router.post("/loans", status_code=201)
    def borrow(body: Borrow) -> LoanOut:
        return _loan(service.borrow(body.member_id, body.copy_id))

    @router.post("/loans/{loan_id}/return")
    def return_copy(loan_id: str) -> LoanOut:
        return _loan(service.return_copy(loan_id))

    return router
