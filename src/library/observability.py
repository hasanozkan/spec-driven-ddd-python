"""Operability (feature 004, specs/telemetry.yaml): OpenTelemetry metrics,
scraped at /metrics.

Domain numbers are counted by subscribing to the integration events — the
same way the catalog learns about loans — so neither context knows it is
being measured. The meter provider is process-wide (OpenTelemetry allows one
global provider); `create_app` only attaches subscribers to its own bus.
"""

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from opentelemetry import metrics

from library.contracts.events import LoanClosed, LoanOpened
from library.shared.events import EventBus

_configured = False


def _configure_provider() -> None:
    global _configured
    if _configured:
        return
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource

    resource = Resource.create({"service.name": "library"})
    metrics.set_meter_provider(
        MeterProvider(resource=resource, metric_readers=[PrometheusMetricReader()])
    )
    _configured = True


class Instruments:
    def __init__(self) -> None:
        m = metrics.get_meter("library")
        self.request_duration = m.create_histogram(
            "http.server.request.duration", unit="s", description="Duration of HTTP server requests"
        )
        self.loans_opened = m.create_counter("library.loans.opened", description="Loans opened")
        self.loans_closed = m.create_counter(
            "library.loans.closed", description="Loans closed, by lateness"
        )
        self.late_fees = m.create_counter(
            "library.late_fees.cents", description="Late fees charged, in cents"
        )
        self.refusals = m.create_counter(
            "library.refusals", description="Domain refusals, by problem code"
        )


_instruments: Instruments | None = None


def instruments() -> Instruments:
    global _instruments
    if _instruments is None:
        _configure_provider()
        _instruments = Instruments()
    return _instruments


def instrument(app: FastAPI, bus: EventBus) -> None:
    """OPS-R1..R4 for one app instance."""
    ins = instruments()

    def on_opened(_: LoanOpened) -> None:
        ins.loans_opened.add(1)  # OPS-R2

    def on_closed(event: LoanClosed) -> None:
        ins.loans_closed.add(1, {"library.late": str(event.late_fee_cents > 0).lower()})  # OPS-R2
        if event.late_fee_cents:
            ins.late_fees.add(event.late_fee_cents)

    bus.subscribe(LoanOpened, on_opened)
    bus.subscribe(LoanClosed, on_closed)

    @app.middleware("http")
    async def request_duration(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        template = getattr(route, "path", None)
        if template and template != "/metrics":
            ins.request_duration.record(  # OPS-R1
                time.perf_counter() - started,
                {
                    "http.request.method": request.method,
                    "http.route": template,
                    "http.response.status_code": response.status_code,
                },
            )
        return response

    from prometheus_client import make_asgi_app

    app.mount("/metrics", make_asgi_app())  # OPS-R4


def count_refusal(code: str) -> None:
    instruments().refusals.add(1, {"library.code": code})  # OPS-R3
