# Forge Runtime Install and Update Specification

| Field | Value |
|---|---|
| Document | Forge Runtime Install and Update Specification |
| Version | 1.1.0rc1 |
| Date | 2026-06-05 |
| Status | `draft` |
| Scope | GitHub-installed CLI contract, safe runtime init/update semantics, ownership boundaries |
| Dependency | `specs/context-initialization.md`, `specs/runtime-migration.md`, `specs/adapter-command-foundation.md` |

---

## 0. Purpose

This document defines the `1.1.0rc1` release-candidate install/update layer for Forge.

It standardizes:
- a lightweight Python CLI package
- GitHub-based installation through `uv tool install`
- service and workspace runtime profiles
- install manifest schema
- safe ownership boundaries for runtime-managed files
- safe update and adoption-preview behavior

This document does NOT:
- redesign the Forge lifecycle
- add new lifecycle modes
- add agent runtime behavior
- add orchestration, DAGs, schedulers, CI/CD, memory, RAG, vector databases, or autonomous execution
- permit copying target source code into Forge
- make adapters the source of lifecycle truth

---

## 1. CLI Command Contract

CLI executable name:

```text
forge
```

Initial installation flow:

```text
uv tool install git+https://github.com/yogayulanda/forge-context-engine.git
```

Primary command contract:

```text
forge --version
forge init
forge init --workspace
forge update
forge update --dry-run
forge migrate-context --dry-run
forge migrate-context
forge update --tools codex,copilot
forge update --tools codex,claude
forge update --tools opencode
```

Rules:
- Current directory is the default target.
- `--target` may exist for automation, tests, or scripting, but it is not the primary UX.
- `--tools` supports non-interactive selection such as `codex,copilot`, `codex,claude`, `opencode`, `codex,opencode`, or `all`.
- `--yes` supports future non-interactive confirmation.
- `--dry-run` supports future preview without writing files.

Implemented behavior:
- `forge --version` is implemented.
- `forge init` writes the service profile.
- `forge init --workspace` writes the workspace profile.
- fresh service init seeds the v2 numbered service context profile.
- fresh workspace init seeds the v2 numbered workspace context profile.
- `forge update` updates managed files, supports `--tools`, and supports manifest-less adoption preview.
- `forge migrate-context --dry-run` previews direct legacy-v1 to v2 context migration without writing files.
- `forge migrate-context` directly writes numbered v2 context files into `.forge/context/`, archives legacy-v1 context under `.forge/context-archive/legacy-v1/`, and updates `context_profile_version: "2"` after successful migration.
- `forge update` does not migrate context automatically.

Recommended CLI validation examples:

```text
uv run python -m forge_context_engine.cli --version
uv run python -m forge_context_engine.cli init --help
uv run python -m forge_context_engine.cli update --help
```

Editable tool validation example:

```text
uv tool install --editable .
forge --version
```

---

## 2. Service Profile Behavior

Service profile is the default behavior for:

```text
forge init
```

Expected target-repo output:

```text
AGENTS.md
.github/copilot-instructions.md
.github/skills/
.forge/
```

Additional output only when Claude is explicitly selected:

```text
CLAUDE.md
.claude/.gitignore
.claude/commands/
```

Service profile stores repository-local service context. Forge does not choose or create a global workspace location.

Service profile expectations:
- service context owns repo-specific facts and implementation detail
- service context is the default source for repo-scoped tasks and code execution
- service context does not become a workspace-wide coordination file

Fresh service init seeds these user-owned v2 files under `.forge/context/`:
- `00-index.md`
- `01-service-overview.md`
- `02-architecture.md`
- `03-domain-boundaries.md`
- `04-interfaces-and-contracts.md`
- `05-data-and-persistence.md`
- `06-business-rules-and-flows.md`
- `07-integrations-and-dependencies.md`
- `08-security-and-access.md`
- `09-errors-and-resilience.md`
- `10-observability-and-support.md`
- `11-runtime-deployment-and-config.md`
- `99-open-questions.md`

Tool defaults:
- default selected tools: `codex`, `copilot`
- Claude and OpenCode are opt-in
- only selected tool entrypoints are created

