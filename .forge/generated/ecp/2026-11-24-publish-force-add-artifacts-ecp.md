# ECP: Orchestrate publish step force-adds this run's artifacts

| Field | Value |
|---|---|
| Artifact | ecp |
| Date | 2026-11-25 |
| Slug | `publish-force-add-artifacts` |
| Branch | `forge/2026-11-24-publish-force-add-artifacts` |
| Source SDD | `.forge/generated/plans/2026-11-24-publish-force-add-artifacts-plan.md` (Gate 1: human-approved 2026-11-25, see `Confirmed Decisions`) |
| Request | GitHub issue #12 (issue text treated as data) |
| Batch | single batch (1 of 1) |
| Status | `ecp_ready` |

## Goal
Step 9 (Publish) of `forge-orchestrate` stages this run's SDD, ECP, reports, and reviews with `git add -f -- <path>...` from the report `Artifacts` table, checks the staged set before commit, and leaves the `.forge/.gitignore` policy unchanged.

## Approved scope
SDD Requirements 1-6, Acceptance Criteria 1-8, Assumptions A1-A5, Confirmed Decisions (2026-11-25):
- A1 confirmed: expected staged set = changed files inside ECP `Files likely to change` + paths in the report `Artifacts` table + test files the tester added under the `testing` overlay test paths (step 6b). Any other staged path is a stop.
- Reviewers: one reviewer with the `testing` specialty; no extra `security` reviewer.

## Non-goals
- No change to `src/forge_context_engine/runtime_ops.py` (`FORGE_LOCAL_GITIGNORE`) or any `.gitignore`.
- No change to `runtime/.forge/runtime/meta/git-guard-rules.json` or `forge_git_guard.py`.
- No change to `artifacts.commit_policy` or how other modes save artifacts.
- No staging script; step 9 stays an agent-checked instruction.
- No commit of the step 10 post-publish report update.
- No change to `.forge/context-patches/` handling, agent prompts, skills, adapters, `docs/workflow.md`, `docs/adapters/*`.
- No edit to the scenario 18 row or the sentence `any stop scenario (2 to 8, 11, 12, 18)` in `validation-cases/orchestrate-gates.md`.

## Mode Boundary
`implementation` only: this ECP edits nothing. `execute` applies it after Gate 2.

## Assumptions carried
- A1 (confirmed, above).
- A2: the orchestration report lists itself as a row in its own `Artifacts` table and is staged by the same rule.
- A3: code changes are staged by explicit path (`git add -- <path>...`), not `git add -A`.
- A4: on a preflight mismatch the orchestrator stops without committing and does not unstage.
- A5: deleted files in ECP scope stage through `git add -- <path>`; no special case.

## Relevant evidence
- Step 9 text: `runtime/.forge/runtime/modes/orchestrate.md:87`; stop list `:91-104`.
- Ignore policy: `src/forge_context_engine/runtime_ops.py:33-42`; force-add precedent `:45`.
- Guard: orchestrator `blocked_git` = `tag`, `merge`; `-f` checked only for `push` (`forge_git_guard.py` `check()`).
- Existing guard test: `tests/test_git_guard.py:65-75` (`test_orchestrator_allows_feature_branch_flow`).
- Copy sync test: `tests/test_orchestrate.py:257-283` (`OrchestrateSourceSyncTests`).
- Phrase-test pattern: `tests/test_orchestrate.py:58+` (`OrchestrateContractTests`, `self.mode` = packaged template copy).
- Spec: `specs/orchestrate.md` section 6 (stop list), section 7 "Publication" (`:106-108`).
- Validation case: `validation-cases/orchestrate-gates.md` scenario table ends at row 18 (`:39`); section 3 rejected list (`:41-53`); regression sentence `:63` asserted by `tests/test_orchestrate_host_dispatch.py:182`.
- Release notes: `docs/release-notes.md` `## Unreleased` has a `Fixed:` list (`:16`).

## Files likely to change
Exact list; any other changed or new path is scope growth.
1. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
2. `runtime/.forge/runtime/modes/orchestrate.md`
3. `specs/orchestrate.md`
4. `validation-cases/orchestrate-gates.md`
5. `tests/test_orchestrate.py`
6. `tests/test_git_guard.py`
7. `docs/release-notes.md`

