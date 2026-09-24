# Instructions for coding agents

Read before changing anything:

1. **The spec leads.** Behaviour changes start in `specs/features/<n>-<slug>/README.md`
   as numbered rules (`LEND-R8`). New words go into `specs/domain/ubiquitous_language.md`
   first. Do not add behaviour that no rule describes.
2. **Policy numbers live in `specs/policy.yaml`.** Change them there, then copy the
   file to `src/library/lending/domain/policy.yaml`. Never hard-code a limit or a fee.
3. **Contexts never import each other.** `catalog` and `lending` talk through
   `library.contracts.events` only. If you need data from the other context, subscribe
   to its event and keep a projection.
4. **Layers point one way:** `api → application → domain`. The domain imports no
   framework.
5. **Every rule gets a test** tagged `@pytest.mark.rule("<id>")`.
6. **An API change regenerates the snapshot** in the same change: `make contracts-update`.
7. **A decision that constrains future work gets an ADR** in `docs/adr/`.
8. **Run `make check` before you say you are done**, and report its result as it is.
