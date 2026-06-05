# Runtime Migration Protocol Specification

| Field | Value |
|---|---|
| Document | Forge Runtime Migration Protocol Specification |
| Version | 1.2 |
| Date | 2026-05-25 |
| Status | `decision` |
| Scope | Safe adoption of newer Forge runtime behavior by initialized repositories |
| Dependency | `specs/context-validation.md`, `specs/framework-lifecycle.md` |

---

## 0. Purpose

This document defines how an already initialized repository safely adopts newer Forge runtime behavior without re-running initialization or overwriting repository cognition.

Runtime migration is a controlled refresh of runtime-managed files. It is not full regeneration, repository knowledge rewrite, architecture migration, or application code modification.

This document defines:
- Runtime-managed vs repository-owned cognition files.
- Runtime migration lifecycle.
- Migration rules and forbidden behaviors.
- Validation expectations after migration.
- Re-audit expectations.
- Future compatibility direction.

This document does NOT:
- Implement automation tooling.
- Add generators or templates.
- Redesign Forge runtime folders.
- Define repository-specific cognition content.
- Permit application code modification.

---

## 1. File Ownership Boundary

Runtime migration depends on a strict ownership boundary.

### Runtime-Managed Files

Runtime-managed files may be refreshed from `forge-context-engine` runtime updates when schema-compatible.

Examples:
- `.forge/context/modes/*.md`
- `.forge/context/00-meta/conventions.md`
- `.forge/adapter.md`
- `CLAUDE.md`
- `AGENTS.md`
- Optional `.github/copilot-instructions.md` when the repository selected Copilot
- Optional runtime/config metadata when schema-compatible
- `.forge/forge.config.yaml` final v0.3.1 config keys: `forge`, `run`, `workflow`, `context`, `policy`, `team`, `artifacts`, and `tools`

Purpose:
- Operational behavior.
- Loading strategy.
- Runtime semantics.
- Interactive vs non-interactive workflow behavior.
- Automation-safe decision boundaries.
- Framework conventions.
- AI operational contract updates.

Runtime-managed files are framework behavior carriers. They must remain compatible with the target repository's existing Forge structure.

### Repository-Owned Cognition Files

Repository-owned cognition files must not be overwritten automatically by runtime migration.

Examples:
- `.forge/context/01-core/*`
- `.forge/context/layers/*`
- `.forge/context/systems/*`
- `.forge/context/knowledge/*`
- Repository-specific inferred, unknown, assumption, confirmation, and decision files

Purpose:
- Local repository evidence.
- Repository topology interpretation.
- Local constraints and decisions.
- Audit history.
- Inferred knowledge and unknown boundaries.

Repository-owned cognition files are the repository's local cognition state. Runtime migration may validate them, but must not rewrite them as part of the refresh.

---

## 2. Runtime Migration Lifecycle

Runtime migration follows this lifecycle:

1. Runtime update exists in `forge-context-engine`.
2. Target repository is already initialized and has older runtime-managed files.
3. Runtime migration is executed against the target repository.
4. Runtime-managed files are refreshed from the runtime source.
5. Repository-owned cognition files are preserved.
6. Validation and audit checks are rerun when required by semantic change.
7. Migration is completed and recorded through normal repository history.

Runtime migration must be narrow. A repository that needs full context reconstruction is outside runtime migration scope.

---

## 3. Migration Rules

Runtime migration must:
- Preserve local evidence.
- Preserve inferred, assumption, confirmation, and unknown boundaries.
- Preserve repository cognition when migrating legacy config fields such as `runtime.profile`, `runtime.non_interactive`, or `runtime.decision_authority`; these are compatibility inputs only and must map to final v0.3.1 config vocabulary.
- Preserve secret-safety boundaries: raw secrets must not be printed, copied, summarized, or migrated into runtime-managed files.
- Preserve audit/history semantics.
- Preserve repository topology reasoning.
- Refresh only runtime-managed files needed for the runtime update.
- Avoid broad context regeneration.
- Avoid application code changes.
- Keep mode files as loading deltas.
- Preserve canonical mode schema: `include`, `on_demand`, `exclude`, `token_budget`, `notes`.
- Preserve numeric-only `token_budget`.
- Use `run.interaction` for interaction behavior.
- Use `policy.require_human_confirmation_for` for important human-confirmation boundaries.
- Use `workflow.default_mode` and `workflow.disabled_modes` for workflow configuration.
- Use `artifacts.output_dir`, `artifacts.patch_dir`, `artifacts.temp_dir`, and `artifacts.cache_dir` for artifact and local-data paths.
- Report legacy-to-final config conflicts clearly instead of silently changing behavior.