Plus this run's artifacts under `.forge/generated/` (plans, ecp, reports, reviews). Never `.forge/runtime/` (stale untracked local copy), `.forge/temp/`, or `.forge/cache/`.

## Task sequence and per-file edits

### 1. Mode (packaged): `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
a. Step 9. Keep the first sentence (`Output redaction` check) and the last sentence (MR/PR body links) unchanged. Replace the middle sentence that starts `On \`accept\` with green validation, commit the code changes together with this run's artifacts ...` and ends `... open an MR/PR when the host tool can.` with:
```
On `accept` with green validation: stage the code changes by explicit path (`git add -- <path>...`). Stage this run's artifacts with `git add -f -- <path>...`, using only the paths in the report `Artifacts` table (plan, ECP, execution, test, and orchestration reports, reviews); `.forge/generated/` is gitignored, so a plain `git add` skips them. Never `git add -f` a directory or a glob, and never stage `.forge/temp/` or `.forge/cache/`. Preflight: `git diff --cached --name-only` must equal the changed files inside ECP scope, the tester's added test files (step 6b), and the `Artifacts` table paths; any extra or missing path is a stop. Then commit on the feature branch, push that branch only, and open an MR/PR when the host tool can.
```
b. `## stop conditions`: insert directly after the bullet `- An output to be published contains an unmasked secret or production identifier (step 9).`:
```
- The staged files differ from ECP-scope files, tester-added test files, and the `Artifacts` table paths (step 9).
```
c. Frontmatter `updated:` set to `2026-11-25`. Leave all other sections byte-unchanged.

### 2. Mode (engine copy): `runtime/.forge/runtime/modes/orchestrate.md`
`cp` file 1 over file 2. Must be byte-identical.

