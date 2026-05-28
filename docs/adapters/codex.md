# Codex Adapter

Codex enters Forge through `AGENTS.md` and shared Forge skills.

## How Invocation Works

Codex invocation syntax may vary by surface or version. Acceptable request styles include:

```text
$forge-review
/skill forge-review
Use Forge review mode on this branch.
Use Forge planning mode for this change.
```

The expected path is:

```text
Codex request -> AGENTS.md -> shared skill -> .forge/context mode -> scoped repository evidence
```

## What The Adapter Does

`AGENTS.md` maps user wording to shared skills:

| Mode wording | Shared skill |
|---|---|
| `ask` | `forge-ask` |
| `planning` | `forge-plan` |
| `implementation` | `forge-implement` |
| `execute` | `forge-execute` |
| `testing` | `forge-test` |
| `review` | `forge-review` |
| `incident` | `forge-incident` |
| `refactor` | `forge-refactor` |

Codex remains skills-first. There is no separate Codex command-wrapper layer unless a future Codex runtime explicitly requires one.

## Expected Usage Style

Good Codex request:

```text
Use Forge execute mode for these approved task cards.
Report changed files, validation, rollback notes, and hidden change check.
```

Good review request:

```text
Use Forge review mode.
Prioritize bugs, behavioral regressions, validation gaps, and MR readiness.
```

## Boundaries

The Codex adapter must not:

- store repo-specific facts
- duplicate `.forge/context`
- invent lifecycle behavior
- auto-advance between modes
- imply autonomous agents, workflow engines, or persistent memory

Repository evidence and Forge mode files remain authoritative.
