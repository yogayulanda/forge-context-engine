# Forge Runtime Install and Update Specification

| Field | Value |
|---|---|
| Document | Forge Runtime Install and Update Specification |
| Version | 1.0.0rc1 |
| Date | 2026-06-05 |
| Status | `draft` |
| Scope | GitHub-installed CLI contract, safe runtime init/update semantics, ownership boundaries |
| Dependency | `specs/context-initialization.md`, `specs/runtime-migration.md`, `specs/adapter-command-foundation.md` |

---

## 0. Purpose

This document defines the `1.0.0rc1` release-candidate install/update layer for Forge.

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
forge update --tools codex,claude
forge update --tools opencode
```

Rules:
- Current directory is the default target.
- `--target` may exist for automation, tests, or scripting, but it is not the primary UX.
- `--tools` supports non-interactive selection such as `codex,claude`, `opencode`, `codex,opencode`, or `all`.
- `--yes` supports future non-interactive confirmation.
- `--dry-run` supports future preview without writing files.

Implemented behavior:
- `forge --version` is implemented.
- `forge init` writes the service profile.
- `forge init --workspace` writes the workspace profile.
- `forge update` updates managed files, supports `--tools`, and supports manifest-less adoption preview.

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
CLAUDE.md
.forge/
```

Additional output only when GitHub Copilot is explicitly selected:

```text
.github/copilot-instructions.md
```

Service profile stores repository-local service context. Forge does not choose or create a global workspace location.

Service profile expectations:
- service context owns repo-specific facts and implementation detail
- service context is the default source for repo-scoped tasks and code execution
- service context does not become a workspace-wide coordination file

Tool defaults:
- default selected tools: `codex`, `claude`
- Copilot and OpenCode are opt-in
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
  - claude
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

---

## 4. Install Manifest Schema

Installed repositories use:

```text
.forge/forge-install.yaml
```

Minimum schema:

```yaml
manifest_version: "1"
forge_version: "1.0.0rc1"
profile: service
selected_tools:
  - codex
  - claude
installed_from: git+https://github.com/yogayulanda/forge-context-engine.git
installed_at: "2026-06-05T00:00:00Z"
template_revision: "<package-template-revision>"
source_revision: "<git-commit-or-tag>"
managed_paths:
  - AGENTS.md
  - CLAUDE.md
  - .forge/adapter.md
  - .forge/forge.config.yaml
  - .forge/forge-install.yaml
  - .forge/context/00-meta/
  - .forge/context/modes/
user_owned_paths:
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
  .forge/context/00-meta/conventions.md: "<sha256>"
  .forge/context/modes/ask.md: "<sha256>"
```

The manifest exists to:
- detect installed profile and selected tools
- define managed vs user-owned vs local-only boundaries
- support safe updates
- support adoption-preview for older manifest-less installs

`forge update --tools ...` updates `selected_tools`, adds missing selected entrypoints safely, and does not prune older entrypoints unless a future explicit prune flag is introduced.

---

## 5. Ownership Model

### 5.1 Managed Paths

Managed paths may be updated by `forge update` when safe:
- `.forge/.gitignore`
- `AGENTS.md` when Codex or OpenCode selected
- `CLAUDE.md` when Claude selected
- `.github/copilot-instructions.md` when Copilot selected
- `.forge/adapter.md`
- `.forge/forge.config.yaml`
- `.forge/forge-install.yaml`
- runtime-owned `.forge/context/00-meta/*`
- runtime-owned `.forge/context/modes/*`

### 5.2 User-Owned Paths

User-owned paths must be preserved:
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
- default selected tools: `codex`, `claude`
- Copilot and OpenCode are opt-in
- `all` means `codex`, `claude`, `copilot`, `opencode`
- only selected tool entrypoints are created

Default target output stays:

```text
AGENTS.md
CLAUDE.md
.forge/
```

Copilot adds:

```text
.github/copilot-instructions.md
```

OpenCode does not add a second root wrapper. It uses the shared `AGENTS.md` surface when selected.

Detailed adapter docs remain in the Forge engine repository/package and are not copied into every target repository.

---

## 8. Update and Adoption Behavior

### 8.1 Manifest Present

When `.forge/forge-install.yaml` exists:
- detect profile
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
- show selected tools
- show planned creates, updates, skips, adoptions, and conflicts
- do not write files
- do not write `.forge/forge-install.yaml` during adoption preview

---

## 10. Safety Boundaries

Forge install/update must not:
- copy target source code into Forge
- modify target source code as part of init/update
- copy engine-only folders such as `docs/`, `specs/`, `validation-cases/`, or `runtime/adapters/` into target repositories
- add lifecycle modes
- add runtime agents, orchestration, CI/CD, DAGs, schedulers, memory systems, or autonomous execution
- move lifecycle ownership into adapters or tool entrypoints

---

## 11. Validation Expectations

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
- packaged runtime templates contain no `__pycache__` or `*.pyc`
- packaged runtime templates include `.forge/context/00-meta/*` and `.forge/context/modes/*`
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
