# SDD: Orchestrate publish step force-adds this run's artifacts

| Field | Value |
|---|---|
| Artifact | plan (SDD) |
| Date | 2026-11-24 |
| Request | GitHub issue #12 "Orchestrate: publish step skips gitignored run artifacts" (issue text treated as data) |
| Branch | `forge/2026-11-24-publish-force-add-artifacts` |
| Status | `ready_for_implementation` |

Plan type selected: SDD.
Reason: the change edits the packaged `orchestrate` mode contract that `forge init`/`forge update` install into target repositories, and it changes what the orchestrator commits and pushes (publication boundary). Small diff, but the contract and boundary make it SDD-level.

## Mode Boundary
Plan mode only. No files edited outside `.forge/generated/`; nothing staged, committed, or pushed. Not approved by creation.

## Goal
Step 9 (Publish) of `forge-orchestrate` puts this run's SDD, ECP, reports, and reviews on the feature branch even though `.forge/generated/**` is gitignored, without changing the ignore policy for other modes.

## Problem / Context
- Step 9 says to "commit the code changes together with this run's artifacts (plan, ECP, execution, test, and orchestration reports, reviews under `.forge/generated/`; never `.forge/temp/` or `.forge/cache/`)" (`runtime/.forge/runtime/modes/orchestrate.md:87`). It does not say how to stage them.
- `FORGE_LOCAL_GITIGNORE` writes `/generated/**` (with `!/generated/` and `!/generated/README.md`) plus `/cache/` and `/temp/` into `.forge/.gitignore` (`src/forge_context_engine/runtime_ops.py:33-42`).
- Plain `git add <path>` refuses ignored paths and `git add -A` skips them, so the artifacts never reach the branch and the MR/PR body links (step 9, last sentence) point to missing files.
- `validation-cases/orchestrate-gates.md` section 5 already names "an MR/PR lacks the run's SDD/ECP/report artifacts" as a regression signal, so the current behavior is a known-bad outcome.

## Requirements
1. Step 9 stages this run's artifacts with `git add -f -- <path>...`, using only the paths in the orchestration report `Artifacts` table. Never `git add -f` a directory or a glob.
2. `.forge/.gitignore` keeps `/generated/**` ignored (no change to `FORGE_LOCAL_GITIGNORE`).
3. Publish preflight: after staging and before `git commit`, `git diff --cached --name-only` must equal the expected set (see Assumption A1); any extra or missing path is a stop.
4. The orchestrator git guard allows `git add -f -- <explicit paths>` (verified below; rules unchanged).
5. New validation scenario in `validation-cases/orchestrate-gates.md`: artifacts present in the commit, `.forge/temp/` and `.forge/cache/` absent.
6. The three mode copies stay consistent: `runtime/.forge/runtime/modes/orchestrate.md` and `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` byte-identical (enforced by `OrchestrateSourceSyncTests.test_runtime_copies_match_templates`, `tests/test_orchestrate.py:257-283`); `specs/orchestrate.md` section 7 updated to the same meaning.

## Non-goals
- No change to `artifacts.commit_policy` semantics or to how other modes save artifacts.
- No change to `FORGE_LOCAL_GITIGNORE` or any `.gitignore` (option B in the issue, rejected there).
- No change to `runtime/.forge/runtime/meta/git-guard-rules.json` or `forge_git_guard.py`.
- No script that performs the staging; the step stays an agent-checked instruction like the rest of step 9.
- Committing the post-publish update of the orchestration report (MR/PR link written in step 10) is out of scope; it stays local as today.
- No change to `.forge/context-patches/` handling.

