# Test report: orchestrate resume in place (#16)

| Field | Value |
|---|---|
| Artifact | test report |
| Date | 2026-11-25 |
| SDD | `.forge/generated/plans/2026-11-24-orchestrate-resume-in-place-plan.md` |
| ECP | `.forge/generated/ecp/2026-11-24-orchestrate-resume-in-place-ecp.md` |
| Branch | `forge/2026-11-24-orchestrate-resume-in-place` |
| Verdict | pass |

## Entry points changed
- `orchestrate` mode step 1 / 1a, stop list, footer, `next mode transitions` (both copies: `runtime/.forge/runtime/modes/orchestrate.md`, `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`).
- `specs/orchestrate.md` §6, §9, §9a; `validation-cases/orchestrate-gates.md` rows 23, 24, §3, §5.
- No executable code changed: the resume rule is a Markdown contract. Tests are contract tests over both mode copies, spec, and validation cases (repo's existing style). No e2e harness (`e2e: n/a`).

## Scenario matrix
New file `tests/test_orchestrate_resume.py` (`ResumeInPlaceFailurePathTests`), each test runs over both mode copies.

| Scenario | AC | Test | Result |
|---|---|---|---|
| Any failed condition stops for a dirty tree; conditions are all-of (no partial resume) | AC2 | `test_ResumeRefused_WhenAnyConditionFails_AllConditionsAreConjunctive` | pass |
| Gate 2 not `✓` or a `✗` step refuses resume; the `[ecp] Gate 2` line the rule keys on exists in the report `Steps` template; spec §9a matches | AC1, AC3, AC4 | `test_ResumeRefused_WhenGate2NotDone_ReferencesRealReportStepLine` | pass |
| Changed path outside ECP scope and test paths refuses; case 24 expects stop, no worker started; §3 rejects it | AC2 | `test_ResumeRefused_WhenPathOutsideEcpScopeAndTestPaths` | pass |
| Tester files allowed only while a `[test]` step is `✓`/`✱`; counted as tester-added at step 9; overlay `Test paths` line exists | AC1 (Q3/Q4) | `test_TesterFiles_AllowedOnlyAfterTestStepStarted_AndCountAsTesterAdded` | pass |
| Default/protected branch still stops; branch check is independent of the resume exception; resume requires the `Run` branch | AC2, AC4 | `test_ResumeRefused_OnDefaultBranch_BranchStopIsIndependentOfResume` | pass |
| Never resumes at Publish; 6a then new tester and reviewer; case 23 and §3 agree | AC1 | `test_NeverResumesAtPublish_TestAndReviewRerunInFreshContext` | pass |
| Fix-round counter formula carried over, never resets, limit 2; report has `Review rounds` and repeated `[execute]` lines | AC1 | `test_FixRoundCounter_CarriedOver_NeverResets` | pass |
| Resume line uses a valid stage ID (`clarify`), same report, no new file, no new status value | AC4 | `test_ResumeRecorded_InSameReport_WithValidStageId` | pass |

Categories n/a: input validation, auth, dependency failure, concurrency, idempotency (no executable entry point; the rule is prose the orchestrator follows). Already covered by the executor's test in `tests/test_orchestrate.py` (`OrchestrateResumeInPlaceTests`): presence of the core 1a phrases, spec "state file" ban, row 24 regression list; not duplicated.

## Commands
- `uv run python -m unittest tests.test_orchestrate_resume -v`: 8 tests, OK.
- `uv run python -m unittest discover -s tests -q`: 207 tests, OK.
- `diff` of the two mode copies: identical (AC6).
- Security/static scan: no command exists in the repo or `testing` overlay; not run.

## Failures
None.

## Limits
Contract tests check wording, not orchestrator behavior; an agent could still misapply the rule. A deterministic scope-check script (SDD Full-Version Path) would make the failure paths executable.

## Round 2

Fix round 1 scope: mode step 1a and spec section 9a (S1, R1, R2, R3). Written from the SDD/review findings, not the executor's reasoning. No e2e harness (prose mode contract); text-contract integration tests run with the standard suite.

| Scenario | Category | Test | Result |
|---|---|---|---|
| S1: `Artifacts` row naming `src/x.py` or another slug's artifact is not adopted; only `.forge/generated/` paths starting with the ECP's `<YYYY-MM-DD>-<slug>`; no second unrestricted `Artifacts` clause | Input validation / scope | `test_ArtifactsRow_OutsideGeneratedOrOtherSlug_NotAdopted` | pass |
| R1: report located by the ECP file's date and slug | Data state | `test_ReportLocated_ByEcpDateAndSlug_NotAnyReport` | pass |
| R2: last `[execute]` is `✱` -> re-run execute with last review findings, same round | Idempotency / retry | `test_ExecuteRerun_WhenLastExecuteInProgress_SameRoundWithLastFindings` | pass |
| R3: execution report missing per `Artifacts` table -> re-run execute | Dependency failure (lost artifact) | `test_ExecuteRerun_WhenExecutionReportMissing_PerArtifactsTable` | pass |
| Runtime and template mode copies state an identical step 1a | Contract | `test_BothModeCopies_StateIdenticalResumeStep` | pass |
| Round 1 scenarios (8 tests) | Regression | `ResumeInPlaceFailurePathTests` | pass |

Commands:
- `uv run python -m unittest tests.test_orchestrate_resume -q` -> Ran 13 tests, OK
- `uv run python -m unittest discover -s tests -q` -> Ran 212 tests, OK

Failures: none. Files changed: `tests/test_orchestrate_resume.py` (5 tests added).

Verdict: pass

## Round 3

Fix round 2 scope: mode step 1a and spec section 9a require every `Artifacts` table path (not only porcelain-visible ones) to be under `.forge/generated/` with the ECP's `<YYYY-MM-DD>-<slug>` prefix, else stop; R2 wording "the ECP, plus the last review findings if any". Written from the SDD/review findings, not the executor's reasoning.

| Scenario | Category | Test | Result |
|---|---|---|---|
| Gitignored `.env` in `Artifacts` (invisible to porcelain, force-added at step 9) is refused: all-`Artifacts`-paths rule in both mode copies and spec §9a, placed before the stop sentence; reason stated in both | Security / scope | `test_EveryArtifactsPath_MustBeUnderGeneratedWithEcpPrefix_InModeAndSpec` | pass |
| Runtime and template mode copies state the same all-`Artifacts`-paths sentence | Contract | `test_BothModeCopies_AgreeOnAllArtifactsPathsRule` | pass |
| R2 wording "the ECP, plus the last review findings if any" in mode and spec | Regression | `test_ExecuteRerun_WhenLastExecuteInProgress_SameRoundWithLastFindings` (existing) | pass |
| Rounds 1-2 scenarios (13 tests) | Regression | `ResumeInPlaceFailurePathTests` | pass |

Commands:
- `uv run python -m unittest tests.test_orchestrate_resume -q` -> Ran 15 tests, OK
- `uv run python -m unittest discover -s tests -q` -> Ran 214 tests, OK

Failures: none. Files changed: `tests/test_orchestrate_resume.py` (2 tests added).

Verdict: pass
