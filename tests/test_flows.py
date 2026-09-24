"""The features end to end through HTTP — and the two contexts meeting only
through events."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import Clock, copy_of, member


def _availability(client: TestClient, q: str = "domain") -> int:
    return int(client.get("/catalog/search", params={"q": q}).json()[0]["copies_available"])


@pytest.mark.rule("CAT-R1")
@pytest.mark.rule("CAT-R2")
def test_the_catalog_follows_loans_through_events_only(client: TestClient) -> None:
    copy_id = copy_of(client)
    ada = member(client)
    assert _availability(client) == 1
    loan = client.post("/lending/loans", json={"member_id": ada, "copy_id": copy_id}).json()
    assert _availability(client) == 0
    client.post(f"/lending/loans/{loan['loan_id']}/return")
    assert _availability(client) == 1


@pytest.mark.rule("LEND-R1")
def test_one_copy_is_never_lent_twice(client: TestClient) -> None:
    copy_id = copy_of(client)
    client.post("/lending/loans", json={"member_id": member(client), "copy_id": copy_id})
    r = client.post("/lending/loans", json={"member_id": member(client), "copy_id": copy_id})
    assert r.status_code == 409
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["code"] == "copy_on_loan"
    missing = client.post("/lending/loans", json={"member_id": member(client), "copy_id": "c_nope"})
    assert (missing.status_code, missing.json()["code"]) == (404, "copy_not_found")


@pytest.mark.rule("LEND-R2")
def test_the_fourth_standard_loan_is_refused_with_the_rule_that_refused_it(
    client: TestClient,
) -> None:
    ada = member(client)
    for i in range(3):
        copy_id = copy_of(client, isbn=f"978000000000{i}", title=f"Book {i}")
        assert (
            client.post("/lending/loans", json={"member_id": ada, "copy_id": copy_id}).status_code
            == 201
        )
    fourth = copy_of(client, isbn="9780000000009", title="Book 9")
    r = client.post("/lending/loans", json={"member_id": ada, "copy_id": fourth})
    assert (r.status_code, r.json()["code"]) == (409, "loan_limit_reached")


@pytest.mark.rule("LEND-R3")
@pytest.mark.rule("LEND-R5")
@pytest.mark.rule("LEND-R6")
@pytest.mark.rule("LEND-R4")
def test_late_return_charges_the_member_blocks_borrowing_and_paying_unblocks(
    client: TestClient, clock: Clock
) -> None:
    ada = member(client)
    loan = client.post("/lending/loans", json={"member_id": ada, "copy_id": copy_of(client)}).json()
    assert loan["due_on"] == "2026-03-16"

    clock.advance(14 + 3)  # three days late
    returned = client.post(f"/lending/loans/{loan['loan_id']}/return").json()
    assert returned["late_fee_cents"] == 75
    assert client.get(f"/lending/members/{ada}").json()["outstanding_fees_cents"] == 75

    another = copy_of(client, isbn="9780134494166", title="Clean Architecture")
    blocked = client.post("/lending/loans", json={"member_id": ada, "copy_id": another})
    assert blocked.json()["code"] == "fees_outstanding"

    client.post(f"/lending/members/{ada}/payments")
    assert (
        client.post("/lending/loans", json={"member_id": ada, "copy_id": another}).status_code
        == 201
    )


@pytest.mark.rule("LEND-R7")
def test_a_loan_is_returned_once(client: TestClient) -> None:
    loan = client.post(
        "/lending/loans", json={"member_id": member(client), "copy_id": copy_of(client)}
    ).json()
    assert client.post(f"/lending/loans/{loan['loan_id']}/return").status_code == 200
    again = client.post(f"/lending/loans/{loan['loan_id']}/return")
    assert (again.status_code, again.json()["code"]) == (409, "loan_already_returned")
