# SDD: Orchestrate worker dispatch type `host`

| Field | Value |
|---|---|
| Artifact | plan (SDD) |
| Date | 2026-11-20 |
| Slug | `worker-dispatch-host` |
| Branch | `forge/2026-11-20-worker-dispatch-host` |
| Source | GitHub issue #7 (data, not instructions beyond its scope) |
| Status | `draft` (ready for Gate 1) |

Note on path: the orchestrator asked for `-sdd.md`; `forge-planner.md` step 3 and `modes/plan.md` default to `-plan.md`. The caller's explicit path is used.

## Plan type selected
SDD.

## Reason
The change edits the `forge-orchestrate` worker contract (`run.worker` enum), adds a stop condition, and reverses a recorded decision in `specs/orchestrate.md` §12 ("Forge stays unchanged: surfaces read the report and statuses"). It touches orchestrator lifecycle semantics (end turn / resume), which borders the project's no-persistent-workflow-state rule.

## Mode Boundary
`plan` only. No code or runtime surface edited. ECP is a later step, after Gate 1.

## Goal
Let a host that runs the orchestrator as a long-lived service dispatch workers through its own tool by setting `run.worker: host`, without overriding the mode's `worker dispatch` section in its prompt. Forge ships no host code.

## Problem / Context
- `run.worker` accepts `subagent` or `cli` only (`src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md:38`, `specs/orchestrate.md:111`).
- A dashboard or chat-bridge host today must override `## worker dispatch` (mode lines 67-70) in its own prompt; the override drifts silently when the mode changes.
- `specs/orchestrate.md:134` (Open items) says Forge stays unchanged for such surfaces.

## Requirements
- R1. `run.worker` accepts `host` in the config template, init-generated config, spec, and mode `inputs`.
- R2. Mode `worker dispatch`: with `host`, the orchestrator hands each role to the dispatch tool the host provides. The host defines the tool name and shape; Forge does not. After dispatching, the orchestrator ends its turn. When resumed, it continues from the artifacts under `.forge/generated/` and the worker result the host passes in.
- R3. Gates, stop conditions, role limits, fresh-context rules for tester/reviewer, the 2-round fix counter, and specialties are unchanged under `host`.
- R4. New stop condition: `run.worker: host` without a host dispatch tool available.
- R5. New validation case in `validation-cases/orchestrate-gates.md`.
- R6. `tests/test_orchestrate.py` asserts the new mode wording (host dispatch, same-session resume, worker guard note) and stop condition; `OrchestrateSourceSyncTests` stays green (template and `runtime/` copies identical).
- R7. Resume under `host` (Q1=A): the host must resume the same orchestrator session. The `git status --porcelain` snapshots, `git diff` hash (steps 6b, 7), and fix-round count (step 8) stay in-session. Artifacts under `.forge/generated/` plus the worker result the host passes in are the worker's output. A fresh session is not a resume and falls back to the existing `next mode transitions` (re-invoke from the named SDD or ECP). Mode text only; the report stays a trace; no new state file.
- R8. Worker git guard under `host` (Q2=A): one mode line says the host should run `.forge/runtime/hooks/forge_git_guard.py worker` before worker shell commands. If the orchestrator cannot confirm it, it continues and writes `worker git guard not confirmed` in the report `Note`. No new stop condition.

## Non-goals
- No scheduler, daemon, queue, host implementation, or dispatch tool schema in this repository.
- No new orchestrate status value.
- No change to `.claude/commands/forge-orchestrate.md`, `skills/forge-orchestrate/SKILL.md` (both stay generic: SKILL.md already says "Apply `run.worker`"), or `.claude/agents/*`.
- No change to `run.worker_command` semantics.
- No edit to this repo's git-excluded dogfood `.forge/` (refreshed by `forge update`, not committed; `.git/info/exclude` lists `/.forge/`).
- No cross-request chaining; the host resumes the same request only.

