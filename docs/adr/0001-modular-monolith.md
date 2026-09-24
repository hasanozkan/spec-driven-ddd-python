# ADR-0001 — One deployable, bounded contexts inside it

**Status:** accepted

## Context
Two contexts (Catalog, Lending) with different language and invariants, one
small team, one database's worth of data.

## Decision
A modular monolith: one process, one repository, each context a package with
its own `domain / application / infrastructure / api` layers. Boundaries are
enforced by import rules at build time (`make imports`), not by network hops.

## Rejected
- **Microservices from day one** — pays for distribution (deploys, retries,
  eventual consistency across the network) before any boundary has proven it
  needs it.
- **One flat package** — cheapest today, but nothing stops the catalog from
  reading loan tables tomorrow; the boundary would exist only in people's heads.

## Consequences
A context can be extracted later along a line that already exists in the
code: its only coupling is the event contracts.
