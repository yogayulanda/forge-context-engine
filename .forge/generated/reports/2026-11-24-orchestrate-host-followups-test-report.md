# Test report: orchestrate-host-followups (issue #18)

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| SDD | `.forge/generated/plans/2026-11-24-orchestrate-host-followups-plan.md` |
| ECP | `.forge/generated/ecp/2026-11-24-orchestrate-host-followups-ecp.md` |
| Branch | `forge/2026-11-24-orchestrate-host-followups` |
| Verdict | pass |

## Entry points changed
- Packaged runtime text installed by `forge init` / `forge update`: `modes/orchestrate.md` (step 1, step 2, `## worker dispatch` guard bullet, report Steps line), `agents/forge-planner.md` step 3, `agents/specialties/testing.md` `## As reviewer` (template + `runtime/` copies).
- `specs/orchestrate.md` §4b, §6a, §8 `host` bullet.
- No Python code, CLI, or config schema changed.

## Added tests
`tests/test_orchestrate_host_followups.py` (11 tests). Existing tests already covered AC1, AC2, AC3 (template copies), AC6 sync; new tests cover the gaps below.

## Scenario matrix
| Category | Scenario | AC | Test | Result |
|---|---|---|---|---|
| Happy path (install) | `forge init` installs mode step 1 with role `orchestrator`, `git-guard-rules.json`, `orchestrator git guard not confirmed`, `git guard hook missing` kept | AC1, R1 | `test_ForgeInit_InstalledMode_Step1HasNonClaudeOrchestratorGuardNote` | pass |
| Happy path (install) | installed step 2 names `-plan.md` path and the three `plan` statuses; report line uses `<YYYY-MM-DD>-<slug>-plan.md` | AC3, R3 | `test_ForgeInit_InstalledMode_NamesOnePlanPathAndPlanStatuses` | pass |
| Happy path (install) | installed planner step 3 and testing overlay carry new lines | AC3, R6 | `test_ForgeInit_InstalledPlannerAndOverlay_CarryNewLines` | pass |
| Negative (install) | no installed `.forge/**/*.md` names `-sdd.md`, `` `draft` ``, `status: draft` | AC3, R4 | `test_ForgeInit_NoInstalledFileNamesSddFileOrDraftStatus` | pass |
| Negative (shipped) | no template file, no `runtime/` md/yaml/json/toml file, nor spec names `-sdd.md` / `` `draft` `` / `status: draft` | AC3, R4 | `test_NoShippedRuntimeFileNamesSddFileOrDraftStatus` | pass |
| Contract | `runtime/` planner copy names path with `plan` mode status | AC3 | `test_RuntimePlannerCopy_NamesPlanPathWithPlanStatus` | pass |
| Failure path | template mode `-plan.md` -> `-sdd.md` makes `test_sdd_path_and_status_are_one_set` fail, message names `orchestrate.md (template)` | AC4 | `test_SddNameCheck_Fails_WhenTemplateModeSaysSddFile` | pass |
| Failure path | extra stop line with `resume` makes the A4 check fail, message names `orchestrate.md (runtime/)` | AC4 | `test_StopLinesCheck_Fails_WhenAnotherResumeStopIsAdded` | pass |
| Failure path | broken `runtime/` guard note fails both guard tests, message names `orchestrate.md (runtime/)` | AC4, R5 | `test_GuardCheck_FailureMessage_NamesRuntimeCopy` | pass |
| Contract (test shape) | no asserted literal in host dispatch tests contains `. `; no `"Gate 1 approval"` | AC5 | `test_NoAssertedLiteralSpansTwoSentences_AndNoGate1Phrase` | pass |
| Contract (test shape) | every assert inside a `_mode_copies()` loop passes `name` | AC5 | `test_EveryAssertInCopyLoop_PassesCopyName` | pass |
| Regression | sync tests, existing host dispatch tests, full suite | AC6 | full suite | pass |
| Input validation / boundaries / auth / dependency failure / idempotency / concurrency / data state | n/a: Markdown contract text only, no runtime code path changed | - | - | n/a |

## Commands
- `uv run python -m unittest discover -s tests -p test_orchestrate_host_followups.py -v` -> `Ran 11 tests ... OK`
- `uv run python -m unittest tests.test_orchestrate tests.test_orchestrate_host_dispatch` -> `Ran 61 tests ... OK`
- `uv run python -m unittest discover -s tests -q` -> `Ran 228 tests ... OK` (baseline 214; executor added 3, tester 11)
- `cmp` runtime vs template for `orchestrate.md`, `forge-planner.md`, `specialties/testing.md` -> identical
- `git status --porcelain` -> only Affected Surface Inventory files plus `tests/test_orchestrate_host_followups.py` (AC7)

## Failures
None.

## Notes
- e2e: n/a (no e2e harness; tests are integration-level via `run_init` and run with the standard command).
- No security/static scan command exists in the repo; none run.
- `testing` overlay Team settings are placeholders; commands taken from the task/ECP (`uv run python -m unittest discover -s tests -q`).
- Minor (not failing): in `test_sdd_path_and_status_are_one_set` the final `assertIn` on the report line and the step-2 status loop carry no copy-naming message; they check the template only, so AC5 (copy loops) is still met.
