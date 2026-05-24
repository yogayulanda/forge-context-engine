# Runtime Migration Protocol Specification

| Field | Value |
|---|---|
| Document | Forge Runtime Migration Protocol Specification |
| Version | 1.0 |
| Date | 2026-05-24 |
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
- Implement automation or tooling.
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
- `CLAUDE.md`
- Optional runtime/config metadata when schema-compatible

Purpose:
- Operational behavior.
- Loading strategy.
- Runtime semantics.
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
- Preserve secret-safety boundaries: raw secrets must not be printed, copied, summarized, or migrated into runtime-managed files.
- Preserve audit/history semantics.
- Preserve repository topology reasoning.
- Refresh only runtime-managed files needed for the runtime update.
- Avoid broad context regeneration.
- Avoid application code changes.
- Keep mode files as loading deltas.
- Preserve canonical mode schema: `include`, `on_demand`, `exclude`, `token_budget`, `notes`.
- Preserve numeric-only `token_budget`.

Runtime migration must not:
- Re-run initialization.
- Regenerate repository context.
- Overwrite repository-owned cognition.
- Rewrite repository decisions.
- Promote inferred knowledge automatically.
- Modify architecture or runtime semantics without evidence.
- Silently change topology interpretation.
- Broad-load or rewrite the full Forge context by default.
- Modify application code, build logic, database migrations, or deployment assets.
- Copy raw secrets from existing runtime files, repository-owned cognition, configs, logs, or reports.
- Add runtime tooling, automation, generators, or folders.

If a runtime update conflicts with repository-owned cognition, record the conflict as an audit finding or unknown. Do not resolve it by guessing. If a secret is encountered, record only redacted evidence and classify it as a security finding; recommend rotation when exposure is possible.

---

## 4. Validation Expectations

After runtime migration:

| Check | Expected Result |
|---|---|
| Mode schema | Every mode file exposes `## include`, `## on_demand`, `## exclude`, `## token_budget`, `## notes` |
| Token budget | `token_budget` contains only a decimal integer |
| Runtime parity | Refreshed runtime-managed files match the selected runtime source |
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

These are future compatibility directions only. This specification does not implement automation, runtime tooling, folder redesign, or migration generators.

---

## 7. Completion Criteria

A runtime migration is complete when:
- Required runtime-managed files are refreshed from the selected runtime source.
- Repository-owned cognition files are preserved.
- Validation expectations pass.
- Any required re-audit is recorded or completed.
- No application code or repository architecture changed.
- Migration is captured through normal repository history.
