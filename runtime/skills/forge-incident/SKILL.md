# forge-incident

## Purpose
Diagnose incidents, regressions, or production-like symptoms using Forge incident mode.

## Load
Read `.forge/forge.config.yaml` first. Apply `runtime.non_interactive` and respect `runtime.profile`. Load `.forge/context/00-meta/conventions.md`, use `.forge/context/00-meta/context-manifest.md` only as a routing index, then read `.forge/context/modes/incident.md`. Load only scoped evidence tied to the symptom, affected flow, blast radius, and likely rollback or mitigation path.

## Invocation
Use when the user reports a bug, outage, regression, failed validation, unexpected behavior, or operational symptom requiring diagnosis.

## Focus
Separate observed facts, hypotheses, missing evidence, impact, mitigation, rollback possibility, and next checks.

## Output
Return incident-mode diagnosis with current evidence, likely cause or unknowns, impact, mitigation, validation checks, and follow-up decisions.

## Do NOT
Do not speculate beyond evidence, redesign architecture, modify code without approved execution scope, broad-load unrelated context, or create incident automation/orchestration semantics.
