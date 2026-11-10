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

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/security.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. Put team-specific rules (libraries, error shapes, naming, test commands) in the copy, not here.

## Load
- `.forge/runtime/meta/conventions-risk.md`.
- The security/access profile file and the interfaces/contracts profile file.

## As reviewer
- Authentication: every new or changed entry point requires the expected authentication.
- Authorization: the caller is checked against the resource owner or role, not only "is logged in".
- Input: values crossing a trust boundary are validated for type, length, range, and format.
- Injection: queries, commands, and templates use parameters, never string concatenation of input.
- Secrets: no raw secrets, tokens, keys, or credentials in code, tests, logs, artifacts, or examples.
- Data exposure: responses and logs return only fields the caller needs; PII is masked in logs.
- Money and transactions: amounts use exact types, state transitions are guarded, and duplicates are rejected or idempotent. Never classify this as LOW risk.
- Dependencies: no new dependency with known issues or without a stated reason.
- Verdict rule: any finding in this checklist blocks `accept` until fixed or explicitly accepted by a human.
