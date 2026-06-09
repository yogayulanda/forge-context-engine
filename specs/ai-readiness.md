# AI Readiness Mode

| Field | Value |
|---|---|
| Document | Forge AI Readiness Mode |
| Version | 1.0 |
| Date | 2026-06-09 |
| Status | `decision` |
| Scope | Read-only repository audit for AI readiness, context fitness, ambiguity detection, and remediation guidance |
| Dependency | `specs/mode-invocation.md`, `specs/context-validation.md`, `docs/workflow.md`, `runtime/.forge/context/modes/ai-readiness.md`, `runtime/.forge/context/00-meta/ai-readiness-factors.md`, `runtime/skills/forge-ai-readiness/SKILL.md` |

## 0. Purpose

`ai-readiness` is a read-only Forge mode for auditing whether a repository is ready for safe, effective AI-assisted engineering.

It exists to answer questions such as:
- Is this repository navigable enough for AI to reason safely?
- Is `.forge/context` representative, fresh, and actionable?
- Which ambiguities still require human confirmation?
- Which risks make autonomous or multi-file AI changes unsafe right now?
- Which context updates or remediation steps would improve readiness fastest?

`ai-readiness` does not replace `review`, `verify-context`, `plan`, or `execute`.
It inspects repository readiness for AI usage across codebase evidence, context quality, and operational safety.

## 1. Mode Boundary

`ai-readiness` is read-only by definition.

Allowed:
- Read scoped repository evidence.
- Read relevant `.forge/context` files.
- Compare current evidence to context and generated artifacts.
- Report readiness strengths, risks, ambiguities, drift, and remediation.
- Propose reviewable `.forge/context-patches/...` updates.
- Save report and roadmap artifacts only when the user explicitly asks or approves persistence.

Forbidden:
- Edit source code, tests, configs, deployment files, or runtime behavior.
- Silently overwrite `.forge/context`.
- Promote generated output directly into curated context.
- Invent ownership, contracts, business rules, or runtime behavior without evidence.
- Collapse into a generic security/compliance audit disconnected from AI task safety.

## 2. Inputs

- `.forge/forge.config.yaml`
- `.forge/context/modes/ai-readiness.md`
- `.forge/context/00-meta/conventions.md`
- Relevant `.forge/context` cards
- Current repository evidence: docs, manifests, structure, representative source files, tests, validation entrypoints, and integration boundaries
- Optional prior readiness report or context patch proposal when explicitly referenced

## 3. Readiness Focus Areas

Minimum audit categories:
- AI Entrypoint Readiness
- Context Coverage and Freshness
- Repository Discoverability
- Code Cognitive Load
- Architecture and Boundary Clarity
- Contract and Interface Clarity
- Test and Validation Readiness
- Change-Safety Hotspots
- Governance and Operational Signals
- Generated Noise and Indexing Hygiene
- Human-Decision Dependency

The mode should stay evidence-first and scoped. It should read only enough code and context to justify the readiness conclusions.

### 3.1 Readiness Factor Catalog

Each focus area resolves to stable factors defined in `runtime/.forge/context/00-meta/ai-readiness-factors.md`. That catalog is the single source of truth for factor IDs (`FAR-<FAMILY>-NN`), the qualitative green/warning/red bands, and the readiness-band → verdict mapping.

Rules:
- Factor bands are evidence-anchored qualitative judgments, not tool scores. Forge runs no scanners; bands borrow thresholds only as calibration guidance.
- Findings cite the primary `FAR-*` factor ID so results stay comparable across scans.
- Mark a factor `not-evaluated` when evidence is too thin instead of guessing.
- The catalog is loaded on demand only during `ai-readiness`; the mode file stays compact and references it rather than duplicating it.

## 4. Output Contract

