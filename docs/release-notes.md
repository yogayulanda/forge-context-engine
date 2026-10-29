# Release Notes

## Unreleased

Proposed (design only, no code yet): opt-in autopilot control plane, `forge run`, that lets any AI tool orchestrate a spec through plan, ECP, execute, review, and validation to one pull/merge request per spec or batch, with deterministic gates and human merge. See `docs/decisions/ADR-0001-autopilot-control-plane.md` and `specs/autopilot.md`.

Batched execution from real usage (go-core internal release, 2026-10): per-workstream ECP approval took 4-5 round trips per batch; grouping and one approval per round cut about 15 review cycles to 2. No new modes, statuses, or artifact types.

Fixed:

- `forge update` no longer stops with a conflict when a wrapper (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`) has user content outside the Forge-managed block; only the block is refreshed, as specified.
- Adopting a previous-generation Forge wrapper without managed-block markers now archives and replaces it instead of appending a second copy, so the next `forge update` stays conflict-free.
- `scripts/validate_forge_cli.py` realigned with the current CLI: version read from `version.py`, v2 numbered context, `.forge/runtime/` paths, `codex,copilot` default tools, `.github/skills/`, and replace semantics for `--tools`.

- `plan`: an SDD is closed against the code before `ready_for_implementation`, with all decisions needed in one list; Implementation Split groups work into the fewest reviewable batches.
- `implementation`: may produce one ECP per remaining batch in one response, with recurring rules and the non-blocking details execute may decide.
- `execute`: may run a named set of approved batch ECPs in order, reporting per batch; decides non-blocking details and reports them instead of stopping.
- Gate 2 (`docs/workflow.md`): one explicit approval may cover a named set of batch ECPs, never batches not yet produced or not named.

## 1.1.0rc1

Forge `1.1.0rc1` is the release-candidate hardening milestone for daily repo usage. This RC keeps the product simple:

- fresh repo: `forge init`
- existing or legacy Forge repo: `forge update`
- workspace repo: `forge init --workspace`
- preview before refresh: `forge update --dry-run`
- refresh selected wrappers: `forge update --tools codex,copilot` or `forge update --tools codex,claude`

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
- Copilot support is opt-in and uses `.github/copilot-instructions.md` plus `.github/skills/**/SKILL.md` when selected.
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
