# Forge Autopilot Specification

| Field | Value |
|---|---|
| Document | Forge Autopilot Control Plane |
| Version | 0.1 |
| Date | 2026-10-29 |
| Status | `draft` |
| Scope | `forge run` command group, run state, deterministic gates, role-agent dispatch, pull/merge request output |
| Dependency | `docs/decisions/ADR-0001-autopilot-control-plane.md`, `specs/mode-invocation.md`, `specs/artifact-lifecycle.md`, `docs/workflow.md` |

---

## 0. Purpose

Autopilot takes one spec from a human and produces one reviewable pull/merge request (PR) per spec, or one per batch ECP for large specs, without a human writing prompts between stages.

It standardizes:
- who does what: human, orchestrator, role agents, Forge
- the `forge run` CLI contract the orchestrator calls
- run state and stage transitions
- deterministic gates that replace human Gate 1 and Gate 2 inside a run
- role-agent dispatch through configured command templates
- PR policy and the run report

This document does NOT:
- change mode files, mode statuses, or mode boundaries
- add schedulers, triggers, daemons, CI/CD, deploy, or auto-merge
- add persistent AI memory or cross-run learning
- make agent-declared risk the only safety signal

---

## 1. Roles

| Role | Who | Owns | Never does |
|---|---|---|---|
| Human | Maintainer | Writes or selects the spec; reviews the PR; decides merge | Approve stages inside a run |
| Orchestrator | Any LLM tool: Claude Code, Codex, Copilot, Hermes | Reads the spec, decides what to dispatch, writes stage prompts, reads reports, retries within limits | Edit files, commit, push, open PRs, or bypass a gate directly |
| Role agent | Configured per role: `planner`, `dev`, `reviewer`, `security`, `tester` | Does one stage's work under the matching Forge mode | Choose its own next stage |
| Forge | `forge run` CLI | Run state, gates, worktree and branch, dispatch, validation commands, PR, report | Make judgment calls the orchestrator or agents own |

A role may be set to `self`: the orchestrator does that stage in its own session and submits the artifact with `forge run submit`. This covers "Claude orchestrates and plans, Copilot implements".

---

## 2. Invocation

The human tells the orchestrator one thing, through its normal surface:

```text
/forge-autopilot specs/payments-retry.md
```

Free text works the same way: the human may write a normal request instead of a path, for example "fix the duplicate transfer on retry in transaction-history-service and open a PR".

### 2.1 Spec Resolution

Every run starts with a `spec` stage that turns the request into one checked spec:

1. **Find a spec.** If the request names a spec, or a matching plan artifact exists under `.forge/generated/plans/`, use it. A spec is a Forge plan artifact (`specs/artifact-lifecycle.md`); autopilot adds no new artifact location.
2. **No spec found.** The orchestrator writes one from the request and saves it as `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md`.
3. **Check the spec against the repository.** Verify that files, symbols, contracts, and behavior the spec relies on exist as described. List every ambiguity and every gap between spec and code.
4. **Resolve ambiguity with a recommendation.** For each ambiguity, pick the recommended option, record it in the spec under `## Decisions taken by autopilot` with the alternatives and the reason, and continue. Do not wait for the human.
5. **Stop only when no reasonable recommendation exists**: no target repository can be identified, the spec contradicts the code in a way that changes the goal, or the request conflicts with a hard block (section 6.1). The run ends `blocked` with the questions.

The spec stage reports `status: ready` or `status: blocked`. After G1, Forge commits the spec and the plan, including the decisions section, as one plan artifact at `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md`; it is the first commit of the run branch, so it ships in the PR. The PR body lists the decisions taken first, so the reviewer can reject an interpretation before reading the diff.

The `forge-autopilot` shared skill instructs the orchestrator to drive `forge run` commands until the run reaches `pr_open` for every batch or a terminal status. Adapter wrappers for Claude, Codex, and Copilot point to that skill. Hermes invokes the same CLI through its shell tool.

---

## 3. Spec Sources

| Source | Form | Accepted by |
|---|---|---|
| File | `md:<path>` | Human (they wrote it) |
| Free text | `text:<path>`, written by the orchestrator from the human's request as a plan artifact (2.1) | Human (their request); the interpreted spec is shown in the PR |
| PAOS backlog | `paos:<path>` inside a configured paos-context checkout, read-only | Human (they wrote it) |
| Self audit | `self:<kind>`, kind in `security`, `code-standards`, `test-gaps`, `ai-readiness` | Human: audit output is a candidate list in `.forge/runs/<run-id>/candidates.md`; the run stops at `awaiting_selection` |

One spec item shape for all sources:

```markdown
- [ ] Add idempotency key to transfer handler
  repo: transaction-history-service
  accept: retry with the same key creates no second record; unit tests pass
```

---

## 4. Run Lifecycle

```text
created -> spec_ready -> planned -> ecp_ready -> [per batch: executing -> reviewing -> security_review? -> testing -> validating -> pr_open] -> done
```

