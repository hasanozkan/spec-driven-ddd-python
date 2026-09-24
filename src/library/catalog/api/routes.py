from fastapi import APIRouter
from pydantic import BaseModel, Field

from library.catalog.application.services import CatalogService


class RegisterBook(BaseModel):
    isbn: str = Field(min_length=10, max_length=17)
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)


class BookOut(BaseModel):
    isbn: str
    title: str
    author: str


class CopyOut(BaseModel):
    copy_id: str
    isbn: str


class CopyStatusOut(BaseModel):
    copy_id: str
    on_loan: bool


class AvailabilityOut(BaseModel):
    isbn: str
    title: str
    author: str
    copies_total: int
    copies_available: int


def build_router(service: CatalogService) -> APIRouter:
    router = APIRouter(prefix="/catalog", tags=["catalog"])

    @router.post("/books", status_code=201)
    def register_book(body: RegisterBook) -> BookOut:
        b = service.register_book(body.isbn, body.title, body.author)
        return BookOut(isbn=b.isbn, title=b.title, author=b.author)

    @router.post("/books/{isbn}/copies", status_code=201)
    def add_copy(isbn: str) -> CopyOut:
        c = service.add_copy(isbn)
        return CopyOut(copy_id=c.copy_id, isbn=c.isbn)

    @router.get("/books/{isbn}/copies")
    def list_copies(isbn: str) -> list[CopyStatusOut]:
        return [CopyStatusOut(copy_id=c.copy_id, on_loan=c.on_loan) for c in service.copies(isbn)]

    @router.get("/search")
    def search(q: str) -> list[AvailabilityOut]:
        return [
            AvailabilityOut(
                isbn=a.book.isbn,
                title=a.book.title,
                author=a.book.author,
                copies_total=a.copies_total,
                copies_available=a.copies_available,
            )
            for a in service.search(q)
        ]

    return router
