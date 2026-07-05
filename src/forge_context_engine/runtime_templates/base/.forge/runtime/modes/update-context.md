---
id: mode.update-context
title: "Mode: Update Context"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-07-05
---

# Mode: Update Context

## include
- `00-index.md`
- Active profile context files under `.forge/context/`
- `14-decisions-assumptions-and-constraints.md`
- `98-glossary.md`
- `99-open-questions.md`

## on_demand
- README and high-signal repository docs
- Module and package manifests such as `go.mod`, `package.json`, `pyproject.toml`, or language equivalents
- Runtime config, entrypoints, API/proto/OpenAPI files, migrations, schemas, and targeted tests
- Legacy archive context under `.forge/context-archive/` only when active context is empty, thin, or migration history is needed

## exclude
- `.forge/generated/` unless explicitly needed as supporting evidence
- Vendored, build, cache, and unrelated large generated directories
- Unrelated source trees once the active context area is confirmed

## token_budget
7000

## purpose
Audit the current repository state and safely refresh active curated context under `.forge/context/`.

## default workflow
1. Read `.forge/forge.config.yaml`.
2. Apply `run.interaction` and related final run config fields.
3. Read `.forge/runtime/meta/conventions.md`.
4. Use `.forge/runtime/meta/context-manifest.md` only as a routing and layout aid.
5. Read this mode file and `.forge/context/00-index.md` if present.
6. Detect the active context layout from the manifest, index, and current `.forge/context/` files.
7. Build a quick repository map from top-level files and directories.
8. Read high-signal evidence first, then expand selectively only where active context is stale, unsupported, or missing.
9. Update only the relevant `.forge/context/*.md` files.
10. Keep active context consistent across related `.forge/context/` files when current evidence requires it.
11. Report changed files, remaining unknowns, and the next action.

## token optimization
- Do not read the whole repository blindly.
- Start with routing files, then inspect top-level directories and high-signal repository metadata.
- Prefer targeted search and selective file reads over broad source loading.
- Do not read `.forge/generated/` by default or treat it as active evidence by default.
- Do not read `.forge/context-archive/` by default except as legacy reference when active context is thin or migration history matters.
- Skip vendored, dependency, cache, and build output directories unless they are the direct subject of active context.
- Keep context updates concise and non-duplicative.

## evidence rules
- Confirm facts from current repository evidence before writing them as facts.
- Do not duplicate the same fact across multiple context files.
- If evidence is insufficient, write an open question or explicit unknown instead of guessing.
- If legacy or archived context is useful but not confirmed in current code, docs, config, or tests, mark it as legacy-derived or needing confirmation.
- Do not promote archive facts as confirmed unless current code, docs, config, or tests also support them.
- Treat `.forge/context/` as active curated context, `.forge/runtime/` as read-only runtime instructions, `.forge/generated/` as generated artifacts, `.forge/context-archive/` as legacy reference only, and `.forge/context-patches/` as proposed patches until applied.
- Remove or correct stale context that contradicts current repository evidence.

## allowed writes
- `.forge/context/*.md` only.

## forbidden writes
- Application code.
- `.forge/runtime/`
- `.forge/generated/`
- `.forge/context-archive/`
- `.forge/context-patches/`
- `.forge/forge-install.yaml`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/commands/`

## context routing
- Use the active manifest, index, and current `.forge/context/` layout to decide where confirmed facts belong.
- This workflow is not v2-only.
- Detect the active context layout from the manifest, runtime index, and `.forge/context/00-index.md`.
- For v2 service layout, route updates to the numbered files by subject area and use `14-decisions-assumptions-and-constraints.md`, `98-glossary.md`, and `99-open-questions.md` for assumptions, terms, and unknowns.
- For workspace layout, follow the active workspace index and manifest instead of assuming service-only files.
- For future layouts, rely on the active manifest and index rather than hardcoding a single layout.

## cross-file consistency
- Cross-file updates are allowed when required to keep active context consistent.
- Keep cross-file updates minimal, directly related to the evidence, and limited to `.forge/context/`.
- This is not scope creep. It is active context consistency.
- Examples: a corrected security fact may also require an open question in `99-open-questions.md`; a new integration fact may also require a glossary term in `98-glossary.md`; a clarified business rule may also require updating assumptions, constraints, or decisions; removing an unsupported claim may also require recording the missing confirmation as an open question.

## output format
```markdown
# Forge Context Update

## Status
updated | no-change | partial | blocked

## Summary
Short summary of what changed and why.

## Files Changed
- `.forge/context/...`

## Confirmed Updates
- ...

## Open Questions Added
- ...

## Assumptions or Constraints Updated
- ...

## Glossary Terms Added
- ...

## Skipped or Left Unknown
- ...

## Next Action
- review diff
- run forge-verify-context
- confirm listed open questions
```

## next action guidance
- Use `updated` when active context was refreshed safely.
- Use `no-change` when current active context already matches current repository evidence.
- Use `partial` when safe updates were applied but important areas remain unknown or ambiguous.
- Use `blocked` when the update cannot proceed safely with current evidence or boundaries.
- Recommend `forge-verify-context` after larger updates or when the user wants a read-only follow-up check.
