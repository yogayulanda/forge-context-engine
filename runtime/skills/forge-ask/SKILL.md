# forge-ask

## Purpose
Answer repository-understanding questions using Forge ask mode.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/ask.md`. Load only scoped context needed for the question.

## Invocation
Use when the user asks to understand repository behavior, structure, evidence, assumptions, unknowns, or Forge context without planning or mutation.

## Focus
Prefer current repository evidence. Separate evidence-backed facts, inferences, proposed defaults, assumptions, and unknowns.

## Output
Return a concise answer with relevant evidence, explicit unknowns, and any scoped context gap that affects confidence.

## Do NOT
Do not plan, implement, review, refactor, mutate files, broad-load `.forge/context`, invent repository facts, or treat generated artifacts as source of truth.
