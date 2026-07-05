# forge-verify-context

## Purpose
Verify `.forge/context` health, freshness, and consistency only.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/verify-context.md`. Load only affected context files and source paths needed for context verification.

## Invocation
Use when the user asks to verify context freshness, check context drift, inspect context metadata, or determine whether a reviewable context patch is needed.

## Focus
Check source paths, metadata, stale cards, contradictions with current repo evidence, unresolved unknowns, decision freshness, and context-patch need.

## Output
Return verify-context status: `pass`, `stale`, `incomplete`, or `blocked`, with affected context files, evidence, required decisions, and next action.

## Do NOT
Do not verify plan readiness, ECP completeness, code diff result, MR readiness, or general validation. This workflow is read-only. It must not modify files. Do not modify `.forge/context`. Do not treat `.forge/generated/` or `.forge/context-archive/` as active source of truth. Detect context drift and recommend `forge-update-context` when safe updates are needed.
