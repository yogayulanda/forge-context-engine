# MR Review

Use this example when a branch or MR needs a senior engineering review.

## Review Request

```text
Use Forge review mode on this branch.
Focus on correctness, approved boundaries, validation honesty, rollback readiness, and MR readiness.
```

Expected output:

- one review result
- MR readiness
- critical, major, minor, and info findings
- validation gaps
- rollback and safety notes
- suggested next action

## Good Review Focus

Ask for specific risks when relevant:

```text
Use Forge review mode on this MR.
Focus on retry safety, idempotency, raw payload logging, transaction boundaries, and hidden schema changes.
```

## Fixing Findings

After a human accepts the findings to fix:

```text
Use Forge execute mode to fix the approved MAJOR findings only.
Do not make unrelated cleanup or file-wide formatting changes.
```

Review mode should not become a broad task list or silently mutate the repository.
