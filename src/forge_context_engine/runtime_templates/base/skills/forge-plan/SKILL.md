# forge-plan

## Purpose
Convert developer intent into a Forge Quick Plan or SDD.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Read `.forge/context/modes/plan.md`, then load `.forge/context/00-meta/conventions.md` and scoped convention files only when needed for output shape, evidence, validation, risk, or language rules. Use `.forge/context/00-meta/context-manifest.md` only as a routing index. Load only scoped context needed for the plan.

## Invocation
Use when the user asks for change planning, design direction, implementation strategy, SDD, or a reviewable plan before implementation.

## Focus
Choose Quick Plan or SDD, show the reason, ground the plan in repository evidence, separate assumptions/unknowns/decisions, and always include assumptions, acceptance criteria, validation commands, and one final plan status.

## Output
Return plan-mode output with one status: `ready_for_implementation`, `blocked_by_decision`, or `needs_more_context`.

## Do NOT
Do not put mode-boundary statements under `Assumptions`. Do not produce an ECP, detailed executable task cards, code changes, commits, HIGH-risk approvals, broad context loading, invented contracts, or orchestration/runtime behavior.
