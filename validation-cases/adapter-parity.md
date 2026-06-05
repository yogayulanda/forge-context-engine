# Adapter Parity

| Field | Value |
|---|---|
| Pattern | `adapter-parity` |
| Lifecycle state | `benchmarked` |
| Coverage category | Adapter thinness, artifact neutrality, cross-tool lifecycle parity |
| Scope | Repository-neutral adapter benchmark |

---

## Expected Behavior

- `.forge/adapter.md` is the shared contract for lifecycle rules, context loading, artifact policy, and safety boundaries.
- `AGENTS.md`, `CLAUDE.md`, and optional `.github/copilot-instructions.md` stay thin wrappers that point to `.forge/adapter.md` and `.forge/context`.
- All tools honor the same mode boundaries, selective loading rules, and human approval gates.
- All tools treat `.forge/context` as curated source of truth, `.forge/generated/...` as working artifacts, and `.forge/context-patches/...` as proposals only.
- Universal Plan, ECP, Execution Report, and Review artifacts stay tool-neutral unless explicitly target-tool-specific.
- Tool-specific guidance is allowed only in wrappers or a clearly labeled `Target Tool Notes` section.
- Copilot instructions remain lightweight and do not promise full autonomous workflow execution.
- Commit, push, merge, and similar repository publication actions remain human-controlled unless explicitly requested.

Minimum common artifact shape:
- Plan: `Mode Boundary`, `Assumptions`, `Goal / Scope / Non-goals`, `Evidence`, `Risks`, `Acceptance Criteria`, `Validation Commands`, `Next Step`, `Status`
- ECP: `Approved Scope`, `Files likely to change`, `Task sequence`, `Coding rules`, `Safety constraints`, `Validation commands`, `Stop conditions`, `Expected execution report`, `Status`
- Execution Report: `Changed files`, `What changed`, `Validation run`, `Deviations`, `Remaining risks`, `Status`
- Review: `Verdict`, `Diff Reviewed`, `Findings`, `Validation assessment`, `Context Impact`, `Recommended next step`, `Status`

## Incorrect Behaviors Forge Must Reject

- Duplicating the full lifecycle contract inside `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.
- Treating Copilot instructions as a second workflow system or promising autonomous execution.
- Emitting universal artifact instructions such as `Use apply_patch`, `Use Codex`, or `Run Claude tool X`.
- Treating `.forge/generated/...` as curated context or `.forge/context-patches/...` as accepted context.
- Letting one tool skip approval gates, broad-load context, or ignore artifact continuity rules that other tools follow.

## Regression Signals

This case regresses if wrappers stop being thin, if shared lifecycle rules drift out of `.forge/adapter.md`, if Copilot instructions become agent-heavy, or if universal artifacts start leaking tool-specific mechanics without explicit labels.
