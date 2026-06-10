# Target Repo Surface

| Field | Value |
|---|---|
| Pattern | `target-repo-surface` |
| Lifecycle state | `benchmarked` |
| Coverage category | Adapter thinness, target repo noise policy, opt-in Copilot |
| Scope | Repository-neutral packaging benchmark |

---

## Expected Behavior

Default target-repo output is:

```text
AGENTS.md
CLAUDE.md
.forge/
```

Additional output only when GitHub Copilot is explicitly selected:

```text
.github/copilot-instructions.md
```

`AGENTS.md`, `CLAUDE.md`, and optional `.github/copilot-instructions.md` stay thin wrappers that point to `.forge/adapter.md` and `.forge/context`.

`AGENTS.md` may be shared by Codex and OpenCode. Selecting OpenCode must not create a second root wrapper file.

## Incorrect Behaviors Forge Must Reject

- Copying `docs/`, `specs/`, `validation-cases/`, `runtime/adapters/`, or `runtime/skills/` into every target repository by default.
- Making `AGENTS.md` or `CLAUDE.md` the source of truth for lifecycle, policy, validation, artifact semantics, or repository cognition.
- Making `.github/copilot-instructions.md` a source of truth for lifecycle, policy, validation, artifact semantics, or repository cognition.
- Creating `.github/copilot-instructions.md` when Copilot was not selected.
- Treating `.forge/temp` or `.forge/cache` as pushable target-repo content.

## Regression Signals

This case regresses if target-repo output grows beyond thin wrappers plus `.forge/` by default, or if Copilot stops being opt-in.
