# 001 — Borrow a copy

**Status:** shipped · **Context:** Lending (+ Catalog projection) · **ADRs:** 0002, 0003

## Why
A member takes a copy home. The library must never lend one copy twice, must
keep a member within their tier's limits, and must tell them when it is due.

## Rules
Each rule has an id. Every id is proven by at least one test tagged
`@pytest.mark.rule("<id>")`, and `make trace` fails the build otherwise.

- **LEND-R1** — Only a copy the library knows about and that is not on an active loan can be borrowed.
- **LEND-R2** — A member's active loans never exceed their tier's `max_active_loans`.
- **LEND-R3** — A loan is due `loan_days` (by tier) after the day it is borrowed.
- **LEND-R4** — A member with outstanding fees cannot borrow until they are paid.
- **CAT-R1** — The catalog shows a copy as on loan from the moment its loan opens until it closes.

## Flow
1. `POST /lending/loans {member_id, copy_id}`
2. Lending checks LEND-R1, R4, R2 (in that order — the answer names the first rule that refused).
3. Loan opens with `due_on` (LEND-R3); `LoanOpened` is published.
4. Catalog marks the copy on loan (CAT-R1).

## Errors
| Situation | HTTP | `code` |
|---|---|---|
| Unknown member or copy | 404 | `member_not_found` / `copy_not_found` |
| Copy already on loan | 409 | `copy_on_loan` |
| Tier limit reached | 409 | `loan_limit_reached` |
| Outstanding fees | 409 | `fees_outstanding` |

## Done when
- [x] Rules above each have a tagged test
- [x] Contract snapshot (`contracts/openapi.json`) updated
- [x] Catalog projection follows the events, not the lending tables