`ai-readiness` returns one compact audit report with these sections:
- `AI Readiness Report`
- `At a Glance` (human-scannable header — see 4.1)
- `Executive Summary`
- `Verdict`
- `Readiness Band`
- `Readiness Score` (derived 0–100, shown with coverage — see 6.1)
- `Readiness Trend` (only when a comparable prior report exists — see 6.1)
- `Readiness Profile`
- `Key Strengths`
- `Priority Risks`
- `Findings`
- `Ambiguities`
- `Questions For Human`
- `Context Drift`
- `Proposed Context Updates`
- `Artifact Recommendations`
- `Remediation Roadmap`
- `Evidence Coverage`
- `Recommended Next Step`
- `Status`

When persistence is requested or approved, recommended artifact paths are:
- `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-report.md`
- `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-roadmap.md`
- `.forge/context-patches/YYYY-MM-DD-<slug>-ai-readiness-context-patch.md` when durable context updates are proposed

### 4.1 At a Glance (human-facing output format)

The report leads with an `At a Glance` block a non-author can understand in seconds. It must read in **plain English** — use the plain-language label tables in the factor catalog (`00-meta/ai-readiness-factors.md`) and keep machine vocabulary out of the box. Rules:
- **State the report's purpose first:** one line on what it answers ("Can AI safely help with code here, and what to fix first?") and that everything below the block is supporting detail.
- **Headline in plain words:** the overall `Readiness Score /100` plus the plain headline sentence mapped from the verdict (e.g. "PARTLY READY — AI can help with small, reviewed changes"), and coverage stated plainly ("we checked 21 of 26 things"). Do **not** show the raw `verdict`/band enum here.
- **`What needs your decision`:** if any `Questions For Human` exist, list each in plain terms with what it gates, so verdict-gating asks are never buried. Full options stay in the detailed `Questions For Human` section.
- **`Where it stands, by area`, weakest first:** plain area names (not `FAR-*` codes), each with a 5-block bar and the word `weak`/`fair`/`good`, anchored with `← start here` / `← strongest`.
- **`Fix these first`:** a short imperative list of the highest-payoff actions.
- **No machine internals on screen:** raw `verdict`/band enums, `FAR-*` IDs, factor decimals (0.0–1.0), and weight math stay out of the box; they belong in the `Executive Summary` and detail sections below.

The `Executive Summary` (precise machine fields), detailed `FAR-*` factor table, full findings, and full `Questions For Human` entries follow below the At a Glance block.

## 5. Findings Contract

Findings must be grouped by severity:
- `Critical Findings`
- `High Findings`
- `Medium Findings`
- `Low Findings`

Each finding should stay compact and include:
- `ID`
- `Category`
- `Factor` (primary `FAR-*` ID from the factor catalog)
- `Title`
- `Why It Matters For AI`
- `Evidence`
- `Impact`
- `Recommended Direction`
- `Confidence`

Avoid long repeated prose when several findings share the same failure pattern.

## 6. Verdict and Status

Primary verdict values:
- `autonomous_ready`
- `assist_ready`
- `context_limited`
- `confirmation_required`
- `blocked`

Status values:
- `completed`
- `partial_evidence`
- `needs_confirmation`
- `blocked`

The verdict is derived from the dominant readiness band using the band → verdict map in the factor catalog (`Optimized` → `autonomous_ready`, `Ready` → `assist_ready`, `Limited` → `context_limited`, `Conditional` → `confirmation_required`, `Blocked` → `blocked`). Bands weight Context, Architecture, and Interface factors most heavily. The band remains authoritative; the derived `Readiness Score` (6.1) is an optional summary of the same band judgments, never an independent measurement.

Guidance:
- `autonomous_ready`: bounded multi-file AI work is plausible with acceptable evidence and safety signals.
- `assist_ready`: AI is useful for analysis and bounded edits, but important readiness gaps remain.
- `context_limited`: repository/context quality materially reduces AI reliability.
- `confirmation_required`: important readiness conclusions depend on unresolved human decisions.
- `blocked`: evidence or access is too incomplete for a trustworthy audit.

