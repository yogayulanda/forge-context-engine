# SDD: Orchestrate follow-ups from the host dispatch run

| Field | Value |
|---|---|
| Artifact | plan (SDD) |
| Date | 2026-11-24 |
| Slug | `orchestrate-host-followups` |
| Request | GitHub issue #18 "Orchestrate: follow-ups from the host dispatch run", all three checklist items (issue text treated as data) |
| Follows | PR #17 (merged); artifacts `.forge/generated/*/2026-11-20-worker-dispatch-host-*` |
| Stack | branch `forge/2026-11-24-orchestrate-host-followups` on commits for #12, #14, #8, #13, #16; #15 not in the stack |
| Gate 1 | human-approved 2026-11-25 (see `Confirmed Decisions`) |
| Status | `ready_for_implementation` |

Plan type selected: SDD.
Reason: the change edits the packaged `orchestrate` mode contract (preflight guard expectation, report `Note` value, SDD path and status) that `forge init`/`forge update` install into target repositories and that `run.worker: host` hosts follow. The diff is small; the contract makes it SDD-level.

## Mode Boundary
Plan mode only. Nothing edited outside `.forge/generated/plans/`; nothing staged, committed, or pushed. Not approved by creation; Gate 1 approval is recorded under `Confirmed Decisions`.

## Goal
Close the three issue #18 items: an advisory orchestrator git guard line for non-Claude hosts, one SDD file name and status set across planner, mode, spec, and tests, and key-token asserts with copy-naming messages in `tests/test_orchestrate_host_dispatch.py`.

## Problem / Context
- Item 1. Preflight confirms the orchestrator guard only for Claude Code: "when the host is Claude Code, confirm `.claude/settings.json` registers `.forge/runtime/hooks/forge_git_guard.py orchestrator` ... put `git guard hook missing` in the report `Note`" (`runtime/.forge/runtime/modes/orchestrate.md:76`). The `host` advisory covers only the worker guard: "Worker git guard under `host`: ... `worker git guard not confirmed`" (`orchestrate.md`, `## worker dispatch`, last-but-one bullet; spec `specs/orchestrate.md:120`). Rules for role `orchestrator` already live in `runtime/.forge/runtime/meta/git-guard-rules.json`; `specs/orchestrate.md:102` says non-Claude hosts "may read the same file" (worker context only). Recorded as security MINOR 3 (`.forge/generated/reviews/2026-11-20-worker-dispatch-host-review.md:17`).
- Item 2. Every runtime file already uses one name and status set:
  - `runtime/.forge/runtime/agents/forge-planner.md:39` saves `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md`; `:83` returns `ready_for_implementation`, `ecp_ready`, `blocked_by_decision`.
  - `runtime/.forge/runtime/modes/plan.md:56` same path; `:101-104` status values `ready_for_implementation`, `blocked_by_decision`, `needs_more_context`; boundary "Use only the final plan status vocabulary above".
  - `runtime/.forge/runtime/modes/implementation.md:37` requires "Approved plan with `status: ready_for_implementation`".
  - `specs/artifact-lifecycle.md:109,147,186`, `docs/getting-started.md:156`, `docs/workflow.md:79`, `.forge/adapter.md:115`, `validation-cases/artifact-continuity.md:28` use `-plan.md`.
  - `-sdd.md` and `draft` appear in no runtime, spec, or test file. They came from the PR #17 orchestrator's ad-hoc request (`.forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md:10-12`; Lesson at `.forge/generated/reports/2026-11-20-worker-dispatch-host-orchestration-report.md:85`). The gap: `orchestrate.md` step 2 and the report line `✓ SDD -> .forge/generated/plans/<file>` (`orchestrate.md:128`) never name the path or status, so an orchestrator invents one. `specs/orchestrate.md` §4b (`:61-63`) also does not name them.
