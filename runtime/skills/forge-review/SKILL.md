# forge-review

## Purpose
Inspect executed result against approved plan, ECP, validation evidence, risk policy, security expectations, and context impact.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Read `.forge/runtime/modes/review.md`, then load `.forge/runtime/meta/conventions.md` and scoped convention files only when needed for evidence, validation, risk, or language rules. Use `.forge/runtime/meta/context-manifest.md` only as a routing index. Load only scoped evidence needed to review the requested change.

## Invocation
Use when the user asks for MR-style review, correctness/risk assessment, validation honesty, security review, boundary preservation, context impact, or reviewer focus.

## Focus
Prioritize goal alignment, scope drift, lifecycle boundary compliance, validation evidence, risk/safety, security impact, and context impact.

## Output
Return review-mode output with one verdict: `accept`, `request_changes`, `needs_more_validation`, or `blocked`.

## Do NOT
Do not implement changes, produce an ECP, replace execution, broad-load unrelated context, or add orchestration/runtime behavior. Keep review-mode boundary statements separate from findings and assumptions.
