# forge-ai-readiness

## Purpose
Audit repository AI readiness, context fitness, ambiguity, and remediation priorities without editing code.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/ai-readiness.md`. Load `.forge/runtime/meta/ai-readiness-factors.md` on demand as the factor catalog and band→verdict map. Load only scoped context and repository evidence needed for the readiness audit.

## Invocation
Use when the user asks for an AI-readiness audit, wants context and repo gaps identified, wants ambiguity surfaced for human confirmation, or wants readiness reports and remediation guidance before trusting AI-assisted changes.

## Focus
Assess AI entrypoint readiness, context coverage/freshness, repository discoverability, architecture and interface clarity, validation readiness, change-safety hotspots, governance signals, generated-noise hygiene, and human-decision dependency.

## Output
Return an AI Readiness Report with verdict `autonomous_ready`, `assist_ready`, `context_limited`, `confirmation_required`, or `blocked`, a readiness band (`Optimized`/`Ready`/`Limited`/`Conditional`/`Blocked`), a derived `Readiness Score` (0–100 shown with coverage), and a compact readiness profile of factor families with band and confidence. Lead with a plain-English `At a Glance` block: a purpose line, the headline score `/100` with a plain verdict sentence (not the raw enum), `What needs your decision` for open questions, `Where it stands, by area` weakest-first using plain area names and `weak`/`fair`/`good` bars, and `Fix these first`. Use the plain-language label tables in the factor catalog; keep enums, `FAR-*` IDs, and decimals in the detail sections. Cite the primary `FAR-*` factor ID in each finding so results stay comparable across scans. Include grouped findings, ambiguities, structured questions for human, context drift, proposed context updates, remediation roadmap, evidence coverage, and recommended next step. When a comparable prior report exists, add a `Readiness Trend`. Each human question should include the decision needed, why it is unresolved, three distinct options (two only when no genuine third path exists), exactly one recommended option, why it is recommended, and the impact if unanswered.

## Do NOT
Do not edit code, tests, deployment/config behavior, or `.forge/context` directly. Do not collapse into MR review, implementation planning, or a generic compliance checklist. Do not treat generated artifacts as source of truth. Do not ask open-ended clarification questions when three bounded options and a named recommendation can be stated.