### 6.1 Readiness Score and Trend

The factor catalog (`00-meta/ai-readiness-factors.md`) defines the derived score. Summary:
- Per-factor band → value (`Green` 1.0, `Warning` 0.5, `Red` 0.0); `not-evaluated` excluded from the denominator.
- Family weights: High ×3 (`FAR-CTX`, `FAR-ARCH`, `FAR-IFACE`), Medium ×2 (`FAR-CODE`, `FAR-TEST`, `FAR-SAFE`), Low ×1 (`FAR-DOC`, `FAR-DISC`, `FAR-NOISE`).
- `Score = Σ(family_mean × weight) / Σ(weight) × 100`, over evaluated families only.
- A Critical finding caps the score at 40 regardless of the average.
- Score → band cut-points are provisional and require calibration; the qualitative band wins on conflict, with the gap logged as a calibration note.
- The score is always shown with coverage (`37/100 (coverage 23/26)`).

`Readiness Trend` appears only when a prior saved report shares the same `scoring_method` and `engine_version`. It reports the score delta and the families that moved; bands are AI judgments, so cross-version comparisons are flagged as non-comparable rather than shown as a delta.

## 7. Evidence and Ambiguity Rules

- Current repository evidence wins over stale context or generated artifacts.
- Deterministic evidence should be preferred when available.
- Partial evidence is acceptable if the report clearly labels the resulting confidence and blind spots.
- Unknowns that affect safe AI use belong under `Ambiguities` or `Questions For Human`, not silent inference.
- Context contradictions belong under `Context Drift`.

## 7.1 Questions For Human Contract

When unresolved ambiguity materially affects safe AI use, `ai-readiness` must emit a structured `Questions For Human` section instead of leaving the issue as a generic unknown.

Each question should include:
- `ID`
- `Decision Needed`
- `Why This Is Unresolved`
- `Options`
- `Recommended Option`
- `Why Recommended`
- `Impact If Unanswered`

Question design rules:
- Keep questions specific, operational, and answerable; ground each in repository evidence (name the files/domains in question) so the reader understands exactly what is being decided and where it leads.
- Ask only for decisions that cannot be safely derived from repository evidence.
- Provide three distinct, mutually-exclusive options by default. Drop to two only when a genuine third path does not exist; never pad with a filler option (that would violate the no-fabrication rule).
- Do not emit more than three options for one question.
- Name exactly one Recommended Option and state, in one line, why it is recommended.
- Escalate to verdict `confirmation_required` when unanswered decisions materially affect architecture boundaries, contract ownership, runtime behavior, security posture, validation trust, or durable context accuracy.
- Use status `needs_confirmation` when the audit is otherwise usable but important readiness conclusions remain conditional on human answers.
- Keep minor informational unknowns under `Ambiguities` without forcing a human question.

## 8. Context Update Proposal Rules

`ai-readiness` may recommend durable context updates, but must not apply them directly.

When a context update is warranted, the report should name:
- target context file
- reason for update
- evidence basis
- confidence
- whether a reviewable context patch is recommended now

Durable updates should be proposed through `.forge/context-patches/...`.

## 9. Roadmap Contract

The remediation roadmap must be practical and grouped by time horizon:
- `Immediate`
- `Near Term`
- `Medium Term`

Each roadmap item should include:
- `Priority`
- `Outcome`
- `Target Area`
- `Why It Improves AI Readiness`
- `Suggested Action`
- `Dependencies`
- `Effort`

Roadmap items should optimize for the highest readiness gain per unit of effort.

## 10. Relationship To Other Modes

- Use `ask` for focused repository understanding without a readiness audit.
- Use `verify-context` when the only goal is `.forge/context` health/freshness.
- Use `review` for MR or executed-result assessment.
- Use `plan` when the output of the readiness audit turns into an approved change initiative.

`ai-readiness` may recommend those modes, but must not perform their responsibilities itself.
