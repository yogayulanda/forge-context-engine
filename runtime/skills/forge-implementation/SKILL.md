# forge-implementation

## Purpose
Convert an approved Forge plan into an Execution Context Package (ECP).

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/implementation.md`. Load the approved plan and only scoped repository context needed for ECP generation.

## Invocation
Use only after human approval of a plan with `status: ready_for_implementation`.

## Focus
Produce a bounded, tool-ready ECP with allowed files, task sequence, validation checklist, security constraints, acceptance criteria, stop conditions, and expected execution report format.

## Output
Return implementation-mode ECP with status `ecp_ready`, `blocked_by_decision`, `needs_more_evidence`, or `needs_plan_approval`.

## Do NOT
Do not edit code, commit, push, merge, deploy, apply changes, hide blockers, redefine the approved plan, or treat ECP readiness as approval to execute.
