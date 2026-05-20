---
id: knowledge.confirmations
title: Confirmations Audit Log
type: knowledge
status: confirmed
confidence: high
source: human
owner: TBD
updated: 2026-05-20
---

# Confirmations

Audit log for status promotions to `confirmed`. Source of truth for when & by whom context was promoted.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Audit ledger — append-only, authoritative |
| AI writable | No — only humans write confirmations (AI proposes only) |
| Human confirmation | This IS the confirmation file |
| Populated | Each time an entry is promoted from `inferred`/`assumption` to `confirmed` |

## Rules

- Entries never deleted, only appended.
- Each entry references target file/ID & supporting evidence.

## Entries

| Date | Target ID | From → To | Confirmer | Evidence | Notes |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