| Stage | Forge mode | Default role | Gate before next stage |
|---|---|---|---|
| spec | `plan` (spec check only) | `planner` | G0 |
| plan | `plan` | `planner` | G1 |
| ecp | `implementation` | `planner` | G2 |
| execute | `execute` | `dev` | G3 scope |
| review | `review` | `reviewer` | G4 review |
| security | `review` (security focus) | `security` | G4s security; runs only when the batch is high-risk (6.2) or `autopilot.security.always: true` |
| test | `execute` limited to test paths | `tester` | G5 tests |
| validate | none; Forge runs `tools.validation_commands` and `autopilot.e2e.command` | Forge | G6 validation |
| pr | none | Forge | none; human reviews |

Terminal statuses: `done`, `blocked`, `failed`, `cancelled`, `awaiting_selection`.

Batches run in ECP order. Batch N+1 branches from batch N's branch, so PRs stack. One spec with one batch gives one PR.

---

## 5. CLI Contract

All `forge run` subcommands accept `--json` and `--target <repo>` and return machine-readable output with `run_id`, `stage`, `status`, and `next`.

| Command | Effect |
|---|---|
| `forge run start <source>` | Create run, worktree, and branch; parse spec; return `run_id` |
| `forge run list` | All runs with stage, status, and PR links |
| `forge run status [<run-id>]` | Current stage, batch, gate results, allowed next commands |
| `forge run dispatch <run-id> --stage <stage> [--batch <id>] --prompt-file <path>` | Spawn the role agent configured for that stage with the orchestrator's prompt plus the Forge mode contract; capture output to the run directory |
| `forge run submit <run-id> --stage <stage> --file <path>` | Record an artifact produced by the orchestrator itself (`self` role) |
| `forge run gate <run-id> --stage <stage>` | Evaluate the gate; advance on pass; return reasons on fail |
| `forge run pr <run-id> --batch <id>` | Push the batch branch and open the PR; only allowed after G6 |
| `forge run report <run-id>` | Write the run report |
| `forge run stop <run-id>` | Cancel; keep worktree and state for inspection |
| `forge run resume <run-id>` | Continue from the last passed gate |

`dispatch` and `gate` refuse out-of-order stages. There is no command that advances a stage without its gate.

---

## 6. Gates

Gates are computed by Forge from artifacts, the diff, and config. Agent statements are inputs, not verdicts.

| Gate | Passes when | On fail |
|---|---|---|
| G0 spec | Spec file exists and is committed; every listed ambiguity has a recorded decision or the run is `blocked` | `blocked` with the open questions |
| G1 plan | Plan artifact exists; status `ready_for_implementation`; no open decision marked blocking | Orchestrator may revise up to `limits.plan_rounds`, then `blocked` |
| G2 ECP | Every batch ECP has status `ecp_ready`, allowed files, validation commands, stop conditions | Same as G1 |
| G3 scope | Diff touches only the batch's allowed files; no hard-blocked path (6.1); changed files and lines under limits | `blocked`; nothing is pushed |
| G4 review | Reviewer verdict has no blocking finding | Back to execute, up to `limits.review_rounds`, then `blocked` |
| G4s security | Security agent reports no blocking finding (auth/authz, input validation, injection, IDOR, SSRF, secrets, sensitive data exposure) | Back to execute; counts toward `limits.review_rounds`, then `blocked` |
| G5 tests | Tester changed only test paths (`autopilot.e2e.test_paths`); every new or changed endpoint has at least one e2e test | Back to test, up to `limits.test_rounds`, then `blocked` |
| G6 validation | Forge ran every validation command and the e2e suite; record each result | A failing e2e test caused by the change sends the batch back to execute once; after that, failures and unrun commands mark the PR `not_validated` |

### 6.1 Hard blocks

Regardless of plan or ECP, a diff that touches these stops the batch at G3:
- `.github/workflows/**`, `.gitlab-ci.yml`, and other CI definitions
- files matching `autopilot.hard_block_paths`
- secret-like files (`.env*`, `*.pem`, `*.key`) or added content matching secret patterns
- deletion of test files, unless the ECP lists them explicitly

### 6.2 Risk

`high_risk = any changed path matches high_risk_paths OR the spec, plan, or ECP declares risk: high`

The planner should declare `risk: high` whenever the work touches a category in `policy.high_risk_areas` or `policy.require_human_confirmation_for`.

High-risk batches still run to a PR. The PR gets the configured high-risk labels and a risk section in the body.

---

## 7. Configuration

Autopilot config lives in `.forge/autopilot.json` (JSON, so the stdlib CLI can read nested values). Every key is optional; missing keys use the defaults below, shown here as YAML for readability.