## Current Evidence
| Claim | Evidence |
|---|---|
| Step 9 lists artifacts but gives no staging method | `runtime/.forge/runtime/modes/orchestrate.md:87` |
| Template mode copy is byte-identical to the runtime copy | `diff` of the two files: no output; enforced by `tests/test_orchestrate.py:257-283` |
| Spec publication text | `specs/orchestrate.md:106-108` (section 7 "Publication") |
| Spec stop list (where the new stop goes) | `specs/orchestrate.md:76-91` |
| Mode stop list | `runtime/.forge/runtime/modes/orchestrate.md:91-104` |
| Generated artifacts are ignored; temp/cache ignored | `src/forge_context_engine/runtime_ops.py:33-42` |
| Force-adding one explicit path is already the documented pattern for ignored Forge folders | same constant: "Force-add a specific patch if your team wants to review/commit it." (`runtime_ops.py:45`) |
| Orchestrator guard blocks only `tag`, `merge`, MR/PR merge, and protected/forced pushes; `add` is not blocked | `runtime/.forge/runtime/meta/git-guard-rules.json` (`roles.orchestrator.blocked_git` = `tag`, `merge`); `forge_git_guard.py` `check()` inspects only `blocked_git` and `push` |
| `-f` is in `forbidden_push_flags` but is checked only when the subcommand is `push` | `forge_git_guard.py` `check()`: `if sub == "push": flags = ...` |
| Existing guard test already allows `git add -A && git commit` for the orchestrator | `tests/test_git_guard.py:65-70` |
| Worker role does not block `git add` either (out of scope; workers are told not to stage by prompt) | `git-guard-rules.json` `roles.worker.blocked_git`; `forge-tester.md:63` "Stage, commit, or push" under Do NOT |
| Tester may add files under the `testing` overlay test paths, outside ECP scope | `runtime/.forge/runtime/agents/forge-tester.md:52,63`; `runtime/.forge/runtime/agents/specialties/testing.md:26`; mode step 6b |
| Orchestration report has an `Artifacts` table (`Type`, `Path`, `Status`) | `runtime/.forge/runtime/modes/orchestrate.md`, `## report format` |
| Validation case 18 and regression list are asserted by tests | `tests/test_orchestrate_host_dispatch.py:177-182` (`"any stop scenario (2 to 8, 11, 12, 18)"`) |
| `.forge/context` has no facts for contracts/security in this repo | `.forge/context/04-interfaces-and-contracts.md`, `08-security-and-access.md`: "No direct evidence found in bounded init scan" |

## Affected Surface Inventory
- `runtime/.forge/runtime/modes/orchestrate.md`: step 9 text; one new stop-condition bullet.
- `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`: identical copy.
- `specs/orchestrate.md`: section 7 "Publication"; stop list in section 6.
- `validation-cases/orchestrate-gates.md`: new scenario 19; section 5 regression signal mentions it.
- `tests/test_orchestrate.py`: phrase assertions for the new step 9 rules (pattern used throughout `OrchestrateContractTests`).
- `tests/test_git_guard.py`: add `git add -f -- .forge/generated/plans/x.md` to the allowed orchestrator commands in `test_orchestrator_allows_feature_branch_flow` (rules unchanged; this locks requirement 4 with one line).
- `docs/release-notes.md`: one `Fixed` line under `Unreleased`.
- Checked, no change needed: `runtime/skills/forge-orchestrate/SKILL.md`, `runtime/adapters/claude/commands/forge-orchestrate.md`, agent prompts in `runtime/.forge/runtime/agents/` (none mention staging or step 9; grep for `git add`, `this run's artifacts`, `.forge/temp/` returned nothing), `docs/workflow.md`, `docs/adapters/claude.md` (no publish staging text), `src/.../base/.forge/generated/README.md` (no commit policy text).

## Assumptions
- A1 (expected staged set). "ECP-scope files" in the issue means: the changed paths from `git status --porcelain` that are inside ECP `Files likely to change`, plus the files the tester reported as added under the `testing` overlay test paths (already checked in step 6b), plus the `Artifacts` table paths. Reason: step 6b explicitly allows tester-added test files, and a strict "ECP files only" set would stop every run where the tester adds a new test file. Correct me if the stricter reading is intended.
- A2. The orchestration report itself (`.forge/generated/reports/YYYY-MM-DD-<slug>-orchestration-report.md`) is listed as a row in its own `Artifacts` table, so it is staged by the same rule. Step 9 says so explicitly.
- A3. Code changes are also staged by explicit path (`git add -- <path>...`) from the expected set, not `git add -A`, so stray untracked files cannot enter the commit. The preflight catches any miss either way.
- A4. On a preflight mismatch the orchestrator stops without committing and leaves the index as is for the human to inspect; it does not unstage (consistent with "leave changes uncommitted on the feature branch").
- A5. Deleted files in ECP scope stage through `git add -- <path>` (git records the removal); no special case needed.