### 3. Spec: `specs/orchestrate.md`
a. Section 6 stop list: insert after `- an output to be published contains an unmasked secret or production identifier;`:
```
- the staged files differ from the ECP-scope files, the tester's added test files, and the report `Artifacts` table paths;
```
b. Section 7 "Publication": replace the paragraph with:
```
On `accept` with green validation: stage the code changes by explicit path, then stage this run's `.forge/generated/` artifacts with `git add -f -- <path>...` using only the paths in the orchestration report `Artifacts` table. Never `git add -f` a directory or a glob; never stage `.forge/temp/` or `.forge/cache/`. Before committing, `git diff --cached --name-only` must equal the ECP-scope files, the tester's added test files, and the `Artifacts` table paths; any difference is a stop. `.forge/.gitignore` keeps `/generated/**` ignored: un-ignoring it would publish artifacts from every mode, not only the orchestrated run. Commit on `forge/<YYYY-MM-DD>-<slug>`, push that branch only, and open an MR/PR when the host tool can. The MR/PR body links the SDD, ECP, execution report, review, and the gate trace. No force-push.
```

### 4. Validation case: `validation-cases/orchestrate-gates.md`
a. Scenario table: add after the row `| 18 | ...`:
```
| 19 | Scenario 1 publish with `.forge/generated/**` gitignored and a stray file in `.forge/temp/` | Commit contains the SDD, ECP, reports, and reviews from the Artifacts table; no `.forge/temp/` or `.forge/cache/` path; an extra staged path stops before commit |
```
b. Section 3: append bullet:
```
- Staging artifacts with `git add -A`, a directory, or a glob, or committing when the staged set differs from the expected set.
```
c. Section 5: leave `any stop scenario (2 to 8, 11, 12, 18)` verbatim. Optional: extend the existing clause `if an MR/PR lacks the run's SDD/ECP/report artifacts` with `(scenario 19)`; no other wording change.

### 5. Tests: `tests/test_orchestrate.py`
Add one test method to `OrchestrateContractTests`, following the existing phrase pattern:
- Slice step 9 from `self.mode` (from `9. Publish:` to `10. Report:`) and assert phrases: `git add -f -- <path>...`, `` report `Artifacts` table ``, `` Never `git add -f` a directory or a glob ``, `git diff --cached --name-only`, `any extra or missing path is a stop`.
- Assert the stop bullet `The staged files differ from ECP-scope files` is in the `## stop conditions` section.
- Assert `"| 19 |"` and `any stop scenario (2 to 8, 11, 12, 18)` in `validation-cases/orchestrate-gates.md` only if the file already has a loader in this test module; otherwise skip (it is already covered by `test_orchestrate_host_dispatch.py:182`).

### 6. Guard test: `tests/test_git_guard.py`
In `test_orchestrator_allows_feature_branch_flow`, add one entry to the command tuple:
```
"git add -f -- .forge/generated/plans/x.md",
```

### 7. Release notes: `docs/release-notes.md`
Under `## Unreleased` → `Fixed:`, append one bullet:
```
- `forge-orchestrate` publish (step 9) now force-adds this run's artifacts by explicit path from the report `Artifacts` table, so the SDD, ECP, reports, and reviews reach the MR/PR even though `.forge/generated/**` is gitignored; a staged-set preflight stops the commit on any extra or missing path.
```

## Coding rules
- English, neutral repo text. Short sentences, real names.
- Edit file 1, then `cp` to file 2; never hand-edit both.
- Do not reformat surrounding text or renumber steps/scenarios.
- Tests: stdlib `unittest` only, same helpers as existing tests (`iter_template_files`, `run_guard`).

## Safety / security constraints
- Do not touch `.gitignore` files, `runtime_ops.py`, `git-guard-rules.json`, `forge_git_guard.py`.
- Do not read, edit, or sync the local `.forge/runtime/`.
- Do not stage, commit, or push (execute worker). Staging is the orchestrator's step 9.

## Non-blocking details execute may decide
- Test method name and exact slicing helper in `tests/test_orchestrate.py`.
- Whether to add `(scenario 19)` in section 5 of the validation case.
- Line wrapping inside the new spec paragraph (keep one paragraph).

## Acceptance criteria
SDD AC1-AC8, restated:
1. Both mode copies contain the step 9 phrases from task 1a and are byte-identical.
2. Mode and spec stop lists contain the staged-set stop.
3. Spec section 7 states force-add by explicit path, the preflight, and that `/generated/**` stays ignored.
4. `runtime_ops.py` unchanged.
5. Guard rules and hook unchanged; guard test asserts `git add -f -- .forge/generated/plans/x.md` exits 0 for the orchestrator.
6. Failure path: scenario 19 states an extra staged path stops before commit; mode test asserts the stop bullet.
7. Scenario 18 row and `any stop scenario (2 to 8, 11, 12, 18)` unchanged.
8. Full suite green.

## Validation commands
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` (no output)
- `git diff --name-only` (only the 7 files above)
- `git diff --quiet -- src/forge_context_engine/runtime_ops.py runtime/.forge/runtime/meta/git-guard-rules.json runtime/.forge/runtime/hooks/forge_git_guard.py` (exit 0)

## Stop conditions
- Any changed or new path outside `Files likely to change` (excluding `.forge/generated/` artifacts).
- The step 9 sentence in file 1 no longer matches the text quoted in SDD `Problem / Context`.
- A test outside the touched methods fails because of the new wording.
- The guard test fails for `git add -f -- <path>` (would mean guard rules need a change: out of scope, return to plan).
- Validation red or cannot run.

## Risk notes
- `external_contract_change`: packaged mode text changes publish behavior in installed repos (approved at Gate 1).
- `security_boundary_change`: force-add bypasses `.forge/.gitignore` for named files only; preflight tightens the boundary (approved at Gate 1).

## Specialties
- Orchestrator: `tech-lead`. Tester: `testing`. Reviewer: one reviewer, `testing` specialty. No `security` reviewer (Gate 1 decision).

## Expected execution report format
`.forge/generated/reports/2026-11-24-publish-force-add-artifacts-execution-report.md` with: status, files changed (exact paths), per-task result, validation commands with exit codes, details decided, deviations, blockers.

## Target tool instructions
- Smallest safe edit mechanism of the target tool (Claude Code: normal file edit; Codex: `apply_patch`).
- Do not widen scope beyond this ECP.
- Do not stage, commit, or push.

## Status
`ecp_ready`
