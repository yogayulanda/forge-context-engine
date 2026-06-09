# Codex Adapter

Codex enters Forge through `AGENTS.md` and shared Forge skills.

## How Invocation Works

Codex invocation syntax may vary by surface or version. Acceptable request styles include:

```text
$forge-review
/skill forge-review
Use Forge review mode on this branch.
Use Forge plan mode for this change.
Use Forge execute mode for the approved ECP.
Use Forge ai-readiness mode on this repo before larger AI-driven work.
```

The expected path is:

```text
Codex request -> AGENTS.md -> shared skill -> .forge/context mode -> scoped repository evidence
```

## What The Adapter Does

`AGENTS.md` maps user wording to shared skills:

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

Codex remains skills-first. There is no separate Codex command-wrapper layer unless a future Codex runtime explicitly requires one.

## Expected Usage Style

Good Codex request:

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

The Codex adapter must not:

- store repo-specific facts
- duplicate `.forge/context`
- invent lifecycle behavior
- auto-advance between modes
- imply autonomous agents, workflow engines, or persistent memory

Repository evidence and Forge mode files remain authoritative.