---

## 3. Workspace Profile Behavior

Workspace profile is selected with:

```text
forge init --workspace
```

Workspace profile stores cross-service and domain context in the current repository only. It is a thin coordination layer and does not replace service repo context.

Expected additions relative to service profile:
- `.forge/workspace.yaml`

Expected `.forge/workspace.yaml` shape:

```yaml
version: 1
workspace:
  name: <workspace-name>
  description: ""
  default_context_policy: selective
linked_services:
  - name: <service-name>
    path: <relative-path-or-reference>
    role: <optional-service-role>
    context_root: .forge/context
    notes: <optional-user-note>
boundaries:
  - Workspace context coordinates services; service context owns repo-specific facts.
  - Do not duplicate service-level implementation details here.
loading_policy:
  default: service-first
  cross_repo: load workspace summary, then only relevant linked service context
default_tools:
  - codex
  - copilot
```

Rules:
- linked services are user-editable
- workspace summary is human-editable and must remain lightweight
- workspace context coordinates repos/services but does not duplicate service-local implementation detail
- service repo `.forge/context` remains authoritative for service-specific facts
- repo-scoped tasks start from current repo context first
- cross-repo tasks load workspace context first, then only relevant linked service context
- broad-loading all linked repos by default is forbidden
- Forge does not choose workspace location automatically
- workspace repositories do not imply global state or background coordination

Fresh workspace init seeds these user-owned v2 files under `.forge/context/`:
- `00-index.md`
- `01-platform-overview.md`
- `02-system-map.md`
- `03-service-catalog.md`
- `04-domain-boundaries.md`
- `05-cross-service-flows.md`
- `06-interfaces-and-contracts.md`
- `07-data-ownership-and-consistency.md`
- `08-security-and-access.md`
- `09-observability-and-support.md`
- `10-testing-and-quality.md`
- `12-release-and-feature-flags.md`
- `99-open-questions.md`

---

## 4. Install Manifest Schema

Installed repositories use:

```text
.forge/forge-install.yaml
```

Minimum schema:

```yaml
manifest_version: "1"
context_profile_version: "2"
forge_version: "1.1.0rc1"
profile: service
selected_tools:
  - codex
  - copilot
installed_from: git+https://github.com/yogayulanda/forge-context-engine.git
installed_at: "2026-06-05T00:00:00Z"
template_revision: "<package-template-revision>"
source_revision: "<git-commit-or-tag>"
managed_paths:
  - AGENTS.md
  - .github/copilot-instructions.md
  - .github/skills/
  - .forge/adapter.md
  - .forge/forge.config.yaml
  - .forge/forge-install.yaml
  - .forge/generated/README.md
  - .forge/context-patches/README.md
  - .forge/context-archive/README.md
  - .forge/skills/
  - .forge/runtime/meta/
  - .forge/runtime/modes/
user_owned_paths:
  - .forge/context/00-index.md
  - .forge/context/01-service-overview.md
  - .forge/context/00-index.md
  - .forge/context/01-platform-overview.md
  - .forge/context/99-open-questions.md
  - .forge/context/01-core/
  - .forge/context/layers/
  - .forge/context/repo-map/
  - .forge/context/systems/
  - .forge/context/knowledge/
  - .forge/context/decisions/
  - .forge/context/unknowns/
  - .forge/context-patches/
  - .forge/generated/
local_only_paths:
  - .forge/temp/
  - .forge/cache/
managed_file_hashes:
  .forge/adapter.md: "<sha256>"
  .forge/forge.config.yaml: "<sha256>"
  .forge/runtime/meta/conventions.md: "<sha256>"
  .forge/runtime/modes/ask.md: "<sha256>"
```

The manifest exists to:
- detect installed profile and selected tools
- detect context profile version for compatibility
- define managed vs user-owned vs local-only boundaries
- support safe updates
- support adoption-preview for older manifest-less installs

`forge update --tools ...` replaces `selected_tools`, adds missing selected entrypoints safely, and removes obsolete managed entrypoints only when the existing files are still safe managed content. User-edited or ambiguous files are preserved and reported as conflicts for manual review.

