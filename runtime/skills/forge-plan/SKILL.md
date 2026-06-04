# forge-plan

## Purpose
Convert developer intent into a Forge Quick Plan or SDD.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/plan.md`. Load only scoped context needed for the plan.

## Invocation
Use when the user asks for change planning, design direction, implementation strategy, SDD, or a reviewable plan before implementation.

## Focus
Choose Quick Plan or SDD, show the reason, ground the plan in repository evidence, separate assumptions/unknowns/decisions, and end with one final plan status.

## Output
Return plan-mode output with one status: `ready_for_implementation`, `blocked_by_decision`, `needs_more_evidence`, or `not_recommended`.

## Do NOT
Do not produce an ECP, detailed executable task cards, code changes, commits, HIGH-risk approvals, broad context loading, invented contracts, or orchestration/runtime behavior.
