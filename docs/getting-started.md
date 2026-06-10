# Getting Started

Use this guide when you want the first successful Forge setup and invocation in a repository.

Goal: within 10-15 minutes, a new engineer should be able to install the runtime template, invoke one mode, and understand the next workflow step.

Release note:
- `1.0.0rc1` hardening focuses on install, init, update, adoption, workspace usage, recovery guidance, and compact default context
- `forge init`, `forge init --workspace`, and `forge update` are the primary user flows
- manual runtime copy remains a compatible fallback when the CLI install path is not available

## What You Need

- A repository with code or docs that Forge can inspect.
- For CLI setup: `uv`
- For manual fallback setup: the Forge `runtime/` directory from this repository.
- At least one supported AI tool surface:
  - Claude with `CLAUDE.md`
  - Codex with `AGENTS.md`
  - GitHub Copilot with opt-in instructions

Forge does not require a server, daemon, workflow engine, scheduler, or separate memory store.

## CLI Flow

Current CLI flow:

```bash
uv tool install git+https://github.com/yogayulanda/forge-context-engine.git

cd my-service
forge init

cd existing-forge-repo
forge update
forge update --dry-run
forge update --tools codex,claude

cd work-context
forge init --workspace
```

Current behavior:
- `forge --version` works
- `forge init` writes the service profile in the current directory by default
- `forge init --workspace` writes the workspace profile in the current directory by default
- `forge update` updates managed runtime files, supports `--tools`, supports dry-run preview, and supports manifest-less adoption preview
- workspace profile is represented in `.forge/forge-install.yaml` as `profile: "workspace"`
- use `--yes` only for non-interactive automation or scripted adoption

Local CLI smoke examples:

```bash
uv run python -m forge_context_engine.cli --version
uv run python -m forge_context_engine.cli init --help
uv run python -m forge_context_engine.cli update --help
```

## What Forge Is

- a repo-local workflow and context contract for AI coding tools
- a safe init/update path that writes thin wrappers plus `.forge/`
- a shared lifecycle across Codex, Claude, and optional Copilot
- a boundary between curated context, generated working artifacts, and reviewable context promotions

## What Forge Is Not

- not a daemon, background agent, scheduler, CI/CD layer, or memory/vector service
- not a replacement for code, docs, ADRs, or human approval
- not a reason to store repo cognition in `AGENTS.md`, `CLAUDE.md`, or Copilot wrappers

## Manual Setup Flow

Manual setup remains available when you want to copy runtime files directly.

1. Copy the runtime template into the target repository.

   ```text
   forge-context-engine/runtime/.forge -> <target-repo>/.forge
   forge-context-engine/runtime/CLAUDE.md -> <target-repo>/CLAUDE.md
   forge-context-engine/runtime/AGENTS.md -> <target-repo>/AGENTS.md
   ```

   Default target-repo output is:

   ```text
   AGENTS.md
   CLAUDE.md
   .forge/
   ```

   Add `.github/copilot-instructions.md` only when GitHub Copilot is explicitly selected. Do not copy engine-only folders such as `docs/`, `specs/`, `validation-cases/`, `runtime/adapters/`, or `runtime/skills/` into every target repository.

2. Open `<target-repo>/.forge/forge.config.yaml`.

   Check:
   - `forge.version` for the current runtime config shape.
   - `ui.language: en` by default; switch to `id` when you want Indonesian human-facing narration and progress updates.
   - Forge Plans, ECPs, Execute Reports, Review Reports, task cards, specs, validation commands, commit messages, and generated Markdown artifacts stay English by default unless you explicitly request another language.
   - `run.interaction: manual` for local human-in-the-loop work.
   - `workflow.default_mode: ask` unless the repository has an explicit reason to start elsewhere.
   - `context.root: .forge/context` so context stays repository-local.
   - `policy.require_human_confirmation_for` covers important domain, data, architecture, contract, security, and migration changes.
   - `tools.adapters` defaults to `codex` and `claude`; add Copilot or OpenCode only when needed.

3. Keep `.forge/context` repository-first.

   Start from runtime skeleton files, then populate repo facts from code, docs, ADRs, and human confirmations. Do not copy broad assumptions into context.

   For a broad audit before trusting larger AI changes, use `ai-readiness` to inspect repository discoverability, context fitness, ambiguity, and remediation priorities without editing code.

4. Keep service and workspace responsibilities separate.

   - Service repo context owns repo-specific facts and implementation detail.
   - Workspace context owns cross-repo coordination, ownership, and dependency flow only.
   - For repo-scoped work, start from the current repo's `.forge/context`.
   - Load workspace context only when the task spans multiple repos/services or cross-repo boundaries.
   - For cross-repo work, load only the relevant linked services; do not broad-load every repo.

