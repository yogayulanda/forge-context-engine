# Artifact Continuity

| Field | Value |
|---|---|
| Pattern | `artifact-continuity-v010` |
| Lifecycle state | `candidate` |
| Coverage category | Generated artifact continuity |
| Scope | Saved plan, ECP, execution report, and review report handoff |

---

## Expected Behavior

Saved generated artifacts are optional working files under `.forge/generated/...`.

Directories:

```text
.forge/generated/plans/
.forge/generated/ecp/
.forge/generated/reports/
.forge/generated/reviews/
```

Naming guidance:

```text
.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md
.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md
.forge/generated/reports/YYYY-MM-DD-<slug>-execution-report.md
.forge/generated/reviews/YYYY-MM-DD-<slug>-review.md
```

Metadata guidance:
- saved artifacts should include a small `forge_artifact` metadata header
- metadata remains optional for normal chat-only responses
- generated artifacts are not durable source of truth

Mode mapping:
- saved `plan` artifact -> `implementation`
- saved `ecp` artifact -> `execute`
- saved `execution_report` artifact -> `review`
- saved `review_report` artifact -> follow-up planning or `.forge/context-patches/...` proposal

Continuation guardrails:
- read the referenced artifact first
- verify artifact type matches requested mode
- verify the artifact still has enough evidence and approved scope
- check for material drift when evidence is available
- block or request more context when the artifact is stale or ambiguous
- do not execute from a plan artifact directly
- do not mutate `.forge/context` from generated artifact content alone

Persistence behavior:
- chat output remains the default
- save only when requested or approved
- do not overwrite existing generated artifacts without explicit approval
- do not auto-promote saved artifacts into `.forge/context`

## Dogfood Scenario

1. Create a sample plan artifact in a temp repo at `.forge/generated/plans/2026-06-05-sample-change-plan.md`.
2. Continue with implementation mode from that plan and verify the result is an ECP, not code execution.
3. Create a sample ECP artifact at `.forge/generated/ecp/2026-06-05-sample-change-ecp.md`.
4. Continue with execute mode from that ECP and verify execution stays inside approved scope.
5. Create a sample execution report at `.forge/generated/reports/2026-06-05-sample-change-execution-report.md`.
6. Continue with review mode from that report and verify review remains read-only.
7. Re-run one continuation flow with a stale or contradictory artifact and verify the outcome blocks or requests more context.

## Incorrect Behaviors Forge Must Reject

- Auto-saving every plan, ECP, execution report, or review report.
- Saving artifacts directly into `.forge/context`.
- Treating a saved artifact as approved only because it exists on disk.
- Executing from a plan artifact without an approved ECP.
- Treating a stale generated artifact as authoritative over current repository evidence.
- Overwriting `YYYY-MM-DD-<slug>-*.md` continuity files without explicit approval.
