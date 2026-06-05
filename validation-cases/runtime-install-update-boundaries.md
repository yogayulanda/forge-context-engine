# Runtime Install Update Boundaries

| Field | Value |
|---|---|
| Pattern | `runtime-install-update-boundaries` |
| Lifecycle state | `benchmarked` |
| Coverage category | Ownership, noise policy, safe update boundaries |
| Scope | Forge v0.4 install/update contract |

---

## Expected Behavior

Managed paths include:
- selected root tool entrypoints
- `.forge/adapter.md`
- `.forge/forge.config.yaml`
- `.forge/forge-install.yaml`
- runtime-owned `.forge/context/00-meta/*`
- runtime-owned `.forge/context/modes/*`

User-owned paths include:
- `.forge/context/01-core/`
- `.forge/context/layers/`
- `.forge/context/repo-map/`
- `.forge/context/systems/`
- `.forge/context/knowledge/`
- `.forge/context/decisions/`
- `.forge/context/unknowns/`
- `.forge/context-patches/`
- `.forge/generated/`

Local-only paths include:
- `.forge/temp/`
- `.forge/cache/`

Default target-repo output is:

```text
AGENTS.md
CLAUDE.md
.forge/
```

Copilot remains opt-in and adds:

```text
.github/copilot-instructions.md
```

## Incorrect Behaviors Forge Must Reject

- Treating engine docs/specs/validation assets as target-repo runtime output.
- Overwriting user-owned context as part of runtime update.
- Treating `.forge/temp` or `.forge/cache` as managed output.
- Making Copilot a default target-repo file.
- Choosing a global workspace location automatically.

## Regression Signals

This case regresses if install/update behavior expands beyond runtime/template file ownership or if the default repo surface grows beyond the thin target output.
