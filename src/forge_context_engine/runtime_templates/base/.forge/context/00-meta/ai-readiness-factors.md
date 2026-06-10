---
id: meta.ai-readiness-factors
title: "AI Readiness Factors"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/ai-readiness.md }]
owner: forge-context-engine
updated: 2026-06-09
---

# AI Readiness Factors

Stable, tool-free factor catalog for the `ai-readiness` mode. Loaded on demand.

Purpose:
- Give every readiness finding a stable `FAR-*` ID so results stay trackable across scans.
- Calibrate qualitative judgment with shared bands instead of ad-hoc opinion.

Rules:
- Bands are evidence-anchored judgments, not tool scores. Forge does not run scanners.
- Use current repository evidence over stale context. State confidence honestly.
- Mark a factor `not-evaluated` when evidence is too thin instead of guessing.

## Families

| Family | Focus Area | Plain area name (for At a Glance) | IDs |
|---|---|---|---|
| Context fitness | Context Coverage and Freshness | Project context (.forge) | `FAR-CTX-*` |
| Entrypoint and docs | AI Entrypoint Readiness | README & guides | `FAR-DOC-*` |
| Discoverability | Repository Discoverability | Folder layout & naming | `FAR-DISC-*` |
| Code cognitive load | Code Quality | Code readability | `FAR-CODE-*` |
| Interface clarity | Contract and Interface Clarity | APIs & contracts | `FAR-IFACE-*` |
| Architecture boundaries | Architecture and Boundary Clarity | Architecture clarity | `FAR-ARCH-*` |
| Validation readiness | Test and Validation Readiness | Tests & validation | `FAR-TEST-*` |
| Indexing hygiene | Generated Noise and Indexing Hygiene | Repo cleanliness | `FAR-NOISE-*` |
| Safety and decisions | Change-Safety / Governance / Human-Decision | Safety & ownership | `FAR-SAFE-*` |

## Factor Bands

| ID | Factor | Green | Warning | Red |
|---|---|---|---|---|
| FAR-CTX-01 | Context/source file size fit | No file an agent must read whole > ~8k tokens | Some files ~8k–20k tokens | Any file > ~20k tokens, or many oversized files |
| FAR-CTX-02 | Core context freshness vs evidence | `.forge/context` matches current repo evidence | Minor drift in non-critical cards | Core/arch context contradicts current code |
| FAR-CTX-03 | System/layer coverage for active areas | Active systems/layers have usable cards | Cards exist but thin on boundaries | Active areas have no usable context |
| FAR-DOC-01 | README accuracy and setup | Purpose, setup, and commands present and correct | Missing one signal or minor conflict | Missing or contradicts the repo |
| FAR-DOC-02 | Architecture doc coverage | Style, boundaries, flows, and feature guidance documented | Partial coverage of those areas | No architecture doc |
| FAR-DOC-03 | Agent-instruction actionability | Scan/plan/edit/validate workflow and limits stated | Exists but vague | Missing |
| FAR-DOC-04 | Build/test commands discoverable | Commands verifiable in package metadata, no conflict | Only in docs/CI or conflicting | No discoverable commands |
| FAR-DISC-01 | Folder navigability | Shallow, logical, easy to traverse | Some deep or unclear paths | Deep nesting or confusing layout |
| FAR-DISC-02 | Identifier meaningfulness | Names are descriptive and consistent | Some generic/ambiguous names | Pervasive generic/ambiguous names |
| FAR-CODE-01 | Function/method length | Functions short, single-purpose | Some long functions (~50–150 lines) | Very long functions (> ~150 lines) |
| FAR-CODE-02 | Branching/cognitive complexity | Control flow easy to follow | Pockets of high complexity | Widespread hard-to-reason logic |
| FAR-CODE-03 | Nesting depth | Mostly shallow (≤ ~4) | Some deep nesting (~5–6) | Deep nesting (> ~6) |
| FAR-CODE-04 | Module/class size | Modules cohesive and bounded | Some large modules | God-modules / >1000-line units |
| FAR-CODE-05 | Dependency fan-out | Low import fan-out per unit | Some high fan-out hubs | Pervasive high fan-out |
| FAR-CODE-06 | Naming/role consistency | Consistent conventions and clear role names | Mixed styles or vague role names | Conflicting conventions repo-wide |
| FAR-CODE-07 | Domain term consistency | One term per concept | A few undocumented synonyms | Many conflicting domain synonyms |
| FAR-CODE-08 | Error-handling consistency | One or few coherent patterns | Several mixed patterns | Inconsistent/ad-hoc handling |
| FAR-CODE-09 | Type/signature clarity | Interfaces clearly typed | Partial typing | Largely untyped public surface |
| FAR-IFACE-01 | Contract ownership clarity | Owner/authority of shared contracts is clear | Implied but unconfirmed | Ambiguous, blocks safe edits |
| FAR-IFACE-02 | Public API documentation | Public surface well documented | Partial docs | Undocumented public surface |
| FAR-ARCH-01 | Architecture style documented | Style and dependency rules stated | Style stated, rules vague | Undocumented |
| FAR-ARCH-02 | Layer boundary integrity | No visible layer-boundary violations | Minor/heuristic violations | Clear cross-layer violations |
| FAR-ARCH-03 | Dependency direction | Direction clear and respected | Some questionable coupling | Inverted/forbidden direction |
| FAR-ARCH-04 | Cycle freedom | No evident circular dependencies | Possible cycle-risk clusters | Confirmed cycles |
| FAR-TEST-01 | Test coverage signal | Critical flows visibly tested | Sparse/uneven tests | Little or no test evidence |
| FAR-TEST-02 | Lint/type-check availability | Lint and type-check configured | Only one present/undocumented | None where applicable |
| FAR-TEST-03 | Validation entrypoint clarity | Clear how to validate critical flows | Exists but partial | Unclear/missing for risky areas |
| FAR-NOISE-01 | Generated/vendor hygiene | Generated/vendor excluded from source indexing | Some leakage | Generated/vendor treated as source |
| FAR-NOISE-02 | Dead-code limited | Negligible dead/commented-out code | Some dead code | Pervasive dead/commented-out code |
| FAR-SAFE-01 | Change-safety hotspots known | High-risk edit areas identifiable | Partly identifiable | Risky areas opaque to agents |
| FAR-SAFE-02 | Governance/ownership signals | Ownership and risk areas legible | Partial signals | No ownership/risk legibility |
| FAR-SAFE-03 | Human-decision dependency | No blocking unresolved decisions | A few non-blocking unknowns | Unresolved decisions gate safe AI work |

