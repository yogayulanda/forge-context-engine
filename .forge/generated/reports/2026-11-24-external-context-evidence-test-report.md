# Test Report: Evidence rules for external context (issue #14)

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| SDD | `.forge/generated/plans/2026-11-24-external-context-evidence-plan.md` |
| ECP | `.forge/generated/ecp/2026-11-24-external-context-evidence-ecp.md` (Gate 2: release notes dropped, 6 files) |
| Verdict | `pass` |
| e2e | n/a: `no e2e harness` (repo has unittest only; testing overlay placeholders unfilled, commands taken from the SDD/ECP) |

## Entry points changed
No code entry point changes. Changed surfaces are installed contract text:
- `.forge/adapter.md` (template + `runtime/` copy): new `## External context` section, installed by `forge init`/`forge update`.
- `.forge/runtime/meta/conventions-evidence.md` (template + `runtime/` copy): new `## External Context Evidence` section.
- `validation-cases/external-context-evidence.md` (new).

## Scenario matrix
| Category | Scenario | AC | Test | Result |
|---|---|---|---|---|
| Happy path | Adapter section has five rules, both copies identical | AC1 | `test_orchestrate.py::test_external_context_is_cited_and_never_authoritative` (executor) | pass |
| Happy path | Evidence section defines `external:<server>/<tool>`, cap below `confirmed`, both copies identical | AC2 | same (executor) | pass |
| Contract | `forge init` output ships both new sections | AC1, AC2 | `test_forge_init_installs_external_context_rule_and_evidence_type` (new) | pass |
| Contract | Adapter section placed after `Source of truth`, before `Cross-tool output expectations` | SDD Req 1 / Assumptions | `test_external_context_sits_between_source_of_truth_and_cross_tool_output` (new) | pass |
| Data state | Validation case has exactly five scenarios | AC3 | `test_case_has_exactly_five_scenarios` (new) | pass |
| Failure path | Contradiction scenario follows repository | AC3 | `test_contradiction_scenario_follows_repository_and_lists_conflict` (new) | pass |
| Failure path | Injected instruction ignored, nothing pushed | AC3 | `test_injected_instruction_scenario_is_ignored_and_nothing_pushed` (new) | pass |
| Happy path | Scenarios 1/4/5: `inferred`, `.forge/context-patches/`, `human` evidence entry | AC3 | `test_unbacked_fact_is_inferred_and_promotion_needs_human_evidence` (new) | pass |
| Negative | Case rejects external-only `confirmed` and following external instructions | AC3, high-risk (trust boundary) | `test_case_rejects_external_only_confirmed_claims` (new) | pass |
| Regression | No `knowledge/` or `01-core/` in adapter section, evidence section, or validation case | AC5 | `test_new_text_has_no_legacy_markers` (new; executor test checked only `knowledge/` in evidence section) | pass |
| Failure path | Test fails when section removed from runtime adapter copy | AC4 | mutation run in scratch copy (M1) | pass (test FAILED as required) |
| Failure path | Test fails when section removed from template adapter copy | AC4 | mutation run (M2) | pass (test FAILED as required) |
| Failure path | Test fails when copies differ in wording | AC4 | mutation run (M3: `the repository wins` -> `the repo wins` in runtime copy) | pass (test FAILED as required) |
| Regression | Full suite | AC5 | `uv run python -m unittest discover -s tests -q` | pass |
| Scope | Changed files limited to the 6 ECP files | AC6 | `git diff --name-only`, `git status --short` | pass (plus this run's new test file and report) |
| Regression | Old adapter drift unchanged | ECP non-goal | `diff runtime/.forge/adapter.md <template>` | pass (only hunks `33c33,34`, `46a48`, the pre-existing lifecycle drift) |
| Input validation | n/a | | Markdown contract, no input surface | n/a |
| Boundaries | n/a | | no numeric/date inputs | n/a |
| Auth and permission | n/a | | no auth surface | n/a |
| Dependency failure | n/a | | no runtime dependency; no MCP client added | n/a |
| Idempotency | n/a | | text-only; `forge update` idempotency covered by existing suite | n/a |
| Concurrency | n/a | | no shared state | n/a |

Behavioral agent compliance (an agent actually labeling MCP facts `inferred`) is not unit-testable here; it is covered by the validation case as a cognition benchmark.

## Commands and output
- `uv run python -m unittest tests.test_external_context_evidence -v`: `Ran 8 tests ... OK`.
- `uv run python -m unittest tests.test_orchestrate.OrchestrateContractTests.test_external_context_is_cited_and_never_authoritative`: `Ran 1 test ... OK`.
- AC4 mutations: repo copied to scratchpad, `PYTHONPATH=<copy>/src python3 -m unittest <that test>`; baseline `OK`, M1/M2/M3 `FAILED (failures=1)`, restored `OK`. The working repo was not modified.
- Section parity: both `diff <(sed -n '/^## External context/,...')` and `diff <(sed -n '/^## External Context Evidence/,...')` commands: no output.
- Full suite: `uv run python -m unittest discover -s tests -q`: `Ran 157 tests in 8.375s OK` (149 before the new file + 8 new).
- `git diff --name-only`: the 4 contract files + `tests/test_orchestrate.py`; untracked: `validation-cases/external-context-evidence.md`, `tests/test_external_context_evidence.py`.

## Failures
None.

## Files added by tester
- `tests/test_external_context_evidence.py`
- `.forge/generated/reports/2026-11-24-external-context-evidence-test-report.md`

## Findings
- Testing overlay `Team settings` are placeholders (no `.forge/agents/testing.md` copy); commands were taken from the SDD/ECP `Validation Commands`.