---

## 5. Ownership Model

### 5.1 Managed Paths

Managed paths may be updated by `forge update` when safe:
- `.forge/.gitignore`
- `AGENTS.md` when Codex or OpenCode selected
- `CLAUDE.md` when Claude selected
- `.claude/.gitignore` when Claude selected
- `.claude/commands/*` when Claude selected
- `.github/copilot-instructions.md` when Copilot selected
- `.github/skills/*` when Copilot selected
- `.forge/adapter.md`
- `.forge/forge.config.yaml`
- `.forge/forge-install.yaml`
- `.forge/generated/README.md`
- `.forge/context-patches/README.md`
- `.forge/context-archive/README.md`
- `.forge/skills/*`
- runtime-owned `.forge/runtime/meta/*`
- runtime-owned `.forge/runtime/modes/*`

### 5.2 User-Owned Paths

User-owned paths must be preserved:
- v2 numbered service/workspace context files under `.forge/context/`
- `.forge/context/repo-map/`
- `.forge/context/systems/`
- `.forge/context/knowledge/`
- `.forge/context/decisions/`
- `.forge/context/unknowns/`
- `.forge/context-patches/`
- `.forge/generated/`
- current v0.3.1 repo-owned context paths such as `.forge/context/01-core/` and `.forge/context/layers/` when present

### 5.3 Local-Only Paths

Local-only paths must never be treated as pushable runtime-managed output:
- `.forge/temp/`
- `.forge/cache/`

---

## 6. Managed Block Strategy

Managed blocks apply to root entrypoint files when Forge must coexist with user content.

Managed block markers:

```html
<!-- BEGIN FORGE MANAGED BLOCK -->
<!-- END FORGE MANAGED BLOCK -->
```

