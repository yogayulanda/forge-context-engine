# forge-implementation

## Purpose
Convert an approved Forge plan into an Execution Context Package (ECP).

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Read `.forge/runtime/modes/implementation.md`, then load `.forge/runtime/meta/conventions.md` and scoped convention files only when needed for evidence, validation, risk, or language rules. Use `.forge/runtime/meta/context-manifest.md` only as a routing index. Load the approved plan and only scoped repository context needed for ECP generation.

## Invocation
Use only after human approval of a plan with `status: ready_for_implementation`.

## Focus
Produce a bounded, tool-ready ECP with assumptions, exact likely files, task sequence, coding rules, safety constraints, acceptance criteria, validation commands, stop conditions, and expected execution report format.

## Output
Return implementation-mode ECP with status `ecp_ready`, `blocked_by_decision`, `needs_more_evidence`, or `needs_plan_approval`.

## Do NOT
Do not put mode-boundary statements under `Assumptions`. Do not edit code, commit, push, merge, deploy, apply changes, hide blockers, redefine the approved plan, or treat ECP readiness as approval to execute.
