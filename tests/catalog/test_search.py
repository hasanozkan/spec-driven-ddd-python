from fastapi.testclient import TestClient

from tests.conftest import copy_of


def test_search_matches_title_author_or_isbn_case_insensitively(client: TestClient) -> None:
    copy_of(client)
    for q in ("DOMAIN", "evans", "9780321125217"):
        assert [b["title"] for b in client.get("/catalog/search", params={"q": q}).json()] == [
            "Domain-Driven Design"
        ]
    assert client.get("/catalog/search", params={"q": "kafka"}).json() == []


def test_a_copy_needs_a_registered_book(client: TestClient) -> None:
    r = client.post("/catalog/books/9999999999/copies")
    assert (r.status_code, r.json()["code"]) == (404, "book_not_found")
