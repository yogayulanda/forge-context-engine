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
- `00-meta/ai-readiness-factors.md`
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
- Assess repository discoverability, context fitness, code cognitive load, architecture and boundary clarity, interface clarity, validation readiness, change-safety hotspots, governance signals, ambiguity, and generated-noise hygiene.
- Evaluate against the `FAR-*` factor families in `00-meta/ai-readiness-factors.md`. Bands are evidence-anchored qualitative judgments, not tool scores; Forge runs no scanners. Mark a factor not-evaluated rather than guessing when evidence is thin.
- Cite the primary `FAR-*` factor ID in each finding so results stay trackable across scans.
- Derive the verdict from the dominant readiness band using the band→verdict map in `00-meta/ai-readiness-factors.md`.
- Separate confirmed facts, inferred risks, ambiguities, and questions that require human confirmation.
- Emit structured `Questions For Human` entries when unresolved decisions materially affect safe AI use. Each question should include `ID`, `Decision Needed`, `Why This Is Unresolved`, `Options`, `Recommended Option`, `Why Recommended`, and `Impact If Unanswered`. Provide three distinct, mutually-exclusive options by default (drop to two only when a genuine third path does not exist; never pad with a filler option), and name exactly one Recommended Option grounded in repository evidence.
- Compute the derived `Readiness Score` (0–100) and coverage using the scoring rules in `00-meta/ai-readiness-factors.md`. The qualitative band stays authoritative; record any score/band gap as a calibration note rather than overriding the band.
- When a comparable prior saved report exists (same `scoring_method` and `engine_version`), include a `Readiness Trend` showing the score delta and which families moved; omit unchanged families.
- Prefer current repository evidence when context or artifacts drift.
- Produce a compact readiness report, a remediation roadmap, and optional context-patch recommendations.
- Lead the report with an `At a Glance` block written in plain English for a non-author, using the plain-language label tables in `00-meta/ai-readiness-factors.md`. It must:
  1. Open with one line stating what the report answers (e.g. "Can AI safely help with code here, and what to fix first?") and a note that everything after the block is supporting detail.
  2. Give the overall `Readiness Score /100` plus the plain headline sentence mapped from the verdict — not the raw enum — and the coverage in plain words ("we checked N of M things").
  3. List every open decision under `What needs your decision`, each in plain terms with what it gates; full options stay in `Questions For Human` below.
  4. Show `Where it stands, by area`, sorted weakest-first, using the plain area names with a 5-block bar and the word `weak`/`fair`/`good`; anchor with `← start here` / `← strongest`.
  5. End with `Fix these first`, a short imperative list of the highest-payoff actions.
- Keep machine values (`verdict`, band name, `FAR-*` IDs, internal decimals/weights) out of the `At a Glance` box; place them in the `Executive Summary` and detail sections below.
- Default to chat output first; save artifacts only when explicitly requested or approved.
- If saving, use `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-report.md` and `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-roadmap.md`.
- Propose durable context changes via `.forge/context-patches/YYYY-MM-DD-<slug>-ai-readiness-context-patch.md`; do not modify `.forge/context` directly.
- Keep findings grouped by severity and optimized for scanning.

## outputs
- AI Readiness Report.
- At a Glance summary (plain English: purpose line, headline `Readiness Score /100` + plain verdict sentence, `What needs your decision`, `Where it stands, by area` weakest-first, `Fix these first`).
- Verdict.
- Readiness Band (`Optimized`, `Ready`, `Limited`, `Conditional`, `Blocked`).
- Readiness Score (derived 0–100, always shown with coverage, e.g. `37/100 (coverage 23/26)`).
- Readiness Trend (only when a comparable prior report exists; score delta + families that moved).
- Readiness Profile (full factor-detail table of `FAR-*` factors with band and confidence, below the At a Glance block).
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
- Do not ask open-ended clarification questions when three bounded options (two only when no genuine third path exists) and a named recommendation can be stated.

## next mode transitions
- Use `ask` for narrower repo understanding.
- Use `verify-context` for context-health-only follow-up.
- Use `plan` when the remediation path becomes an approved engineering initiative.
- Use `review` only for executed-result or MR assessment.
