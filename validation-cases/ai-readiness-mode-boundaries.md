# AI Readiness Mode Boundaries

## Goal

Validate that `ai-readiness` remains a read-only repository audit focused on AI safety, context fitness, ambiguity, and remediation guidance.

## Expected Behavior

- Produces one readiness verdict from `autonomous_ready`, `assist_ready`, `context_limited`, `confirmation_required`, or `blocked`.
- Groups findings by severity and keeps them compact.
- Surfaces ambiguities and explicit questions for human when evidence is insufficient.
- Uses structured `Questions For Human` entries with decision, unresolved reason, bounded options, recommended option, why recommended, and impact if unanswered.
- May recommend `.forge/context-patches/...` but does not mutate `.forge/context` directly.
- May save report/roadmap artifacts only when explicitly requested or approved.
- Does not edit source code, tests, configs, deployment files, or runtime behavior.
- Does not collapse into `review`, `verify-context`, `plan`, or `execute` responsibilities.

## Failure Patterns

- Writes code or config changes.
- Silently rewrites `.forge/context`.
- Emits a review verdict such as `accept` instead of a readiness verdict.
- Treats partial evidence as deterministic certainty.
- Asks vague open-ended questions without two or three bounded options and a named recommendation.
- Becomes a generic compliance checklist without tying findings back to AI task safety.
