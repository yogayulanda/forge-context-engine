# forge-review

## Purpose
Inspect executed result against approved plan, ECP, validation evidence, risk policy, security expectations, and context impact.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/review.md`. Load only scoped evidence needed to review the requested change.

## Invocation
Use when the user asks for MR-style review, correctness/risk assessment, validation honesty, security review, boundary preservation, context impact, or reviewer focus.

## Focus
Prioritize goal alignment, scope compliance, code quality, validation evidence, risk/safety, security impact, and context impact.

## Output
Return review-mode output with one status: `ready_for_mr`, `needs_fix`, `needs_validation`, `needs_context_update`, `blocked_by_decision`, or `unsafe`.

## Do NOT
Do not implement changes, produce an ECP, replace execution, broad-load unrelated context, or add orchestration/runtime behavior.
