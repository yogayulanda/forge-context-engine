# forge-refactor

## Purpose
Evaluate or carry out bounded, behavior-preserving cleanup using Forge refactor mode.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/refactor.md`. Load only scoped evidence for the affected behavior, tests, dependencies, and risk boundaries.

## Invocation
Use when the user asks for technical-debt cleanup, structure improvement, simplification, or behavior-preserving refactor analysis.

## Focus
Preserve behavior. Identify safe changes, risky boundaries, validation needs, and out-of-scope redesigns.

## Output
Return refactor-mode output with target area, evidence, proposed safe changes, risks, validation expectations, and explicit non-goals.

## Do NOT
Do not hide behavior changes, rewrite architecture, change contracts without approval, modify unrelated code, broad-load context, or turn refactoring into autonomous cleanup.
