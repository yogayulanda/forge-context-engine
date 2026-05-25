# forge-plan

## Purpose
Create Forge planning output for a bounded change or investigation.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/planning.md`. Load only scoped context needed for the plan.

## Invocation
Use when the user asks for an ECP, change plan, phase plan, design direction, or evidence-led implementation strategy.

## Focus
Ground the plan in repository evidence. Keep repository evidence, inferred assumptions, proposed defaults, blockers, and unknowns separate.

## Output
Return the planning-mode result shape: goal, evidence, constraints, proposed approach, risks, unknowns, validation expectations, and next decision points.

## Do NOT
Do not produce detailed executable task cards, modify code, approve HIGH-risk decisions, broad-load context, invent contracts, or add orchestration/runtime behavior.