Targets:
- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`

Rules:
- if the file does not exist, Forge may create the full file
- if the file exists and already contains a Forge-managed block, Forge may update only that block
- if the file exists and has user content but no managed block, Forge must not overwrite blindly
- when safe in-place block insertion is not possible, Forge must stop with an explicit conflict or preview result
- shared adapter behavior remains centralized in `.forge/adapter.md`
- root entrypoints remain thin wrappers and must not become duplicate lifecycle or policy stores

---

## 7. Tool Selection Behavior

Tool selection contract:
- default selected tools: `codex`, `copilot`
- Claude and OpenCode are opt-in
- `all` means `codex`, `claude`, `copilot`, `opencode`
- only selected tool entrypoints are created
- explicit `--tools` replaces the selected tool set instead of unioning with previous defaults

Default target output stays:

```text
AGENTS.md
.github/copilot-instructions.md
.github/skills/
.forge/
```

Claude adds:

```text
CLAUDE.md
.claude/.gitignore
.claude/commands/
```

Legacy `.github/prompts/**` wrappers are not part of current init/update output.

OpenCode does not add a second root wrapper. It uses the shared `AGENTS.md` surface when selected.

Detailed adapter docs remain in the Forge engine repository/package and are not copied into every target repository.

---

## 8. Update and Adoption Behavior

### 8.1 Manifest Present

When `.forge/forge-install.yaml` exists:
- detect profile
- detect context profile version and context layout
- detect selected tools
- detect managed paths
- update only managed runtime/template files
- preserve user-owned and local-only paths
- do not silently overwrite local modifications

### 8.2 Manifest Missing But Forge Runtime Detected

`forge update` enters adoption-preview mode when:
- Forge runtime files are present
- `.forge/forge-install.yaml` is missing

Adoption-preview behavior:
- detect likely profile and selected tools
- show the proposed manifest content and managed-path interpretation
- require confirmation unless `--yes` is provided
- write `.forge/forge-install.yaml` only after confirmation

### 8.3 No Forge Runtime Detected

If no Forge runtime is detected:
- stop with a clear message
- do not infer or create installation state silently

---

## 9. Conflict and Dry-Run Behavior

Conflict behavior:
- never overwrite existing entrypoint files blindly
- never overwrite user-owned context paths
- if a managed file was locally modified, report conflict and exit non-zero
- `--yes` does not bypass unsafe managed-file overwrite boundaries
- if ownership is ambiguous, stop and report the ambiguity

Dry-run behavior:
- show target root
- show selected profile
- show detected Forge profile
- show detected context profile version; manifest-less `empty-or-unknown` adoption reports legacy-v1 compatibility because no v2 migration is implied
- show detected context layout: `legacy-v1`, `v2`, `mixed`, or `empty-or-unknown`
- show that migration or cleanup is not applied automatically
- show that user-owned context is preserved
- show selected tools
- show planned creates, updates, skips, adoptions, and conflicts
- do not write files
- do not write `.forge/forge-install.yaml` during adoption preview

---

## 10. Forge v2 Migration and Update Acceptance Matrix

| Invariant | Expected behavior | Evidence / source | Current test coverage | Gap if any | Recommended minimal fix |
| --- | --- | --- | --- | --- | --- |
| Active v2 context stays under `.forge/context/**` | Treat numbered v2 context files as user-owned source of truth; update refreshes runtime around them but does not overwrite them | `specs/artifact-lifecycle.md`, `install_manifest.py`, `runtime_ops.py`, real state in `transaction-history-service/.forge/context/` and `go-core/.forge/context/` | `tests/test_context_profiles.py` covers v2 detection, migration, and preservation | None confirmed | None |
| Runtime lives under `.forge/runtime/**`, not `.forge/context/00-meta` or `.forge/context/modes` | Update should use `.forge/runtime/meta/**` and `.forge/runtime/modes/**`; legacy runtime under `.forge/context/00-meta` and `.forge/context/modes` is deprecated residue to report or archive/clean safely | `runtime_ops.py` deprecated runtime constants and cleanup logic; real archive state in `go-core/.forge/context-archive/deprecated-runtime/` | Deprecated runtime dry-run/apply and idempotence tests in `tests/test_context_profiles.py` | None confirmed | None |
| Copilot support uses `.github/skills/**/SKILL.md` plus `.github/copilot-instructions.md` | Current output exports Copilot skills from canonical Forge skills; Copilot wrappers stay thin | `docs/adapters/github-copilot.md`, `runtime_ops.py`, real state in both repos under `.github/skills/` | `tests/test_tool_selection.py`, `tests/test_context_profiles.py` Copilot init/update coverage | None confirmed | None |
| Forge no longer generates `.github/prompts/**` | Init/update must not materialize legacy prompt wrappers | `runtime_templates/` excludes prompt wrappers; `build_managed_paths()` excludes `.github/prompts/` | `tests/test_tool_selection.py` asserts no prompt templates/output; update tests assert `.github/prompts` absent after clean convergence | None confirmed | None |
| Known legacy `.github/prompts/forge-*.prompt.md` are obsolete managed output | Dry-run reports them; apply removes only the known Forge-managed prompt files; unknown prompt files remain | `LEGACY_COPILOT_PROMPT_FILES` in `runtime_ops.py`; real residue in `transaction-history-service/.github/prompts/` | Existing dry-run/apply preservation tests in `tests/test_context_profiles.py` | Confirmed before this change: cleanup/reporting was gated on Copilot still being selected | Remove tool-selection gate; keep cleanup list explicit and preserve unknown prompt files |
| Claude files exist only when Claude is selected | `CLAUDE.md`, `.claude/.gitignore`, and `.claude/commands/**` are managed only for Claude-enabled repos; explicit tool replacement removes obsolete managed Claude files safely | `build_managed_paths()`, `_build_init_files()`, obsolete managed cleanup in `runtime_ops.py` | `tests/test_context_profiles.py` and `tests/test_tool_selection.py` cover Claude init/update/removal | None confirmed | None |
| OpenCode is opt-in and not tracked as shared tool-neutral output | Canonical shared skills stay under `.forge/skills/**`; OpenCode adds only `.opencode/opencode.json` and `.opencode/skills/**` when selected, while sharing `AGENTS.md` | `install_manifest.py`, `runtime_ops.py`, `docs/adapters/opencode.md` | `tests/test_tool_selection.py` covers managed paths, init files, detection, and migration to canonical Forge skills | None confirmed | None |
| `.forge/context-archive/**`, `.forge/context-patches/**`, and `.forge/generated/**` are not active source of truth | Archive is low-trust historical reference, patches are reviewable proposals, generated is working output only | `specs/artifact-lifecycle.md`, `docs/workflow.md`, update-context skill/mode templates | `tests/test_tool_selection.py` asserts update-context instructions forbid treating these as active truth | No install/update matrix row previously captured this convergence rule explicitly | Add this matrix row for acceptance clarity only |
| Archive directories are preserved as ignored/low-trust user-owned paths | Update should keep `.forge/context-archive/README.md` managed, archive contents local by default, and never promote archive facts automatically | `FORGE_LOCAL_GITIGNORE`, `build_user_owned_paths()`, real archive state in both repos | Archive and migration tests in `tests/test_context_profiles.py` | None confirmed | None |
| Unknown user files are preserved | Safe cleanup applies only to known managed files/paths; ambiguous or user-owned content is reported or left untouched | Obsolete managed cleanup logic, entrypoint conflict handling, real unknown prompt preservation requirement | Unknown prompt preservation and user-edited wrapper preservation tests in `tests/test_context_profiles.py` | None confirmed | None |
| Dry-run reports cleanup without writing files | Preview must list safe cleanup candidates, including known legacy prompt residue and deprecated runtime paths, without modifying the repo | `run_update(..., dry_run=True)` behavior in `runtime_ops.py` | Dry-run tests for prompts, migration, adoption, and deprecated runtime paths | None confirmed | None |
| Apply mode performs only safe known managed cleanup | Apply may remove known obsolete managed files, archive deprecated managed runtime, and stop on ambiguous ownership | `runtime_ops.py` cleanup and conflict paths | Existing apply tests for obsolete managed files, runtime archive, and prompt cleanup | None confirmed after prompt-gate fix | None |
| Repeated `forge update` is idempotent | After safe convergence, a repeat dry-run should show `Created: 0`, `Updated: 0`, `Conflicts: 0` | `run_update()` refresh flow and manifest hashing | Existing idempotence tests for deprecated runtime cleanup and Copilot convergence | None confirmed | None |

---

## 11. Safety Boundaries

Forge install/update must not:
- copy target source code into Forge
- modify target source code as part of init/update
- copy engine-only folders such as `docs/`, `specs/`, `validation-cases/`, or `runtime/adapters/` into target repositories
- add lifecycle modes
- add runtime agents, orchestration, CI/CD, DAGs, schedulers, memory systems, or autonomous execution
- move lifecycle ownership into adapters or tool entrypoints

---

## 12. Validation Expectations

Validation for the CLI install/update layer should cover:
- package metadata and console-script wiring
- `forge --version`
- `forge init --help`
- `forge update --help`
- service init writes the expected default files
- workspace init writes `.forge/workspace.yaml`
- dry-run writes nothing
- update preserves user-owned context
- update reports conflict for modified managed files
- manifest-less adoption dry-run writes nothing
- manifest-less adoption with `--yes` writes `.forge/forge-install.yaml`
- known legacy `.github/prompts/forge-*.prompt.md` files are reported in dry-run
- known legacy `.github/prompts/forge-*.prompt.md` files are removed in apply mode
- unknown `.github/prompts/*.prompt.md` files are preserved
- current Copilot support does not generate `.github/prompts/**`
- repeated `forge update --tools codex,copilot` converges cleanly
- packaged runtime templates contain no `__pycache__` or `*.pyc`
- packaged runtime templates include `.forge/runtime/meta/*` and `.forge/runtime/modes/*`
- manifest schema documentation completeness
- ownership model completeness
- Copilot opt-in behavior
- current-directory default target behavior
- absence of engine-folder copy semantics in target-repo output
- absence of new lifecycle modes

```text
uv run python -m forge_context_engine.cli --version
uv run python -m forge_context_engine.cli init --help
uv run python -m forge_context_engine.cli update --help
uv tool install --editable .
forge --version
```

Batch B adds validation for actual init/update filesystem behavior.
