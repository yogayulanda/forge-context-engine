---
id: mode.review
title: "Mode: Review"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
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
Inspect a plan, ECP, or executed result against goal alignment, scope boundaries, validation evidence, risk policy, security expectations, lifecycle compliance, and context impact.

## inputs
- Approved plan when available.
- ECP when available.
- Execution report when available.
- Git diff / changed files when available.
- Validation results when available.
- Relevant `.forge/context`.
- Policy config.

## behavior
- Check goal alignment, scope drift, lifecycle boundary compliance, validation evidence, risk/safety, security, and context impact.
- Inspect security-sensitive areas when relevant: auth/authz, input validation, sensitive data exposure, secret handling, injection risk, IDOR, SSRF, file upload, and OWASP-relevant risks.
- Assess whether follow-up execute work or a context patch is needed.
- Treat validation gaps as review findings without becoming execute mode.
- Do not fix code directly.

## outputs
- Verdict.
- Summary.
- Mode Boundary.
- Critical Findings.
- Major Findings.
- Minor Findings.
- Validation Result Assessment.
- Lifecycle Boundary Assessment.
- Security / Risk Assessment.
- Context Impact.
- Recommended Next Step.

## verdict values
- `accept`
- `request_changes`
- `needs_more_validation`
- `blocked`

## boundaries
- Review mode inspects plan/ECP/diff/results.
- It does not apply fixes unless explicitly moved to an approved execution flow.
- Do not edit code, produce an ECP, or run broad implementation planning.
- Do not approve unsupported production-ready or fully validated claims.
- Do not replace current repository evidence with stale context/artifacts.

## next mode transitions
- `accept` -> merge/MR decision outside Forge, or `verify-context` if context may need refresh.
- `request_changes` -> bounded fix scope through `implementation` or `execute` after human approval.
- `needs_more_validation` -> `execute` or manual validation activity.
- `blocked` -> human decision, `plan`, or context patch depending on blocker type.
