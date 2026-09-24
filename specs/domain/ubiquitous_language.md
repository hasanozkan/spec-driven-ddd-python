# Ubiquitous language

The words below mean exactly this — in the specs, in the code, in tests and in
conversations. A new term enters here before it enters a class name.

| Term | Context | Meaning |
|---|---|---|
| **Book** | Catalog | A work identified by ISBN. Not lendable itself. |
| **Copy** | Catalog, Lending | One physical item of a book. The unit that is lent. |
| **Member** | Lending | A person who may borrow, on a **tier**. |
| **Tier** | Lending | `standard` or `premium`; sets limits and fees (`specs/policy.yaml`). |
| **Loan** | Lending | One copy lent to one member, from **borrowed on** to **returned on**. |
| **Active loan** | Lending | A loan not yet returned. |
| **Due on** | Lending | The date a loan should be returned by. |
| **Late fee** | Lending | Owed when a copy comes back after its due date; capped per tier. |
| **Outstanding fees** | Lending | Late fees a member has not paid yet. |
