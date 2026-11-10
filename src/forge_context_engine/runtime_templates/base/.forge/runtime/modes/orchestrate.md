---
id: mode.orchestrate
title: "Mode: Orchestrate"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
---

# Mode: Orchestrate

## include
- `.forge/forge.config.yaml` (`run.worker`, `run.worker_command`, `policy.*`)
- `.forge/runtime/modes/plan.md`, `implementation.md`, `execute.md`, `review.md` (passed to workers by path, not inlined)

## on_demand
- `.forge/runtime/meta/conventions-risk.md`
- `.forge/runtime/meta/conventions-validation.md`
- Saved plan, ECP, report, and review artifacts under `.forge/generated/`

## exclude
- Broad `.forge/context` loading in the orchestrator session; workers load their own scoped context.
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
6000

## purpose
Run one request through `plan -> implementation -> execute -> review` by delegating each step to a worker agent, and finish at a pushed feature branch and an open MR/PR for human review.

## inputs
- One request: free text, an issue reference, or a saved plan artifact path.
- `run.worker`: `subagent` (default; the host tool's own subagent, such as a Claude Code subagent) or `cli` (an external agent CLI started through `run.worker_command`).
- `run.worker_command`: command template used only when `run.worker: cli`. `{prompt_file}` is replaced with the path of the worker prompt file.
- `policy.high_risk_areas` and `policy.require_human_confirmation_for`.
- Validation commands from the ECP or `tools.validation_commands`.

## roles
- Orchestrator: the invoking session. Owns sequencing, gate decisions, branch, commit, push, MR/PR, and the final report. Does not write application code.
- Planner worker: runs `plan` and then `implementation`; returns SDD and ECP artifacts.
- Execute worker: runs `execute` for the ECP; may edit files only inside ECP scope.
- Reviewer worker: runs `review` in a fresh context that did not see the execute worker's reasoning; inputs are the SDD, ECP, diff, and validation output only.

## behavior
1. Preflight: confirm the working tree is clean, the current branch is not the default/protected branch, and create a feature branch `forge/<YYYY-MM-DD>-<slug>` when not already on one.
2. Plan: planner worker produces the SDD and saves it to `.forge/generated/plans/`.
3. Gate 1 (risk-gated): classify the SDD against `policy.high_risk_areas` and `policy.require_human_confirmation_for`. If any area matches, or the classification is uncertain, stop with `awaiting_sdd_approval`. Otherwise record `Gate 1: auto (no high-risk area)` with the evidence and continue.
4. Implementation: planner worker produces the ECP and saves it to `.forge/generated/ecp/`.
5. Gate 2 (automatic): accept the ECP for execution when it has no blocking unknowns, its scope matches the SDD, and it adds no high-risk area that Gate 1 did not clear. Record `Gate 2: auto` with the ECP path. Otherwise stop.
6. Execute: execute worker applies the ECP and runs its validation commands.
7. Review: reviewer worker reviews the diff in a fresh context.
8. Fix loop: on `request_changes`, pass only the review findings and the ECP to the execute worker as the fix scope, then review again. Maximum 2 fix rounds. If the verdict is still not `accept` after round 2, stop with `review_unresolved`.
9. Publish: on `accept` with green validation, commit on the feature branch, push that branch only, and open an MR/PR when the host tool can. The MR/PR body links the SDD, ECP, execution report, review, and the gate trace.
10. Report: return the orchestration report.

## stop conditions
Stop immediately, keep work local, and report when any of these happens:
- Validation is red, or required validation cannot run (`blocked_by_environment`).
- The diff touches an external contract, a database migration, or a secret, unless the SDD was human-approved at Gate 1 and named that change.
- Scope grows: the diff changes files outside the ECP `Files likely to change`, or a worker proposes new scope.
- A worker returns a blocking unknown, `blocked`, or `blocked_by_decision`.
- The working tree was dirty at start, or the branch is the default/protected branch.
- `run.worker: cli` is set but `run.worker_command` is empty or the command fails to start.

## outputs
- Orchestration Report: `Request`, `Branch`, `Gate trace`, `Artifacts`, `Rounds`, `Validation`, `Review verdict`, `MR/PR`, `Stop reason` (when stopped), `Status`.
- Saved artifacts under `.forge/generated/plans/`, `ecp/`, `reports/`, and `reviews/`. Orchestrate saves by default because workers continue from them.

## status values
- `mr_opened`
- `awaiting_sdd_approval`
- `stopped`
- `review_unresolved`
- `blocked_by_environment`

## boundaries
- Starting `forge-orchestrate` is the human's approval for Gate 2 and for Gate 1 on non-high-risk SDDs, for this one request only. It is not approval for other requests or later scope.
- Never merge, tag, release, deploy, or push to the default/protected branch.
- Never force-push, rewrite shared history, or change secrets, CI/CD, or deploy config.
- Workers keep their own mode boundaries; the orchestrator does not edit application code itself.
- Gate decisions and the gate trace are reported in the MR/PR; they are not persistent memory or workflow state.
- One request = one feature branch = one MR/PR. Do not chain into another request.

## next mode transitions
- `awaiting_sdd_approval` -> human approves the SDD by path, then re-invoke `forge-orchestrate` with that SDD; it resumes at step 4.
- `stopped` or `review_unresolved` -> human decides: fix manually, re-scope with `plan`, or discard the branch.
- `mr_opened` -> human reviews and merges outside Forge.