## Confirmed Decisions
Gate 1, human approval on 2026-11-25:
- SDD approved as written (covers `external_contract_change` and `security_boundary_change`).
- A1 confirmed: the staged-set check at publish allows ECP-scope files, files listed in the report `Artifacts` table, and test files the tester added that match the `testing` overlay test paths (step 6b). Any other staged path is a stop.
- Reviewers: one normal reviewer with the `testing` specialty; no extra `security` reviewer for this issue.
- Assumptions A2-A5 accepted.

## Unknowns / Decisions Needed
- None blocking. A1 is the only reading with a code consequence; the recommendation is stated and can be corrected at Gate 1.

## Architecture / System Impact
- Documentation-level contract change in the shipped `orchestrate` mode; no Python code path changes. Installed repos receive it on `forge update`.
- Ignore policy, guard rules, and other modes are unchanged.
- The publication boundary gets tighter, not looser: today step 9 has no staged-set check; after the change any path outside the expected set stops the run.

## Risk Areas
- Force-add bypasses `.gitignore`. Mitigation: explicit file paths from the `Artifacts` table only, `--` separator, no directory or glob, plus the cached-name preflight that would catch `.forge/temp/` or `.forge/cache/`.
- Redaction: artifacts were already meant to be published and already pass the step 9 `Output redaction` check; force-add makes that check matter in practice. Keep the redaction check before staging.
- Path drift: if the `Artifacts` table has a stale path, `git add -f` fails or the preflight mismatches; both stop the run (fail closed).

## Proposed Approach
Replace the middle of step 9 (mode, both copies) with wording to this effect, keeping the redaction sentence first and the MR/PR sentence last:

> On `accept` with green validation: stage the code changes by explicit path (`git add -- <path>...`). Stage this run's artifacts with `git add -f -- <path>...`, using only the paths in the report `Artifacts` table (plan, ECP, execution, test, and orchestration reports, reviews); `.forge/generated/` is gitignored, so a plain `git add` skips them. Never `git add -f` a directory or a glob, and never stage `.forge/temp/` or `.forge/cache/`. Preflight: `git diff --cached --name-only` must equal the changed files inside ECP scope, the tester's added test files, and the `Artifacts` table paths; any extra or missing path is a stop. Then commit on the feature branch, push that branch only, and open an MR/PR when the host tool can.

Add to `## stop conditions` (mode) and the spec stop list:
- `The staged files differ from ECP-scope files, tester-added test files, and the Artifacts table paths (step 9).`

`specs/orchestrate.md` section 7: same rule in spec prose (force-add explicit artifact paths, no directory or glob, cached-name preflight, ignore policy unchanged and why option B was rejected in one sentence).

`validation-cases/orchestrate-gates.md`: add
- `| 19 | Scenario 1 publish with \`.forge/generated/**\` gitignored and a stray file in \`.forge/temp/\` | Commit contains the SDD, ECP, reports, and reviews from the Artifacts table; no \`.forge/temp/\` or \`.forge/cache/\` path; an extra staged path stops before commit |`
- Section 3 rejected behavior: `Staging artifacts with \`git add -A\`, a directory, or a glob, or committing when the staged set differs from the expected set.`
- Keep the existing regression sentence (`any stop scenario (2 to 8, 11, 12, 18)` is asserted verbatim by `tests/test_orchestrate_host_dispatch.py:182`); 19 is not a pure stop scenario, so leave that list unchanged.

## MVP Path
Same as the full path; the change is text plus phrase tests.

