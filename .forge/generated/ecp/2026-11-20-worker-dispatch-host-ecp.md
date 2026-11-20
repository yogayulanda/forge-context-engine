# ECP: Orchestrate worker dispatch type `host`

| Field | Value |
|---|---|
| Artifact | ecp |
| Date | 2026-11-20 |
| Slug | `worker-dispatch-host` |
| Branch | `forge/2026-11-20-worker-dispatch-host` (base `928102d`) |
| Source SDD | `.forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md` (Gate 1: human-approved 2026-11-20, extra `security` reviewer) |
| Batch | single batch (1 of 1) |
| Status | `ecp_ready` |

## Goal
Let a host that runs the orchestrator as a long-lived service dispatch workers through its own tool by setting `run.worker: host`. Forge ships no host code.

## Approved scope
SDD R1-R8, A1-A6, Confirmed Decisions Q1=A (same-session resume), Q2=A (advisory worker git guard with report `Note`). Issue #6 dependency: confirmed by human (closed, merged via PR #5).

## Non-goals
- No scheduler, daemon, queue, host implementation, dispatch tool schema, or state file.
- No new orchestrate status value. No new stop for the guard.
- No change to `skills/forge-orchestrate/SKILL.md`, `.claude/commands/forge-orchestrate.md`, `.claude/agents/*`, role prompts, `docs/adapters/*`, `docs/workflow.md`, or the git-excluded dogfood `.forge/`.
- No change to `run.worker_command` semantics. No new config sync test (SDD Full-Version follow-up).
- No mixing of `host` with `subagent`/`cli` (A1).

## Mode Boundary
`implementation` only: this ECP edits nothing. `execute` applies it.

## Assumptions carried
A1-A6 from the SDD. Report `Target tool` records `host` per role via the existing `<worker>` placeholder (A4); no report-format edit.

## Files likely to change
Exact list; any other changed or new path is scope growth.
1. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
2. `runtime/.forge/runtime/modes/orchestrate.md`
3. `src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml`
4. `runtime/.forge/forge.config.yaml`
5. `src/forge_context_engine/runtime_ops.py`
6. `specs/orchestrate.md`
7. `validation-cases/orchestrate-gates.md`
8. `tests/test_orchestrate.py`
9. `docs/release-notes.md`

Plus this run's artifacts under `.forge/generated/` (plans, ecp, reports, reviews).

## Task sequence and per-file edits

### 1. Mode (packaged): `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
a. `## inputs`, line 38. Replace:
```
- `run.worker`: `subagent` (default, also when the key is missing) or `cli`.
```
with:
```
- `run.worker`: `subagent` (default, also when the key is missing), `cli`, or `host`.
```
b. `## worker dispatch`. Insert these three bullets after the `run.worker: cli` bullet (line 69) and before the existing mixed-dispatch bullet (line 70, unchanged):
```
- `run.worker: host`: hand every role to the dispatch tool the host provides. The host defines the tool name and shape; Forge does not. `run.worker_command` is ignored. The tester and reviewer are always new workers with fresh context; a worker that ends without a complete report counts as `blocked`. After each dispatch, end the turn.
- Resume under `host`: the host must resume the same orchestrator session. The `git status --porcelain` snapshots, the `git diff` hash (steps 6b, 7), and the fix-round count (step 8) stay in that session. The worker's output is its artifacts under `.forge/generated/` plus the worker result the host passes in. A fresh session is not a resume: it restarts through `next mode transitions` from the named SDD or ECP.
- Worker git guard under `host`: the host should run `.forge/runtime/hooks/forge_git_guard.py worker` before worker shell commands. If the orchestrator cannot confirm it, continue and put `worker git guard not confirmed` in the report `Note`.
```
c. `## stop conditions`. Insert directly after the `run.worker: cli` stop (line 95):
```
- `run.worker: host` is set but no host dispatch tool is available.
```
d. Report footer, line 160. Replace:
```
Step markers: `✓` done, `✱` in progress or waiting, `○` not started, `✗` stopped here. The report is a human-readable trace, not resumable workflow state; resume always starts from the named SDD or ECP artifact.
```
with:
```
Step markers: `✓` done, `✱` in progress or waiting, `○` not started, `✗` stopped here. The report is a human-readable trace, not resumable workflow state; resume starts from the named SDD or ECP artifact, except a `host` resume of the same orchestrator session (see `worker dispatch`).
```
e. Leave frontmatter (`updated: 2026-11-20` already), gates, roles, specialties, git guard section, behavior steps, status values, boundaries, and next mode transitions byte-unchanged (AC3).

