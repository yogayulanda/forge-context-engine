# AGENTS.md - Forge Codex Adapter

Thin, repository-native entrypoint for Codex-compatible assistants.

Codex is skills-first for Forge usage. This file maps Codex prompts to shared Forge skills; it stores no repository cognition and does not define a parallel Codex command-wrapper layer. `.forge/context` remains source of truth.

## Natural Invocation

When the user says "Use Forge <mode> mode", resolve the request to the matching shared skill under `runtime/skills/<skill>/SKILL.md`, then enter that Forge mode:

| User wording | Shared skill | Use for |
|---|---|---|
| `ask` | `forge-ask` | Repository understanding |
| `planning` | `forge-plan` | ECP/change planning |
| `implementation` | `forge-implement` | Execution task cards |
| `execute` | `forge-execute` | Bounded code changes |
| `testing` | `forge-test` | Structured validation |
| `review` | `forge-review` | MR-style review |
| `incident` | `forge-incident` | Diagnosis and mitigation |
| `refactor` | `forge-refactor` | Bounded technical debt work |

Codex invocation syntax may vary by surface or version. Accept `$forge-review`, `/skill forge-review`, or natural prompts such as "Use Forge review mode" when they resolve to the same shared skill.

## Load

1. Read the matching shared skill under `runtime/skills/<skill>/SKILL.md`.
2. Read `.forge/forge.config.yaml` first.
3. Apply `runtime.non_interactive` and respect `runtime.profile`.
4. Read `.forge/context/00-meta/conventions.md`.
5. Read `.forge/context/00-meta/context-manifest.md` only as the routing index.
6. Read `.forge/context/modes/<mode>.md` for the requested mode.
7. Load only scoped repository context relevant to the task and mode.

Do not broad-load `.forge/context`.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Responsibilities:
- `.forge/context` owns repository cognition and lifecycle semantics.
- `runtime/skills/*/SKILL.md` owns reusable Forge workflow behavior.
- `runtime/adapters/*` owns tool-specific bridge text only.
- `CLAUDE.md` and `AGENTS.md` are entrypoints.

## Safety

- Repo code, repo docs, ADRs, and human confirmations win over adapter text.
- Keep repository-owned cognition in `.forge/context`; skills are reusable behavior layers only.
- Preserve evidence, inference, assumption, proposed-default, and unknown boundaries.
- Treat generated artifacts as non-authoritative handoff records.
- Require human approval for HIGH-risk decisions.
- Do not assume facts across repositories.
- Redact secrets before output or context writes.
- Do not duplicate lifecycle semantics, governance rules, mode behavior, or repo-specific cognition in this adapter.
- Do not create Codex command wrappers unless the Codex runtime explicitly requires them later.

## Execute Mode

For `execute`, require an approved execution contract or task cards. Stop if scope is unclear, required values are missing, or a HIGH-risk decision lacks human approval.

Report changed files, validation performed, validation gaps, rollback notes when relevant, and whether any failure was implementation failure or environment/tooling failure.

## Output

Keep responses concise, operational, developer-friendly, and aligned to the active Forge mode. Avoid giant narrative reports, AI framework jargon, and unnecessary runtime internals.

See `skills/README.md`, `adapters/codex/AGENTS.md`, `adapters/codex/README.md`, and `adapters/shared/command-semantics.md` for shared skill and thin adapter guidance.
