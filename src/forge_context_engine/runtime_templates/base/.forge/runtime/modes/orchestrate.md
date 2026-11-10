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
- `.forge/runtime/agents/forge-planner.md`, `forge-executor.md`, `forge-reviewer.md` (passed to workers by path, not inlined)

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
- Optional specialties: `--as <name>[,<name>]`, for example `--as backend,security`.
- `run.worker`: `subagent` (default, also when the key is missing) or `cli`.
- `run.worker_command`: command template used only when `run.worker: cli`. `{prompt_file}` is replaced with the path of the worker prompt file.
- `policy.high_risk_areas` and `policy.require_human_confirmation_for`.
- Validation commands from the ECP or `tools.validation_commands`.

## roles
| Role | Prompt | Runs mode | May edit |
|---|---|---|---|
| Orchestrator | this file | sequencing, gates, git, MR/PR, report | `.forge/generated/` only; never application code |
| Planner | `.forge/runtime/agents/forge-planner.md` | `plan`, then `implementation` | `.forge/generated/plans/`, `ecp/` |
| Executor | `.forge/runtime/agents/forge-executor.md` | `execute` | files inside ECP scope, `.forge/generated/reports/` |
| Reviewer | `.forge/runtime/agents/forge-reviewer.md` | `review` in a fresh context | nothing |

## specialties
- A specialty is an overlay file with a `Load` section and one `As <role>` section per role it applies to. It never changes role steps, gates, stop conditions, or tool limits.
- Lookup per name: `.forge/agents/<name>.md` (user-owned, wins) then `.forge/runtime/agents/specialties/<name>.md` (Forge-provided examples).
- Selection order: names passed with `--as`; otherwise the planner matches each specialty's `applies_when` against the layers and files the SDD touches and lists the result in the SDD under `Specialties`; otherwise no overlay.
- `tech-lead` always applies to the orchestrator.
- When the SDD lists any high-risk area, run one extra reviewer with the `security` specialty in addition to the normal reviewer. Both must return `accept`.
- Pass the role prompt and the selected overlay paths to each worker. Do not inline their content.

## worker dispatch
- `run.worker: subagent`: start each role as a separate subagent of the host tool. Claude Code uses `.claude/agents/forge-<role>.md`. The reviewer is always a new subagent, never a resumed one.
- `run.worker: cli`: write a prompt file under `.forge/temp/orchestrate/` that points to the role prompt and lists the inputs, then run `run.worker_command` with `{prompt_file}` replaced. Read the worker result from the artifact path it reports. Flags for any specific CLI are not defined by Forge and must be verified by the user.
- The orchestrator may run the planner and reviewer as subagents while only the executor uses `cli`; it reports which worker ran each role.

## behavior
1. Preflight: confirm the working tree is clean, the current branch is not the default/protected branch, and create a feature branch `forge/<YYYY-MM-DD>-<slug>` when not already on one.
2. Clarify, then plan: the planner reads the request against the repository (step list in `forge-planner.md`) before writing the SDD. If it finds any ambiguity, contradiction, or missing value that changes the outcome, it saves the plan with status `blocked_by_decision` and a `Clarification Questions` section. Stop with `awaiting_clarification` and show all questions at once, in `ui.language`. Do not continue on guesses.
2b. Resume after answers: the human answers in one reply (accepting recommendations is allowed, for example `ok all recommendations, except Q2: B`). The planner records the answers in the plan under `Confirmed Decisions` and writes the SDD. Ask again only if an answer itself creates a new blocking question.
3. Gate 1 (risk-gated): classify the SDD against `policy.high_risk_areas` and `policy.require_human_confirmation_for`. If any area matches, or the classification is uncertain, stop with `awaiting_sdd_approval`. Otherwise record `Gate 1: auto (no high-risk area)` with the evidence and continue.
4. Implementation: planner worker produces the ECP and saves it to `.forge/generated/ecp/`.
5. Gate 2 (automatic): accept the ECP for execution when it has no blocking unknowns, its scope matches the SDD, and it adds no high-risk area that Gate 1 did not clear. Record `Gate 2: auto` with the ECP path. Otherwise stop.
6. Execute: execute worker applies the ECP and runs its validation commands.
6a. Diff risk check: map every changed file to `policy.high_risk_areas`. If the diff touches a high-risk area that the SDD did not list, stop; Gate 1 was decided on incomplete evidence.
7. Review: record `git status --porcelain` and `git diff` hash, then run the reviewer worker in a fresh context, plus a security reviewer when the SDD lists a high-risk area. If the working tree changed during review, stop: reviewers must not modify files.
8. Fix loop: on `request_changes`, pass only the review findings and the ECP to the execute worker as the fix scope, then review again. Maximum 2 fix rounds. If the verdict is still not `accept` after round 2, stop with `review_unresolved`.
9. Publish: on `accept` with green validation, commit the code changes together with this run's artifacts (plan, ECP, execution and orchestration reports, reviews under `.forge/generated/`; never `.forge/temp/` or `.forge/cache/`) on the feature branch, push that branch only, and open an MR/PR when the host tool can. The MR/PR body links the SDD, ECP, execution report, review, and the gate trace.
10. Report: return the orchestration report.

