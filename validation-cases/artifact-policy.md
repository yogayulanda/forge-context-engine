# Artifact Policy

| Field | Value |
|---|---|
| Pattern | `final-artifact-policy` |
| Lifecycle state | `benchmarked` |
| Coverage category | Artifact lifecycle, context boundary, local-only data |
| Scope | Repository-neutral artifact benchmark |

---

## Expected Behavior

Final artifact and context paths:

```text
.forge/context = committed curated source of truth
.forge/context-patches = reviewable context update proposals
.forge/generated = generated artifacts committed manually when relevant
.forge/temp = ignored/local-only
.forge/cache = ignored/local-only
```

Generated artifacts may include Quick Plans, ECPs, execution reports, review results, and context verification results when they help reviewers understand or validate the change.

## Incorrect Behaviors Forge Must Reject

- Treating `.forge/generated` as always ignored or always committed.
- Treating `.forge/generated` as authoritative over source code, ADRs, or `.forge/context`.
- Committing `.forge/temp` or `.forge/cache`.
- Storing raw secrets, hidden chain-of-thought, or broad conversation history in artifacts.

## Regression Signals

This case regresses if artifact paths drift back to `.forge/context/generated` as the current policy or if temp/cache are not local-only.
