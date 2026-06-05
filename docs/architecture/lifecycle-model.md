# Lifecycle Model

Forge lifecycle modes separate different engineering jobs so one assistant response does not blur `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context`.

## Core Modes

| Mode | Owns | Does not own |
|---|---|---|
| `init` | Creating confirmed repository context and Forge config. | Dumping the whole repository into context or making hidden decisions. |
| `ask` | Understanding current behavior and context from scoped evidence. | Planning, mutation, broad audit, or ECP creation. |
| `plan` | Quick Plan or SDD with scope, risk, evidence, validation, and status. | Detailed executable task cards or code changes. |
| `implementation` | Execution Context Package from an approved plan. | Code changes, commits, pushes, merges, deploys, or applying patches. |
| `execute` | Approved ECP application within explicit boundaries. | Redesigning the plan or approving missing high-risk decisions. |
| `review` | Executed-result review: correctness, scope, validation, security, and context impact. | Mutating code by default or replacing execution. |
| `verify-context` | `.forge/context` health, freshness, and consistency only. | Plan readiness, ECP completeness, code diff correctness, MR readiness, or general validation. |

## Scenarios, Not Core Modes

Incident response, behavior-preserving refactors, and test-focused work are workflow scenarios. They use the core modes as needed: usually `ask`, `plan`, `implementation`, `execute`, and `review`. Validation work happens inside `execute` and `review`, with deeper test planning treated as a scoped validation activity rather than a core lifecycle mode.

## Human-Directed Transitions

A common path is:

```text
init -> ask -> plan -> implementation -> execute -> review -> verify-context
```

These transitions are human-directed. Forge does not automatically advance modes, approve risky decisions, open PRs, deploy, or merge.

## Handoff Artifacts

Artifacts can record:

- Quick Plan or SDD
- Execution Context Package
- Execution Report
- Review Result
- Context Verification Result
- Context patch proposal

Artifacts are optional continuity helpers. Links between artifacts are trace references only, not workflow state, dependency graphs, triggers, or orchestration.

## Status Honesty

Forge reports blockers and validation limits explicitly. Missing tools or infrastructure are environment blockers. Missing contracts, approval, ownership, runtime behavior, or context freshness are work blockers. Unvalidated changes must not be reported as fully validated.
