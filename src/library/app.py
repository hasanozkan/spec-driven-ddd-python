"""Composition root: the one place that knows every context. It wires
repositories, the bus and the routers; the contexts themselves never meet."""

from collections.abc import Callable
from datetime import date

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from library.catalog.api.routes import build_router as catalog_router
from library.catalog.application.services import CatalogService
from library.catalog.infrastructure.memory import InMemoryCatalogRepository
from library.lending.api.routes import build_router as lending_router
from library.lending.application.services import LendingService
from library.lending.domain.policy import load_policy
from library.lending.infrastructure.memory import InMemoryLendingRepository
from library.observability import count_refusal, instrument
from library.shared.errors import Conflict, DomainError, NotFound
from library.shared.events import EventBus


def create_app(clock: Callable[[], date] = date.today) -> FastAPI:
    app = FastAPI(title="Library — spec-driven DDD sample", version="0.1.0")
    bus = EventBus()
    catalog = CatalogService(InMemoryCatalogRepository(), bus)
    lending = LendingService(InMemoryLendingRepository(), load_policy(), bus, clock)

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        # Liveness/readiness for the platform; not part of the API contract.
        return {"status": "ok"}

    instrument(app, bus)
    app.include_router(catalog_router(catalog))
    app.include_router(lending_router(lending))

    @app.exception_handler(DomainError)
    def domain_error(_: Request, exc: DomainError) -> JSONResponse:
        status = 404 if isinstance(exc, NotFound) else 409 if isinstance(exc, Conflict) else 422
        count_refusal(exc.code)
        return JSONResponse(
            {"type": "about:blank", "status": status, "code": exc.code, "detail": str(exc)},
            status_code=status,
            media_type="application/problem+json",
        )

    return app


app = create_app()
