# OpenCode Adapter

OpenCode enters Forge through `AGENTS.md` and repo-local shared Forge skills.

OpenCode's official `/init` flow creates `AGENTS.md` in the repository root, so Forge should reuse that surface instead of introducing a separate root wrapper.

## How Invocation Works

OpenCode invocation syntax may vary by surface or version. Acceptable request styles include:

```text
Use Forge ask mode on this repository.
Use Forge plan mode for this change.
Use Forge execute mode for the approved ECP.
/forge-review
forge-review
```

When `forge init --tools opencode` or `forge update --tools opencode` runs, Forge installs shared skills into the repository under `.opencode/skills/forge-*/SKILL.md` so OpenCode can discover them as repo-local skills.

The expected path is:

```text
OpenCode request -> AGENTS.md or repo-local skill -> .forge/context mode -> scoped repository evidence
```

## What The Adapter Does

The shared `AGENTS.md` wrapper and repo-local `.opencode/skills/` directory map user wording to shared skills:

| Mode wording | Shared skill |
|---|---|
| `init` | `forge-init` |
| `ask` | `forge-ask` |
| `plan` | `forge-plan` |
| `implementation` | `forge-implementation` |
| `execute` | `forge-execute` |
| `review` | `forge-review` |
| `ai-readiness` | `forge-ai-readiness` |
| `verify-context` | `forge-verify-context` |

Scenario compatibility skills such as `forge-test`, `forge-incident`, and `forge-refactor` route validation, incident, or refactor requests through the core lifecycle.

OpenCode remains skills-first. Forge installs repo-local skills for OpenCode instead of introducing a second root wrapper or duplicating lifecycle semantics into tool-specific command files.

## Expected Usage Style

Good OpenCode request:

```text
Use Forge execute mode for this approved ECP.
Report changed files, validation, fixes made during execute, rollback notes, and hidden change check.
```

Good review request:

```text
Use Forge review mode.
Prioritize bugs, behavioral regressions, validation gaps, security, context impact, and the exact diff reviewed.
```

Good readiness request:

```text
Use Forge ai-readiness mode on this repo.
Audit context fitness, ambiguity, validation readiness, and remediation priorities.
```

## Boundaries

The OpenCode adapter must not:

- store repo-specific facts
- duplicate `.forge/context`
- invent lifecycle behavior
- auto-advance between modes
- imply autonomous agents, workflow engines, or persistent memory

Repository evidence and Forge mode files remain authoritative.