## Readiness Bands → Verdict

A band is the dominant pattern across evaluated factors, weighted toward Context, Architecture, and Interface. Bands do not require numeric scoring; the derived Readiness Score below is an optional summary of these same band judgments, not a separate measurement.

| Band | Verdict | When |
|---|---|---|
| Optimized | `autonomous_ready` | Most factors green; no Critical findings; arch/contracts clear; validation trustworthy. Bounded multi-file AI work is plausible. |
| Ready | `assist_ready` | Mostly green/warning; no Critical blocker; bounded AI edits safe with review. |
| Limited | `context_limited` | Multiple warning/red in Context/Code/Architecture materially reduce AI reliability. |
| Conditional | `confirmation_required` | Important conclusions hinge on unresolved decisions (`FAR-IFACE-01`, `FAR-ARCH-*`, `FAR-SAFE-03`). |
| Blocked | `blocked` | Evidence too thin to trust the audit, or readiness too low to recommend AI changes. |

## Readiness Score (derived)

The score is a derived summary of the same band judgments — not a new measurement and not a scanner output. The qualitative band stays authoritative; the score never overrides it.

### Per-factor value
| Band | Value |
|---|---|
| Green | 1.0 |
| Warning | 0.5 |
| Red | 0.0 |
| not-evaluated | excluded from the denominator |

### Family weights
Weighted toward Context, Architecture, and Interface, matching the band emphasis.

| Tier | Weight | Families |
|---|---|---|
| High | 3 | `FAR-CTX`, `FAR-ARCH`, `FAR-IFACE` |
| Medium | 2 | `FAR-CODE`, `FAR-TEST`, `FAR-SAFE` |
| Low | 1 | `FAR-DOC`, `FAR-DISC`, `FAR-NOISE` |

### Aggregate
For each evaluated family, take the mean of its evaluated factor values. `Score = Σ(family_mean × weight) / Σ(weight) × 100`, over evaluated families only. Round to a whole number.

### Critical gate
If any Critical finding is present, cap the score at 40 regardless of the weighted average. A Critical blocker must never hide behind a high average.

### Score → band (provisional, calibration-pending)
| Score | Indicative band |
|---|---|
| ≥ 85 | Optimized |
| 70–84 | Ready |
| 45–69 | Limited |
| < 45, or any Critical | Conditional / Blocked |

These cut-points are provisional and must be calibrated against human-labeled repositories before being treated as authoritative. When the derived band and the qualitative band disagree, the qualitative band wins and the gap is recorded as a calibration note.

### Coverage
Always render the score with coverage, e.g. `37/100 (coverage 23/26 factors)`. A high score over thin evidence must stay visible.

### Trend comparability
Saved reports record `readiness_score`, `readiness_coverage`, per-family scores, `scoring_method`, and `engine_version` in front-matter. Compare two reports only when `scoring_method` and `engine_version` match; bands are AI judgments, so cross-version deltas are non-comparable and must be flagged rather than shown as a delta.

## Plain-Language Labels (for the human-facing report)

The `At a Glance` block must read in plain English. Map machine values to plain words; keep the enums (`verdict`, band name, `FAR-*` IDs) and any decimals/weights in the detail sections only.

Verdict → plain headline sentence:

| Verdict | Plain headline |
|---|---|
| `autonomous_ready` | READY — AI can do bounded multi-file work, with review |
| `assist_ready` | PARTLY READY — AI can help with small, reviewed changes; not large hands-off work yet |
| `context_limited` | LIMITED — add context/docs before trusting AI on non-trivial work |
| `confirmation_required` | ON HOLD — answer the decisions below before AI proceeds |
| `blocked` | NOT READY — too little evidence to rely on AI here |

Per-area band → plain word: Green → `good`, Warning → `fair`, Red → `weak`.

Family → plain area name: use the **Plain area name** column in the `## Families` table above (never the `FAR-*` codes in the At a Glance block).

## Finding ID Rule

- Cite the primary `FAR-<FAMILY>-NN` ID in each finding's `Factor` field; keep `Category` as the focus area.
- When a finding spans factors, cite the primary one and mention others in evidence.
- Reuse the same ID across scans for the same factor so drift is comparable.
