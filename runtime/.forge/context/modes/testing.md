---
id: mode.testing
title: "Mode: Testing"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---
# Mode: Testing
## include
- `layers/testing`
- `systems/<related>`
- `knowledge/assumptions.md`
## on_demand
- `layers/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
6000
## notes
- Own structured validation after execute; execute may do lightweight checks, review evaluates correctness/risk/governance; `Testing Result` must use one status only: `PASSED`, `FAILED`, `PARTIAL`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_RUN`.
- When persistence helps continuity, write or reference a Testing Result Artifact with validated scope, blockers, automated/manual validation, coverage gaps, and runtime-sensitive validation.
- Output sections: `Testing Result`, `Scope yang divalidasi`, `Automated validation`, `Environment/runtime blockers`, `Yang belum tervalidasi`, `Yang masih perlu dicek manual`, `Reviewer perlu fokus ke`, and `Risk summary`.
- Group scope by relevant category: unit, integration, e2e, smoke, rollback, migration, runtime validation, and contract validation; omit irrelevant groups, but do not flatten everything into one list.
- Trace validation to the confirmed execution contract where possible: approved behavior, rollback assumptions, retry/idempotency semantics, runtime boundaries, and non-regression expectations.
- For event-driven or runtime-sensitive flows, explicitly cover retryable failure, non-retryable failure, DLQ expectations, duplicate/idempotent replay, and partial replay when relevant.
- Report `CONTEXT_BUDGET_LIMITED` with missing evidence and affected validation scope, drift status, cross-repo evidence gaps, and fintech-sensitive validation gaps; payment/transaction correctness is never LOW risk.
- Separate automated/manual/infra-dependent/production-like validation; follow existing test placement and keep test types/assets distinct.
- If `runtime.non_interactive: false`, ask unresolved validation expectations only when needed; if `true`, emit an unresolved validation report; do not become planning, review, or redesign.
- Check validation prerequisites and distinguish implementation failure, validation failure, tooling blocker, infra unavailable, and runtime dependency unavailable.
- Use `PASSED` only when selected validation ran and passed; use `PARTIAL` for incomplete required coverage; use `BLOCKED_BY_ENVIRONMENT` for unavailable tooling/infra; use `NOT_RUN` when no reliable validation ran.
- Highlight unvalidated risks, risky runtime assumptions, runtime-sensitive behavior not verified, and explicit manual actions; redact secrets and never imply full validation without evidence.