```yaml
  roles:
    planner: self
    dev: copilot
    reviewer: codex
    security: claude
    tester: claude
  worktree_root: ""           # default: ../.forge-worktrees/<repo-name>/
  validation_commands: []
  high_risk_paths: []         # globs; any match marks the batch high-risk
  agents:
    claude:  { command: ["claude", "-p", "@{prompt_file}"] }
    codex:   { command: ["codex", "exec", "--cd", "{workdir}", "@{prompt_file}"] }
    copilot: { command: ["copilot", "-p", "@{prompt_file}"] }
    hermes:  { command: ["hermes", "-z", "@{prompt_file}"] }
  limits:
    plan_rounds: 2
    review_rounds: 2
    test_rounds: 2
    stage_timeout_minutes: 30
    max_changed_files: 30
    max_changed_lines: 1500
  hard_block_paths: []
  security:
    always: false           # true: run the security stage on every batch
  e2e:
    command: ""             # e.g. make e2e; empty means e2e is not_run
    setup: ""               # e.g. docker compose up -d; runs before command
    test_paths: ["test/e2e/**"]
  vcs:
    provider: github        # github | gitlab | none (push and PR skipped; local testing)
    remote: origin
    base: main
    branch_prefix: forge/auto/
    draft: true
    high_risk_labels: [high-risk]
    not_validated_labels: [not-validated]
```

The agent command templates above are placeholders. Exact headless flags for each CLI must be verified against that tool's current documentation before they ship as defaults. `{prompt_file}`, `{workdir}`, and `{run_dir}` are the only substitutions.

A reviewer from a different service than `dev` is recommended, not required.

### 7.1 Security and Tester Roles

- `reviewer` always checks security at the level of the existing `review` mode. `security` is a second, focused review for high-risk batches, ideally on a different service than `dev`.
- `tester` writes e2e tests only; it never edits production code. For each batch it adds or updates e2e tests for every new or changed endpoint, then Forge runs the whole e2e suite, so all existing endpoints are regression-tested on every batch.
- Existing endpoints without e2e coverage are not backfilled inside a feature PR, to keep the PR reviewable. Backfill runs as its own spec (`self:test-gaps`, one PR per group of endpoints).
- e2e needs a running environment. If `autopilot.e2e.setup` or `command` is missing or fails to start, e2e is `not_run: environment`, never `passed`.

---

## 8. State and Artifacts

| Path | Content | Committed |
|---|---|---|
| `.forge/runs/<run-id>/state.json` | Stage, batch, gate results, agent invocations | No (gitignored) |
| `.forge/runs/<run-id>/<stage>/` | Prompts, agent stdout, artifacts | No |
| `.forge/runs/STOP` | Kill switch: every `forge run` command refuses while present | No |
| `.forge/generated/reports/YYYY-MM-DD-<slug>-autopilot-report.md` | Run report | Only if the human keeps it |

One active run per repository. Worktrees live outside the main checkout.

---

## 9. Pull/Merge Request

- One spec gives one PR; a spec split into N batch ECPs gives N stacked PRs.
- Opened as draft by default, through `gh` (GitHub) or `glab` (GitLab).
- The body is the batch section of the run report: goal, spec link, changed files, decisions taken, review rounds and findings, validation table, risk, and deviations.
- Forge never merges, approves, or enables auto-merge.

---

## 10. Validation Honesty

- Forge, not the agent, runs validation commands and records their exit codes.
- A command that could not run is `not_run: <reason>`, never `passed`.
- The report and PR state `not_validated` whenever any command failed or did not run.

---

## 10a. Run Presentation

Autopilot is terminal-first: the active orchestrator session is the place the human talks to, in the style of a coordinator with one thread per run. No separate UI, chat bot, or hub is required.

| Concept | Surface |
|---|---|
| Coordinator | The orchestrator session the human is chatting with (free text) |
| Thread | One run; `forge run list` shows all runs with stage and status |
| Checklist | `forge run status <run-id>` renders stages and batches as `done` / `in progress` / `not started` lines |
| Decisions | The spec's `Decisions taken by autopilot` section; `forge run status` lists them |
| Blocker | A run in `blocked` shows its open questions; the orchestrator asks the human in the session |
| Result | PR link per batch in `forge run status` and the run report |

The orchestrator reports to the human only on a PR opened, a blocked run, or a direct question. Remote or mobile access is used only for repositories reachable from a cloud session; repositories on internal networks run from a local terminal. Other surfaces (PR comments, Telegram, Teams) may render the same `state.json` later; they are optional and out of scope for v0.1.

---

## 11. Rollout

| Version | Adds |
|---|---|
| v0.1 | `md:` and `text:` sources, one batch, `self` and one external role agent, GitHub, G0 to G6, `tester` with e2e, `security` on high-risk, report |
| v0.2 | Multiple batches with stacked PRs, `reviewer` on a second service, GitLab |
| v0.3 | `paos:` and `self:` sources |

Each version ships with a validation case under `validation-cases/` and tests on a throwaway repository before any real repository.

---

## 12. Open Items

- Verify headless invocation and permission flags for `copilot`, `codex exec`, `claude -p`, and `hermes -z`.
- Decide whether `forge run` is also exposed as an MCP server so orchestrators call it as tools instead of shell commands.
- Decide where worktrees live by default.
