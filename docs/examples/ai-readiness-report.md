# AI Readiness Report Example

Use Forge ai-readiness mode on this repo.
Audit AI readiness, group the findings by severity, surface ambiguities that need human confirmation, and propose context updates plus a remediation roadmap.

Expected compact output shape:

```md
# AI Readiness Report

## Executive Summary

- Verdict: `assist_ready`
- Readiness Band: `Ready`
- Status: `needs_confirmation`
- Evidence Coverage: partial but sufficient for a bounded readiness audit
- Summary: The repository is navigable enough for scoped AI assistance, but durable context, contract ownership, and validation confidence are not yet strong enough for larger multi-file AI changes.

## Readiness Profile

| Factor Family | Status | Confidence | Key Reason |
|---|---|---|---|
| Entrypoint and docs (`FAR-DOC-*`) | pass | high | Thin wrappers and scoped mode loading are present |
| Context fitness (`FAR-CTX-*`) | warning | medium | Core context exists, but system-specific cards are thin |
| Discoverability (`FAR-DISC-*`) | warning | medium | Entry paths are visible, but public interfaces are under-documented |
| Code cognitive load (`FAR-CODE-*`) | pass | medium | Modules are small and consistently named; no oversized units observed |
| Architecture boundaries (`FAR-ARCH-*`) | warning | medium | Layering is implied but boundary rules are undocumented |
| Validation readiness (`FAR-TEST-*`) | warning | medium | Narrow validation exists, but critical flows lack explicit safety notes |
| Safety and decisions (`FAR-SAFE-*`) | fail | high | Contract ownership and domain defaults are unresolved |

## Key Strengths

- Repository entrypoints are thin and adapter parity is preserved.
- Context loading rules are explicit and scoped.
- Managed/runtime boundaries are clearly separated from user-owned context.

## Priority Risks

- AI cannot safely infer contract ownership for shared boundaries from current evidence.
- Missing domain confirmations would make durable context updates too speculative.
- Validation readiness is uneven for higher-risk changes.

## Critical Findings

### AR-001 | Contract and Interface Clarity
- Factor: `FAR-IFACE-01`
- Title: Shared contract ownership is not explicitly documented
- Why It Matters For AI: Without contract authority, AI may edit the wrong repository or misstate compatibility boundaries.
- Evidence: current repo references the shared boundary, but no owner record or context decision confirms authority.
- Impact: Architecture and interface recommendations remain conditional.
- Recommended Direction: add a durable context entry naming the owning repo, owner type, and evidence path.
- Confidence: medium

## High Findings

### AR-002 | Context Coverage and Freshness
- Factor: `FAR-CTX-03`
- Title: System-level context is present but under-specified
- Why It Matters For AI: Larger edits need clearer service responsibilities and boundary notes.
- Evidence: `systems/<service>/system.md` exists but lacks explicit integration and ownership coverage.
- Impact: AI can help with local edits but will be weaker on cross-boundary decisions.
- Recommended Direction: enrich the system card and repo-map with real interface and dependency evidence.
- Confidence: high

## Ambiguities

- It is unclear whether retry policy is repo-owned, upstream-owned, or shared by contract.
- It is unclear whether current validation commands cover the highest-risk service paths or only the narrow happy path.

## Questions For Human

1. `AR-Q1`
   - Decision Needed: Which repository owns retry policy for this shared boundary?
   - Why This Is Unresolved: code references retry behavior, but no explicit owner or durable context decision is present.
   - Options:
     - `Option A (Recommended)` Treat retry policy as externally owned until contract authority is documented.
     - `Option B` Treat this repo as retry-policy owner and document the boundary in `.forge/context`.
     - `Option C` Mark retry behavior as shared ownership and document the split explicitly.
   - Recommended Option: `Option A`
   - Why Recommended: lowest-risk default and least likely to invent ownership.
   - Impact If Unanswered: verdict remains `confirmation_required` for contract-boundary conclusions.

## Context Drift

- `.forge/context/systems/<service>/system.md` needs more explicit ownership and interface evidence.

## Proposed Context Updates

- `.forge/context/systems/<service>/system.md`
  Reason: add service responsibility, boundary ownership, and interface evidence.
- `.forge/context/repo-map/overview.md`
  Reason: strengthen entrypoint and integration-path discoverability.

## Artifact Recommendations

- Save report: `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-report.md`
- Save roadmap: `.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-roadmap.md`
- Propose context patch: `.forge/context-patches/YYYY-MM-DD-<slug>-ai-readiness-context-patch.md`

## Remediation Roadmap

- Immediate: resolve contract-ownership ambiguity and enrich the main system card.
- Near Term: tighten validation notes for critical paths.
- Medium Term: expand durable context for service boundaries and public interfaces.

## Evidence Coverage

- Current repository evidence reviewed: wrappers, core context, representative structure, and targeted service/interface files.
- Blind spots: unresolved owner authority and any runtime behavior not visible from repository evidence.

## Recommended Next Step

- Answer `AR-Q1`, then generate a reviewable context patch for system ownership and boundary notes.

## Status

- `needs_confirmation`
```
