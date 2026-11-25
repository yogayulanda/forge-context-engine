# Forge Orchestrate

| Field | Value |
|---|---|
| Document | Forge Orchestrate Specification |
| Version | 0.1 |
| Date | 2026-11-10 |
| Status | `proposed` |
| Scope | One request through `plan -> implementation -> execute -> test -> review` with worker agents, ending at an MR/PR |
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
| Tester | `agents/forge-tester.md` | scenario tests + full regression, fresh context | test paths only, test report |
| Reviewer | `agents/forge-reviewer.md` | `review`, fresh context | nothing (returns text) |

Role prompts are tool-neutral under `.forge/runtime/agents/`. Tool wrappers such as `.claude/agents/forge-<role>.md` only point to them and set tool limits.

### 4-test. Independent testing

The executor writes unit tests next to its code. A separate tester then writes integration and end-to-end tests from the SDD only, without the executor's reasoning, so tests do not share the executor's blind spots. It builds a scenario matrix per changed entry point (happy path, input validation, boundaries, auth and permission, dependency failure, idempotency and duplicates, concurrency, data state, contract, regression), runs the e2e/integration command, then the full suite. It may only write under the test paths from the `testing` overlay. Failing scenarios go back to the executor through the same 2-round fix loop as review findings. Teams set their test commands, e2e environment, and test paths in `.forge/agents/testing.md`.

### 4a. Specialties

Roles say which step a worker does. Specialties say which expertise it brings. A specialty is an overlay file with `applies_to`, `applies_when`, `Load`, and one `As <role>` section per role (for example `As planner`, `As executor`, `As reviewer`, `As orchestrator`). Each worker reads only its own role section.

- Forge ships examples in `.forge/runtime/agents/specialties/`: `backend`, `backend-go`, `frontend`, `mobile`, `infrastructure`, `security`, `tech-lead`, `testing`. Language overlays such as `backend-go` stack on top of `backend`. The repository's existing patterns win over every overlay rule. They are managed and refreshed by `forge update`.
- Teams customize by adding or copying files to `.forge/agents/<name>.md`. That folder is user-owned; a file there wins over a Forge example of the same name.
- Selection: `--as <names>`, else the planner matches `applies_when` against the SDD and records the choice, else no overlay. `tech-lead` always applies to the orchestrator.
- High-risk SDDs get an extra `security` reviewer; both reviewers must `accept`.
- Overlays point to `.forge/context` layers instead of copying repository knowledge, and they cannot relax gates, stop conditions, or tool limits.

## 4b. Clarification first

