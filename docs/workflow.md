# The workflow: spec → decision → slice → gate

This repository is small on purpose. What it demonstrates is the *order* in
which work happens and the *mechanisms* that keep that order honest.

## 1. The spec leads
A change starts in `specs/`, not in `src/`:
- the words it needs go into `specs/domain/ubiquitous_language.md`;
- the behaviour goes into a feature folder as **numbered rules** (`LEND-R5`);
- numbers that are policy (limits, fees) go into `specs/policy.yaml`.

A feature is *ready* (Definition of Ready) when its rules are written, its
errors are named, and the context that owns it is clear.

## 2. Decisions are recorded once
A choice that constrains future work — a module boundary, how contexts talk,
where a number lives — becomes an ADR in `docs/adr/`. The ADR says what was
decided, what was rejected and why. Code comments point at ADRs instead of
re-arguing them.

## 3. The work is a vertical slice
One feature = one slice through one context: `domain` (rules as plain
functions and entities) → `application` (use case, publishes events) → `api`
(HTTP). Another context reacts to the published event; it is never called.

## 4. Gates, not guidelines
Every rule above is checked by the build (`make check`), so a reviewer reads
intent, not conventions:

| Gate | Proves |
|---|---|
| `make imports` | Contexts do not import each other; layers point one way; the domain has no framework |
| `make mirror` | The code's policy is byte-identical to the spec's |
| `make trace` | Every spec rule has a test, and no test cites a rule that does not exist |
| `make test` | The rules hold |
| `make contracts` | The HTTP contract in `contracts/openapi.json` matches the code — an API change is visible in review |
| `make lint` / `make types` | Style and strict typing |
| gitleaks (CI) | No secret enters the history |

## 5. Definition of Done
Rules tagged and green, contract snapshot updated in the same PR, ADR written
if a decision was made, ubiquitous language updated if a word was added.
