# CLI Contract Batch B

| Field | Value |
|---|---|
| Pattern | `cli-contract-batch-b` |
| Lifecycle state | `benchmarked` |
| Coverage category | Packaging, command contract, init/update behavior |
| Scope | Forge v0.4 Batch B |

---

## Expected Behavior

Batch B provides:

```text
forge --version
forge init
forge init --workspace
forge update
```

Constraints:
- `forge --version` returns the installed package version.
- `forge init` writes the service profile safely.
- `forge init --workspace` writes the workspace profile safely.
- `forge update` updates managed runtime files safely.
- `--target` may exist as an optional automation/test argument, but current directory remains the default target UX.
- uv-first validation examples should use `uv run python -m forge_context_engine.cli ...` or `uv tool install --editable .` rather than presenting `pip` as the normal user install path.

## Incorrect Behaviors Forge Must Reject

- Blindly overwriting existing entrypoint files.
- Updating user-owned context as part of `forge update`.
- Copying engine-only docs/specs/validation assets into target repositories.
- Choosing a global workspace location automatically.
- Adding a CLI contract that hides or removes `forge init --workspace`.

## Regression Signals

This case regresses if docs or CLI output imply unsupported behavior, or if init/update bypass safe ownership boundaries.
