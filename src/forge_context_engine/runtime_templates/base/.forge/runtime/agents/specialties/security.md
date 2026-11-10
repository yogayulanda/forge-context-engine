---
id: specialty.security
title: "Specialty: Security"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [reviewer]
applies_when: the SDD lists any high-risk area; orchestrate then runs an extra reviewer with this specialty
---

# Specialty: Security

Overlay for `forge-orchestrate` workers. It adds focus and context to a role; it never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/security.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it.

## Load
- `.forge/runtime/meta/conventions-risk.md` and the security/access profile file.

## Focus
- Review authentication, authorization, input validation, secret handling, and data exposure in the diff.
- Treat payment and transaction correctness as never LOW risk.

## Review checklist
- No raw secrets, tokens, or PII in code, logs, tests, or artifacts.
- Authorization is checked on every new or changed entry point.
- Inputs crossing a trust boundary are validated.
- Any finding here blocks `accept`.
