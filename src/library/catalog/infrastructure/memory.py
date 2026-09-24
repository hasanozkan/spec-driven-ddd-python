from library.catalog.domain.model import Book, Copy


class InMemoryCatalogRepository:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}
        self._copies: dict[str, Copy] = {}

    def add_book(self, book: Book) -> None:
        self._books[book.isbn] = book

    def get_book(self, isbn: str) -> Book | None:
        return self._books.get(isbn)

    def books(self) -> list[Book]:
        return list(self._books.values())

    def add_copy(self, copy: Copy) -> None:
        self._copies[copy.copy_id] = copy

    def get_copy(self, copy_id: str) -> Copy | None:
        return self._copies.get(copy_id)

    def copies_of(self, isbn: str) -> list[Copy]:
        return [c for c in self._copies.values() if c.isbn == isbn]
