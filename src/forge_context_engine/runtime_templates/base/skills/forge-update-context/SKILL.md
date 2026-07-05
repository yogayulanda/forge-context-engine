# forge-update-context

## Purpose
Update active curated context under `.forge/context/` so it matches current repository evidence.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Read `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/update-context.md`. Read `.forge/context/00-index.md` if present. Load only the active context files and repository evidence needed to confirm or correct current context.

## Invocation
Use when the user asks to resync stale Forge context, update active context from current code, refresh `.forge/context`, or simply invokes `/forge-update-context` or `Use forge-update-context skill.`

## Default Workflow
- Detect the active context layout from the current manifest, index, and active `.forge/context/` files.
- Start from routing files and a quick top-level repository map.
- Read high-signal docs, package/module metadata, config, entrypoints, contracts, schema, and tests before expanding into source files.
- Compare active context claims against current repository evidence selectively.
- Update only the relevant `.forge/context/*.md` files with concise confirmed facts.
- Record missing confirmations, ambiguity, or stale legacy-derived claims in `99-open-questions.md` or the active assumptions/constraints file instead of guessing.

## Boundaries
- Update active curated context only under `.forge/context/`.
- Do not modify application code.
- Do not modify `.forge/runtime/`, `.forge/generated/`, `.forge/context-archive/`, `.forge/context-patches/`, `.forge/forge-install.yaml`, `AGENTS.md`, `CLAUDE.md`, or `.claude/commands/`.
- Do not broad-load the whole repository when targeted evidence is sufficient.
- Do not present unconfirmed claims as facts.

## Output
Return `# Forge Context Update` with status `updated`, `no-change`, `partial`, or `blocked`, the changed context files, confirmed updates, new open questions, assumptions or constraints changed, glossary additions, skipped or unknown areas, and the next action.
