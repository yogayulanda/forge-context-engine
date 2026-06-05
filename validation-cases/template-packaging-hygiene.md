# Template Packaging Hygiene

| Field | Value |
|---|---|
| Pattern | `template-packaging-hygiene` |
| Lifecycle state | `benchmarked` |
| Coverage category | Packaged payload boundaries, target repo noise policy |
| Scope | Forge v0.4 packaged runtime templates |

---

## Expected Behavior

Packaged target-runtime payload includes:
- `.forge/adapter.md`
- `.forge/forge.config.yaml`
- `.forge/generated/.gitkeep`
- `.forge/context/00-meta/*`
- `.forge/context/modes/*`
- `AGENTS.md`
- `CLAUDE.md`
- optional `.github/copilot-instructions.md`

Packaged payload must not include:
- `__pycache__/`
- `*.pyc`
- `docs/`
- `specs/`
- `validation-cases/`
- `runtime/adapters/`
- `runtime/skills/`

## Incorrect Behaviors Forge Must Reject

- Packaging Python cache artifacts into runtime templates.
- Packaging engine-only docs or adapter/skill source trees into target payload.
- Losing required context contract files from the packaged templates.

## Regression Signals

This case regresses if required contract files disappear from the packaged payload or if engine-only content starts shipping into target repositories.
