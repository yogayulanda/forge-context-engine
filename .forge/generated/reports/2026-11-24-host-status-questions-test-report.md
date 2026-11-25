# Test Report: Orchestrate optional host status and question contract

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| SDD | `.forge/generated/plans/2026-11-24-host-status-questions-plan.md` (issue #8; Confirmed Decision Q5 = B) |
| ECP | `.forge/generated/ecp/2026-11-24-host-status-questions-ecp.md` |
| Verdict | `pass` |
| e2e | `no e2e harness` (contract is Markdown text; phrase/structure tests run with the standard unittest command) |

## Entry points changed
- Mode `orchestrate.md` (runtime + template): `## host status and questions`, steps 2/2b/3, report `## Steps`, `## next mode transitions`.
- Worker prompts planner/executor/tester/reviewer (runtime + template): `## Host status`, planner question format and resume line.
- `specs/orchestrate.md` 4b, 8a; `validation-cases/orchestrate-gates.md` 20-22 and rejected behaviors; `docs/release-notes.md`.

## Scenario matrix
| # | Category | Scenario | AC | Test | Result |
|---|---|---|---|---|---|
| 1 | Happy path | Host section: 7 stage IDs, 4 host states, Q5=B mapping, one question at a time | 1 | `OrchestrateHostInteractionTests.test_mode_host_section_defines_stages_states_and_mapping` | pass |
| 2 | Regression | `## status values` byte-equal to 6 values; stop conditions have no question tool / `Gate 1 approval` | 2 | `test_mode_status_values_and_stop_conditions_unchanged`; `test_orchestrate_host_dispatch` | pass |
| 3 | Security (failure path) | Gate 1: only `Approve` continues; free text or timeout -> `awaiting_sdd_approval` | 3 | `test_steps_2_and_3_question_tool_path`; new `test_Spec8a_TimeoutAndFreeTextAtGate1_NeverApprove` | pass |
| 4 | Contract | Every report `## Steps` line has a stage ID | 4 | `test_report_steps_carry_stage_ids` | pass |
| 5 | Input validation | Planner: 2-4 options, label max 120 chars, exactly one recommended, free text valid; old phrases kept | 5 | `test_planner_question_shape_is_bounded`; `test_planner_clarifies_before_sdd_in_one_batch` | pass |
| 6 | Happy path | Four workers: `## Host status`, stage ID, never use question tool | 6 | `test_workers_report_status_and_never_ask` | pass |
| 7 | Contract | Workers return questions as `blocked_by_decision` (planner) / blocking unknown (others) | 6 | new `test_PlannerResume_AcceptsOneAtATimeAndFreeText` | pass |
| 8 | Regression | `## Return to orchestrator` unchanged vs HEAD in all four prompts | 6 | command check (below) | pass |
| 9 | Dependency failure (timeout) | Timeout stops with step status, lists received answers in `Note`, ends turn | 7 | new `test_Timeout_StopsWithStepStatus_AndEndsTurn_NeverContinues` | pass |
| 10 | Dependency failure (timeout) | Timeout/non-approve resume only via human re-invocation | 7 | new `test_Timeout_ResumesOnlyThroughHumanReinvocation` | pass |
| 11 | Security (failure path) | Worker result never a human answer / Gate 1 approval in either channel | 7 | new `test_WorkerResult_NeverCountsAsHumanAnswer_InBothChannels` | pass |
| 12 | Data state | Free-text clarification answer valid and recorded under `Confirmed Decisions` (step 2b, planner resume) | 5 | new `test_Step2b_FreeTextAnswer_RecordedUnderConfirmedDecisions`, `test_PlannerResume_AcceptsOneAtATimeAndFreeText` | pass |
| 13 | Failure paths in validation case | Scenarios 21, 22; rejected behaviors (one-at-a-time w/o tool, batch with tool, worker/free text/timeout as approval) | 7 | `test_spec_and_validation_cover_question_tool_path` | pass |
| 14 | Contract | Spec 4b/8a match mode; scenario 18 + regression sentence verbatim | 8 | `test_spec_and_validation_cover_question_tool_path`; `test_orchestrate_host_dispatch` | pass |
| 15 | Regression | Runtime/template copies byte-identical | 1, 9 | `OrchestrateSourceSyncTests` + `diff` | pass |
| - | Auth and permission | n/a: no auth code; approval channel covered in rows 3, 11 | - | - | - |
| - | Boundaries | n/a beyond 2-4 options / 120 chars (text contract, row 5) | - | - | - |
| - | Idempotency, concurrency | n/a: no runtime code or state; report stays a trace | - | - | - |

## Commands
- `uv run python -m unittest tests.test_orchestrate_host_questions -v` -> Ran 6 tests, OK.
- `uv run python -m unittest tests.test_orchestrate tests.test_orchestrate_host_dispatch -q` -> Ran 53 tests, OK.
- `uv run python -m unittest discover -s tests -q` -> Ran 170 tests, OK.
- `diff` runtime vs template mode and four agent prompts -> identical.
- `git show HEAD:<prompt>` vs working copy, `## Return to orchestrator` section, four prompts -> unchanged.

## Failures
None.

## Files added
- `tests/test_orchestrate_host_questions.py`

## Round 2

Fix round 1 re-test (security findings S1-S4, R2, R3). Verdict: `pass`. New tests in `tests/test_orchestrate_host_questions.py`; each asserts mode (runtime + template), spec 8a, or worker prompts (runtime + template) as relevant.

| # | Category | Scenario | Finding | Test | Result |
|---|---|---|---|---|---|
| 16 | Security (failure path) | Gate 1 question has no recommended/default option (mode + spec 8a) | S1 | `test_Gate1_HasNoRecommendedOrDefaultOption_InModeAndSpec` | pass |
| 17 | Security (failure path) | Default/preselected/expired answer counts as timeout, never `Approve` (spec 8a; mode already in `test_orchestrate.py`) | S1 | `test_Gate1_DefaultPreselectedOrExpiredAnswer_CountsAsTimeout_InSpec` | pass |
| 18 | Security (failure path) | `Approve` = selected `Approve <SDD path>` option, never approval-like free text (mode + spec) | S2 | `test_Gate1_ApproveMatchedBySelectedOption_NeverFreeText` | pass |
| 19 | Security (failure path) | Worker `done` covers only its stage; run `done` only from orchestrator with stage `publish` (4 prompts x 2 copies, mode, spec) | S3 | `test_WorkerDone_CoversOnlyOwnStage_RunDoneOnlyFromOrchestratorAtPublish` | pass |
| 20 | Security (failure path) | Clarification question never shows `Approve <SDD path>`; clarification answer never Gate 1 approval (mode + spec) | S4 | `test_ClarificationQuestion_NeverShowsApproveOption_NorCountsAsGate1` | pass |
| 21 | Dependency failure (timeout) | Spec 8a timeout lists answers so far in report `Note` | R2 | `test_Spec8a_Timeout_ListsAnswersSoFarInNote` | pass |
| 22 | Contract | Gate 1 non-approve/timeout puts answer or `timeout` in report `Note` | R3 | `test_Gate1_TimeoutOrOtherAnswer_RecordedInNote` | pass |

Commands:
- `uv run python -m unittest tests.test_orchestrate_host_questions -v` -> Ran 13 tests, OK.
- `uv run python -m unittest discover -s tests -q` -> Ran 177 tests, OK.
- Security/static scan: none; the repo has no security or static-analysis command.

Failures: none. Existing tests unchanged. Files changed: `tests/test_orchestrate_host_questions.py` (7 tests added).
