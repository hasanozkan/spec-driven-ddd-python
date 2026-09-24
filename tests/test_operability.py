"""Feature 004: the service emits specs/telemetry.yaml — every metric, with its
attributes — at /metrics. The .NET implementation is held to the same file."""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from tests.conftest import Clock, copy_of, member

SPEC = yaml.safe_load(
    (Path(__file__).resolve().parent.parent / "specs" / "telemetry.yaml").read_text()
)


def prometheus_name(m: dict[str, object]) -> str:
    base = str(m["name"]).replace(".", "_")
    return base + "_seconds" if m.get("unit") == "s" else base


def scrape(client: TestClient) -> dict[str, set[str]]:
    """family name -> label names seen on its samples"""
    out: dict[str, set[str]] = {}
    for fam in text_string_to_metric_families(client.get("/metrics/").text):
        labels = out.setdefault(fam.name, set())
        for s in fam.samples:
            labels.update(k for k in s.labels if k != "le")
    return out


def value(client: TestClient, sample: str, **labels: str) -> float:
    for fam in text_string_to_metric_families(client.get("/metrics/").text):
        for s in fam.samples:
            if s.name == sample and all(s.labels.get(k) == v for k, v in labels.items()):
                return float(s.value)
    return 0.0


def _exercise(client: TestClient, clock: Clock) -> None:
    ada = member(client)
    loan = client.post("/lending/loans", json={"member_id": ada, "copy_id": copy_of(client)}).json()
    clock.advance(14 + 2)
    client.post(f"/lending/loans/{loan['loan_id']}/return")
    client.post("/lending/loans", json={"member_id": ada, "copy_id": "c_nope"})  # refused


@pytest.mark.rule("OPS-R4")
def test_every_metric_in_the_telemetry_contract_is_exposed_with_its_attributes(
    client: TestClient, clock: Clock
) -> None:
    _exercise(client, clock)
    seen = scrape(client)
    for m in SPEC["metrics"]:
        name = prometheus_name(m)
        assert name in seen, f"{m['name']} missing as {name}"
        expected = {a.replace(".", "_") for a in m["attributes"]}
        assert expected <= seen[name], f"{name} lacks {expected - seen[name]}"


@pytest.mark.rule("OPS-R1")
def test_requests_are_timed_by_route_template_not_raw_path(client: TestClient) -> None:
    client.get("/catalog/books/9999999999/copies")
    labels = scrape(client)["http_server_request_duration_seconds"]
    assert {"http_request_method", "http_route", "http_response_status_code"} <= labels
    assert (
        value(
            client,
            "http_server_request_duration_seconds_count",
            http_route="/catalog/books/{isbn}/copies",
            http_response_status_code="404",
        )
        >= 1
    )


@pytest.mark.rule("OPS-R2")
def test_loans_and_late_fees_are_counted_from_events(client: TestClient, clock: Clock) -> None:
    before = (
        value(client, "library_loans_opened_total"),
        value(client, "library_loans_closed_total", library_late="true"),
        value(client, "library_late_fees_cents_total"),
    )
    _exercise(client, clock)
    assert value(client, "library_loans_opened_total") == before[0] + 1
    assert value(client, "library_loans_closed_total", library_late="true") == before[1] + 1
    assert (
        value(client, "library_late_fees_cents_total") == before[2] + 50
    )  # two days late, standard tier


@pytest.mark.rule("OPS-R3")
def test_refusals_are_counted_by_problem_code(client: TestClient, clock: Clock) -> None:
    before = value(client, "library_refusals_total", library_code="copy_not_found")
    _exercise(client, clock)
    assert value(client, "library_refusals_total", library_code="copy_not_found") == before + 1