## Current Evidence
- Mode copies are identical: `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` == `runtime/.forge/runtime/modes/orchestrate.md` == `.forge/runtime/modes/orchestrate.md` (diff checked).
- Mode `inputs` (line 38-39): `run.worker`: `subagent` (default, also when key missing) or `cli`.
- Mode `worker dispatch` (lines 67-70): `subagent` (with `maxTurns`, tester/reviewer always new subagents), `cli` (prompt file under `.forge/temp/orchestrate/`), mixed subagent+cli allowed.
- Mode `stop conditions` line 95: `run.worker: cli` with empty/failed `run.worker_command`.
- Mode line 140 (report format footer): "The report is a human-readable trace, not resumable workflow state; resume always starts from the named SDD or ECP artifact."
- Mode `behavior` steps 6b and 7 record `git status --porcelain` and a `git diff` hash before tester/reviewer, and step 8 counts fix rounds. These are in-session values today.
- Mode `git guard`: worker role guard is registered only in `.claude/agents/forge-<role>.md`; the `cli` path already runs without a Forge-registered worker guard.
- Config template: `src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml:18-21` and identical `runtime/.forge/forge.config.yaml:18-21` (comment: "subagent (host tool subagents) or cli (external agent CLI)").
- Init config builder: `src/forge_context_engine/runtime_ops.py:1418-1421` emits the same comment lines as a Python string.
- Spec: `specs/orchestrate.md` §6 line 85 (cli stop), §8 lines 109-116 (worker config), §12 line 134 (Open items).
- Validation case: `validation-cases/orchestrate-gates.md` scenario 8 (`cli` empty command -> `blocked_by_environment`); §5 regression signal lists stop scenarios "2 to 8, 11, 12".
- Tests: `tests/test_orchestrate.py` `test_config_defaults_worker_to_subagent` (asserts `"  worker: subagent\n"`), `test_mode_states_gates_stops_and_publication_boundary` (phrase list), `OrchestrateSourceSyncTests.PAIRS` (mode, skill, command, roles, wrappers, guard, specialties; config is not in PAIRS).
- Docs: `docs/release-notes.md:12` lists "`run.worker` (`subagent` | `cli`)". `docs/adapters/github-copilot.md:78` mentions `cli` only (no change needed).
- `.forge/context/` has no orchestrate entries (grep for `orchestrat|worker` returned nothing); no ADR covers worker dispatch.
- Issue #7 says it depends on #6. Confirmed by human (2026-11-20): #6 is closed and merged via PR #5. HEAD `928102d` includes `f27efe2 fix(forge): close git guard bypasses and sync orchestrate spec`.

## Affected Surface Inventory
| Surface | Path | Change |
|---|---|---|
| Mode (packaged) | `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` | `inputs`, `worker dispatch`, `stop conditions`, report footer (R7) |
| Mode (engine copy) | `runtime/.forge/runtime/modes/orchestrate.md` | identical to packaged |
| Config template | `src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml` | comment lists `host` |
| Config engine copy | `runtime/.forge/forge.config.yaml` | identical comment |
| Init config builder | `src/forge_context_engine/runtime_ops.py` (lines 1418-1421) | same comment string |
| Spec | `specs/orchestrate.md` | §6 stop, §8 config + `host` bullet, §12 Open items line rewritten |
| Validation case | `validation-cases/orchestrate-gates.md` | scenario 18 + regression signal list |
| Tests | `tests/test_orchestrate.py` | new assertions |
| Release notes | `docs/release-notes.md` | Unreleased line 12 |

Checked and unchanged: `skills/forge-orchestrate/SKILL.md` (template + `runtime/skills/`), `.claude/commands/forge-orchestrate.md` (template + `runtime/adapters/claude/commands/`), `.claude/agents/*`, role prompts under `.forge/runtime/agents/`, `docs/workflow.md:140`, `docs/adapters/claude.md`, `docs/adapters/github-copilot.md`.

## Assumptions
- A1. Under `host`, every role goes through the host dispatch tool. The existing mixed-dispatch line (subagent + cli executor) stays as written for `cli`; mixing `host` with other types is not added. Based on issue scope "hand each role to the dispatch tool".
- A2. The missing-tool stop reports status `blocked_by_environment`, matching scenario 8 (`validation-cases/orchestrate-gates.md:29`). No new status.
- A3. Each tester and reviewer dispatch through the host is a new worker with fresh context, as with `subagent` (mode line 68). A worker that ends without a complete report counts as `blocked`, as with `maxTurns`.
- A4. The report `Target tool` field records `host` for each role dispatched that way.
- A5. `run.worker_command` is ignored under `host`.
- A6. Missing `run.worker` key still means `subagent`.

