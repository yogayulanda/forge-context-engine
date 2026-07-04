# forge-test

## Purpose
Scenario compatibility skill for validation-focused work.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/testing.md` as scenario guidance.

## Invocation
Use only when an older prompt asks for `forge-test` or when the user explicitly asks for validation strategy/evidence. Route actual lifecycle work through `execute` and `review`.

## Focus
Separate scoped validation, final validation, manual checks, environment blockers, coverage gaps, and risks.

## Output
Return validation guidance or evidence report. Point to `execute` for approved code/validation changes and `review` for MR readiness and risk assessment.

## Do NOT
Do not present testing as a core lifecycle mode, claim success without evidence, treat environment failure as implementation failure, broad-load context, or add CI/CD/runtime execution semantics.
