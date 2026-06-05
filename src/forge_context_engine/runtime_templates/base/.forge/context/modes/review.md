---
id: mode.review
title: "Mode: Review"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-04
---

# Mode: Review

## include
- `layers/<related>`
- `knowledge/decisions/`

## on_demand
- Approved plan
- ECP
- Execution report
- Git diff / changed files
- Validation results
- `systems/<related>`
- `knowledge/inferred.md`
- `knowledge/assumptions.md`
- `.forge/generated/<relevant>`

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
6000

## purpose
Inspect executed result against approved plan, ECP, validation evidence, risk policy, security expectations, and context impact.

## inputs
- Approved plan.
- ECP.
- Execution report.
- Git diff / changed files.
- Validation results.
- Relevant `.forge/context`.
- Policy config.

## behavior
- Check goal alignment, scope compliance, code quality/repo style, validation evidence, risk/safety, security, and context impact.
- Inspect security-sensitive areas when relevant: auth/authz, input validation, sensitive data exposure, secret handling, injection risk, IDOR, SSRF, file upload, and OWASP-relevant risks.
- Treat validation gaps as review findings without becoming execute mode.
- Do not fix code directly.

## outputs
- Review Result.
- Status.
- Summary.
- Critical Findings.
- Major Findings.
- Minor Findings.
- Validation Evidence.
- Security Review.
- Context Impact.
- Recommendation.
- Next Mode.

## status values
- `ready_for_mr`
- `needs_fix`
- `needs_validation`
- `needs_context_update`
- `blocked_by_decision`
- `unsafe`

## boundaries
- Do not edit code, produce an ECP, or run broad implementation planning.
- Do not approve unsupported production-ready or fully validated claims.
- Do not replace current repository evidence with stale context/artifacts.

## next mode transitions
- `needs_fix` -> `execute`.
- `needs_validation` -> `execute`.
- `needs_context_update` -> context patch / `verify-context`.
- `blocked_by_decision` -> `plan`.
- `unsafe` -> stop / redesign.
- `ready_for_mr` -> MR-ready.
