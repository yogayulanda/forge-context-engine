---
id: knowledge.inferred
title: Inferred Knowledge Ledger
type: knowledge
status: confirmed
confidence: high
source: human
owner: TBD
updated: 2026-05-20
---

# Inferred

AI inference ledger quarantined from human-authored facts. **Non-authoritative.**

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Quarantine ledger — append-only |
| AI writable | Yes — new inferences written here, **never** to `source: human` files |
| Human confirmation | Required to promote entry to `confirmed` |
| Populated | During init (brownfield gap-filling) and throughout normal operation |

## Rules

- Each entry **must** have `evidence` (code path, doc, ADR, or external source).
- Entry status ≤ `inferred` until promoted via `confirmations.md`.
- If evidence changes, entry demotes to `assumption` or is removed.

## Entries

| ID | Inference | Evidence | Owner | Created | Status |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