5. Keep tool entrypoints thin.

   `CLAUDE.md` and the shared `AGENTS.md` wrapper should point to `.forge/adapter.md` and `.forge/context`. Optional `.github/copilot-instructions.md` should do the same. These wrappers should not store repo-specific cognition, lifecycle logic, or artifact policy.

6. Make one scoped first request.

   ```text
   Use Forge ask mode to explain how this service handles retries. Cite the repository evidence and list unknowns.
   ```

   Read-only mode prompt UX:

   ```text
   Use Forge plan mode for adding a small health check function.
   ```

   You do not need to append `Do not edit files` for `plan` or `implementation`. That wording is still allowed as a safety probe, but the mode contract already enforces the no-edit boundary.

7. Save generated artifacts only when you actually need continuity.

   Recommended saved artifact paths:

   ```text
   .forge/generated/plans/YYYY-MM-DD-<slug>-plan.md
   .forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md
   .forge/generated/reports/YYYY-MM-DD-<slug>-execution-report.md
   .forge/generated/reviews/YYYY-MM-DD-<slug>-review.md
   ```

   Default behavior is still chat output first. Saved artifacts are working files only; they are not `.forge/context`, and they are not auto-promoted into durable context.

## Fresh Repo, Existing Repo, And Workspace

Use the smallest matching entrypoint:

- Fresh service repo: `forge init`
- Existing or legacy Forge repo: `forge update`
- Workspace coordination repo: `forge init --workspace`
- Safer preview before a managed refresh: `forge update --dry-run`

Existing or legacy repo adoption guidance:
- if Forge files already exist without `.forge/forge-install.yaml`, `forge update` is the adoption path
- adoption preserves user-owned context and local-only directories
- adoption may stop on locally modified managed files so you can review them instead of losing changes

## CLAUDE.md And AGENTS.md Usage

Use `CLAUDE.md` for Claude-compatible assistants. It should be a thin wrapper that tells the assistant to:

- read `.forge/adapter.md`
- treat `.forge/context` as source of truth
- follow the requested lifecycle mode with scoped context only

Use `AGENTS.md` for AGENTS-compatible assistants such as Codex and OpenCode. It should be a thin wrapper that maps natural prompts such as `Use Forge review mode` to the Forge lifecycle defined in `.forge/adapter.md`.

Both files are entrypoints only. `.forge/context` remains the source of truth, `.forge/generated` remains generated output only, and `.forge/temp` plus `.forge/cache` stay local-only.

Universal lifecycle artifacts stay tool-neutral. If you need tool-specific hints, place them under a clearly labeled `Target Tool Notes` section instead of mixing them into universal Plan, ECP, Execute Report, or Review instructions.

Workspace repos add one more rule: `.forge/workspace.yaml` coordinates linked services, but service repo `.forge/context` remains authoritative for service-specific facts.

## Supported Tool Overview

| Tool | Common invocation | Runtime path |
|---|---|---|
| Claude | `/forge-plan`, `/forge-review`, or natural language | `CLAUDE.md`, `.forge/adapter.md`, `.forge/context/` |
| Codex | `$forge-review`, `/skill forge-review`, or natural language | `AGENTS.md`, `.forge/adapter.md`, `.forge/context/` |
| GitHub Copilot | `/forge-review`, `/forge-plan`, `/forge-ask`, or natural language | `.github/copilot-instructions.md` when selected |
| OpenCode | `Use Forge review mode`, `/forge-review`, or natural language | `AGENTS.md`, `.forge/adapter.md`, `.forge/context/` |

Tool syntax may differ. The expected behavior should resolve to:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

## First Successful Invocation

Start with `ask` mode because it does not mutate files or require an approved plan.

Good first request:

```text
Use Forge ask mode to explain the request path for creating an order.
Separate repository evidence, inferred assumptions, and unknowns.
```

Expected output:

- short explanation of the current flow
- file or code references when available
- clear unknowns instead of guesses
- no change plan unless you ask for plan mode
- no code modification

If the answer says evidence is missing, that is a successful Forge outcome. It means the assistant stayed inside repository-first truth.

## Expected First Workflow

A first real change usually looks like this:

1. `ask`: understand current behavior.
2. `plan`: describe the change, risks, validation, rollback, and unknowns.
3. Human approval: approve the plan for implementation.
4. `implementation`: produce an ECP and stop conditions.
5. Human approval: approve the ECP for execution.
6. `execute`: apply the approved ECP only and run scoped validation.
7. `review`: assess verdict, diff reviewed, security, validation gaps, and context impact.
8. `verify-context`: run when source changes may affect curated context.

Small, low-risk edits can skip `plan` when the scope is obvious. Risky, ambiguous, contract-heavy, or production-sensitive work should not skip plan.

Saved artifact continuation examples:

```text
Use Forge implementation mode from .forge/generated/plans/2026-06-05-add-export-plan.md
Use Forge execute mode from .forge/generated/ecp/2026-06-05-add-export-ecp.md
Use Forge review mode from .forge/generated/reports/2026-06-05-add-export-execution-report.md
```

