# forge-ask

## Purpose
Answer repository-understanding questions using Forge ask mode.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/ask.md`. Load only scoped context needed for the question.

## Invocation
Use when the user asks to understand repository behavior, structure, evidence, assumptions, unknowns, or Forge context without planning or mutation.

## Focus
Use context first and perform scoped code verification when needed. Separate evidence-backed facts, inferences, assumptions, and unknowns.

## Output
Return ask-mode output: answer, confirmed facts, inference, assumptions, unknowns, evidence, verification needed, and suggested next mode when useful.

## Do NOT
Do not plan, produce an ECP, implement, review, mutate files, broad-load `.forge/context`, invent repository facts, or treat generated artifacts as source of truth.
