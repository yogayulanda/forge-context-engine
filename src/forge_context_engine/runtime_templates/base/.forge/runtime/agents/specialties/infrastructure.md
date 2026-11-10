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

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/infrastructure.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. Put team-specific rules (libraries, error shapes, naming, test commands) in the copy, not here.

## Load
- `.forge/context` layer `infrastructure` files.
- The runtime/deployment and operations profile files.

## As planner
- Treat the change as high-risk; Gate 1 stays human under `forge-orchestrate`.
- Name the environments affected and the order of rollout.
- State the rollback: exact revert step and expected recovery time.
- State blast radius: which services, jobs, or users are affected if it fails.
- Never plan an apply, deploy, or secret rotation as an execute task; those stay human actions.

## As reviewer
- No secret values in manifests, variables, or defaults.
- Resource limits, replicas, and health checks are set and consistent with existing services.
- The change is reversible and the rollback in the SDD is correct for this diff.
- No change to CI/CD or deploy pipelines unless the human-approved SDD names it.
