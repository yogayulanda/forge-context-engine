# forge-plan

## Purpose
Convert developer intent into a Forge Quick Plan or SDD.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Read `.forge/runtime/modes/plan.md`, then load `.forge/runtime/meta/conventions.md` and scoped convention files only when needed for output shape, evidence, validation, risk, or language rules. Use `.forge/runtime/meta/context-manifest.md` only as a routing index. Load only scoped context needed for the plan.

## Invocation
Use when the user asks for change planning, design direction, implementation strategy, SDD, or a reviewable plan before implementation.

## Focus
Choose Quick Plan or SDD, show the reason, ground the plan in repository evidence, separate assumptions/unknowns/decisions, and always include assumptions, acceptance criteria, validation commands, and one final plan status. When the request changes existing behavior, inventory the affected surface first: search for all known call sites, references, entry points, handlers, routes, tests, and config touchpoints before finalizing scope.

## Output
Return plan-mode output with one status: `ready_for_implementation`, `blocked_by_decision`, or `needs_more_context`.

## Do NOT
Do not put mode-boundary statements under `Assumptions`. Do not stop after inspecting only one or two obvious files when the task targets an existing function, API, event, config key, or workflow with multiple usages. Do not produce an ECP, detailed executable task cards, code changes, commits, HIGH-risk approvals, broad context loading, invented contracts, or orchestration/runtime behavior.
