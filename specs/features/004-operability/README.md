# 004 — Operability: the service reports what it does

**Status:** shipped · **Context:** platform (both contexts) · **Contract:** [`specs/telemetry.yaml`](../../telemetry.yaml)

## Why
A library that lends books but cannot say how many loans it opened today, or
why borrowing is being refused, cannot be operated. The numbers are part of
the product's contract with the people who run it, so they are specified
like any other behaviour.

## Rules
- **OPS-R1** — Every HTTP request is recorded in `http.server.request.duration` with its method, route template and status code, in the bucket boundaries `specs/telemetry.yaml` gives.
- **OPS-R2** — Opening and closing a loan are counted (`library.loans.opened`, `library.loans.closed` with `library.late`), and late fees are summed in cents (`library.late_fees.cents`) — from the integration events, not from inside the domain.
- **OPS-R3** — Every domain refusal is counted in `library.refusals` by its problem `code`.
- **OPS-R4** — Metrics are exposed for scraping at `GET /metrics`, outside the API contract; every metric in `specs/telemetry.yaml` appears there with its attributes.
