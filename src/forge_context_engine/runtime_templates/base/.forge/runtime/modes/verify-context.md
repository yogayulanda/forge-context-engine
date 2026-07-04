---
id: mode.verify-context
title: "Mode: Verify Context"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
---

# Mode: Verify Context

## include
- `00-meta/context-manifest.md`
- `00-meta/conventions.md`
- `knowledge/decisions/`
- Context files under review

## on_demand
- Source paths referenced by affected context cards
- Changed files relevant to context freshness
- Context patches under `.forge/context-patches`

## exclude
- Unrelated systems/layers
- Plan, ECP, code diff, and MR readiness checks unless only used as evidence of context impact

## token_budget
5000

## purpose
Verify `.forge/context` health, freshness, consistency, and reviewable context-patch quality against current repo/code evidence.

## inputs
- `.forge/context`.
- Context metadata such as `source_paths`, `source_commit`, and `last_verified`.
- Current repository evidence.
- Changed files when available.
- Context patch proposals under `.forge/context-patches` when relevant.

## behavior
- Check whether context card `source_paths` still exist.
- Check whether source files changed after `last_verified` or `source_commit`.
- Check required metadata.
- Detect contradictions between context cards and current code evidence.
- Detect obviously stale, noisy, duplicate, or low-signal curated context against the v0.8A quality rules.
- Validate context-patch proposals for target files, evidence, proposed update quality, confidence, and promotion notes when a patch is under review.
- Identify unresolved unknowns or stale decision ledger entries.
- Report whether a reviewable context patch is required.
- Distinguish lightweight per-task context freshness/impact follow-up from larger periodic Context Quality Audit work.

## outputs
- Status.
- Reason.
- Affected context files.
- Evidence.
- Required decisions.
- Next action.

## status values
- `pass`
- `stale`
- `incomplete`
- `blocked`

## boundaries
- Verify context health only.
- It may validate context quality and reviewable context-patch proposals.
- Do not verify plan readiness, ECP completeness, code diff result, MR readiness, or general validation.
- Do not run broad code review or become a general testing mode.
- Do not silently overwrite `.forge/context`.
- Do not accept context patches automatically.

## next mode transitions
- Create a reviewable context patch when context is stale or incomplete.
- Use `ask`, `plan`, `execute`, or `review` only for their own lifecycle responsibilities.
