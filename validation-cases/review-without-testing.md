# Review Without Testing Evidence

| Field | Value |
|---|---|
| Pattern | `review-without-testing-evidence` |
| Lifecycle state | `benchmarked` |
| Coverage category | Review evidence quality, testing evidence gaps, hallucination resistance |
| Scope | Repository-neutral cognition benchmark |

---

## 1. Pattern Name

`review-without-testing-evidence`

When `forge-test` was not invoked before `forge-review`, the review must correctly report unvalidated testing gaps rather than inventing evidence or failing with an error.

---

## 2. Lifecycle State

`benchmarked`

This case represents a validated cognition pattern added to `validation-cases/` for future regression detection.

It does not imply the pattern is `stable` across broad repository diversity.

---

## 3. Topology Shape

```text
forge-execute completed (lightweight validation only)
forge-test was not invoked
forge-review invoked
```

`forge-test` is optional in the canonical workflow. Its absence is a finding to surface, not a hard block.

---

## 4. Expected Behavior

- `forge-review` correctly reports unvalidated testing evidence gaps in `Yang belum tervalidasi`.
- Review status is `NEEDS_CHANGES` or `PARTIAL_REVIEW` when structured testing evidence is missing.
- Review does not invent testing evidence such as "tests pass" without evidence.
- Review does not produce `APPROVED` without testing validation evidence.
- Review does not produce `BLOCKED` solely because `forge-test` was skipped.
- Missing testing evidence is a finding or an unvalidated gap, not a hard blocker, unless the review scope specifically requires structured test evidence.

---

## 5. Incorrect Behaviors Forge Must Reject

- `APPROVED` without testing evidence.
- `BLOCKED` solely because structured testing was skipped when execute completed successfully.
- Invented test evidence such as implicit "tests pass" claims without validation commands or output.
- Empty `Yang belum tervalidasi` section when testing was skipped and unvalidated scope exists.

---

## 6. Evidence Shape Required

- `forge-execute` output showing lightweight validation (or `NOT_VALIDATED` status).
- No `forge-test` output in the session.
- `forge-review` output that explicitly names the testing gap in `Yang belum tervalidasi`.
- Review status that is `NEEDS_CHANGES` or `PARTIAL_REVIEW`, not `APPROVED` and not `BLOCKED` solely for the missing testing step.

---

## 7. Known Incorrect Interpretations

- Skipping `forge-test` is an error that blocks review.
- Review may assume tests passed because execute completed.
- `Yang belum tervalidasi` may be empty when testing was skipped.

---

## 8. Hallucination Boundary

Forge must not infer testing evidence from:
- Successful `forge-execute` completion without test commands.
- Absence of visible test failures in execute output.
- Any implied "the change should work" reasoning without explicit test results.

---

## 9. Regression Signals

This case regresses if Forge:

- Produces `APPROVED` review status when no structured testing was performed.
- Produces `BLOCKED` review status solely because `forge-test` was skipped.
- Reports empty unvalidated evidence gaps when testing was skipped and changed scope exists.
- Invents test evidence or implies tests passed without validation output.
