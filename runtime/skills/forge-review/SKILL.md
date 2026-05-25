# forge-review

## Purpose
Review a requested change using Forge review mode.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/review.md`. Load only scoped evidence needed to review the requested change.

## Invocation
Use when the user asks for MR-style review, correctness/risk assessment, validation honesty, boundary preservation, or reviewer focus.

## Focus
Prioritize bugs, correctness risks, missing validation, boundary drift, unsafe secrets/PII handling, rollback risk, and approved-contract adherence.

## Output
Return review status, MR readiness, severity-grouped findings, unvalidated scope, rollback/safety notes, and suggested next action.

## Do NOT
Do not implement changes, produce task cards unless explicitly requested, replace testing mode, broad-load unrelated context, or add orchestration/runtime behavior.
