# Workspace Multi-Repo Boundary

| Field | Value |
|---|---|
| Pattern | `workspace-multirepo-boundary` |
| Lifecycle state | `benchmarked` |
| Coverage category | Workspace/service boundary, selective cross-repo loading |
| Scope | Forge v0.9 workspace dogfood |

---

## Expected Behavior

- `forge init --workspace` creates a human-editable `.forge/workspace.yaml`.
- Workspace profile is represented in `.forge/forge-install.yaml` as `profile: "workspace"`.
- Workspace context is a thin coordination layer for linked repos/services, ownership, dependency flow, and cross-repo planning.
- Service repo `.forge/context` remains authoritative for repo-specific facts and implementation details.
- Repo-scoped work starts from current service repo context first.
- Cross-repo work loads workspace context first and then only the relevant linked service contexts.
- Broad-loading all linked repos by default is forbidden.
- User-edited linked service entries in `.forge/workspace.yaml` are preserved by `forge update`.

## Incorrect Behaviors Forge Must Reject

- Treating workspace context as a replacement for service context.
- Duplicating service-specific implementation detail into `.forge/workspace.yaml`.
- Broad-loading every linked repo for ordinary single-repo work.
- Discarding user-edited linked service entries during workspace update.

## Regression Signals

This case regresses if workspace docs/specs imply broad multi-repo loading, if service/workspace authority becomes ambiguous, or if workspace update stops preserving user-edited linked service references.
