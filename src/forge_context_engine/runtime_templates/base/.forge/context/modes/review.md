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
- Run a small per-task Context Impact Check; do not turn routine review into a full context quality audit.
- Use `update_needed: false` when changes stay internal and do not affect durable repository knowledge.
- Use `update_needed: true` when changes affect durable repository knowledge such as architecture boundaries, public API behavior, domain rules, security boundaries, operational conventions, repository structure, service/system responsibilities, dependency/provider behavior, testing/validation conventions, workflow conventions, or durable decisions/constraints.
- Use `update_needed: unknown` when evidence is insufficient to determine whether durable context should change.
- When `update_needed: true`, propose a reviewable `.forge/context-patches/<date>-<slug>.md` patch instead of editing `.forge/context` directly.
- Treat validation gaps as review findings without becoming execute mode.
- When reviewing executed changes, name the exact diff surface reviewed under `Diff Reviewed`.
- If no diff or changed-file evidence is available, say that explicitly and usually return `needs_more_validation`.
- Do not fix code directly.

## outputs
- Review Report.
- Verdict.
- Mode Boundary.
- Diff Reviewed.
- Summary.
- Critical Findings.
- Major Findings.
- Minor Findings.
- Validation Result Assessment.
- Lifecycle Boundary Assessment.
- Security / Risk Assessment.
- Context Impact.
- Recommended Next Step.

## context impact contract
Context Impact:
- `update_needed: true | false | unknown`
- `reason:`
- `affected_context_files:`
  - `.forge/context/...`
- `suggested_context_patch:`
  - `none`
  - `.forge/context-patches/<date>-<slug>.md`

When `update_needed: true`, the suggested patch proposal should be human-reviewable and include:
- Target context file(s)
- Reason
- Evidence
- Proposed update or diff
- Confidence
- Promotion notes stating human review is required before promotion into `.forge/context`

## verdict values
- `accept`
- `request_changes`
- `needs_more_validation`
- `blocked`

## boundaries
- Review mode inspects plan/ECP/diff/results.
- It does not apply fixes, commit, push, merge, or open MR/PR actions; fixes require a separately approved execution flow.
- Do not edit code, produce an ECP, or run broad implementation planning.
- Do not mutate `.forge/context` directly from review mode.
- Do not approve unsupported production-ready or fully validated claims.
- Do not replace current repository evidence with stale context/artifacts.

## next mode transitions
- `accept` -> human decides whether to commit, open MR/PR, request changes, discard the change, or continue normal repo workflow outside Forge. Forge does not commit, push, merge, or open MR/PR automatically.
- `request_changes` -> bounded fix scope through `implementation` or `execute` after human approval.
- `needs_more_validation` -> `execute` or manual validation activity.
- `blocked` -> human decision, `plan`, or context patch depending on blocker type.