### 2. Mode (engine copy): `runtime/.forge/runtime/modes/orchestrate.md`
Copy file 1 verbatim after editing (`cp`). Must be byte-identical (`OrchestrateSourceSyncTests`).

### 3. Config template: `src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml`
Line 18. Replace:
```
  # forge-orchestrate worker: subagent (host tool subagents) or cli (external agent CLI).
```
with:
```
  # forge-orchestrate worker: subagent (host tool subagents), cli (external agent CLI), or host (dispatch tool provided by a host that runs the orchestrator).
```
`worker: subagent` and the `worker_command` lines stay.

### 4. Config engine copy: `runtime/.forge/forge.config.yaml`
Same one-line replacement as file 3; file stays byte-identical to the template.

### 5. Init config builder: `src/forge_context_engine/runtime_ops.py` (line 1418, inside `_build_init_files`)
Replace:
```python
        "  # forge-orchestrate worker: subagent (host tool subagents) or cli (external agent CLI).\n"
```
with:
```python
        "  # forge-orchestrate worker: subagent (host tool subagents), cli (external agent CLI), or host (dispatch tool provided by a host that runs the orchestrator).\n"
```
String literal only; no logic change.

### 6. Spec: `specs/orchestrate.md` (status and version unchanged)
a. §6, after line 85 (`- \`run.worker: cli\` is set without a working \`run.worker_command\`;`), insert:
```
- `run.worker: host` is set but no host dispatch tool is available;
```
b. §8, line 111. Replace:
```
  worker: subagent      # subagent | cli; missing key means subagent
```
with:
```
  worker: subagent      # subagent | cli | host; missing key means subagent
```
c. §8, after the `cli` bullet (line 116), add:
```
- `host`: a host that runs the orchestrator as a long-lived service (for example a dashboard or chat bridge) dispatches every role through its own tool. The host defines the tool name and shape; Forge ships no host code. After each dispatch the orchestrator ends its turn; the host resumes the same orchestrator session with the worker result, and a fresh session restarts from the named SDD or ECP. The host should run the `worker` git guard before worker shell commands; when the orchestrator cannot confirm it, the report `Note` says `worker git guard not confirmed`. A missing dispatch tool stops the run with `blocked_by_environment`.
```
d. §12, line 134. Replace the sentence `Forge stays unchanged: surfaces read the report and statuses; bridge code lives outside Forge.` with:
```
Such hosts set `run.worker: host` instead of overriding the mode's `worker dispatch` section; bridge and host code live outside Forge.
```
Rest of the line unchanged.

### 7. Validation case: `validation-cases/orchestrate-gates.md`
a. §2 table, after row 17, add:
```
| 18 | `run.worker: host` and no host dispatch tool available | `blocked_by_environment`; no worker started; nothing committed |
```
b. §5, line 62: replace `(2 to 8, 11, 12)` with `(2 to 8, 11, 12, 18)`.

