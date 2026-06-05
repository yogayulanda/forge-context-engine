# Release Notes

## 1.0.0rc1

Forge `1.0.0rc1` is the release-candidate hardening milestone for daily repo usage. This RC keeps the product simple:

- fresh repo: `forge init`
- existing or legacy Forge repo: `forge update`
- workspace repo: `forge init --workspace`
- preview before refresh: `forge update --dry-run`
- refresh selected wrappers: `forge update --tools codex,claude`

Included in this RC:

- stable init/update/adoption flow for service and workspace repos
- shared `.forge/adapter.md` with thin Codex, Claude, and optional Copilot wrappers
- artifact continuity through `.forge/generated/...` without making generated files default context
- context patch workflow through `.forge/context-patches/...`
- selective workspace loading and service-first authority rules
- install/update troubleshooting, release checklist, and runtime/template sync checks

Validation performed:

- CLI validator run from source
- local CLI help/version smoke
- fresh service init smoke plus `forge update --dry-run`
- workspace init smoke plus `forge update --dry-run`
- local editable/install smoke
- read-only real-repo `forge update --dry-run` checks for `go-core` and `transaction-history-service`

Known limitations:

- GitHub plus `uv` is the documented install path for this RC; PyPI publishing is not part of the release.
- `forge update` refreshes Forge-managed files only; it does not migrate arbitrary repo conventions.
- Copilot support is opt-in and depends on the host environment honoring the instruction file.
- Workspace repos coordinate linked services but do not replace service-repo `.forge/context`.

Recommended daily workflow:

1. `ask` for current behavior and evidence.
2. `plan` for non-trivial changes.
3. Human approval.
4. `implementation` for the ECP.
5. Human approval.
6. `execute` inside approved scope.
7. `review` for findings and context impact.
8. `verify-context` only when durable context may need refresh.

Upgrade note:

- fresh repo -> `forge init`
- existing or legacy repo -> `forge update`