Next, read [First Workflow](first-workflow.md) to see this path end to end, then use [Mode Selection](mode-selection.md) when you need to choose the smallest fitting lifecycle mode.

## Artifact Directories And Boundaries

Use these paths consistently:

- `.forge/context/` for curated source-of-truth context
- `.forge/generated/plans/`, `.forge/generated/ecp/`, `.forge/generated/reports/`, `.forge/generated/reviews/` for saved working artifacts
- `.forge/context-patches/` for reviewable durable-context update proposals
- `.forge/temp/` and `.forge/cache/` for local-only scratch and cache

Short rule:
- context is durable truth
- generated is working output
- context-patches are proposals awaiting review

## Common Beginner Mistakes

| Mistake | Better approach |
|---|---|
| Asking `execute` to start before scope or values are clear. | Use `plan` or `implementation` first. |
| Loading all of `.forge/context` for every question. | Load the requested mode and task-relevant context only. |
| Treating workspace context as a replacement for service context. | Use workspace context for cross-repo coordination only; read the service repo's `.forge/context` for service facts. |
| Treating generated artifacts as source of truth. | Use artifacts as handoff records; current repo evidence wins. |
| Putting repo facts in `CLAUDE.md`, `AGENTS.md`, or adapters. | Put repo cognition in `.forge/context`. |
| Using an incident scenario as a redesign request. | Diagnose first; hand off approved remediation to `plan`, `implementation`, and `execute` as needed. |
| Treating Copilot, Claude, or Codex behavior as separate Forge versions. | Keep the tool surface thin, route to `.forge/adapter.md`, and preserve the same artifact boundaries. |

## Known Limitations

- The documented install path is GitHub plus `uv`; PyPI publishing is not part of this release flow.
- `forge update` refreshes managed runtime files; it does not redesign an existing repository.
- Copilot support is opt-in and may depend on the host environment's prompt-file behavior.
- Manifest-less legacy repos can be adopted, but local managed-file edits may require manual conflict resolution.
- Workspace repos coordinate linked services; they do not replace service-repo evidence.

## Troubleshooting And Recovery

- `forge: command not found`
  Reinstall with `uv tool install git+https://github.com/yogayulanda/forge-context-engine.git` and confirm the `uv` tool bin directory is on `PATH`.
- Running from the wrong directory
  Run Forge from the repository root you want to initialize or update. `forge update` expects an existing Forge runtime in that repo.
- Dirty repo before update
  Review `git status` and run `forge update --dry-run` first so managed-file changes are obvious before you apply them.
- Legacy config migration
  If update detects an older config shape, Forge backs up the old file as `.forge/forge.config.legacy.yaml` before writing the current managed config.
- Managed file conflict
  Forge stops instead of overwriting a locally modified managed file. Keep your edits, inspect the conflicting file, and decide whether to preserve or replace it.
- Wrapper already exists
  Forge can adopt an existing Forge-like wrapper and avoid duplicating the managed block. Check the update report to confirm adoption.
- `forge update --dry-run` still shows changes
  That usually means the repo has not yet adopted the current managed template set, selected tools changed, or a managed file is out of date.
- Copilot opt-in behavior
  `.github/copilot-instructions.md` is created only when Copilot is selected. Existing non-Copilot repos do not get `.github/` output by default.
- Accidental local artifacts such as `__pycache__`
  Delete local cache files and directories before packaging, release review, or template sync checks.

## Release Checklist

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 scripts/validate_forge_cli.py`
- fresh service init smoke
- workspace init smoke
- legacy/adoption update smoke
- idempotent update dry-run
- runtime/template sync check
- artifact hygiene check
- docs sanity check

## Lightweight Setup Example

For a backend service:

```text
1. Copy runtime files.
2. Keep `backend` and `testing` in `layers_enabled` when the repository actually owns those layers.
3. Add one system entry for the service after verifying repo evidence.
4. Ask: "Use Forge ask mode to explain retry and idempotency behavior."
5. If a change is needed, ask: "Use Forge plan mode for improving retry behavior without changing the public contract."
```

For an OSS contributor:

```text
1. Read README and docs/mode-selection.md.
2. Ask `ask` mode to understand the affected area.
3. Use `plan` for non-trivial changes.
4. Keep the MR description aligned with Forge validation and review output.
```

## Setup Checklist

- `.forge/forge.config.yaml` exists.
- `.forge/adapter.md` exists.
- `.forge/context/modes/` contains the visible lifecycle modes.
- `CLAUDE.md` and/or `AGENTS.md` point to `.forge/adapter.md` and `.forge/context` instead of duplicating repo facts.
- `.forge/temp/` and `.forge/cache/` are treated as local-only and are not pushed.
- First `ask` request returns evidence, inferences, and unknowns.
- No adapter implies autonomous execution, orchestration, or hidden memory.
