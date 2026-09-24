"""Catalog use cases. Availability is a projection of Lending's events
(CAT-R1, CAT-R2) — the catalog never asks Lending anything."""

import uuid

from library.catalog.domain.model import (
    Availability,
    Book,
    BookAlreadyRegistered,
    BookNotFound,
    Copy,
    availability,
)
from library.catalog.domain.repository import CatalogRepository
from library.contracts.events import CopyRegistered, LoanClosed, LoanOpened
from library.shared.events import EventBus


class CatalogService:
    def __init__(self, repo: CatalogRepository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus
        bus.subscribe(LoanOpened, self._on_loan_opened)
        bus.subscribe(LoanClosed, self._on_loan_closed)

    def register_book(self, isbn: str, title: str, author: str) -> Book:
        if self._repo.get_book(isbn) is not None:
            raise BookAlreadyRegistered(isbn)
        book = Book(isbn=isbn, title=title, author=author)
        self._repo.add_book(book)
        return book

    def add_copy(self, isbn: str) -> Copy:
        if self._repo.get_book(isbn) is None:
            raise BookNotFound(isbn)
        copy = Copy(copy_id=f"c_{uuid.uuid4().hex[:10]}", isbn=isbn)
        self._repo.add_copy(copy)
        self._bus.publish(CopyRegistered(copy_id=copy.copy_id, isbn=isbn))
        return copy

    def search(self, text: str) -> list[Availability]:
        needle = text.casefold()
        return [
            availability(b, self._repo.copies_of(b.isbn))
            for b in self._repo.books()
            if needle in b.title.casefold() or needle in b.author.casefold() or needle == b.isbn
        ]

    def _on_loan_opened(self, event: LoanOpened) -> None:
        self._set_on_loan(event.copy_id, True)

    def _on_loan_closed(self, event: LoanClosed) -> None:
        self._set_on_loan(event.copy_id, False)

    def _set_on_loan(self, copy_id: str, on_loan: bool) -> None:
        copy = self._repo.get_copy(copy_id)
        if copy is not None:
            copy.on_loan = on_loan
