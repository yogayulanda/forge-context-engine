# forge-init

## Purpose
Create confirmed repository context and Forge config through bounded initialization.

## Load
Read `.forge/forge.config.yaml` if present. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md` and `.forge/runtime/meta/context-manifest.md` when present, then read `.forge/runtime/modes/init.md`.

## Invocation
Use when creating or refreshing the initial Forge repository context/config from repository evidence.

## Focus
Run a bounded repo scan, draft context/config, ask three-option ambiguity questions for important decisions, and require developer confirmation before finalizing important context.

## Output
Return init-mode status: `ready`, `blocked_by_decision`, or `needs_more_evidence`, plus affected context/config outputs.

## Do NOT
Do not dump the whole repository into context, silently decide important ambiguity, overwrite confirmed context without reviewable confirmation, or add orchestration/agent/runtime behavior.
