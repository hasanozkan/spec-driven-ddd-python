# 002 — Return a copy, late fees

**Status:** shipped · **Context:** Lending (+ Catalog projection) · **ADRs:** 0003

## Rules
- **LEND-R5** — A copy returned after its due date costs `late_fee_per_day_cents` for each day late, capped at `max_late_fee_cents` (by tier). On or before the due date it costs nothing.
- **LEND-R6** — The fee is added to the member's outstanding fees when the copy is returned; paying clears them.
- **LEND-R7** — A loan can be returned once; a second return is refused.
- **CAT-R2** — Once returned, the copy shows as available again.

## Flow
1. `POST /lending/loans/{loan_id}/return` → the loan closes with its late fee (LEND-R5, R6); `LoanClosed` is published.
2. Catalog marks the copy available (CAT-R2).
3. `POST /lending/members/{member_id}/payments` clears outstanding fees (LEND-R6).

## Errors
| Situation | HTTP | `code` |
|---|---|---|
| Unknown loan | 404 | `loan_not_found` |
| Already returned | 409 | `loan_already_returned` |
