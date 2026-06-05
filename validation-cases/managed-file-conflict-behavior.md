# Managed File Conflict Behavior

| Field | Value |
|---|---|
| Pattern | `managed-file-conflict-behavior` |
| Lifecycle state | `benchmarked` |
| Coverage category | Safe update, conservative overwrite boundaries |
| Scope | Forge v0.4 update behavior |

---

## Expected Behavior

Managed root entrypoints:
- use Forge managed blocks
- update only the managed block when one already exists
- preserve surrounding user content

Managed non-entrypoint files:
- update only when current content still matches the manifest-tracked managed hash
- report conflict and exit non-zero when the managed file was locally modified

## Incorrect Behaviors Forge Must Reject

- Blind overwrite of a modified managed file.
- Replacing user-authored root entrypoint content instead of appending/updating only the managed block.
- Treating `--yes` as permission to bypass unsafe overwrite boundaries.

## Regression Signals

This case regresses if `forge update` silently overwrites local managed-file edits or if root entrypoints lose safe managed-block behavior.