## stop conditions
Stop immediately and report. Do not commit or push: leave changes uncommitted on the feature branch so the human can inspect or discard them. Stop when any of these happens:
- Validation is red, or required validation cannot run (`blocked_by_environment`).
- The diff touches an external contract, a database migration, or a secret, unless the SDD was human-approved at Gate 1 and named that change.
- Scope grows: the diff changes files outside the ECP `Files likely to change`, or a worker proposes new scope.
- A worker returns a blocking unknown, `blocked`, or `blocked_by_decision`.
- The working tree was dirty at start, or the branch is the default/protected branch.
- A worker finds a new blocking ambiguity after clarification. Report it as a `clarify miss` so the planner's checks can be improved; do not guess.
- `run.worker: cli` is set but `run.worker_command` is empty or the command fails to start.
- The diff touches a high-risk area the SDD did not list (step 6a).
- A reviewer changed the working tree (step 7).

## outputs
- Orchestration Report at `.forge/generated/reports/YYYY-MM-DD-<slug>-orchestration-report.md`, in the report format below. Update it after every step so the human can open it mid-run; print the same content in chat at the end.
- Saved artifacts under `.forge/generated/plans/`, `ecp/`, `reports/`, and `reviews/`. Orchestrate saves by default because workers continue from them.

## report format
```markdown
# Orchestration Report: <short goal>

| Field | Value |
|---|---|
| Artifact | orchestration_report |
| Repo | <repo name> @ <base commit short sha> |
| Date | YYYY-MM-DD |
| Target tool | orchestrator=<tool>; planner=<worker>; executor=<worker>; reviewer=<worker> |
| Specialties | orchestrator=tech-lead; executor=<names>; reviewer=<names> |
| Status | <status value> |
| Run | <slug> on branch `forge/<YYYY-MM-DD>-<slug>` |
| Goal | <one sentence, from the request> |
| Note | <stop reason, human action needed, or `none`> |

## Steps
✓ Preflight (clean tree, feature branch)
✓ Clarify: 0 questions | ✱ Clarify: awaiting answers (<n> questions)
✓ SDD -> .forge/generated/plans/<file>
✓ Gate 1: auto (no high-risk area) | ✱ Gate 1: awaiting human (<areas>)
○ ECP
○ Gate 2
○ Execute
○ Review round 1
○ Publish (push + MR/PR)

## Artifacts
| Type | Path | Status |
|---|---|---|

## Gate trace
- Gate 1: <auto|human|stopped> - <evidence>
- Gate 2: <auto|stopped> - <evidence>

## Validation
| Command | Result |
|---|---|

## Review rounds
| Round | Verdict | Open findings |
|---|---|---|

## MR/PR
<link, or `not opened` with reason>
```
Step markers: `✓` done, `✱` in progress or waiting, `○` not started, `✗` stopped here. The report is a human-readable trace, not resumable workflow state; resume always starts from the named SDD or ECP artifact.

## status values
- `mr_opened`
- `awaiting_clarification`
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
- `awaiting_clarification` -> human answers the questions in one reply, then re-invoke `forge-orchestrate` with the plan path; it resumes at step 2b.
- `awaiting_sdd_approval` -> human approves the SDD by path, then re-invoke `forge-orchestrate` with that SDD; it resumes at step 4.
- `stopped` or `review_unresolved` -> human decides: fix manually, re-scope with `plan`, or discard the branch.
- `mr_opened` -> human reviews and merges outside Forge.
