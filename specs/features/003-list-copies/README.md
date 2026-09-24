# 003 — List a book's copies

**Status:** shipped · **Context:** Catalog · **ADRs:** 0002

## Why
A client that lets a reader borrow needs to name a copy. Search answers "how
many are on the shelf"; this answers "which ones".

## Rules
- **CAT-R3** — Listing a book's copies returns each copy's id and whether it is on loan, following the same loan events as availability; an unknown book is refused.

## Flow
1. `GET /catalog/books/{isbn}/copies` → `[{copy_id, on_loan}]`

## Errors
| Situation | HTTP | `code` |
|---|---|---|
| Unknown book | 404 | `book_not_found` |
