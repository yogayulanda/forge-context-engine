# Getting Started

Use this guide when you want the first successful Forge setup and invocation in a repository.

Goal: within 10-15 minutes, a new engineer should be able to install the runtime template, invoke one mode, and understand the next workflow step.

Status note:
- v0.4 GitHub-installed `forge` CLI is implemented
- `forge init`, `forge init --workspace`, and `forge update` are now implemented
- manual runtime copy remains a compatible fallback for direct repo use

## What You Need

- A repository with code or docs that Forge can inspect.
- For CLI setup: `uv`
- For manual fallback setup: the Forge `runtime/` directory from this repository.
- At least one supported AI tool surface:
  - Claude with `CLAUDE.md`
  - Codex with `AGENTS.md`
  - GitHub Copilot with opt-in instructions

Forge does not require a server, daemon, workflow engine, scheduler, or separate memory store.

## v0.4 CLI Flow

Implemented v0.4 flow:

```text
uv tool install git+https://github.com/yogayulanda/forge-context-engine.git

cd my-service
forge init

cd work-context
forge init --workspace

cd initialized-repo
forge update
forge update --tools codex,claude
```

Current behavior:
- `forge --version` works
- `forge init` writes the service profile in the current directory by default
- `forge init --workspace` writes the workspace profile in the current directory by default
- `forge update` updates managed runtime files, supports `--tools`, and supports manifest-less adoption preview

Local CLI smoke examples:

```text
uv run python -m forge_context_engine.cli --version
uv run python -m forge_context_engine.cli init --help
uv run python -m forge_context_engine.cli update --help
```

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
   - `forge.version: "0.5.0a0"` for the current runtime config shape.
   - `ui.language: en` by default; switch to `id` when you want Indonesian human-facing narration and progress updates.
   - Forge Plans, ECPs, Execute Reports, Review Reports, task cards, specs, validation commands, commit messages, and generated Markdown artifacts stay English by default unless you explicitly request another language.
   - `run.interaction: manual` for local human-in-the-loop work.
   - `workflow.default_mode: ask` unless the repository has an explicit reason to start elsewhere.
   - `context.root: .forge/context` so context stays repository-local.
   - `policy.require_human_confirmation_for` covers important domain, data, architecture, contract, security, and migration changes.
   - `tools.adapters` defaults to `codex` and `claude`; add Copilot only when needed.

3. Keep `.forge/context` repository-first.

   Start from runtime skeleton files, then populate repo facts from code, docs, ADRs, and human confirmations. Do not copy broad assumptions into context.

4. Keep tool entrypoints thin.

   `CLAUDE.md` and `AGENTS.md` should point to `.forge/adapter.md` and `.forge/context`. They should not store repo-specific cognition, lifecycle logic, or artifact policy.

5. Make one scoped first request.

   ```text
   Use Forge ask mode to explain how this service handles retries. Cite the repository evidence and list unknowns.
   ```

   Read-only mode prompt UX:

   ```text
   Use Forge plan mode for adding a small health check function.
   ```

   You do not need to append `Do not edit files` for `plan` or `implementation`. That wording is still allowed as a safety probe, but the mode contract already enforces the no-edit boundary.

## CLAUDE.md And AGENTS.md Usage

Use `CLAUDE.md` for Claude-compatible assistants. It should be a thin wrapper that tells the assistant to:

- read `.forge/adapter.md`
- treat `.forge/context` as source of truth
- follow the requested lifecycle mode with scoped context only

Use `AGENTS.md` for Codex-compatible assistants. It should be a thin wrapper that maps natural prompts such as `Use Forge review mode` to the Forge lifecycle defined in `.forge/adapter.md`.

Both files are entrypoints only. `.forge/context` remains the source of truth, `.forge/generated` remains generated output only, and `.forge/temp` plus `.forge/cache` stay local-only.

## Supported Tool Overview

| Tool | Common invocation | Runtime path |
|---|---|---|
| Claude | `/forge-plan`, `/forge-review`, or natural language | `CLAUDE.md`, `.forge/adapter.md`, `.forge/context/` |
| Codex | `$forge-review`, `/skill forge-review`, or natural language | `AGENTS.md`, `.forge/adapter.md`, `.forge/context/` |
| GitHub Copilot | `/forge-review`, `/forge-plan`, `/forge-ask` prompt files | `.github/copilot-instructions.md` when selected |

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
3. `implementation`: produce an ECP and stop conditions.
4. Human approval: approve the ECP for execution.
5. `execute`: apply the approved ECP only and run scoped validation.
6. `review`: assess MR readiness, security, validation gaps, and context impact.
7. `verify-context`: run when source changes may affect curated context.

Small, low-risk edits can skip `plan` when the scope is obvious. Risky, ambiguous, contract-heavy, or production-sensitive work should not skip plan.

Next, read [First Workflow](first-workflow.md) to see this path end to end, then use [Mode Selection](mode-selection.md) when you need to choose the smallest fitting lifecycle mode.

## Common Beginner Mistakes

| Mistake | Better approach |
|---|---|
| Asking `execute` to start before scope or values are clear. | Use `plan` or `implementation` first. |
| Loading all of `.forge/context` for every question. | Load the requested mode and task-relevant context only. |
| Treating generated artifacts as source of truth. | Use artifacts as handoff records; current repo evidence wins. |
| Putting repo facts in `CLAUDE.md`, `AGENTS.md`, or adapters. | Put repo cognition in `.forge/context`. |
| Using an incident scenario as a redesign request. | Diagnose first; hand off approved remediation to `plan`, `implementation`, and `execute` as needed. |
| Treating Copilot, Claude, or Codex behavior as separate Forge versions. | Keep the tool surface thin and resolve to shared skills. |

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
