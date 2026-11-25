# Test report: Worker handoff envelope and result block

| Field | Value |
|---|---|
| Artifact | test-report |
| Date | 2026-11-25 |
| Slug | `worker-result-block` |
| SDD | `.forge/generated/plans/2026-11-24-worker-result-block-plan.md` (issue #13) |
| ECP | `.forge/generated/ecp/2026-11-24-worker-result-block-ecp.md` |
| Diff | `git diff HEAD` (HEAD holds the stacked #12, #14, #8 changes) |
| Verdict | `pass` |

## Entry points
No code entry point changes (SDD non-goal: no parser, transport, or Python runtime code). The changed surfaces are text contracts in shipped templates:
- `modes/orchestrate.md` `## worker handoff`, `cli` / `host` dispatch bullets (runtime + template copy).
- `agents/forge-{planner,executor,tester,reviewer}.md` `## Return to orchestrator` (runtime + template copy).
- `specs/orchestrate.md` section 8.

Because there is no parser, the failure-path scenarios use a small test-side reader (`_read_result` in the new test file). It is built only from the rules the mode states, and it takes its allowed `role` / `status` / `verdict` values from the mode's own `FORGE_RESULT` block. So these tests check that the contract can be read by a machine and fails closed. They do not test a shipped implementation.

## Scenario matrix
| # | Category | Scenario | AC | Test | Result |
|---|---|---|---|---|---|
| 1 | Happy path | Mode has `## worker handoff` with the 9 envelope fields and the 6 result fields, between dispatch and host-status sections | 1 | `test_orchestrate.py::test_mode_defines_handoff_envelope_and_result_block` (executor) | pass |
| 2 | Contract | Runtime and template copies are byte-identical (mode + 4 agents) | 1, 6 | `OrchestrateSourceSyncTests.test_runtime_copies_match_templates` + `diff` commands | pass |
| 3 | Contract | Every worker prompt ends `## Return to orchestrator` with the block, six fields in order, its own `role:` | 2 | `test_orchestrate.py::test_worker_prompts_end_with_result_block` (executor) | pass |
| 4 | Contract | Each role lists exactly its A1 `status` / `verdict` values | 2 | `test_each_role_lists_exactly_its_a1_status_and_verdict_values` (new) | pass |
| 5 | Contract / drift | Each role's values stay within the mode's allowed values; the mode's `role` set = the 4 roles | 2 | `test_role_values_stay_within_mode_allowed_values` (new) | pass |
| 6 | Contract | Planner and reviewer `changed_files: 0` (A2); reviewer `artifact: none` | 2 | `test_planner_and_reviewer_report_zero_changed_files` (new), executor test | pass |
| 7 | Contract | Planner, executor, and tester artifacts point under `.forge/generated/` | 2 | `test_non_reviewer_artifacts_point_under_forge_generated` (new) | pass |
| 8 | Fail-closed mapping | Each prompt states its fail-closed mapping (planner `needs_*` -> `blocked`; executor non-`success` -> `blocked`; tester e2e note; reviewer `blocked`/`n/a`) | 2 (A1) | `test_fail_closed_mappings_are_stated_per_role` (new) | pass |
| 9 | Contract | Mode states: block first, then artifact; not-last, over-1000, contradicting = `blocked` | 3 | executor test phrases | pass |
| 10 | Input validation | Mode also names "A missing block" and "a value outside the listed ones" | 3 | `test_mode_names_missing_block_and_out_of_range_value_as_blocked` (new) | pass |
| 11 | Regression | `## status values` is exactly the 6 existing values; `## stop conditions` still has 14 bullets (same as HEAD) | 4 | `test_status_values_and_stop_conditions_are_unchanged` (new) | pass |
| 12 | Regression | `tests/test_orchestrate_host_dispatch.py` passes unchanged | 4 | existing suite | pass |
| 13 | Contract | Spec section 8 names both markers and the `blocked` rule; `host` bullet unchanged | 5 | executor test + host_dispatch verbatim asserts | pass |
| 14 | Happy path | A valid block as the last text is read (`done` / `pass`) | 3 | `test_valid_result_is_read` (new) | pass |
| 15 | Input validation | Missing block -> `blocked` | 3 | `test_missing_block_counts_as_blocked` (new) | pass |
| 16 | Input validation | Text after the block -> `blocked` | 3 | `test_block_not_last_text_counts_as_blocked` (new) | pass |
| 17 | Boundaries | Block over 1000 characters -> `blocked` | 3 | `test_block_over_1000_characters_counts_as_blocked` (new) | pass |
| 18 | Input validation | Unknown status (`success`, the executor's own mode status) -> `blocked` | 3 (A1) | `test_unknown_status_counts_as_blocked` (new) | pass |
| 19 | Input validation | Unknown verdict or role -> `blocked` | 3 | `test_unknown_verdict_or_role_counts_as_blocked` (new) | pass |
| 20 | Input validation | Missing or reordered field -> `blocked` | 3 | `test_missing_or_reordered_field_counts_as_blocked` (new) | pass |
| 21 | Input validation | Non-numeric `changed_files` -> `blocked` | 3 | `test_non_numeric_changed_files_counts_as_blocked` (new) | pass |
| 22 | Duplicates | Two blocks: only the last one is read (A3) | 3 | `test_duplicate_block_reads_only_the_last` (new) | pass |
| 23 | Security (spoof) | A quoted block followed by trailing text -> `blocked` | 3 (A3) | `test_spoofed_block_before_trailing_text_counts_as_blocked` (new) | pass |
| 24 | Full suite | Full suite green | 7 | `uv run python -m unittest discover -s tests -q` | pass |
| - | Contradicting artifact | Block vs artifact disagreement -> `blocked` | 3 | phrase only (row 9); needs a parser and artifact reader, which are an SDD non-goal | n/a |
| - | Auth / permission | n/a: no auth surface | - | - | n/a |
| - | Dependency failure | n/a: no runtime dependency; text contract only | - | - | n/a |
| - | Concurrency | n/a: no shared state | - | - | n/a |
| - | e2e | `no e2e harness` in this repo; integration-level unittest only | - | - | n/a |

## Commands
- `uv run python -m unittest tests.test_worker_result_block -v` -> `Ran 17 tests ... OK`.
- `uv run python -m unittest tests.test_orchestrate_host_dispatch tests.test_orchestrate -q` -> `Ran 56 tests ... OK`.
- `diff` of the mode and the 4 agent prompts, runtime vs template -> identical.
- `uv run python -m unittest discover -s tests -q` -> `Ran 197 tests in 8.382s, OK`.
- Security / static scan: the repo has no security or static scan command (no Makefile target, no CI workflow, no linter config to invoke). Not run.

## Failures
None. No acceptance criterion fails.

## Findings (non-blocking)
- Low: the mode's "a value outside the listed ones" lists the union of all roles' values, so it does not say whether a role-specific value is out of range (for example reviewer `verdict: pass`). The per-role sets exist only in the prompts. If role-level checks are intended, the mode could say "the values listed for that role". The test-side reader uses the mode-level sets.
- Info: the "contradicts its artifact" rule cannot be tested without a parser, which is an SDD non-goal. It is covered by a phrase test only.

## Files added or changed
- Added `tests/test_worker_result_block.py` (17 tests).
- Added this report.
