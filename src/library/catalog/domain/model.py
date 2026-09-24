from dataclasses import dataclass

from library.shared.errors import Conflict, NotFound


@dataclass(frozen=True, slots=True)
class Book:
    isbn: str
    title: str
    author: str


@dataclass(slots=True)
class Copy:
    copy_id: str
    isbn: str
    on_loan: bool = False


class BookNotFound(NotFound):
    code = "book_not_found"


class BookAlreadyRegistered(Conflict):
    code = "book_already_registered"


@dataclass(frozen=True, slots=True)
class Availability:
    """What a reader sees: a view, not an invariant (bounded_contexts.md)."""

    book: Book
    copies_total: int
    copies_available: int


def availability(book: Book, copies: list[Copy]) -> Availability:
    return Availability(
        book=book,
        copies_total=len(copies),
        copies_available=sum(1 for c in copies if not c.on_loan),
    )
