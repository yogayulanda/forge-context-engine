# Forge Command Semantics

Commands are lightweight tool entrypoints. They invoke shared Forge skills; they do not replace Forge.

Natural language such as "Use Forge review mode" or "Use Forge planning mode" is equivalent to invoking the matching shared skill, such as `forge-review` or `forge-plan`.

Final architecture:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Responsibilities:
- `.forge/context` is the cognition source of truth.
- `runtime/skills/*/SKILL.md` is reusable Forge workflow behavior.
- `runtime/adapters/*` is the tool-specific bridge.
- `CLAUDE.md` and `AGENTS.md` are entrypoints.
- GitHub Copilot prompt files are UX wrappers, not cognition sources.

## Canonical Structure

```text
# <tool command>

Invoke shared skill: runtime/skills/<skill>/SKILL.md

The shared skill owns Purpose, Load, Invocation, Focus, Output, and Do NOT.
```

## Mode Mapping

| Mode | Shared skill | Intent |
|---|---|---|
| `ask` | `forge-ask` | Repository understanding |
| `planning` | `forge-plan` | ECP/change planning |
| `implementation` | `forge-implement` | Execution task cards |
| `execute` | `forge-execute` | Bounded code changes |
| `testing` | `forge-test` | Structured validation |
| `review` | `forge-review` | MR-style review |
| `incident` | `forge-incident` | Diagnosis and mitigation |
| `refactor` | `forge-refactor` | Bounded technical debt work |

For `execute`, the `forge-execute` skill requires approved task cards or an execution contract, stops on unclear scope, stops on HIGH-risk decisions without human approval, and reports validation honestly.

## Naming

Shared skills:

- `forge-ask`
- `forge-plan`
- `forge-implement`
- `forge-execute`
- `forge-test`
- `forge-review`
- `forge-incident`
- `forge-refactor`

Tool-specific surfaces may expose equivalent names, such as Claude `/forge-review`, Codex `$forge-review`, Codex `/skill forge-review`, GitHub Copilot `/forge-review` prompt files, or future-compatible `/forge-review`.

Scoped variants may use `forge:<mode>:<scope>`, for example `forge:review:security`. Scope suffixes are focus hints, not new modes.

Do not add lifecycle semantics, governance rules, repository cognition, orchestration, runtime execution, memory, scheduler, CI/CD, deploy behavior, or autonomous chaining to command wrappers.