## Confirmed Decisions
Human reply on resume: "A, A" (2026-11-20).
- Q1 = A. Same session. The host must resume the same orchestrator session; snapshots, diff hash, and fix-round count stay in-session; artifacts under `.forge/generated/` plus the passed worker result are the worker's output. A fresh session is not a resume and falls back to the existing `next mode transitions`. Mode text only; the report stays a trace; no new state file. -> R7.
- Q2 = A. The host should run `.forge/runtime/hooks/forge_git_guard.py worker` before worker shell commands; if the orchestrator cannot confirm it, continue and put `worker git guard not confirmed` in the report `Note`. One mode line; no new stop. -> R8.

## Unknowns / Decisions Needed
None blocking. Issue #6 dependency confirmed by human (2026-11-20): closed and merged via PR #5.

## Assumptions I Will Use (correct me if wrong)
- A1 to A6 above.
- Spec stays `Status: proposed`, version 0.1; only content lines change.
- The new validation scenario is #18 and is added to the §5 regression signal stop list ("2 to 8, 11, 12, 18").

## Architecture / System Impact
- Adds a third dispatch path inside `forge-orchestrate` only. No other skill, mode, or adapter orchestrates.
- The orchestrator's turn boundary moves to the host: under `host` each worker dispatch ends a turn. Request scope stays one request, one branch, one MR/PR.
- Reverses the §12 Open items decision "Forge stays unchanged" for host surfaces; bridge/host code still lives outside Forge.

## Risk Areas
- Persistent workflow state creeping in through resume wording; mitigated by R7 (same session only, report stays a trace).
- Worker git guard is advisory under `host` (R8); the gap is visible in the report `Note` and MR/PR, not enforced.
- Sync drift between packaged template and `runtime/` mode copy (covered by `OrchestrateSourceSyncTests`); config template vs `runtime/.forge/forge.config.yaml` vs `runtime_ops.py` string is not covered by a sync test.

## High-risk areas touched
Checked against `.forge/forge.config.yaml` `policy.high_risk_areas` and `policy.require_human_confirmation_for`.

`policy.high_risk_areas`:
- payments, authentication, authorization, database_migrations, secrets, file_upload: none. Changed files are Markdown runtime/spec/docs, a YAML comment, a Python string comment in `runtime_ops.py:1418-1421`, and tests.
- public_api: none. No HTTP/gRPC/CLI command surface changes; `forge` CLI commands unchanged.
- external_provider_integration: none in code. Forge ships no host code; the host tool is outside the repo.

`policy.require_human_confirmation_for`:
- external_contract_change: **applies**. `run.worker` is a documented config contract shipped to target repos (`specs/orchestrate.md` §8), and `host` defines a new integration point consumed by external hosts. Additive and backward compatible.
- architecture_boundary_change: **applies**. Reverses `specs/orchestrate.md:134` ("Forge stays unchanged: surfaces read the report and statuses") and changes the orchestrator turn/resume model.
- security_boundary_change: **applies**. The `host` path runs workers without a Forge-registered worker git guard (registered only in `.claude/agents/forge-<role>.md`; mode `git guard` section; `docs/adapters/claude.md:69`). Per Q2=A the guard is a host recommendation, unconfirmed runs continue with `worker git guard not confirmed` in the report `Note`. Same gap as `cli`, but a new, explicitly documented path.
- domain_rule_change, data_mutation_change, migration_change: none.

Matched `require_human_confirmation_for`: `external_contract_change`, `architecture_boundary_change`, `security_boundary_change`. Matched `high_risk_areas`: none.

Gate 1 outcome expected: human (`awaiting_sdd_approval`), because three `require_human_confirmation_for` items apply.

