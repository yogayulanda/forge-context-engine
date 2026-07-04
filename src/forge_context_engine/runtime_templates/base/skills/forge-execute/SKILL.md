# forge-execute

## Purpose
Apply an approved ECP into code within explicit boundaries.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction`, `run.write_behavior`, and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/execute.md`. Load the approved ECP and only scoped repository context needed for execution.

## Invocation
Use only when the human has explicitly approved an ECP. ECP readiness is not execution approval.

## Focus
Modify only approved scope with minimal diffs. Run scoped per-task validation, fix ordinary in-scope failures when safe, run final validation, and stop on scope/domain/security/evidence/environment blockers.

## Output
Return execute-mode report with status, changed files, commands run, validation results, fixes made during execute, deviations from ECP, blocked items, risks, and next mode `review`.

## Do NOT
Do not redefine approved architecture, expand scope silently, ignore validation failure, commit, push, merge, deploy, change secrets, add schedulers, introduce CI/CD/deploy behavior, or treat execution as orchestration.
