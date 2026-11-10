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

## 5. Gates (G2 Hybrid)

| Gate | Manual flow | Under `forge-orchestrate` |
|---|---|---|
| Gate 1 (SDD -> implementation) | Human approval | Automatic when the SDD's `High-risk areas touched` is `none` with evidence. Human approval when any `policy.high_risk_areas` or `policy.require_human_confirmation_for` area matches, or when classification is uncertain. |
| Gate 2 (ECP -> execute) | Human approval | Automatic. The invocation is the approval for this request's ECP only. Stops if the ECP adds a high-risk area that Gate 1 did not clear or has blocking unknowns. |

The high-risk list comes from config, so each repository can tune it. The default list covers payments, authentication, authorization, public API, database migrations, secrets, external provider integration, and file upload.

## 6. Stop conditions

The orchestrator stops, does not push, and reports when:

- validation is red or cannot run;
- the diff changes an external contract, a migration, or a secret not named in a human-approved SDD;
- the diff changes files outside the ECP scope, or a worker proposes new scope;
- a worker returns a blocking unknown or a blocked status;
- the review verdict is not `accept` after 2 fix rounds;
- the working tree is dirty at start, or the branch is the default/protected branch;
- `run.worker: cli` is set without a working `run.worker_command`.

## 7. Publication

On `accept` with green validation: commit on `forge/<YYYY-MM-DD>-<slug>`, push that branch only, and open an MR/PR when the host tool can. The MR/PR body links the SDD, ECP, execution report, review, and the gate trace. No force-push.

## 8. Worker configuration

```yaml
run:
  worker: subagent      # subagent | cli; missing key means subagent
  worker_command: ""    # used only when worker: cli; {prompt_file} is substituted
```

- `subagent`: the host tool's own subagents. Verified target: Claude Code subagents via `.claude/agents/`.
- `cli`: any external agent CLI that accepts a prompt file non-interactively. **GitHub Copilot CLI support is unverified**: Forge does not define or test its flags. Users must confirm the command on their own machine before relying on it.

## 9. Statuses

`mr_opened`, `awaiting_sdd_approval`, `stopped`, `review_unresolved`, `blocked_by_environment`.

## 10. Validation

See `validation-cases/orchestrate-gates.md`. A trial is considered stable only when every stop scenario stops correctly and real low-risk runs reach an MR without intervention at an agreed rate.

## 11. Open items

- Specialty overlays (backend, frontend, security, tech-lead persona) on top of the three roles: proposed, pending decision.
- Parallel requests via one git worktree per request: later stage, after single-request runs prove stable.
- Relationship with the earlier `forge run` control-plane draft: pending decision.
