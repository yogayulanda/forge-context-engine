# GitHub Copilot Adapter

GitHub Copilot uses repository prompt files as a Forge UX layer.

This adapter is a thin invocation bridge. It points Copilot prompts to shared Forge skills under `runtime/skills/*/SKILL.md`, and each shared skill loads the relevant `.forge/context` mode and scoped repository evidence.

## Repository Integration

Copy or materialize these files into a target repository when Copilot prompt files are supported:

```text
.github/
+-- copilot-instructions.md
+-- prompts/
    +-- forge-init.prompt.md
    +-- forge-ask.prompt.md
    +-- forge-plan.prompt.md
    +-- forge-implementation.prompt.md
    +-- forge-execute.prompt.md
    +-- forge-review.prompt.md
    +-- forge-verify-context.prompt.md
```

Compatibility prompt files for validation, incident, and refactor scenarios may be included when useful, but they are not core lifecycle modes.

The source templates live in:

```text
runtime/adapters/copilot/
+-- copilot-instructions.md
+-- prompts/
```

## Invocation

GitHub Copilot prompt invocation may use:

- `/forge-init`
- `/forge-ask`
- `/forge-plan`
- `/forge-implementation`
- `/forge-execute`
- `/forge-review`
- `/forge-verify-context`

Prompt behavior must resolve to the matching shared skill:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

## Boundary

Copilot prompts are UX wrappers only.

They must not:

- Duplicate `.forge/context`.
- Copy shared skill workflow behavior.
- Define repository cognition, lifecycle semantics, or governance policy.
- Add orchestration, schedulers, runtime executors, CI/CD, deploy behavior, memory systems, or autonomous chaining.
- Become an alternate Forge workflow system.

When behavior needs detail, load the matching shared skill and `.forge/context/modes/<mode>.md`.