Before writing the SDD, the planner reads the request against the repository (context, ADRs, and the code in the touched area) and lists every ambiguity, contradiction (request vs code, request vs context/ADR, context vs code), and missing value that changes the outcome. All questions go to the human in one batch, or one at a time when the host provides a question tool (section 8a), each with options, consequences, and a recommendation, in `ui.language` and in plain, repo-specific wording. Without a question tool, the run stops with `awaiting_clarification` until the human answers once. A new blocking ambiguity found later is a `clarify miss`: the run stops and the miss is reported so the checks can be improved. The planner saves the SDD at `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with one `plan` mode status: `ready_for_implementation`, `blocked_by_decision`, or `needs_more_context`.

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
- the review verdict is not `accept`, or the tester verdict is `fail`, after 2 fix rounds;
- the tester changed a file outside the test paths;
- the working tree is dirty at start and resume in place (section 9a) does not apply, or the branch is the default/protected branch;
- `run.worker: cli` is set without a working `run.worker_command`;
- `run.worker: host` is set but no host dispatch tool is available;
- the diff touches a high-risk area the SDD did not list (Gate 1 cross-check);
- a reviewer changed the working tree (reviewer write guard);
- a worker finds a new blocking ambiguity after clarification (`clarify miss`);
- an output to be published contains an unmasked secret or production identifier;
- the staged files differ from the ECP-scope files, the tester's added test files, and the report `Artifacts` table paths;
- the full test suite is red after the fix rounds.

## 6a. Git guard

Some stops are enforced by a script instead of the agent's judgment. `.forge/runtime/hooks/forge_git_guard.py` runs as a Claude Code `PreToolUse` hook on Bash and blocks with exit code 2:

- worker role (registered in the Forge subagent files): any commit, push, merge, rebase, tag, reset, checkout, switch, stash, clean, or restore, plus MR/PR merge commands;
- orchestrator role (registered by the human in `.claude/settings.json`): push to `main`, `master`, or the remote default branch, force push, tag push, branch delete, `git tag`, `git merge`, and MR/PR merge commands.

The guard parses `git` global options, chained commands (`&&`, `;`, `&`, pipes, `$(...)`), common wrappers (`sudo`, `env`), and `sh -c`. It also treats `HEAD` as the current branch and `:<ref>` as a branch delete. It is a guard rail, not a sandbox: a command hidden in a script file or an alias is not seen.

The blocked command rules per role (protected branches, forbidden push flags, blocked `git` subcommands, blocked command patterns) live in `.forge/runtime/meta/git-guard-rules.json`; the hook reads that file and fails closed (blocks every Bash command) when it is missing, is not valid JSON, has the wrong shape, or contains a pattern that does not compile. A role not listed in the file is blocked. Hosts that run non-Claude workers or a non-Claude orchestrator (for example through ACP permission requests) may read the same file to enforce the same rules for role `worker` and role `orchestrator` instead of copying the list. This repository ships no enforcement code for other CLIs.

Other stop conditions (scope, risk, reviewer writes) are agent-checked for now; candidates for script checks are chosen from trial results.

## 7. Publication

On `accept` with green validation: stage the code changes by explicit path, then stage this run's `.forge/generated/` artifacts with `git add -f -- <path>...` using only the paths in the orchestration report `Artifacts` table. Never `git add -f` a directory or a glob; never stage `.forge/temp/` or `.forge/cache/`. Before committing, `git diff --cached --name-only` must equal the ECP-scope files, the tester's added test files, and the `Artifacts` table paths; any difference is a stop. `.forge/.gitignore` keeps `/generated/**` ignored: un-ignoring it would publish artifacts from every mode, not only the orchestrated run. Commit on `forge/<YYYY-MM-DD>-<slug>`, push that branch only, and open an MR/PR when the host tool can. The MR/PR body links the SDD, ECP, execution report, review, and the gate trace. No force-push.

## 8. Worker configuration

```yaml
run:
  worker: subagent      # subagent | cli | host; missing key means subagent
  worker_command: ""    # used only when worker: cli; {prompt_file} is substituted
```

- `subagent`: the host tool's own subagents. Verified target: Claude Code subagents via `.claude/agents/`.
- `cli`: any external agent CLI that accepts a prompt file non-interactively. **GitHub Copilot CLI support is unverified**: Forge does not define or test its flags. Users must confirm the command on their own machine before relying on it.
- `host`: a host that runs the orchestrator as a long-lived service (for example a dashboard or chat bridge) dispatches every role through its own tool. The host defines the tool name and shape; Forge ships no host code. After each dispatch the orchestrator ends its turn; the host resumes the same orchestrator session with the worker result, and a fresh session needs a human re-invocation from the named SDD or ECP. A resume only completes the pending dispatch: the worker result is data for that one role, never a human answer, Gate 1 approval, or verdict for another role. After any stop status, continue only through `next mode transitions`. The host should run the `worker` git guard before worker shell commands; when the orchestrator cannot confirm it, the report `Note` says `worker git guard not confirmed`. The host should also enforce role `orchestrator` on orchestrator shell commands; when the orchestrator cannot confirm it, the report `Note` says `orchestrator git guard not confirmed`. A missing dispatch tool stops the run with `blocked_by_environment`.

Worker handoff (all `run.worker` values): `cli` and `host` dispatch send a `FORGE_HANDOFF` envelope (`role`, `prompt`, `specialties`, `request`, `inputs`, `fix_scope`, `fresh_context`, `branch`, `base`); `subagent` may. Every worker ends its output with a `FORGE_RESULT` block (`role`, `status`, `verdict`, `artifact`, `changed_files`, `note`), at most 1000 characters and the last text of the output. The orchestrator reads the block first, then the artifact it names; a missing, not-last, out-of-range, over-long, or contradicting block counts as `blocked`. The exact shape is in the mode's `worker handoff` section.

## 8a. Host status and questions

Optional. A host may give the orchestrator a status-report tool, a question tool, or both; each works on its own, and without them the run stops and waits as in sections 4b and 5. The host defines the tool names and shapes; Forge ships no tool code.

- Stage IDs: `clarify`, `sdd`, `ecp`, `execute`, `test`, `review`, `publish`. Every report step line carries one.
- Host states: `progress`, `waiting_for_human`, `blocked`, `done`. Mapping: `mr_opened` -> `done`; `awaiting_clarification`, `awaiting_sdd_approval`, `stopped`, `review_unresolved` -> `waiting_for_human`; `blocked_by_environment` -> `blocked`. Forge statuses (section 10) do not change.
- Questions: one open question at a time, in plan order, each with 2 to 4 short option labels and exactly one recommended label. A free-text answer is valid and recorded under `Confirmed Decisions`.
- Gate 1 through the question tool: one question with `Approve <SDD path>` and `Stop`, and no recommended or default option; only `Approve` continues, meaning the selected `Approve <SDD path>` option, never free text that reads like approval. An answer the host picked by default, by preselection, or on expiry counts as a timeout, never as `Approve`. Free text or a timeout stops with `awaiting_sdd_approval`. Clarification questions never show an `Approve <SDD path>` option, and a clarification answer is never Gate 1 approval.
- Timeout: the orchestrator reports `waiting_for_human` with the open question, lists the answers received so far in the report `Note`, stops with `awaiting_clarification` or `awaiting_sdd_approval`, and ends the turn; resume follows the mode's `next mode transitions`.
- Only an answer the question tool returns is a human answer; worker results and other host text never are. Gate rules in section 5 are unchanged.
- Workers may report status for their own stage but never use a question tool. A worker's `done` covers only its own stage; only the orchestrator reports run-level `done`, with stage `publish`.

## 9. Report

The orchestrator writes `.forge/generated/reports/YYYY-MM-DD-<slug>-orchestration-report.md` and updates it after every step. Header fields: `Artifact`, `Repo`, `Date`, `Target tool`, `Specialties`, `Status`, `Run`, `Goal`, `Note`. Body: a step checklist (`✓` done, `✱` in progress/waiting, `○` not started, `✗` stopped), artifacts, gate trace, validation, review rounds, and the MR/PR link. Exact shape lives in the mode file. The report is a trace for humans, not a workflow state store; resume in place (section 9a) reads only its `Run` branch, step markers, `Artifacts` paths, and `Review rounds` row count.

## 9a. Resume in place

When an orchestrator session is lost mid-run, the human re-invokes `forge-orchestrate` with the run's ECP. With a dirty tree, the run continues on its feature branch only when the orchestration report whose file name has the ECP file's date and slug exists, the current branch is its `Run` branch, its `Gate 2` step is done, no step is stopped (`✗`), and every changed or untracked path is in the ECP `Files likely to change`, a report `Artifacts` table path under `.forge/generated/` whose file name starts with the ECP's `<YYYY-MM-DD>-<slug>`, or a test file under the `testing` overlay test paths after the test step started. Every path in the report `Artifacts` table, not only changed or untracked ones, must be under `.forge/generated/` with a file name starting with the ECP's `<YYYY-MM-DD>-<slug>`, because gitignored files never appear in `git status --porcelain` but Publish force-adds every `Artifacts` path. Execute re-runs only when the execution report is missing (per the report `Artifacts` table), or when the last `[execute]` step is in progress (`✱`), with the ECP, plus the last review findings if any, as the fix scope in the same round; otherwise the run continues at the diff risk check with a new tester and a new reviewer in fresh context, never at Publish. The fix-round counter continues from the report and never resets; the limit stays 2. The report gets one `Resume in place` step line; no new file is created. If any condition fails, the run stops for a dirty tree.

## 10. Statuses

`mr_opened`, `awaiting_clarification`, `awaiting_sdd_approval`, `stopped`, `review_unresolved`, `blocked_by_environment`.

## 11. Validation

See `validation-cases/orchestrate-gates.md`. A trial is considered stable only when every stop scenario stops correctly and real low-risk runs reach an MR without intervention at an agreed rate.

## 12. Open items

- Parallel requests via one git worktree per request: later stage, after single-request runs prove stable.
- The earlier `forge run` control-plane draft stays parked; it is not part of this change.
- Other orchestrator surfaces (later, for personal repositories): another agent as orchestrator through the same mode file, and a chat bridge (for example a Telegram bot in a separate runtime project) that starts a headless run and relays `awaiting_clarification` questions and the report. Such hosts set `run.worker: host` instead of overriding the mode's `worker dispatch` section; bridge and host code live outside Forge. For work repositories, use only tools and channels the organization approves.