Runtime migration must not:
- Re-run initialization.
- Regenerate repository context.
- Overwrite repository-owned cognition.
- Rewrite knowledge, invalidate assumptions, modify inferred context, or rewrite systems, layers, or core files because interaction behavior changed.
- Rewrite repository decisions.
- Promote inferred knowledge automatically.
- Modify architecture or runtime semantics without evidence.
- Silently change topology interpretation.
- Broad-load or rewrite the full Forge context by default.
- Modify application code, build logic, database migrations, or deployment assets.
- Copy raw secrets from existing runtime files, repository-owned cognition, configs, logs, or reports.
- Add runtime tooling, automation, generators, or folders.
- Add CI/CD, deploy workflow, schedulers, triggers, workflow/DAG execution, agent loops, runtime executors, or autonomous chaining.

If a runtime update conflicts with repository-owned cognition, record the conflict as an audit finding or unknown. Do not resolve it by guessing. If a secret is encountered, record only redacted evidence and classify it as a security finding; recommend rotation when exposure is possible.

---

## 4. Validation Expectations

After runtime migration:

| Check | Expected Result |
|---|---|
| Mode schema | Every mode file exposes `## include`, `## on_demand`, `## exclude`, `## token_budget`, `## notes` |
| Token budget | `token_budget` contains only a decimal integer |
| Runtime parity | Refreshed runtime-managed files match the selected runtime source |
| Interaction flag | `run.interaction` is `manual` or `auto` |
| Run behavior | `run.output`, `run.output_detail`, `run.write_behavior`, and `run.failure_behavior` use final v0.3.1 allowed values |
| Workflow config | `workflow.default_mode` references a final core mode and `workflow.disabled_modes` exists |
| Team workflow | `team.context_update_flow` is `reviewable_patch` and `team.require_context_impact_check` is `true` |
| Artifact paths | `.forge/generated`, `.forge/context-patches`, `.forge/temp`, and `.forge/cache` are separated by config |
| Legacy config conflict | Old fields such as `runtime.profile`, `non_interactive`, `decision_authority`, `loading.default_mode`, and `apply_allowed` are removed, mapped, or explicitly marked legacy/compatibility |
| Repository cognition | Repository-owned cognition files are unchanged unless explicitly and separately approved |
| Application code | No application code changed |
| Folder structure | No runtime, context, tooling, or application folder redesign occurred |
| Evidence boundary | Existing evidence/inference/unknown separation remains intact |
| Topology boundary | No deployability, ownership, contract, or runtime topology reinterpretation occurs without evidence |
| Secret safety | No raw secrets appear in migration output, refreshed runtime files, audit findings, or validation notes |

Validation failure means the migration is incomplete or out of scope. Fix the runtime refresh or escalate to an explicit audit task; do not silently regenerate context.

---

## 5. Re-Audit Expectations

Re-audit is required when runtime migration introduces material semantic change, including:
- Runtime semantics changed materially.
- Topology reasoning rules changed.
- Validation rules changed materially.
- Operational cognition behavior changed materially.
- Runtime interaction behavior changed materially.
- Runtime profile, decision authority, or decision risk behavior changed materially.
- Mode loading behavior changed materially.
- AI hallucination boundaries changed materially.

Re-audit is not required for:
- Cosmetic wording cleanup.
- Formatting normalization.
- Comments or examples only.
- Non-semantic runtime documentation changes.
- Metadata refresh that does not change operational behavior.

When re-audit is required, scope it to the affected behavior. Do not treat re-audit as permission to regenerate repository cognition.

---

## 6. Future Compatibility Direction

Future runtime migration may support:
- Runtime version metadata.
- Migration manifests.
- Selective migration categories.
- Dry-run migration checks.
- Runtime source parity checks.
- Migration reports.

These are future compatibility directions only. This specification does not implement automation, runtime tooling, folder redesign, migration generators, CI/CD behavior, deploy workflow, schedulers, triggers, workflow/DAG execution, runtime executors, agent loops, or autonomous chaining.

---

## 7. Completion Criteria

A runtime migration is complete when:
- Required runtime-managed files are refreshed from the selected runtime source.
- Existing repositories may adopt final `run.interaction` behavior by refreshing runtime-managed files only.
- Repository-owned cognition files are preserved.
- Validation expectations pass.
- Any required re-audit is recorded or completed.
- No application code or repository architecture changed.
- Migration is captured through normal repository history.
