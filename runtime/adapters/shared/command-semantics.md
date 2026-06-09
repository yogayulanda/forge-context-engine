# Forge Command Semantics

Commands are lightweight tool entrypoints. They invoke shared Forge skills; they do not replace Forge.

Natural language such as "Use Forge review mode" or "Use Forge plan mode" is equivalent to invoking the matching shared skill, such as `forge-review` or `forge-plan`.

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

## Core Mode Mapping

| Mode | Shared skill | Intent |
|---|---|---|
| `init` | `forge-init` | Repository context/config initialization |
| `ask` | `forge-ask` | Repository understanding |
| `plan` | `forge-plan` | Quick Plan or SDD |
| `implementation` | `forge-implementation` | ECP generation |
| `execute` | `forge-execute` | Approved ECP execution |
| `review` | `forge-review` | Executed-result review |
| `ai-readiness` | `forge-ai-readiness` | Repository AI-readiness audit |
| `verify-context` | `forge-verify-context` | Context health/freshness only |

Scenario compatibility skills:

| Scenario | Shared skill | Routes to |
|---|---|---|
| Validation-focused work | `forge-test` | `execute` / `review` |
| Incident/regression diagnosis | `forge-incident` | `ask` / `plan` / `implementation` / `execute` / `review` |
| Behavior-preserving cleanup | `forge-refactor` | `plan` / `implementation` / `execute` / `review` |

For `execute`, the `forge-execute` skill requires an approved ECP, stops on unclear scope, stops on policy/high-risk decisions without human approval, and reports validation honestly.

## Naming

Core shared skills:

- `forge-init`
- `forge-ask`
- `forge-plan`
- `forge-implementation`
- `forge-execute`
- `forge-review`
- `forge-ai-readiness`
- `forge-verify-context`

Compatibility aliases such as `forge-implement`, `forge-test`, `forge-incident`, and `forge-refactor` must remain thin pointers into the final lifecycle.

Tool-specific surfaces may expose equivalent names, such as Claude `/forge-review`, Codex `$forge-review`, Codex `/skill forge-review`, GitHub Copilot `/forge-review` prompt files, or future-compatible `/forge-review`.

Scoped variants may use `forge:<mode>:<scope>`, for example `forge:review:security`. Scope suffixes are focus hints, not new modes.

Do not add lifecycle semantics, governance rules, repository cognition, orchestration, runtime execution, memory, scheduler, CI/CD, deploy behavior, or autonomous chaining to command wrappers.
