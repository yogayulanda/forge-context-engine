---
id: mode.init
title: "Mode: Init"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-04
---

# Mode: Init

## include
- `00-meta/*`
- `01-core/*`

## on_demand
- Repository tree, README/docs, build/config files, package manifests, tests, representative source files, CI/workflow files, API/interface definitions, migrations, and auth/security files when present

## exclude
- Full raw repository dumps
- Unrelated generated/vendor/cache files

## token_budget
10000

## purpose
Create confirmed repository context and Forge config.

## inputs
- Target repository.
- Existing docs/code/config/tests.
- Developer confirmation for ambiguous or important decisions.

## behavior
- Run a bounded repo scan.
- Draft `.forge/context` and `.forge/forge.config.yaml`.
- Ask ambiguity questions with three options: preserve current behavior, adopt safer/canonical behavior, or conditional/depends.
- Require developer confirmation before finalizing important decisions.
- Save curated context only; do not dump the entire repository into context.

## outputs
- `.forge/forge.config.yaml`.
- `.forge/context/repo-map/`.
- `.forge/context/systems/`.
- `.forge/context/decisions/`.
- `.forge/context/unknowns/`.
- `.forge/context/verification/`.
- `.forge/context/loading-map.md`.

## status values
- `ready`
- `blocked_by_decision`
- `needs_more_evidence`

## boundaries
- Do not silently decide important ambiguity.
- Do not overwrite confirmed context without reviewable confirmation.
- Do not add orchestration, agents, CI/CD behavior, or external memory systems.

## next mode transitions
- Use `ask` for repo questions after initialization.
- Use `verify-context` to check context health.
- Use `plan` when the developer has change intent.
