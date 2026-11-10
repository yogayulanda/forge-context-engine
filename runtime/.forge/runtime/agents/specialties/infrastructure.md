---
id: specialty.infrastructure
title: "Specialty: Infrastructure"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [planner, reviewer]
applies_when: layer infrastructure is active and the change touches deployment or provisioning files
---

# Specialty: Infrastructure

Overlay for `forge-orchestrate` workers. It adds focus and context to a role; it never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/infrastructure.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it.

## Load
- `.forge/context` layer `infrastructure` files.

## Focus
- Infra changes are high-risk by default under `forge-orchestrate`; expect Gate 1 to stay human.
- Never apply or deploy; only edit files inside ECP scope.

## Review checklist
- No secret values in manifests or variables.
- Changes are reversible and the rollback is stated.
