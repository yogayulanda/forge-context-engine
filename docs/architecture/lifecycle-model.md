# Lifecycle Model

Forge lifecycle modes separate different engineering jobs so one assistant response does not blur understanding, planning, coding, validation, and review.

## Visible Modes

| Mode | Owns | Does not own |
|---|---|---|
| `ask` | Understanding current behavior and context. | Planning, mutation, broad audit. |
| `planning` | Engineering change plan. | Detailed executable task cards or code changes. |
| `implementation` | Task cards, execution values, stop conditions. | Code changes. |
| `execute` | Approved repository changes. | Redesigning the plan or approving missing high-risk decisions. |
| `testing` | Structured validation. | MR approval or architecture redesign. |
| `review` | Correctness, risk, validation honesty, MR readiness. | Running the full test strategy or mutating code by default. |
| `incident` | Diagnosis, mitigation, rollback possibility, next checks. | Speculative redesign or unsupported root-cause claims. |
| `refactor` | Bounded behavior-preserving cleanup. | Architecture rewrite or hidden behavior change. |

## Human-Directed Transitions

A common path is:

```text
ask -> planning -> implementation -> execute -> testing -> review
```

These transitions are human-directed. Forge does not automatically advance modes, approve risky decisions, open PRs, deploy, or merge.

## Handoff Artifacts

Artifacts under `.forge/context/generated/artifacts/` can record:

- ECP
- Execution Contract
- Execute Result
- Testing Result
- Review Result
- Incident
- Refactor

Artifacts are optional continuity helpers. Links between artifacts are trace references only, not workflow state, dependency graphs, triggers, or orchestration.

## Status Honesty

Forge reports blockers and validation limits explicitly. Missing tools or infrastructure are environment blockers. Missing contracts, approval, ownership, or runtime behavior are work blockers. Unvalidated changes must not be reported as fully validated.