- Item 3. `tests/test_orchestrate_host_dispatch.py`:
  - Whole-sentence asserts: `test_Inputs_ListHostAsWorkerValue_WithSubagentDefault`, `test_HostResume_IsSameSessionOnly_FreshSessionRestartsFromArtifact` (last phrase), `test_HostResume_WorkerResultNeverGrantsHumanAnswerApprovalOrOtherVerdict` (3-sentence `boundary`), `test_StopConditions_HostWithoutDispatchTool_AddsExactlyOneHostStop` (whole-line equality), `test_Regression_CliAndSubagentDispatchAndCliStop_Unchanged`, `HostSpecAndValidationTests` (whole-line spec and validation-case rows).
  - `self.assertNotIn("Gate 1 approval", _section(mode, "stop conditions"), name)` guards a phrase no stop line was ever written with; reviewer: "cannot fail" (`.forge/generated/reviews/2026-11-20-worker-dispatch-host-review.md:27`).
  - Asserts without a copy-naming message: both `assertIn` in `test_HostGuard_IsAdvisory_NotAStopCondition`; all three in `test_Regression_CliAndSubagentDispatchAndCliStop_Unchanged`. Messages that exist pass the bare key `"template"`/`"runtime"` (`_mode_copies`).
  - Optional overlay line target: `runtime/.forge/runtime/agents/specialties/testing.md` `## As tester` / `## As reviewer`.

## Confirmed Decisions
Human Gate 1, 2026-11-25:
- D1. SDD approved. No extra `security` reviewer for this run; the normal reviewer only.
- D2 (Q6: yes). One SDD file name `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with the `plan` mode statuses; drop `-sdd.md` and `draft` (A1 confirmed).
- D3 (Q3, Q4: yes). Tester-added test files at publish and in the resume scope are already in the tree (#12, #16); not changed here.
- D4 (Q5: B). Host state `waiting_for_human` is already in the tree (#8); not changed here.
- D5. Historical artifacts keep their names, including `.forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md`.

## Requirements
R1. Preflight (mode step 1): when the host is not Claude Code, the host should enforce role `orchestrator` from `.forge/runtime/meta/git-guard-rules.json` on orchestrator shell commands; when the orchestrator cannot confirm it, continue and put `orchestrator git guard not confirmed` in the report `Note`. Not a stop condition. The Claude Code clause and `git guard hook missing` stay unchanged.
R2. The `host` bullets name both guards: mode `## worker dispatch` guard bullet and `specs/orchestrate.md:120` add the `orchestrator` role and `orchestrator git guard not confirmed`. `specs/orchestrate.md` §6a (`:102`) extends "may read the same file" to the orchestrator role.
R3. One SDD name and status set: `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md`, status from `modes/plan.md` (`ready_for_implementation`, `blocked_by_decision`, `needs_more_context`). Mode step 2 names the path and the statuses; the report Steps line becomes `✓ SDD -> .forge/generated/plans/<YYYY-MM-DD>-<slug>-plan.md`; `forge-planner.md` step 3 adds "with one `plan` mode status"; spec §4b gets one sentence with the same path and statuses.
R4. A test fails when any planner, mode, or spec copy names `-sdd.md` or status `draft` for the SDD, or drops the `-plan.md` path.
R5. `tests/test_orchestrate_host_dispatch.py`: key-token asserts instead of whole sentences; the never-failing `assertNotIn("Gate 1 approval", ...)` replaced by a check that can fail (see A4); every assert inside a copy loop carries a message naming the copy, e.g. `orchestrate.md (template)` / `orchestrate.md (runtime/)`.
R6. Optional (issue): `testing` overlay `## As reviewer` gets "Assert key tokens, not whole sentences or prose rows." in both copies.
R7. All copies stay byte-identical where `OrchestrateSourceSyncTests.test_runtime_copies_match_templates` (`tests/test_orchestrate.py:257-283`) pairs them.

