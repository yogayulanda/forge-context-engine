# AI Readiness Mode Boundaries

## Goal

Validate that `ai-readiness` remains a read-only repository audit focused on AI safety, context fitness, ambiguity, and remediation guidance.

## Expected Behavior

- Produces one readiness verdict from `autonomous_ready`, `assist_ready`, `context_limited`, `confirmation_required`, or `blocked`.
- Leads with a plain-English `At a Glance` block: a purpose line, headline `Readiness Score /100` with a plain verdict sentence (not the raw enum), `What needs your decision`, `Where it stands, by area` weakest-first using plain area names and `weak`/`fair`/`good` bars, and `Fix these first`.
- Reports a derived `Readiness Score` (0–100) always shown with coverage, with the qualitative band remaining authoritative on conflict.
- Keeps machine vocabulary (raw `verdict`/band enums, `FAR-*` IDs, factor decimals, weight arithmetic) out of the At a Glance box; places it in the Executive Summary and detail sections.
- Groups findings by severity and keeps them compact.
- Surfaces ambiguities and explicit questions for human when evidence is insufficient.
- Uses structured `Questions For Human` entries with decision, unresolved reason, three distinct options (two only when no genuine third path exists), exactly one recommended option, why recommended, and impact if unanswered.
- May recommend `.forge/context-patches/...` but does not mutate `.forge/context` directly.
- May save report/roadmap artifacts only when explicitly requested or approved.
- Does not edit source code, tests, configs, deployment files, or runtime behavior.
- Does not collapse into `review`, `verify-context`, `plan`, or `execute` responsibilities.

## Failure Patterns

- Writes code or config changes.
- Silently rewrites `.forge/context`.
- Emits a review verdict such as `accept` instead of a readiness verdict.
- Treats partial evidence as deterministic certainty.
- Asks vague open-ended questions without three bounded options (two only when no genuine third path exists) and exactly one named recommendation.
- Buries verdict-gating `Questions For Human` below the fold instead of surfacing them in the `At a Glance` `What needs your decision` block.
- Exposes machine vocabulary (raw `verdict`/band enums, `FAR-*` IDs, factor decimals, or weight arithmetic) in the `At a Glance` box instead of plain words and `/100`/bars.
- Becomes a generic compliance checklist without tying findings back to AI task safety.