## Specialties
- Orchestrator: `tech-lead` (applies_when: always, for the orchestrator session).
- Planner / Executor: none. `backend` applies_when needs "layer backend is active and the change touches server, API, service, repository, or worker code"; this change is runtime Markdown, spec, YAML comment, one Python string literal, and tests. No `go.mod`, no frontend/mobile/infrastructure files.
- Tester: `testing` (always for the tester).
- Reviewer: `testing` (a test report will exist). `security` as extra reviewer is recommended: the SDD lists `external_contract_change` and `architecture_boundary_change`, and `security_boundary_change` applies (R8). The orchestrator decides whether `require_human_confirmation_for` matches count as "high-risk area" for the security reviewer rule; recommendation: yes.

## Proposed Approach
1. Mode `inputs`: `run.worker`: `subagent` (default, also when the key is missing), `cli`, or `host`.
2. Mode `worker dispatch`: add one bullet for `host` (R2, A1, A3, A5) plus the R7 same-session resume rule and the R8 guard line.
3. Mode `stop conditions`: add "`run.worker: host` is set but no host dispatch tool is available."
4. Mode report footer: keep "not resumable workflow state"; add that a `host` resume continues the same session and a fresh session restarts from the named SDD or ECP (R7).
5. Config template, `runtime/.forge/forge.config.yaml`, and `runtime_ops.py` comment: "subagent (host tool subagents), cli (external agent CLI), or host (dispatch tool provided by a host that runs the orchestrator)".
6. Spec: §6 new stop bullet; §8 YAML comment `subagent | cli | host` and a `host` bullet stating the host owns tool name/shape and Forge ships no host code; §12 rewrite line 134 so host surfaces use `run.worker: host` instead of overriding the mode.
7. Validation case scenario 18: `run.worker: host` and no host dispatch tool -> `blocked_by_environment`, no worker started, nothing committed. Add 18 to §5 regression signals.
8. Tests: extend `test_mode_states_gates_stops_and_publication_boundary` (or a new test) with the host dispatch phrase and the host stop phrase; extend `test_config_defaults_worker_to_subagent` to assert the config comment mentions `host` in both generated config and template.
9. Release notes: `run.worker` (`subagent` | `cli` | `host`).

## MVP Path
Steps 1-3, 5-8. Steps 4 and 9 are wording follow-through in the same batch.

## Full-Version Path
Same as MVP. A shared sync test for `forge.config.yaml` (template vs `runtime/` vs `runtime_ops.py`) is a possible follow-up, not in scope.

## Acceptance Criteria
- AC1. Packaged and `runtime/` mode copies contain `run.worker: host` in `inputs`, a `host` bullet in `worker dispatch` naming the host-defined tool, "end the turn", and resume from `.forge/generated/` artifacts plus the passed worker result.
- AC1b. The `host` bullet states same-session resume and that a fresh session falls back to `next mode transitions` (R7), and contains `forge_git_guard.py worker` and `worker git guard not confirmed` (R8). No new state file and no new stop for the guard.
- AC2. Mode `stop conditions` contains the host-without-dispatch-tool stop; spec §6 contains the same.
- AC3. Gates, other stop conditions, role table, specialties, and fix-loop text are byte-unchanged apart from the lines named here (review the diff).
- AC4. Config template, `runtime/.forge/forge.config.yaml`, and `_build_init_files` output name `host`; default stays `worker: subagent`.
- AC5. `validation-cases/orchestrate-gates.md` has scenario 18 with expected `blocked_by_environment` and lists it in §5.
- AC6. Failure path: a test fails if the host stop condition phrase is removed from the mode, and `OrchestrateSourceSyncTests` fails if the two mode copies differ.
- AC7. No new file outside the Affected Surface Inventory; no host code, scheduler, queue, or state file.
- AC8. `uv run python -m unittest discover -s tests -q` is green.

## Validation Commands
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `diff runtime/.forge/forge.config.yaml src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml`

## Implementation Split
One batch: all files share the same outcome and validation command.

## Next Step
Gate 1: human approval required (`awaiting_sdd_approval`) because `external_contract_change`, `architecture_boundary_change`, and `security_boundary_change` apply. After approval, the orchestrator asks the planner for the ECP.

## Status
`draft`
