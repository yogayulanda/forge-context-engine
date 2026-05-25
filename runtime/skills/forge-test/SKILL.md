# forge-test

## Purpose
Use Forge testing mode to plan, run, or assess structured validation.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/testing.md`. Load only scoped code, tests, contracts, and artifacts needed for validation.

## Invocation
Use when the user asks for validation strategy, test implementation guidance, running tests, coverage gaps, or post-execution validation evidence.

## Focus
Separate automated, manual, environment-dependent, and production-like validation. Check prerequisites before running commands that depend on tooling or infrastructure.

## Output
Return testing-mode status, executed checks, failures, blocked checks, coverage gaps, unvalidated risks, and reviewer focus.

## Do NOT
Do not collapse into review mode, claim success without evidence, treat environment failure as implementation failure, broad-load context, or add CI/CD/runtime execution semantics.
