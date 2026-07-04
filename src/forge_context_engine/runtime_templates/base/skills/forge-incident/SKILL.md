# forge-incident

## Purpose
Scenario compatibility skill for incident, regression, or production-like symptom work.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/incident.md` as scenario guidance.

## Invocation
Use only when the user asks for incident/regression diagnosis or an older prompt invokes `forge-incident`.

## Focus
Diagnose from evidence, distinguish symptoms from likely/possible causes, preserve uncertainty, and route remediation through `plan`, `implementation`, `execute`, and `review`.

## Output
Return diagnosis, evidence, unknowns, mitigation options, rollback considerations, and recommended next core mode.

## Do NOT
Do not present incident as a core lifecycle mode, redesign architecture, invent topology, apply fixes without approved plan/ECP flow, or copy raw secrets.
