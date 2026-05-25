# forge-execute

## Purpose
Execute an approved Forge task card set or execution contract within bounded scope.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/execute.md`. Load the approved execution contract or task cards and only scoped repository context needed for execution.

## Invocation
Use only when the user provides approved task cards, an execution contract, or an explicitly approved bounded task subset.

## Focus
Modify only approved scope. Stop on unclear scope, missing execution values, unresolved contract blockers, or HIGH-risk decisions without human approval. Distinguish implementation failures from environment/tooling failures.

## Output
Return execute-mode result with status, changed files grouped by responsibility, validation performed, validation gaps, manual checks, rollback notes, intentionally unchanged scope, reviewer focus, and hidden-change check.

## Do NOT
Do not redefine approved architecture, expand scope silently, broad-load context, run autonomous chains, add schedulers, introduce CI/CD/deploy behavior, or treat execution as an orchestration platform.
