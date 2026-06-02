# forge-implement

## Purpose
Convert approved planning scope into Forge implementation-mode readiness output and task cards.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/implementation.md`. Load approved plans, execution values, and only scoped repository context needed for task decomposition.

## Invocation
Use when the human has explicitly approved a planning output, or when the human directly requested task cards for a stated and understood intent. Do not invoke on planning output alone without a human approval signal.

## Focus
Classify blockers and unknowns. Emit `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, or `READY_FOR_EXECUTION` according to the mode file, with task guardrails for minimal diffs, preserved formatting/line endings, and contract-source checks when relevant.

## Output
Return mode-owned readiness output. Include task cards only when required execution values are concrete and blockers are resolved.

## Do NOT
Do not edit code, hide blockers, mark conditional values as execution-ready, auto-approve HIGH-risk decisions, create workflow state, or turn task cards into orchestration.
Do not invoke on a proposed ECP without human approval. Do not mark the Execution Contract as `approved`; Execution Contract approval requires explicit human confirmation.
