---
id: mode.verify-context
title: "Mode: Verify Context"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-07-05
---

# Mode: Verify Context

## include
- `00-index.md`
- Active profile context files under `.forge/context/`
- `14-decisions-assumptions-and-constraints.md`
- `99-open-questions.md`

## on_demand
- README and high-signal repository docs
- Module and package manifests such as `go.mod`, `package.json`, `pyproject.toml`, or language equivalents
- Source paths referenced by affected active context files
- Changed files relevant to context freshness
- Context patches under `.forge/context-patches` when they are under review
- Legacy archive context under `.forge/context-archive/` only when active context is thin or migration history is needed

## exclude
- `.forge/generated/` unless explicitly needed as supporting evidence
- Vendored, build, cache, and unrelated large generated directories
- Unrelated source trees once the active context area is confirmed
- Plan, ECP, code diff, and MR readiness checks unless only used as evidence of context impact

## token_budget
5000

## purpose
Verify `.forge/context` health, freshness, consistency, and reviewable context-patch quality against current repo/code evidence.

## inputs
- Active `.forge/context/`.
- `.forge/context/00-index.md`, current manifest routing, and current `.forge/context/` layout.
- `14-decisions-assumptions-and-constraints.md` and `99-open-questions.md` when relevant.
- Current repository evidence.
- Changed files when available.
- Context patch proposals under `.forge/context-patches` when relevant.

## behavior
- Detect the active context layout from the manifest, `.forge/context/00-index.md`, and current `.forge/context/` files.
- Check source paths referenced by affected active context files when those references exist.
- Detect contradictions between active context files and current code, docs, config, or tests.
- Detect obviously stale, noisy, duplicate, or low-signal curated context in the active layout.
- Check whether changed files imply active-context drift or a reviewable context patch need.
- Validate context-patch proposals for target files, evidence, proposed update quality, confidence, and promotion notes when a patch is under review.
- Identify unresolved unknowns, unsupported assumptions, or stale cross-cutting constraints.
- Report whether a reviewable context patch is required.
- Distinguish lightweight per-task context freshness/impact follow-up from larger periodic Context Quality Audit work.
- Treat `.forge/context` as the active curated source of truth.
- Treat `.forge/runtime` as read-only instructions.
- Do not treat `.forge/generated/` or `.forge/context-archive/` as active source of truth.

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
- This workflow is read-only.
- Must not modify files.
- It may validate context quality and reviewable context-patch proposals.
- Do not verify plan readiness, ECP completeness, code diff result, MR readiness, or general validation.
- Do not run broad code review or become a general testing mode.
- Do not modify `.forge/context`.
- Do not accept context patches automatically.

## context routing
- This workflow is not v2-only.
- Use the active manifest, index, and current `.forge/context/` layout to decide which active context files need verification.
- For v2 service layout, verify the numbered subject-area files plus `14-decisions-assumptions-and-constraints.md` and `99-open-questions.md`.
- For workspace layout, follow the active workspace index and manifest instead of assuming service-only files.
- For future layouts, rely on the active manifest and index rather than hardcoding a single structure.

## next mode transitions
- Recommend running `forge-update-context` when safe active-context updates are needed.
- Create a reviewable context patch when context is stale or incomplete and patch review is the intended workflow.
- Use `ask`, `plan`, `execute`, or `review` only for their own lifecycle responsibilities.