### 8. Tests: `tests/test_orchestrate.py`
a. `OrchestrateInstallTests.test_config_defaults_worker_to_subagent`: add
```python
        host = "or host (dispatch tool provided by a host that runs the orchestrator)"
        self.assertIn(host, config)
        self.assertIn(host, template)
```
(define `host` before first use; keep existing asserts.)
b. `OrchestrateContractTests`: add a new test
```python
    def test_mode_host_dispatch_resume_and_guard(self) -> None:
        dispatch = self.mode.split("## worker dispatch", 1)[1].split("\n## ", 1)[0]
        for phrase in (
            "`run.worker: host`",
            "dispatch tool the host provides",
            "end the turn",
            "same orchestrator session",
            "A fresh session is not a resume",
            "forge_git_guard.py worker",
            "worker git guard not confirmed",
        ):
            self.assertIn(phrase, dispatch)
        stops = self.mode.split("## stop conditions", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`run.worker: host` is set but no host dispatch tool is available", stops)
```
Exact test name and split helper are execute's choice; phrases are fixed. Removing the stop line must fail this test (AC6).

### 9. Release notes: `docs/release-notes.md` line 12
Replace:
```
- `run.worker` (`subagent` | `cli`) and `run.worker_command` config. Copilot CLI as a worker is unverified.
```
with:
```
- `run.worker` (`subagent` | `cli` | `host`) and `run.worker_command` config. Copilot CLI as a worker is unverified. `host` lets a host that runs the orchestrator dispatch workers through its own tool; Forge ships no host code.
```

## Coding rules
- Smallest edit per file; no reflow of untouched lines; keep existing Markdown style (one bullet per rule, backticked names).
- Edit the packaged mode first, then `cp` it to `runtime/`; same for the config template.
- Mode wording above is fixed (tests assert it). Execute may decide test method name and helper structure only.
- No new files except this run's `.forge/generated/` artifacts.

## Safety / security constraints
- `security_boundary_change` (Gate 1 cleared): the `host` worker guard is advisory only and must be stated as such; do not claim enforcement.
- Do not touch `.claude/agents/*`, `.claude/settings.json`, `forge_git_guard.py`, or the git-excluded dogfood `.forge/runtime/`.
- No secrets or production identifiers involved.

## Acceptance criteria
SDD AC1-AC8 unchanged. Failure path: AC6 (removing the host stop line fails the new test; mode copy drift fails `OrchestrateSourceSyncTests`).

## Validation commands
Verified in this repo on 2026-11-20 (no Makefile or CI config; pytest is not installed; tests are `unittest`):
- `uv run python -m unittest tests.test_orchestrate -q` (baseline: 23 tests OK)
- `uv run python -m unittest discover -s tests -q` (full suite; baseline: 121 tests OK)
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `diff runtime/.forge/forge.config.yaml src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml`
- `git status --porcelain` lists only the 9 files above.

## Stop conditions
- Any validation command red after 3 attempts on the same check.
- A changed or new path outside `Files likely to change`.
- The mode line numbers or existing wording above no longer match (evidence drift): stop with `needs_more_evidence`.
- Any need to touch skills, commands, agent wrappers, guard script, or add a state file.

## Expected execution report
`.forge/generated/reports/2026-11-20-worker-dispatch-host-execution-report.md`: files changed, per-file summary, validation command results, deviations (expected: none).

## Non-blocking details execute may decide
Test method name, local variable names, assert order.

## Risk notes
- Config comment exists in three places (template, `runtime/`, `runtime_ops.py`); only template and generated config are test-covered. Check `runtime/.forge/forge.config.yaml` with the diff command.
- R7 wording must not imply a persisted state file; the report footer keeps "not resumable workflow state".

## Blocking unknowns
None.

## High-risk check for Gate 2
No high-risk area beyond Gate 1. Files touched: Markdown mode/spec/docs/validation case, a YAML comment, one Python string literal, tests. `policy.high_risk_areas`: none. `require_human_confirmation_for`: `external_contract_change`, `architecture_boundary_change`, `security_boundary_change`, all listed in the SDD and cleared by the human at Gate 1. Nothing added.

## Target Tool Instructions
- Claude Code: normal file-edit workflow; `cp` for the `runtime/` copies.
- Codex: `apply_patch` for scoped edits.
- Do not widen scope. Do not commit or push; the orchestrator publishes.

## Status
`ecp_ready`