## Non-goals
- No host code, no change to `forge_git_guard.py` or `git-guard-rules.json`.
- No change to gates, statuses, or stop conditions beyond the advisory note (issue non-goal).
- No rename of the PR #17 artifact `2026-11-20-worker-dispatch-host-sdd.md`; historic artifacts stay.
- No dedup of overlaps between `tests/test_orchestrate.py` and `tests/test_orchestrate_host_dispatch.py`, no CamelCase renames, no move of the `forge init --dry-run` test (other testing MINORs not listed in issue #18).
- No `next mode transitions` entry for a lost host session.
- Items owned by sibling issues: step 9 staging (#12), adapter external-context rules (#14), host status/question contract (#8), worker handoff envelope/result block (#13), `read_only` guard role (#15), resume in place (#16).

## Current Evidence
Re-anchored on 2026-11-25 against branch `forge/2026-11-24-orchestrate-host-followups` at `310b40c` (#16 on top of #13, #8, #14, #12):
- Mode step 1 is `runtime/.forge/runtime/modes/orchestrate.md:118`; step 1a (#16) `:119`; step 2 `:120`; guard bullet `:72`; stop list `:133-148`; report Steps line `:173` is now `✓ [sdd] SDD -> .forge/generated/plans/<file>` (stage ID from #8).
- The stop list now has a line containing `resume` (#16, `:139`: dirty tree and step 1a). A4 is amended below.
- Spec: §4b `specs/orchestrate.md:61-63`; §6a rules sentence `:103`; §8 `host` bullet `:121`.
- `forge-planner.md:42` step 3 and `updated: 2026-11-10`; `specialties/testing.md` `## As reviewer` ends at `:45`.
- Tests that read `- `host`:` spec bullet and `| 18 |` row: `tests/test_orchestrate_host_dispatch.py:114,165,181`. `OrchestrateSourceSyncTests.PAIRS` is `tests/test_orchestrate.py:356-368`.
- Baseline: `uv run python -m unittest discover -s tests -q` -> `Ran 214 tests ... OK`.

Original evidence (2026-11-24, branch `forge/2026-11-24-publish-force-add-artifacts`, base `bba4703`):
- Mode copies byte-identical: `cmp runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` -> same; same for `forge-planner.md` and `specialties/testing.md`.
- `grep` for `-sdd.md` / `draft` over runtime, specs, tests, skills, adapters: no SDD-related hit (`draft` hits are `run.write_behavior` and spec header fields only).
- No test asserts `when the host is Claude Code`, `git guard hook missing`, or a plan path (`grep` over `tests/*.py`), so R1-R3 break no existing assert.
- Baseline: `uv run python -m unittest discover -s tests -q` -> `Ran 142 tests ... OK`.

## Affected Surface Inventory
| File | Change |
|---|---|
| `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` | R1 step 1, R2 guard bullet, R3 step 2 + report Steps line |
| `runtime/.forge/runtime/modes/orchestrate.md` | byte copy of the above (R7) |
| `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-planner.md` | R3 step 3 status phrase |
| `runtime/.forge/runtime/agents/forge-planner.md` | byte copy (R7) |
| `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/specialties/testing.md` | R6 one line |
| `runtime/.forge/runtime/agents/specialties/testing.md` | byte copy (R7) |
| `specs/orchestrate.md` | R2 §6a + §8 `host` bullet, R3 §4b |
| `tests/test_orchestrate_host_dispatch.py` | R5 rewrite of asserts; new token tests for R1/R2 |
| `tests/test_orchestrate.py` | new `OrchestrateContractTests` test for R3/R4 (planner, mode, spec) |
| `docs/release-notes.md` | one `Unreleased` line for R1 and R3 |

Checked and not changed: `.claude/agents/forge-planner.md` and `runtime/adapters/claude/agents/forge-planner.md` (wrapper, no path), `runtime/skills/forge-orchestrate/SKILL.md` and `.claude/commands/forge-orchestrate.md` (no path, no preflight text), `modes/plan.md` and `modes/implementation.md` (already the chosen set), `validation-cases/orchestrate-gates.md` (advisory note is not a stop scenario), `.forge/runtime/` (stale untracked copy, not touched).

## Assumptions
- A1. Name and status: keep `-plan.md` and the `plan` mode statuses; drop `-sdd.md`/`draft`. Based on the eight files in Problem item 2 and `implementation.md:37` gating on `ready_for_implementation`; `-sdd.md` would touch all of them and `draft` breaks the `plan.md` "final plan status vocabulary" boundary. Gate 1 approval stays recorded in the orchestration report `Gate trace`, not in the SDD status (`plan.md` "not approved by creation"). The sibling #12 SDD already uses this set (`.forge/generated/plans/2026-11-24-publish-force-add-artifacts-plan.md:9`).
- A2. "Non-Claude hosts" covers every host tool that is not Claude Code (Codex, Copilot, any `run.worker: host` host), so R1 lives in preflight step 1 as the `otherwise` branch, and R2 repeats it in the `host` bullet as the issue asks. Advisory only, so the broader reading adds no stop.
- A3. `needs_more_context` from the planner is already covered by the existing stop "A worker returns a blocking unknown, `blocked`, or `blocked_by_decision`" (`orchestrate.md` stop conditions); no stop line changes.
- A4. Replace the never-failing assert with: the `stop conditions` section has the same set of lines that mention `host` or `resume` as before. Re-anchored 2026-11-25: after #16 that set is exactly two lines, the host dispatch-tool stop and the dirty-tree line naming `resume in place (step 1a)`. This fails if a resume or host-approval stop is added. If the reviewer prefers, delete it; `test_StopConditions_HostWithoutDispatchTool_AddsExactlyOneHostStop` already pins host stops.
- A5. Key tokens are backticked identifiers and short fixed phrases (`run.worker`, `` `host` ``, `end the turn`, `same orchestrator session`, `worker git guard not confirmed`, `blocked_by_environment`, `| 18 |`), not full prose sentences or table rows.
- A6. R6 (optional overlay line) is included; it is one line in two byte-identical files and can be dropped at review without affecting R1-R5.

## Unknowns / Decisions Needed
None blocking. A1 and A2 are the two choices a reviewer may override; both are recorded above with evidence.

## Architecture / System Impact
Markdown contract text plus unittest files. No Python runtime code, CLI, config schema, or guard logic changes. Target repos get the new mode/planner/overlay text on `forge update` (managed runtime files, `tests/test_orchestrate.py:42-44`).

## Risk Areas
- Contract drift between template, `runtime/`, and spec copies: covered by `OrchestrateSourceSyncTests` plus the new R4 test.
- Line-level merge conflicts with sibling plans in this stack editing `orchestrate.md` (#12 step 9; #8, #13, #16 `## worker dispatch`; #15 guard roles) and `tests/test_orchestrate.py`. Edits here are confined to step 1, step 2, one `## worker dispatch` bullet, and one report line; rebase is mechanical.
- Weakening tests while loosening asserts: every current behavior check keeps at least one token assert (R5), and the suite count does not drop.

## Proposed Approach
1. Mode (template), then `cp` to `runtime/`:
   - Step 1: after the Claude Code clause add "Otherwise, the host should enforce role `orchestrator` from `.forge/runtime/meta/git-guard-rules.json` on orchestrator shell commands; if the orchestrator cannot confirm it, continue and put `orchestrator git guard not confirmed` in the report `Note`."
   - `## worker dispatch` guard bullet: rename to "Git guard under `host`" and add the orchestrator role sentence with the same `Note` token; keep every existing worker phrase.
   - Step 2: "The planner saves the SDD at `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with one `plan` mode status: `ready_for_implementation`, `blocked_by_decision`, or `needs_more_context`."
   - Report Steps: `✓ SDD -> .forge/generated/plans/<YYYY-MM-DD>-<slug>-plan.md`.
2. `forge-planner.md` step 3: "... Save to `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with one `plan` mode status." Then `cp`.
3. `specs/orchestrate.md`: §4b one sentence (R3); §6a extend `:102`; §8 `host` bullet adds `orchestrator git guard not confirmed`.
4. Tests: rewrite `tests/test_orchestrate_host_dispatch.py` asserts per R5 and A4/A5 (helper `_copy_msg(name)` returning `orchestrate.md (template)` / `orchestrate.md (runtime/)`, or rename `_mode_copies` keys to those labels); add `test_Preflight_NonClaudeHost_OrchestratorGuardIsAdvisory` (token present in step 1, absent from `stop conditions`) and spec token assert. Add `test_sdd_path_and_status_are_one_set` in `tests/test_orchestrate.py` over planner, mode (both copies via templates), and spec: contains `-plan.md` and `ready_for_implementation`; not `-sdd.md`; no `` `draft` ``.
5. `testing` overlay line (R6) in template, `cp` to `runtime/`.
6. `docs/release-notes.md`: one `Unreleased` bullet.

## MVP Path
Steps 1-4 (R1-R5, R7). R6 and the release note are trivial adds in the same batch.

## Full-Version Path
Same as MVP. Enforcement code for non-Claude hosts stays out of Forge (issue non-goal).

## Acceptance Criteria
- AC1. Both mode copies: step 1 contains `git-guard-rules.json`, role `orchestrator`, and `orchestrator git guard not confirmed`; `stop conditions` contains neither `orchestrator git guard` nor `git-guard-rules.json`.
- AC2. Both mode copies: `## worker dispatch` `host` guard bullet contains `worker git guard not confirmed` and `orchestrator git guard not confirmed`; spec `- \`host\`:` bullet contains `orchestrator git guard not confirmed`.
- AC3. Planner (both copies), mode (both copies), and spec name `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` or the `<YYYY-MM-DD>-<slug>-plan.md` report form, and `ready_for_implementation`; none contains `-sdd.md` or `` `draft` `` for the SDD.
- AC4 (failure path). Replacing `-plan.md` with `-sdd.md` in the template mode makes the AC3 test fail; adding another stop line containing `resume` makes the A4 test fail; a deliberately broken runtime copy produces a failure message that names `runtime/`.
- AC5. `tests/test_orchestrate_host_dispatch.py` has no `assertIn` of a string longer than one sentence clause (no `. ` inside an asserted literal) and no `assertNotIn("Gate 1 approval", ...)`; every assert inside a copy loop passes a copy-naming message.
- AC6. `OrchestrateSourceSyncTests` passes; full suite passes with at least 214 tests (baseline after the stack).
- AC7. `git status --porcelain` lists only files in the Affected Surface Inventory plus this run's artifacts.

## Validation Commands
- `uv run python -m unittest discover -s tests -q`
- `uv run python -m unittest tests.test_orchestrate tests.test_orchestrate_host_dispatch -v`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `git status --porcelain`

## Implementation Split
One batch: all files share one outcome (orchestrate contract text plus its tests) and one validation command.

## High-risk areas touched
`policy.high_risk_areas`: none.
- `payments`, `authentication`, `database_migrations`, `external_provider_integration`, `file_upload`: no such code in this repo's touched files (Markdown runtime/spec text, two unittest files, release notes).
- `authorization`: the git guard is a permission control, but `forge_git_guard.py` and `git-guard-rules.json` are not changed; only an advisory sentence asks hosts to apply the existing `orchestrator` role.
- `public_api`: `forge` CLI code (`src/forge_context_engine/*.py`) untouched.
- `secrets`: no secret handling or redaction text changes.

`policy.require_human_confirmation_for`:
- `external_contract_change`: **match (likely)**. `orchestrate.md` and `forge-planner.md` are packaged runtime templates (`src/forge_context_engine/runtime_templates/base/.forge/runtime/...`) installed into target repos by `forge init`/`forge update`. The change adds a report `Note` value (`orchestrator git guard not confirmed`) that `run.worker: host` hosts read, and fixes the SDD path/status the orchestrator passes to the planner. Same classification as the sibling #12 SDD.
- `security_boundary_change`: **uncertain, treat as match**. R1/R2 state a new expectation that non-Claude hosts enforce the `orchestrator` guard role (security MINOR 3). Enforcement code and rules are unchanged and the note is advisory, so the effective boundary does not move; a human should still confirm the wording because it defines what hosts are expected to block.
- `architecture_boundary_change`: no. No new component or role; the `## roles` table and guard roles are unchanged.
- `domain_rule_change`: no product domain logic.
- `data_mutation_change`: no data store or schema.
- `migration_change`: no migrations.

Gate 1 consequence: per mode step 3 ("If any area matches, or the classification is uncertain, stop with `awaiting_sdd_approval`"), this SDD goes to human approval.

## Specialties
- Orchestrator: `tech-lead` (always).
- Tester: `testing` (always).
- Executor / reviewer: none matched. No `applies_when` for `backend`, `frontend`, `mobile`, or `infrastructure` fits Markdown contract text and unittest files. `security` reviewer: the mode rule keys on "the SDD lists any high-risk area" and this SDD lists none from `policy.high_risk_areas`; recommendation was to run it anyway; Gate 1 decided no extra reviewer (D1).

## Next Step
Gate 1 approved 2026-11-25 (D1). `implementation`: `.forge/generated/ecp/2026-11-24-orchestrate-host-followups-ecp.md`.

## Status
`ready_for_implementation`
