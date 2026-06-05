# Review With Validation Gaps

| Field | Value |
|---|---|
| Pattern | `review-with-validation-gaps` |
| Lifecycle state | `benchmarked` |
| Coverage category | Review evidence quality, validation evidence gaps, hallucination resistance |
| Scope | Repository-neutral cognition benchmark |

---

## 1. Pattern Name

`review-with-validation-gaps`

When execute ran only partial validation before `forge-review`, the review must correctly report unvalidated gaps rather than inventing evidence or failing with an error.

---

## 2. Lifecycle State

`benchmarked`

This case represents a validated cognition pattern added to `validation-cases/` for future regression detection.

It does not imply the pattern is `stable` across broad repository diversity.

---

## 3. Topology Shape

```text
forge-execute completed with partial or lightweight validation
forge-review invoked
```

Additional validation may be requested through execute or manual review. Missing validation evidence is a finding to surface, not a reason to invent a pass.

---

## 4. Expected Behavior

- `forge-review` correctly reports unvalidated evidence gaps in `Yang belum tervalidasi`.
- Review verdict is `request_changes` or `needs_more_validation` when required validation evidence is missing.
- Review does not invent validation evidence such as "tests pass" without evidence.
- Review does not produce `accept` without required validation evidence.
- Review does not produce `blocked` solely because additional validation was not requested.
- Missing validation evidence is a finding or an unvalidated gap, not a hard blocker, unless the review scope specifically requires that evidence.

---

## 5. Incorrect Behaviors Forge Must Reject

- `accept` without required validation evidence.
- `blocked` solely because additional validation was not requested when execute completed successfully.
- Invented test evidence such as implicit "tests pass" claims without validation commands or output.
- Empty `Yang belum tervalidasi` section when unvalidated scope exists.

---

## 6. Evidence Shape Required

- `forge-execute` output showing lightweight validation, partial validation, or `NOT_VALIDATED` status.
- `forge-review` output that explicitly names the validation gap in `Yang belum tervalidasi`.
- Review verdict that is `request_changes` or `needs_more_validation`, not `accept` and not `blocked` solely for missing additional validation.

---

## 7. Known Incorrect Interpretations

- Missing additional validation is an error that blocks review.
- Review may assume tests passed because execute completed.
- `Yang belum tervalidasi` may be empty when validation evidence is missing.

---

## 8. Hallucination Boundary

Forge must not infer validation evidence from:
- Successful `forge-execute` completion without relevant validation commands.
- Absence of visible failures in execute output.
- Any implied "the change should work" reasoning without explicit validation results.

---

## 9. Regression Signals

This case regresses if Forge:

- Produces `APPROVED` review status when required validation evidence is missing.
- Produces `BLOCKED` review status solely because additional validation was not requested.
- Produces `accept` review verdict when required validation evidence is missing.
- Produces `blocked` review verdict solely because additional validation was not requested.
- Reports empty unvalidated evidence gaps when changed scope lacks validation evidence.
- Invents test evidence or implies tests passed without validation output.
