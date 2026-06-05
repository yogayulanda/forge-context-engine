---
id: scenario.incident
title: "Scenario Guidance: Incident"
type: scenario
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
---

# Scenario Guidance: Incident

`incident` is not a core lifecycle mode. Use this file only as compatibility, scenario, or historical guidance for incident, regression, or production-like symptom work.

## route through core modes
- Use `ask` to understand symptoms and evidence.
- Use `plan` for remediation strategy when changes are needed.
- Use `implementation` to produce an ECP for approved remediation.
- Use `execute` to apply approved remediation.
- Use `review` to inspect the executed result and risk.

## include
- `layers/<related>`
- `systems/<affected>`
- `knowledge/inferred.md`

## on_demand
- `knowledge/decisions/`, `knowledge/assumptions.md`, `knowledge/unknowns.md`
- Logs, traces, metrics, configs, recent changes, contracts, migrations, and runbooks when relevant

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
6000

## notes
- Diagnose from evidence; distinguish symptoms, likely causes, possible causes, and missing evidence.
- Use `LIKELY_CAUSE` only with direct supporting evidence.
- Redact secrets and sensitive data.
- Do not redesign architecture, invent topology, or apply fixes without approved plan/ECP flow.
