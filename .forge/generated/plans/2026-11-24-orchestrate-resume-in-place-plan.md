# SDD: Orchestrate resume in place after a lost session (#16)

| Field | Value |
|---|---|
| Artifact | plan (SDD) |
| Date | 2026-11-24 |
| Request | GitHub issue #16 "Orchestrate: resume in place after a lost session" |
| Status | `ready_for_implementation` |

Plan type selected: SDD.
Reason: changes the shipped `orchestrate` mode contract (a packaged runtime template installed into target repos), relaxes an existing stop condition (dirty tree at start), and changes the stated role of the orchestration report. The change is all Markdown plus tests, but each of these is a contract or safety boundary.

## Confirmed Decisions
Human Gate 1, 2026-11-25:
- Gate 1: this SDD is approved by the human. An extra reviewer with the `security` specialty runs for this SDD, in addition to the normal reviewer; both must return `accept`.
- A1 confirmed by approval: after execute, resume always re-runs step 6a, a new tester, and a new reviewer before Publish.
- Q3 yes (shared with #12): test files the tester added under the `testing` overlay test paths may be staged at publish even when they are not in the ECP `Files likely to change`. Already in the step 9 preflight on this branch (`orchestrate.md:129`).
- Q4 yes: the resume scope check (R1b) uses the same rule as Q3. A changed or new path outside the ECP list that matches the `testing` overlay test paths is allowed. This replaces the strict reading of A2.
- Q5 B: host state for human waits is `waiting_for_human` (already in tree from #8, `orchestrate.md:110`). No change here.
- Q6 yes: single SDD file name `-plan.md`; handled in #18, not here.

## Re-anchoring (2026-11-25, ECP step)
The branch is stacked on #12, #14, #8, #13. Line references below are updated to the current tree:
- Step 1 preflight: `runtime/.forge/runtime/modes/orchestrate.md:118`. Host resume bullet: `:71`. Step 6b: `:126`. Step 9 staged-set preflight with tester-added test files: `:129`. Dirty-tree stop: `:138`. Report `Run` field: `:165`; `Steps`: `:169-179`; `Review rounds`: `:197-199`; footer: `:207`. `next mode transitions`: `:225-229`.
- #8 added stage IDs to step lines (`✓ [execute] Execute`), and fix rounds repeat the `[execute]`, `[test]`, `[review]` lines (`orchestrate.md:207`); there is no `Fix round` step name. A6 is resolved: R4 counts `[execute]` lines.
- Spec: dirty-tree stop `specs/orchestrate.md:84`; §9 report sentence `:139`.
- Validation cases: rows end at 22 (`validation-cases/orchestrate-gates.md:43`); new scenarios are 23 and 24 (A7). Regression sentence `:69` is asserted in two tests: `tests/test_orchestrate.py:513` and `tests/test_orchestrate_host_dispatch.py:184`.
- Tightening found while re-anchoring: a dirty tree appears only from execute onward, so R1c requires the `[ecp] Gate 2` step to be `✓` (instead of "at least one `✓` step"). This keeps resume from starting at Clarify or Gate 1 on a dirty tree. Stricter than the approved text; a failed check falls back to today's stop.
- Consequence of Q4 for step 9: test-path files accepted at resume were added by the lost session's tester, so the new session's step 6b snapshot does not see them as added. Resume records them, and step 9 counts them as tester-added test files.

## Mode Boundary
Plan mode only. No code, mode, spec, or test file is edited. Only this SDD is written under `.forge/generated/plans/`. No staging, commit, or push.

## Goal
When an orchestrator session ends mid-run, a human re-invocation of `forge-orchestrate` with the run's ECP path continues the run in place on its feature branch, instead of stopping for a dirty tree, when the tree, the branch, and the orchestration report prove where the run was. Every other case keeps the current dirty-tree stop.

## Problem / Context
- Step 1 preflight requires a clean tree (`runtime/.forge/runtime/modes/orchestrate.md:76`) and the stop list stops on a dirty tree at start (`orchestrate.md:96`, `specs/orchestrate.md:84`). After a lost session the tree holds the executor's uncommitted changes (stop conditions leave changes uncommitted, `orchestrate.md:91`), so re-invoking with the ECP stops, although the report already records progress.
- The only resume today is a `host` resume of the same session (`orchestrate.md:71`); a fresh session "needs a human re-invocation through `next mode transitions` from the named SDD or ECP". No transition covers a lost session with a dirty tree (also flagged as an open testing MINOR in `.forge/generated/reports/2026-11-20-worker-dispatch-host-orchestration-report.md`, Review rounds row 2: "lost host session not in next mode transitions").
- The report footer says the report is "not resumable workflow state" (`orchestrate.md:164`) and spec §9 says "not resumable state" (`specs/orchestrate.md:124`).

## Requirements
R1. Step 1 gains a `resume in place` path. It applies only when the invocation names an ECP and all of these hold:
  a. the current branch equals the branch in the orchestration report `Run` field;
  b. every path in `git status --porcelain` (changed and untracked) is in the ECP `Files likely to change`, is one of this run's artifacts (paths in the report `Artifacts` table), or (Q4) matches the test paths in the `testing` overlay while a `[test]` step is marked `✓` or `✱`; such test paths count as tester-added test files at step 9;
  c. the orchestration report `.forge/generated/reports/<YYYY-MM-DD>-<slug>-orchestration-report.md` (same date and slug as the ECP) exists, its `[ecp] Gate 2` step is `✓`, and no step is `✗`.
R2. If any condition fails, behavior is today's: stop for a dirty tree at start. No partial resume.
R3. Resume point: the step after the last `✓` step in `Steps`. Execute is re-run only when the execution report is missing. Once execute is done, resume always continues with the step 6a diff risk check, then a new tester (6b) and a new reviewer (7) in fresh context, never from Publish (step 9) directly.
R4. Fix-loop counter continues: fix rounds already used = the larger of (rows in `Review rounds` minus 1) and (number of `[execute]` step lines marked `✓` or `✱`, minus 1). It never resets on resume; the limit stays 2.
R5. Resume appends to the existing orchestration report (one step line `✓ Resume in place (from <step>; fix rounds used: <n>)`) and does not create a new report or any new file.
R6. `next mode transitions` gains one line for a lost session.
R7. The report stays a human-readable trace, not a workflow state store: resume reads only the `Run` branch, the `Steps` markers, the `Artifacts` paths, and the `Review rounds` row count.
R8. Validation cases: resume after execute; resume refused when a changed file is outside ECP scope.
R9. Mode copies stay byte-identical (`tests/test_orchestrate.py` `OrchestrateSourceSyncTests`).

## Non-goals
- No persistence, state file, scheduler, or daemon (issue non-goal; spec §3).
- No resume from a plan/SDD path with a dirty tree; existing `awaiting_clarification` / `awaiting_sdd_approval` transitions are unchanged.
- No resume after a recorded stop (`✗` step): `stopped` / `review_unresolved` still go through `next mode transitions`.
- No change to `host` same-session resume (`orchestrate.md:71`), git guard rules, role prompts, step 9 publish/staging (issue #12), host status/question contract or stage IDs (#8), worker handoff envelope (#13), reviewer guard role (#15), SDD file naming (#18).
- No Python code change in `src/forge_context_engine/*.py`.

## Current Evidence
- Preflight clean-tree rule: `runtime/.forge/runtime/modes/orchestrate.md:76`.
- Dirty-tree stop: `orchestrate.md:96`; spec `specs/orchestrate.md:84`; validation case 7 `validation-cases/orchestrate-gates.md:28` ("Refuses to start").
- Same-session-only resume and "A fresh session is not a resume": `orchestrate.md:71`; spec host bullet `specs/orchestrate.md:120`.
- Session-held snapshots: porcelain snapshots and diff hash (steps 6b, 7) and fix-round count (step 8) "stay in that session" (`orchestrate.md:71`). A new session cannot prove the reviewed tree equals the current tree; this is why R3 re-runs test and review.
- Report fields used by resume: `Run` with branch (`orchestrate.md:122`), `Steps` markers (`orchestrate.md:126-136,164`), `Artifacts` table, `Review rounds` table (`orchestrate.md:154-156`). Real report uses lines `Fix round 1`, `Test round 2`, `Review round 2` (`.forge/generated/reports/2026-11-20-worker-dispatch-host-orchestration-report.md`, Steps).
- Artifact names share date and slug: `.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md`, `.forge/generated/reports/YYYY-MM-DD-<slug>-orchestration-report.md` (`forge-planner.md` step 6; `orchestrate.md:107`).
- `.forge/generated/**` is gitignored in target repos (`src/forge_context_engine/runtime_ops.py` `FORGE_LOCAL_GITIGNORE`; `.forge/.gitignore`), so artifacts normally do not appear in `git status --porcelain`; the artifacts clause in R1b covers repos that un-ignore them.
- Executor prompt has no clean-tree requirement (grep of `runtime/.forge/runtime/agents/forge-executor.md` for `clean|dirty|porcelain`: no match), so re-running execute on in-scope partial changes is allowed by the existing role.
- Test constraints on the mode text (`tests/test_orchestrate_host_dispatch.py`): must keep "not resumable workflow state", "except a `host` resume of the same orchestrator session", "fix-round count (step 8) stay in that session", "A fresh session is not a resume: it needs a human re-invocation through `next mode transitions` from the named SDD or ECP."; must not match `state file|\.forge/state|session\.json`; `status values` must not contain `host`; exactly one `run.worker: host` stop line. Validation-case test asserts the exact text "any stop scenario (2 to 8, 11, 12, 18)" (`test_ValidationCase18_ExpectsBlockedByEnvironment_AndIsInRegressionList`).
- Copies: `runtime/.forge/runtime/modes/orchestrate.md` and `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` are identical today (checked with `diff`).

## Affected Surface Inventory
- `runtime/.forge/runtime/modes/orchestrate.md`: step 1 (resume in place path), stop condition line 96 (exception wording), footer line 164 (add resume in place exception, keep tested phrases), report format Steps (optional `Resume in place` line), `next mode transitions` (one new line).
- `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`: identical copy.
- `specs/orchestrate.md`: §6 dirty-tree stop bullet (exception), §9 last sentence (report role), one short paragraph for resume in place (new subsection `9a. Resume in place` or appended to §9).
- `validation-cases/orchestrate-gates.md`: two new scenarios (resume after execute; resume refused for out-of-scope file); refused case added to the §5 regression list.
- `tests/test_orchestrate.py`: one contract test for the resume-in-place phrases across both mode copies and the spec; extend `test_mode_states_gates_stops_and_publication_boundary` only if simpler.
- `tests/test_orchestrate_host_dispatch.py`: update the exact regression-list string in `test_ValidationCase18_...` to the new list. The same string is also asserted in `tests/test_orchestrate.py:513` (from #8); update it there too.
- `docs/release-notes.md`: one `Added` line under `Unreleased`.
- Checked, no change: `runtime/skills/forge-orchestrate/SKILL.md` and `runtime/adapters/claude/commands/forge-orchestrate.md` (no clean-tree or resume text; grep `dirty|clean tree|resum`), role prompts in `runtime/.forge/runtime/agents/` (only planner "On resume with answers", unrelated), `.forge/adapter.md`, `README.md` / `docs/getting-started.md` (dirty-tree text is about `forge update`, not orchestrate).

## Assumptions
- A1 (re-run test and review). The issue line "test and review always run fresh" is read as: after execute is done, resume always re-runs 6a, test, and review, even when the report shows them `✓`. Reason: the step 7 diff hash and porcelain snapshots live only in the lost session (`orchestrate.md:71`), so a new session cannot prove the reviewed tree equals the current tree before Publish. The looser reading (resume at Publish when Review is `✓`) could publish unreviewed edits. Correct me at Gate 1 if the looser reading is intended.
- A2 (scope set). Superseded by Q4 (see `Confirmed Decisions`): R1b also allows paths that match the `testing` overlay test paths, only after a `[test]` step has started, matching the #12 step 9 rule.
- A3 (recorded stop). A report with any `✗` step is not resumable in place; it follows `next mode transitions`, matching "After any stop status, continue only through `next mode transitions`" (`orchestrate.md:71`).
- A4 (fix counter). Counter formula in R4 counts an in-progress (`✱`) fix round as used, so a crash during a fix round never gives an extra round.
- A5 (trigger). Resume in place is checked only when the invocation names an ECP path; free-text and plan-path invocations keep the clean-tree rule.
- A6 (step names). Resolved: #8 is in the stack; resume keys on the stage-ID step lines (`[ecp] Gate 2`, `[execute]`, `[test]`, `[review]`); fix rounds are repeated `[execute]` lines.
- A7 (validation case numbers). Scenarios 23 and 24 (rows end at 22 on this branch).

## Unknowns / Decisions Needed
- None blocking. A1 and A2 have code consequences; both pick the stricter reading, and a refused resume falls back to today's safe stop. Confirm at Gate 1.

## Architecture / System Impact
- Documentation-level contract change in the packaged `orchestrate` mode; target repos get it on `forge update`.
- The orchestration report becomes an input to one decision (resume point) while staying a trace; no new artifact type, status value, or file.
- The dirty-tree stop is narrowed by an exact allow rule; outside it, behavior is unchanged.

## Risk Areas
- Relaxed stop: a dirty tree no longer always stops. Mitigation: all three conditions, scope set is exact paths, `✗` reports excluded, and test + review always re-run before Publish (A1).
- Report tampering or stale report: a hand-edited report could pick a later resume point. Impact is bounded by A1 (execute report must exist; test and review always re-run; 6a re-checks high-risk areas).
- Partial executor changes: re-running execute on a half-applied ECP. All changed paths are inside ECP scope by R1b, and the executor prompt allows editing in-scope files.
- Merge conflicts with #12 and #8 on the same files (`orchestrate.md` copies, spec, validation cases). Edits here stay in step 1, stop line 96, footer 164, transitions, spec §6/§9; #12 edits step 9 and adds scenario 19.

## Proposed Approach
Mode (both copies), wording to this effect:

1. Step 1, after the existing sentence: "Resume in place: when the invocation names an ECP and the tree is dirty, continue the run only when all hold: the current branch is the `Run` branch in `.forge/generated/reports/<date>-<slug>-orchestration-report.md` (same date and slug as the ECP); every path in `git status --porcelain` is in the ECP `Files likely to change` or the report `Artifacts` table; the report has at least one `✓` step and no `✗` step. Resume at the step after the last `✓`. Re-run execute only when the execution report is missing; after execute, always run step 6a, a new tester, and a new reviewer in fresh context before Publish. Fix rounds used = the larger of (`Review rounds` rows minus 1) and (`Fix round` steps marked `✓` or `✱`); the counter never resets. Add `✓ Resume in place (from <step>; fix rounds used: <n>)` to the same report. If any condition fails, stop for a dirty tree."
2. Stop line 96: "The working tree was dirty at start and resume in place (step 1) does not apply, or the branch is the default/protected branch."
3. Footer 164: keep both tested phrases and add "or a resume in place (step 1), which reads only the `Run` branch, step markers, `Artifacts` paths, and `Review rounds` rows".
4. `next mode transitions`: "- Session lost mid-run (no status written, no `✗` step) -> human re-invokes `forge-orchestrate` with the ECP path; step 1 resumes in place or stops for a dirty tree."

Spec: §6 bullet "the working tree is dirty at start and resume in place does not apply, or ..."; §9 last sentence "The report is a trace for humans, not a workflow state store; resume in place (mode step 1) reads only its branch, step markers, artifact paths, and review-round count."; a short `9a. Resume in place` paragraph mirroring R1-R4.

Validation cases: "Session lost after Execute ✓; tree has only ECP-scope changes; re-invoked with ECP -> resumes: 6a, new tester, new reviewer; fix counter unchanged; report shows `Resume in place`" and "Session lost after Execute; tree has a file outside ECP `Files likely to change` -> stops for dirty tree; nothing committed". Add the refused case to §5 list.

Tests: one contract test asserting the resume phrases (conditions, "never resets", "new tester", "stops for a dirty tree") in both mode copies and the spec; update the regression-list string in `tests/test_orchestrate_host_dispatch.py`; existing tested phrases stay.

## MVP Path
All of the above; it is already the minimum (text + two validation scenarios + one test).

## Full-Version Path
Later, if trials show tampering or miscounts: a deterministic script check of the scope condition (like `forge_git_guard.py`). Not in this change.

## Acceptance Criteria
- AC1. Both mode copies contain the resume in place rule in step 1 with all three conditions, the resume point rule, execute-only-if-report-missing, always-fresh test and review after execute, and the never-reset counter.
- AC2. Failure path: the mode and spec state that any failed condition stops for a dirty tree; validation case "resume refused, file outside ECP scope" expects a stop with nothing committed and is in the §5 regression list.
- AC3. A report with a `✗` step is not resumable in place (mode text).
- AC4. The spec §6, §9, and resume paragraph match the mode; no "state file" wording; no new status value.
- AC5. All existing tests pass, including the host-dispatch phrase tests and `OrchestrateSourceSyncTests`; the new contract test passes.
- AC6. `diff` of the two mode copies is empty.
- AC7. Only files in the Affected Surface Inventory change.

## Validation Commands
- `uv run python -m unittest tests.test_orchestrate tests.test_orchestrate_host_dispatch -q`
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `git status --porcelain` (only Affected Surface Inventory files)

## Implementation Split
One batch: all files share one outcome and one validation run.

## High-risk areas touched
`policy.high_risk_areas`: none.
- `payments`, `authentication`, `authorization`, `database_migrations`, `external_provider_integration`, `file_upload`: no code in these areas exists or changes; only Markdown mode/spec/validation/release-notes text and two test files.
- `public_api`: `forge` CLI code (`src/forge_context_engine/*.py`) untouched; no CLI flag or HTTP API change.
- `secrets`: no secret handling; step 9 `Output redaction` check unchanged.

`policy.require_human_confirmation_for`:
- `external_contract_change`: **match**. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` is installed into target repos by `forge init` / `forge update`; step 1 and the stop list change how `forge-orchestrate` behaves on re-invocation, and `run.worker: host` integrations follow this text (`specs/orchestrate.md` §8).
- `security_boundary_change`: **match**. The dirty-tree-at-start stop (`orchestrate.md:96`, `specs/orchestrate.md:84`) is a safety stop that keeps unreviewed working-tree changes out of a run; this change narrows it. Mitigated by exact-path scope check, `✗` exclusion, and mandatory fresh test + review before Publish (A1).
- `architecture_boundary_change`: **match (likely)**. The report changes from "not resumable state" (`specs/orchestrate.md:124`, `orchestrate.md:164`) to an input for the resume point; spec §3 non-goal "Persistent agent memory" still holds (no new file), but the role of the artifact changes.
- `domain_rule_change`: no product domain logic.
- `data_mutation_change`: no data store or schema.
- `migration_change`: no migrations.

Gate 1 consequence: per mode step 3, this SDD goes to human approval (`awaiting_sdd_approval`). Per `## specialties`, the SDD lists no `policy.high_risk_areas` entry, so the extra `security` reviewer is not required by rule; recommended anyway because of `security_boundary_change` (the #7 run used one for the same reason).

## Specialties
- Orchestrator: `tech-lead` (always).
- Tester: `testing` (always).
- Planner / executor / reviewer: none matched. `backend`, `backend-go`, `frontend`, `mobile`, `infrastructure` `applies_when` target application/service code, UI, or infra; this change is Forge runtime Markdown plus Python `unittest` contract tests. Optional: `security` as extra reviewer (see above).

## Next Step
Human Gate 1 approval of this SDD by path, then `implementation` (ECP).

## Status
`ready_for_implementation`. Gate 1: human-approved 2026-11-25 (see `Confirmed Decisions`); extra `security` reviewer required.
