# ADR-0002 — Contexts talk through integration events only

**Status:** accepted

## Decision
A context never imports or calls another. It publishes facts
(`LoanOpened`, `CopyRegistered`, …) defined in `library.contracts.events`, and
others subscribe. Each context keeps the projection of the other's facts that
it needs (Lending knows which copies exist; Catalog knows which are on loan).

The bus in this sample is synchronous and in-process. In production the same
contracts would travel through a transactional outbox to a broker; the
publishing and subscribing code would not change.

## Rejected
- **Direct calls** (`catalog.is_available(copy)` from Lending) — couples
  Lending's invariant to Catalog's uptime and model.
- **Shared tables** — the fastest way to lose a boundary.
