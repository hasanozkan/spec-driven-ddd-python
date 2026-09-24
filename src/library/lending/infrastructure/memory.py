from library.lending.domain.model import Loan, Member


class InMemoryLendingRepository:
    def __init__(self) -> None:
        self._members: dict[str, Member] = {}
        self._loans: dict[str, Loan] = {}
        self._copies: set[str] = set()

    def add_member(self, member: Member) -> None:
        self._members[member.member_id] = member

    def get_member(self, member_id: str) -> Member | None:
        return self._members.get(member_id)

    def add_loan(self, loan: Loan) -> None:
        self._loans[loan.loan_id] = loan

    def get_loan(self, loan_id: str) -> Loan | None:
        return self._loans.get(loan_id)

    def active_loans_of(self, member_id: str) -> list[Loan]:
        return [x for x in self._loans.values() if x.member_id == member_id and x.active]

    def active_loan_of_copy(self, copy_id: str) -> Loan | None:
        return next((x for x in self._loans.values() if x.copy_id == copy_id and x.active), None)

    def remember_copy(self, copy_id: str) -> None:
        self._copies.add(copy_id)

    def knows_copy(self, copy_id: str) -> bool:
        return copy_id in self._copies
