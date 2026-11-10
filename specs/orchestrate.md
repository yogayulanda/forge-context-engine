# Forge Orchestrate

| Field | Value |
|---|---|
| Document | Forge Orchestrate Specification |
| Version | 0.1 |
| Date | 2026-11-10 |
| Status | `proposed` |
| Scope | One request through `plan -> implementation -> execute -> review` with worker agents, ending at an MR/PR |
| Dependency | `specs/mode-invocation.md`, `runtime/.forge/runtime/modes/orchestrate.md`, `runtime/.forge/runtime/agents/*.md` |

---

## 1. Problem

The manual Forge flow needs a human at every step: approve the SDD, approve the ECP, run execute, run review, scope fixes, then commit and open the MR. With several AI tools involved, the human also copies prompts and results between tools. Most of that time is transport, not decisions.

## 2. Goal

The human types one command and is needed at two points only:

1. Approving an SDD that touches a high-risk area (Gate 1, risk-gated).
2. Reviewing the MR/PR.

Everything between is sequenced by an orchestrator session that delegates to worker agents. Workers exchange files under `.forge/generated/`, not chat copy-paste.

## 3. Non-goals

- Merging, tagging, releasing, or deploying.
- Running several requests in one invocation, or chaining into a next request.
- Schedulers, triggers, daemons, or a background service.
- Persistent agent memory. The gate trace is a report section only.
- Replacing the manual flow. Manual Gate 1 and Gate 2 stay unchanged.

## 4. Roles

| Role | Prompt | Mode | Writes |
|---|---|---|---|
| Orchestrator | `modes/orchestrate.md` | sequencing, gates, git, MR/PR | `.forge/generated/` only |
| Planner | `agents/forge-planner.md` | `plan`, `implementation` | plans, ECPs |
| Executor | `agents/forge-executor.md` | `execute` | ECP-scoped files, execution report |
| Reviewer | `agents/forge-reviewer.md` | `review`, fresh context | nothing (returns text) |

Role prompts are tool-neutral under `.forge/runtime/agents/`. Tool wrappers such as `.claude/agents/forge-<role>.md` only point to them and set tool limits.

### 4a. Specialties

Roles say which step a worker does. Specialties say which expertise it brings. A specialty is an overlay file with `applies_to`, `applies_when`, `Load`, `Focus`, and `Review checklist`.

- Forge ships examples in `.forge/runtime/agents/specialties/`: `backend`, `frontend`, `mobile`, `infrastructure`, `security`, `tech-lead`. They are managed and refreshed by `forge update`.
- Teams customize by adding or copying files to `.forge/agents/<name>.md`. That folder is user-owned; a file there wins over a Forge example of the same name.
- Selection: `--as <names>`, else the planner matches `applies_when` against the SDD and records the choice, else no overlay. `tech-lead` always applies to the orchestrator.
- High-risk SDDs get an extra `security` reviewer; both reviewers must `accept`.
- Overlays point to `.forge/context` layers instead of copying repository knowledge, and they cannot relax gates, stop conditions, or tool limits.

## 5. Gates (G2 Hybrid)

| Gate | Manual flow | Under `forge-orchestrate` |
|---|---|---|
| Gate 1 (SDD -> implementation) | Human approval | Automatic when the SDD's `High-risk areas touched` is `none` with evidence. Human approval when any `policy.high_risk_areas` or `policy.require_human_confirmation_for` area matches, or when classification is uncertain. |
| Gate 2 (ECP -> execute) | Human approval | Automatic. The invocation is the approval for this request's ECP only. Stops if the ECP adds a high-risk area that Gate 1 did not clear or has blocking unknowns. |

The high-risk list comes from config, so each repository can tune it. The default list covers payments, authentication, authorization, public API, database migrations, secrets, external provider integration, and file upload.

## 6. Stop conditions

The orchestrator stops, does not commit or push, leaves changes uncommitted on the feature branch, and reports when:

- validation is red or cannot run;
- the diff changes an external contract, a migration, or a secret not named in a human-approved SDD;
- the diff changes files outside the ECP scope, or a worker proposes new scope;
- a worker returns a blocking unknown or a blocked status;
- the review verdict is not `accept` after 2 fix rounds;
- the working tree is dirty at start, or the branch is the default/protected branch;
- `run.worker: cli` is set without a working `run.worker_command`;
- the diff touches a high-risk area the SDD did not list (Gate 1 cross-check);
- a reviewer changed the working tree (reviewer write guard).

## 7. Publication

On `accept` with green validation: commit the code changes plus this run's `.forge/generated/` artifacts on `forge/<YYYY-MM-DD>-<slug>`, push that branch only, and open an MR/PR when the host tool can. The MR/PR body links the SDD, ECP, execution report, review, and the gate trace. No force-push.

## 8. Worker configuration

```yaml
run:
  worker: subagent      # subagent | cli; missing key means subagent
  worker_command: ""    # used only when worker: cli; {prompt_file} is substituted
```

- `subagent`: the host tool's own subagents. Verified target: Claude Code subagents via `.claude/agents/`.
- `cli`: any external agent CLI that accepts a prompt file non-interactively. **GitHub Copilot CLI support is unverified**: Forge does not define or test its flags. Users must confirm the command on their own machine before relying on it.

## 9. Report

The orchestrator writes `.forge/generated/reports/YYYY-MM-DD-<slug>-orchestration-report.md` and updates it after every step. Header fields: `Artifact`, `Repo`, `Date`, `Target tool`, `Status`, `Run`, `Goal`, `Note`. Body: a step checklist (`✓` done, `✱` in progress/waiting, `○` not started, `✗` stopped), artifacts, gate trace, validation, review rounds, and the MR/PR link. Exact shape lives in the mode file. The report is a trace for humans, not resumable state.

## 10. Statuses

`mr_opened`, `awaiting_sdd_approval`, `stopped`, `review_unresolved`, `blocked_by_environment`.

## 11. Validation

See `validation-cases/orchestrate-gates.md`. A trial is considered stable only when every stop scenario stops correctly and real low-risk runs reach an MR without intervention at an agreed rate.

## 12. Open items

- Parallel requests via one git worktree per request: later stage, after single-request runs prove stable.
- The earlier `forge run` control-plane draft stays parked; it is not part of this change.
