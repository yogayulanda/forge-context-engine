---
id: mode.ai-readiness
title: "Mode: AI Readiness"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/ai-readiness.md }]
owner: forge-context-engine
updated: 2026-06-09
---

# Mode: AI Readiness

## include
- `00-meta/conventions.md`
- `01-core/*`
- `knowledge/inferred.md`
- `knowledge/unknowns.md`

## on_demand
- `00-meta/context-manifest.md`
- `knowledge/decisions/`
- `knowledge/assumptions.md`
- `systems/<related>`
- `layers/<related>`
- `.forge/generated/<relevant>`
- `.forge/context-patches/<relevant>`
- Current docs, manifests, representative source files, tests, build/validation entrypoints, config surfaces, and integration boundaries needed for the audit

## exclude
- Unrelated systems/layers
- Broad full-repo dumps
- Unrelated generated/vendor/cache output unless it is itself a readiness risk

## token_budget
7000

## purpose
Audit whether the repository is ready for safe, effective AI-assisted engineering, and propose context or remediation improvements without editing code.

## inputs
- `.forge/context` and wrapper entrypoints.
- Current repository evidence.
- Optional prior readiness artifacts when explicitly referenced.

## behavior
- Assess repository discoverability, context fitness, architecture clarity, interface clarity, validation readiness, change-safety hotspots, governance signals, ambiguity, and generated-noise hygiene.
- Separate confirmed facts, inferred risks, ambiguities, and questions that require human confirmation.
- Emit structured `Questions For Human` entries when unresolved decisions materially affect safe AI use. Each question should include `ID`, `Decision Needed`, `Why This Is Unresolved`, `Options`, `Recommended Option`, `Why Recommended`, and `Impact If Unanswered`.
- Prefer current repository evidence when context or artifacts drift.
- Produce a compact readiness report, a remediation roadmap, and optional context-patch recommendations.
- Default to chat output first; save artifacts only when explicitly requested or approved.
- If saving, use `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-report.md` and `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-roadmap.md`.
- Propose durable context changes via `.forge/context-patches/YYYY-MM-DD-<slug>-ai-readiness-context-patch.md`; do not modify `.forge/context` directly.
- Keep findings grouped by severity and optimized for scanning.

## outputs
- AI Readiness Report.
- Verdict.
- Readiness Profile.
- Key Strengths.
- Priority Risks.
- Critical Findings.
- High Findings.
- Medium Findings.
- Low Findings.
- Ambiguities.
- Questions For Human.
- Context Drift.
- Proposed Context Updates.
- Artifact Recommendations.
- Remediation Roadmap.
- Evidence Coverage.
- Recommended Next Step.
- Status.

## verdict values
- `autonomous_ready`
- `assist_ready`
- `context_limited`
- `confirmation_required`
- `blocked`

## status values
- `completed`
- `partial_evidence`
- `needs_confirmation`
- `blocked`

## boundaries
- Read-only by definition.
- Do not edit source code, tests, configs, deployment files, or runtime behavior.
- Do not silently overwrite `.forge/context`.
- Do not collapse into MR review, implementation planning, or generic compliance prose.
- Do not claim deterministic certainty when evidence is partial.
- Do not ask open-ended clarification questions when two or three bounded options can be stated.

## next mode transitions
- Use `ask` for narrower repo understanding.
- Use `verify-context` for context-health-only follow-up.
- Use `plan` when the remediation path becomes an approved engineering initiative.
- Use `review` only for executed-result or MR assessment.
