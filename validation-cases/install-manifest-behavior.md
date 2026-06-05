# Install Manifest Behavior

| Field | Value |
|---|---|
| Pattern | `install-manifest-behavior` |
| Lifecycle state | `benchmarked` |
| Coverage category | Manifest schema, adoption-preview, managed ownership |
| Scope | Forge v0.4 install/update |

---

## Expected Behavior

`forge init` and `forge init --workspace` create:

```text
.forge/forge-install.yaml
```

The manifest must include at least:
- `manifest_version`
- `forge_version`
- `profile`
- `selected_tools`
- `installed_from`
- `installed_at`
- `template_revision`
- `source_revision`
- `managed_paths`
- `user_owned_paths`
- `local_only_paths`
- `managed_file_hashes`

Manifest-less runtime adoption behavior:
- `forge update --dry-run` shows adoption preview and writes nothing.
- `forge update --yes` writes `.forge/forge-install.yaml` and proceeds with managed update.

## Incorrect Behaviors Forge Must Reject

- Updating runtime-managed files without install-state ownership boundaries.
- Writing a manifest during adoption dry-run.
- Treating user-owned context or local-only paths as manifest-managed.

## Regression Signals

This case regresses if adoption-preview disappears, if manifest ownership data is incomplete, or if update safety no longer depends on explicit install state.
