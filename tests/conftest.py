from collections.abc import Iterator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from library.app import create_app


class Clock:
    """A clock the test moves: due dates and late fees are about time."""

    def __init__(self) -> None:
        self.today = date(2026, 3, 2)

    def __call__(self) -> date:
        return self.today

    def advance(self, days: int) -> None:
        self.today += timedelta(days=days)


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def client(clock: Clock) -> Iterator[TestClient]:
    with TestClient(create_app(clock)) as c:
        yield c


def copy_of(
    client: TestClient, isbn: str = "9780321125217", title: str = "Domain-Driven Design"
) -> str:
    client.post("/catalog/books", json={"isbn": isbn, "title": title, "author": "Eric Evans"})
    return str(client.post(f"/catalog/books/{isbn}/copies").json()["copy_id"])


def member(client: TestClient, tier: str = "standard") -> str:
    return str(
        client.post("/lending/members", json={"name": "Ada", "tier": tier}).json()["member_id"]
    )