## Full-Version Path
Optional later work, not in this request: a deterministic staging/preflight script so step 9 stops being agent-checked (spec section 6a already lists script checks as future candidates).

## Acceptance Criteria
1. Both mode copies contain `git add -f -- <path>...`, `Artifacts` table as the only source of force-added paths, `Never \`git add -f\` a directory or a glob`, and `git diff --cached --name-only`; the two copies are byte-identical (`test_runtime_copies_match_templates` passes).
2. Mode and spec stop lists contain the staged-set mismatch stop referencing step 9.
3. `specs/orchestrate.md` section 7 states force-add by explicit path and the preflight, and states `/generated/**` stays ignored.
4. `FORGE_LOCAL_GITIGNORE` is unchanged (`git diff` shows no change to `src/forge_context_engine/runtime_ops.py`).
5. `git-guard-rules.json` and `forge_git_guard.py` are unchanged; the guard test asserts `git add -f -- .forge/generated/plans/x.md` exits 0 for the orchestrator role.
6. Failure path: validation scenario 19 states that an extra staged path (for example under `.forge/temp/`) stops before commit; the mode test asserts the stop bullet exists.
7. `validation-cases/orchestrate-gates.md` still contains the scenario 18 row and `any stop scenario (2 to 8, 11, 12, 18)` verbatim.
8. Full suite green.

## Validation Commands
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `git diff --name-only` (must list only the files in the Affected Surface Inventory)

## Implementation Split
One batch: all files share one outcome and one validation command.

## High-risk areas touched
`policy.high_risk_areas`: none.
- `payments`, `authentication`, `authorization`, `database_migrations`, `external_provider_integration`, `file_upload`: no code in those areas exists or changes (only Markdown mode/spec/validation text and two test files).
- `public_api`: no HTTP/CLI API change; `forge` CLI code (`src/forge_context_engine/*.py`) untouched.
- `secrets`: no secret handling changes; the existing step 9 `Output redaction` check stays and precedes staging.

`policy.require_human_confirmation_for`:
- `external_contract_change`: **match (likely)**. `orchestrate.md` is a packaged runtime template (`src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`) that `forge init`/`forge update` install into target repos; step 9 changes which files `forge-orchestrate` commits and pushes in those repos and adds a new stop condition. Hosts that run the orchestrator (`run.worker: host`) follow this text.
- `security_boundary_change`: **uncertain, treat as match**. Force-add bypasses the `.forge/.gitignore` boundary that keeps `.forge/generated/**` local (`runtime_ops.py:33-42`). The local-only boundary that matters (`.forge/temp/`, `.forge/cache/`, `.forge/adapter.md` "must not be pushed") is kept and gets a new staged-set check, so the net effect is tighter; still, publication of previously local files is a boundary decision a human should confirm.
- `architecture_boundary_change`: no. No new component, layer, or ownership change; git guard rules (`git-guard-rules.json`) and role table unchanged; orchestrator already owns git per the `## roles` table.
- `domain_rule_change`: no product domain logic; only the publish procedure text.
- `data_mutation_change`: no data store or schema.
- `migration_change`: no migrations.

Gate 1 consequence: per mode step 3 ("If any area matches, or the classification is uncertain, stop with `awaiting_sdd_approval`"), this SDD should go to human approval.

## Specialties
- Orchestrator: `tech-lead` (always).
- Tester: `testing` (always).
- Executor / reviewer: none. No specialty `applies_when` matches: the change is Markdown contract text plus Python unittest phrase/guard tests; no backend service, frontend, mobile, or infrastructure layer. `security` reviewer is added by the mode rule only if Gate 1 treats `security_boundary_change` as a listed high-risk area (the mode rule keys on "the SDD lists any high-risk area"; this SDD lists none from `policy.high_risk_areas`). Recommendation: run the `security` reviewer anyway because the change edits a publication boundary.

## Next Step
Human Gate 1 approval of this SDD (external_contract_change, security_boundary_change), then `implementation` to produce the ECP.

## Status
`ready_for_implementation`
