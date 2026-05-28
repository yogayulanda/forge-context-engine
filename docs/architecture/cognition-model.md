# Cognition Model

Forge cognition is repository-first and bounded.

## Source Of Truth

The authority order is:

1. Current repository code.
2. Repository docs and ADRs.
3. Explicit human confirmations.
4. `.forge/context` entries supported by evidence.
5. Generated artifacts, only as handoff records.

If context or artifacts conflict with current repository evidence, current repository evidence wins.

## Bounded Cognition

Forge does not load every file or every context note by default. It loads:

- the runtime config
- always-loaded conventions and core context
- the requested mode file
- task-relevant layers, systems, decisions, assumptions, unknowns, or artifacts

When required evidence exceeds the scoped budget, Forge should report the missing evidence and the affected decision instead of guessing.

## Evidence Boundaries

Forge outputs should separate:

- confirmed repository evidence
- inference supported by evidence
- assumptions
- proposed defaults
- unknowns

This keeps AI-assisted work reviewable by engineers.

## What This Is Not

Forge cognition is not:

- persistent AI memory
- RAG infrastructure
- vector search
- a knowledge graph
- an autonomous agent state store
- a workflow engine

Generated artifacts may help handoff, but they do not trigger work or become source of truth.
