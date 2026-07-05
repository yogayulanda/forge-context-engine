# forge-update-context

## Purpose
Update active curated context under `.forge/context/` so it matches current repository evidence.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Read `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/update-context.md`. Read `.forge/context/00-index.md` if present. Load only the active context files and repository evidence needed to confirm or correct current context.

## Invocation
Use when the user asks to resync stale Forge context, update active context from current code, refresh `.forge/context`, or simply invokes `/forge-update-context` or `Use forge-update-context skill.` No target file list, guardrail block, context structure explanation, or output-format explanation is required from the user. The skill must self-load config, conventions, manifest or index routing, and mode instructions.

## Default Workflow
- Detect the active context layout from the current manifest, runtime index, and active `.forge/context/00-index.md` plus current `.forge/context/` files.
- Start from routing files and a quick top-level repository map.
- Read high-signal docs, package/module metadata, config, entrypoints, contracts, schema, and tests before expanding into source files.
- Compare active context claims against current repository evidence selectively.
- Update only the relevant `.forge/context/*.md` files with concise confirmed facts.
- Keep active context consistent across related files when current evidence requires it. Cross-file updates are allowed when they are minimal, directly related, and still limited to `.forge/context/`.
- Examples: correcting a stale security fact may also require a new open question in `99-open-questions.md`; adding a new integration fact may also require a glossary term in `98-glossary.md`; clarifying a business rule may also require updating assumptions, constraints, or decisions; removing an unsupported claim may also require recording the missing confirmation as an open question.
- Record missing confirmations, ambiguity, or stale legacy-derived claims in `99-open-questions.md` or the active assumptions/constraints file instead of guessing.
- For v2 service layout, use the numbered service files by subject area.
- For workspace layout, follow the active workspace index and manifest routing.
- For future layouts, prefer manifest and index routing over hardcoded file assumptions.

## Boundaries
- This workflow is not v2-only.
- In installed target-repo usage, update active curated context only under `.forge/context/`.
- In this Forge repository, runtime templates may change while developing the skill, but that does not change the installed target-repo boundary.
- Do not modify application code.
- Do not modify `.forge/runtime/`, `.forge/generated/`, `.forge/context-archive/`, `.forge/context-patches/`, `.forge/forge-install.yaml`, `AGENTS.md`, `CLAUDE.md`, or `.claude/commands/`.
- Treat `.forge/context/` as the active curated source of truth and the only writable area for this workflow.
- Treat `.forge/runtime/` as read-only Forge runtime instructions.
- Treat `.forge/generated/` as generated artifacts, not active source of truth by default.
- Treat `.forge/context-archive/` as legacy or deprecated backup material, reference only when needed.
- Treat `.forge/context-patches/` as proposed patches, not active context until applied.
- Do not use `.forge/generated/` as active evidence by default.
- Do not promote archive facts as confirmed unless current code, docs, config, or tests also support them.
- Mark legacy-derived facts as legacy-derived or needing confirmation when current repository evidence does not confirm them yet.
- Do not broad-load the whole repository when targeted evidence is sufficient.
- Do not present unconfirmed claims as facts.

## Output
Return `# Forge Context Update` with status `updated`, `no-change`, `partial`, or `blocked`, the changed context files, confirmed updates, new open questions, assumptions or constraints changed, glossary additions, skipped or unknown areas, and the next action.
