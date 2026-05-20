---
id: knowledge.unknowns
title: Unknowns Ledger
type: knowledge
status: confirmed
confidence: high
source: human
owner: TBD
updated: 2026-05-20
---

# Unknowns

Acknowledged knowledge gaps. Mandatory destination when AI encounters incomplete information. **Guessing forbidden.**

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Ledger — append-only |
| AI writable | Yes — AI **must** write here when encountering a gap, not guess |
| Human confirmation | Not required to add; required to close (resolve) |
| Populated | Throughout lifecycle, especially during init & when agents encounter uncertainty |

## Rules

- Each entry has owner & status.
- Resolution: answer goes to correct semantic location (`01-core/`/`layers/`/`systems/` if human fact, or `inferred.md` if AI inference), then unknown entry marked `resolved`.

## Entries

| ID | Question / Gap | Owner | Created | Status | Resolution |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
