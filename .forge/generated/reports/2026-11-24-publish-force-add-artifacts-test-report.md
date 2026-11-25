# Test Report: Orchestrate publish step force-adds this run's artifacts

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| SDD | `.forge/generated/plans/2026-11-24-publish-force-add-artifacts-plan.md` |
| ECP | `.forge/generated/ecp/2026-11-24-publish-force-add-artifacts-ecp.md` |
| Branch | `forge/2026-11-24-publish-force-add-artifacts` (uncommitted) |
| Verdict | `pass` |
| E2E | n/a: `no e2e harness` (Markdown contract engine; integration via stdlib `unittest`) |

## Entry points changed
1. Packaged mode text: `runtime/.forge/runtime/modes/orchestrate.md` and its template copy (step 9, stop list).
2. Spec: `specs/orchestrate.md` section 6 (stop list) and section 7 (Publication).
3. Validation case: `validation-cases/orchestrate-gates.md` scenario 19 and section 3 rejected behavior.
4. Git guard (rules unchanged; behavior locked by tests).

## Scenario matrix
| # | Category | Scenario | Test | AC | Result |
|---|---|---|---|---|---|
| 1 | Happy path / Contract | Mode step 9 has `git add -f -- <path>...`, `Artifacts` table source, no dir/glob, cached preflight | `test_orchestrate.OrchestrateContractTests.test_publish_force_adds_listed_artifacts_with_preflight` (executor-added, reviewed) | 1 | pass |
| 2 | Contract | Runtime and template mode copies byte-identical | `test_runtime_copies_match_templates`; `diff` of both files | 1 | pass |
| 3 | Contract | Mode stop list has staged-set mismatch (step 9) | `test_publish_force_adds_listed_artifacts_with_preflight` | 2, 6 | pass |
| 4 | Contract | Spec section 6 stop list has staged-set mismatch | `PublishForceAddSpecAndValidationTests.test_spec_stop_list_has_staged_set_mismatch` (new) | 2 | pass |
| 5 | Contract | Spec section 7: explicit-path force-add, no dir/glob, no temp/cache, preflight, `/generated/**` stays ignored, no force-push | `test_spec_publication_force_adds_explicit_paths_and_keeps_ignore` (new) | 3 | pass |
| 6 | Regression | `FORGE_LOCAL_GITIGNORE` unchanged; still ignores `/generated/**`, `/temp/`, `/cache/` | `git diff master -- src/forge_context_engine/runtime_ops.py` empty; `test_tool_selection` gitignore assertions | 4 | pass |
| 7 | Auth/permission (guard) | Orchestrator allowed `git add -f -- .forge/generated/plans/x.md` | `test_orchestrator_allows_feature_branch_flow` (executor-added line) | 5 | pass |
| 8 | Auth/permission (negative) | Orchestrator still blocked on `git push -f` alone and chained after `git add -f` | `test_orchestrator_still_blocks_short_force_push_next_to_force_add` (new) | 5 | pass |
| 9 | Regression | Guard rules/hook files unchanged | `git diff master --stat` on `git-guard-rules.json`, `forge_git_guard.py`: empty | 5 | pass |
| 10 | Integration / Data state | Real git repo with `FORGE_LOCAL_GITIGNORE`: plain `git add` refuses the artifact; `git add -A` skips it and `.forge/temp/`, `.forge/cache/`; `git add -f -- <plan>` stages it; `git diff --cached --name-only` equals the expected set exactly | `test_force_add_stages_listed_artifacts_but_not_temp_or_cache` (new) | 1, 5, 6 | pass |
| 11 | Failure path | Validation scenario 19 states no temp/cache path and an extra staged path stops before commit; section 3 rejects `git add -A`/dir/glob staging | `test_validation_case_19_stops_on_extra_staged_path` (new) | 6 | pass |
| 12 | Regression | Scenario 18 row and `any stop scenario (2 to 8, 11, 12, 18)` verbatim | `test_orchestrate_host_dispatch.HostSpecAndValidationTests.test_ValidationCase18_ExpectsBlockedByEnvironment_AndIsInRegressionList` | 7 | pass |
| 13 | Full suite | All tests green | full suite | 8 | pass |

Not applicable:
- Input validation, boundaries: no parser or API input; the contract is agent-checked text.
- Dependency failure, concurrency, idempotency: no runtime code path; the preflight is an agent instruction (SDD non-goal: no staging script). The executable behavior of an orchestrator actually stopping on a staged-set mismatch cannot be tested without a staging script; covered by contract text tests (rows 3, 4, 11) and the git-level premise (row 10).

## Commands
| Command | Result |
|---|---|
| `uv run python -m unittest tests.test_git_guard tests.test_orchestrate -v` | Ran 38 tests, OK |
| `uv run python -m unittest discover -s tests -q` | Ran 148 tests, OK |
| `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` | identical |
| `git diff master --stat -- runtime_ops.py, git-guard-rules.json, forge_git_guard.py` | no changes |

## Failures
None.

## Files added or changed by tester
- `tests/test_git_guard.py`: added `test_orchestrator_still_blocks_short_force_push_next_to_force_add`, `test_force_add_stages_listed_artifacts_but_not_temp_or_cache`.
- `tests/test_orchestrate.py`: added class `PublishForceAddSpecAndValidationTests` (3 tests).
- This report.
