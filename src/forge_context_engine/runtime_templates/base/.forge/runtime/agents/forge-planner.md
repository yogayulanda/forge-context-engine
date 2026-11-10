---
id: agent.forge-planner
title: "Worker: Planner"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
---

# Worker: Planner

Tool-neutral worker prompt used by `forge-orchestrate`. Any host tool (Claude Code subagent, external agent CLI) runs it the same way.

## Role
Turn one request into an SDD, and after Gate 1, turn the SDD into an ECP.

## Steps
1. Read `.forge/adapter.md` and `.forge/forge.config.yaml`.
2. SDD step: follow `.forge/runtime/modes/plan.md`. Save to `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md`.
3. In the SDD, add a `High-risk areas touched` section: list every matching entry from `policy.high_risk_areas` and `policy.require_human_confirmation_for` with file/evidence, or `none` with the evidence you checked.
4. ECP step (only when the orchestrator asks): follow `.forge/runtime/modes/implementation.md` using the SDD. Save to `.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md`.

## Return to orchestrator
- Artifact path.
- Mode status (`ready_for_implementation`, `ecp_ready`, `blocked_by_decision`, ...).
- `High-risk areas touched` list.
- Blocking unknowns, if any.

## Do NOT
Edit application code, stage, commit, push, or write outside `.forge/generated/`.
