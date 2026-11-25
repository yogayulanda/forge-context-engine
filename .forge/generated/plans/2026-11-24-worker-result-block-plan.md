# SDD: Worker handoff envelope and result block

| Field | Value |
|---|---|
| Artifact | sdd |
| Request | GitHub issue #13 "Orchestrate: worker handoff envelope and result block" |
| Date | 2026-11-24 |
| Depends on | #7 (`run.worker: host`, merged on `master` as `1f3f632`) |
| Stack neighbours | #12 (step 9 force-add, `8cd3478`), #14 (adapter external-context evidence, `5d3c250`), #8 (host status/question contract, `1319553`); all three are below this branch |
| Gate 1 | human-approved 2026-11-25 (batch decision, see `Confirmed Decisions`) |

## Plan type selected
SDD.

## Reason
The change defines a new text contract between the orchestrator and every worker. The contract ships in packaged runtime templates that `forge init` / `forge update` install into target repositories, and hosts (`run.worker: host`) will parse it. That is an external-contract change under `policy.require_human_confirmation_for`.

## Mode Boundary
Plan mode, read-only. No code, template, or test file is edited. Only this SDD is written.

## Goal
Every worker hands its result back in one fixed `FORGE_RESULT` block, and every `cli` / `host` dispatch sends one fixed `FORGE_HANDOFF` envelope, so the orchestrator reads status, verdict, and artifact path from stable fields instead of parsing prose.

## Problem / Context
- `cli` dispatch defines only "a prompt file under `.forge/temp/orchestrate/` that points to the role prompt and lists the inputs" and "Read the worker result from the artifact path it reports" (`runtime/.forge/runtime/modes/orchestrate.md:69`). No field names.
- `host` dispatch says the worker output is "its artifacts under `.forge/generated/` plus the worker result the host passes in" (`orchestrate.md:71`). The shape of that worker result is undefined.
- Each worker's `## Return to orchestrator` is a free-form bullet list:
  - planner: artifact path, mode status, high-risk list (`runtime/.forge/runtime/agents/forge-planner.md:89-93`);
  - executor: report path, execute status, changed files, validation, deviations, blockers (`forge-executor.md:42-43`);
  - tester: report path, verdict `pass|fail|blocked_by_environment`, failing scenarios, full-suite result, files added (`forge-tester.md:54-55`);
  - reviewer: review text, verdict `accept|request_changes|needs_more_validation|blocked`, findings, flags (`forge-reviewer.md:49-50`). The reviewer writes no file; the orchestrator saves the review (`forge-reviewer.md:37`).
- Under `host`, the result often arrives as a short summary through the host, so each host parses prose differently.

## Requirements
R1. One `FORGE_HANDOFF` envelope used by `cli` and `host` dispatch; `subagent` may use it. Fields:
```text
FORGE_HANDOFF
role: planner | executor | tester | reviewer
prompt: .forge/runtime/agents/forge-<role>.md
specialties: <overlay paths, comma-separated> | none
request: <one line: the request, or the step asked, for example "write the ECP from the SDD">
inputs: <artifact paths: SDD, ECP, execution report, test report, prior review, prior test report> | none
fix_scope: <failing scenarios and review findings, each with its source artifact path> | none
fresh_context: true | false
branch: forge/<YYYY-MM-DD>-<slug>
base: <base commit short sha>
END_FORGE_HANDOFF
```
`fresh_context` is always `true` for tester and reviewer. `fix_scope` is `none` outside a fix round (step 8).

R2. One `FORGE_RESULT` block every worker ends its output with:
```text
FORGE_RESULT
role: planner | executor | tester | reviewer
status: done | blocked | blocked_by_decision | blocked_by_environment
verdict: accept | request_changes | needs_more_validation | pass | fail | n/a
artifact: <path under .forge/generated/> | none
changed_files: <count>
note: <one line>
END_FORGE_RESULT
```
The block is at most 1000 characters and is the last text of the output. Details stay in the artifact.

R3. `modes/orchestrate.md` reads each worker result from the block first, then from the artifact it names. A missing block, a block that is not the last text, a field outside the allowed values, or a block over 1000 characters counts as `blocked`.

R4. `## Return to orchestrator` in the four worker prompts is replaced by the block, with that role's allowed values.

R5. Tests assert that the four worker prompts and the mode use the same block markers and field names, and that the mode states the `blocked` rule.

R6. Both copies of every changed runtime file stay byte-identical (`tests/test_orchestrate.py:300-320`, `OrchestrateSourceSyncTests`).

## Non-goals
- No transport, no host tool definition, no parser code (issue #13 non-goals).
- No new orchestrate status value, no new stop-condition bullet: a missing or malformed block maps to the existing stop "A worker returns a blocking unknown, `blocked`, or `blocked_by_decision`." (`orchestrate.md:106`).
- No host status events, stage IDs, or question relay (#8, already in the tree). The workers' `## Host status` sections and the mode's `## host status and questions` section stay byte-identical; `FORGE_RESULT` `status` is the worker's result to the orchestrator, not a host state.
- No change to step 9 or its staging rules (#12), to `.forge/adapter.md` (#14), or to resume semantics (#16).
- No new validation scenario in `validation-cases/orchestrate-gates.md`: a missing or malformed block routes to the existing `blocked` stop, which stop scenarios already exercise. Scenarios 19 (#12) and 20 to 22 (#8) are in the tree; a later scenario would be 23. The regression sentence `any stop scenario (2 to 8, 11, 12, 18)` is asserted verbatim (`tests/test_orchestrate_host_dispatch.py`, `tests/test_orchestrate.py` `test_spec_and_validation_cover_question_tool_path`) and stays unchanged.
- No change to Claude wrappers `runtime/adapters/claude/agents/forge-<role>.md` (they only point to the neutral prompt; checked).
- No edits to the untracked local `.forge/runtime/` copy.

## Current Evidence
| Claim | Evidence |
|---|---|
| `cli` prompt file has no defined fields | `runtime/.forge/runtime/modes/orchestrate.md:69` |
| `host` worker result has no defined shape | `orchestrate.md:70-71` |
| Return lists are free-form, one per role | `runtime/.forge/runtime/agents/forge-{planner,executor,tester,reviewer}.md` `## Return to orchestrator` |
| Reviewer writes no file; orchestrator saves the review | `forge-reviewer.md:37`, `## Do NOT` |
| Tester `blocked_by_environment` for e2e continues when unit, integration, full suite are green | `orchestrate.md:95` (step 6b) |
| Fix scope = failing scenarios + review findings + ECP | `orchestrate.md:97` (step 8) |
| Existing stop already covers a `blocked` worker | `orchestrate.md:106` |
| Runtime and template copies must be byte-identical (mode, 4 agents, wrappers, skill) | `tests/test_orchestrate.py:300-320` |
| Runtime and template agent copies are identical today | `diff -q` of each pair: no output |
| Host tests assert exact phrases in `worker dispatch` that must survive | `tests/test_orchestrate_host_dispatch.py:76-140` (e.g. "the worker result the host passes in", "a worker that ends without a complete report counts as `blocked`") |
| Exactly one `run.worker: host` line in stop conditions; no `host` in status values | `tests/test_orchestrate_host_dispatch.py:142-160` |
| Spec host bullet is asserted verbatim in parts | `tests/test_orchestrate_host_dispatch.py:111-123,169-177`; `specs/orchestrate.md:121` |
| Contract tests read templates via `iter_template_files("base")` | `tests/test_orchestrate.py:58-60` |
| No CI workflow; validation is the unittest suite | no `.github/workflows/`; previous plans use `uv run python -m unittest discover -s tests -q` |
| #8 sections that must survive: mode `## host status and questions` between `## worker dispatch` and `## behavior`; worker `## Host status` between `## Specialty overlays` and `## Role`; status values unchanged | `tests/test_orchestrate.py` `OrchestrateHostInteractionTests`, `tests/test_orchestrate_host_questions.py` |
| Execute and implementation mode statuses the result block maps from | `runtime/.forge/runtime/modes/execute.md:73-78`, `implementation.md` `## status values`, `plan.md:101-104` |
| `.forge/context` has no orchestrate facts | grep of `04-interfaces-and-contracts.md`, `14-...`, `99-open-questions.md`: no hit |

## Affected Surface Inventory
Change:
- `runtime/.forge/runtime/modes/orchestrate.md`: new `## worker handoff` section right after `## worker dispatch` and before `## host status and questions` (#8 order test stays green); one sentence each in the `cli` bullet (line 69) and `host` bullet (line 70) pointing to it.
- `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`: identical copy.
- `runtime/.forge/runtime/agents/forge-planner.md`, `forge-executor.md`, `forge-tester.md`, `forge-reviewer.md`: replace `## Return to orchestrator` body.
- `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-planner.md`, `forge-executor.md`, `forge-tester.md`, `forge-reviewer.md`: identical copies.
- `specs/orchestrate.md`: section 8 "Worker configuration": one short paragraph on envelope and result block, after the `host` bullet (bullet text unchanged).
- `tests/test_orchestrate.py`: new tests in `OrchestrateContractTests`.
- `docs/release-notes.md`: one bullet under `## Unreleased`.

Checked, no change: `runtime/skills/forge-orchestrate/SKILL.md`, `runtime/adapters/claude/commands/forge-orchestrate.md`, `runtime/adapters/claude/agents/forge-*.md` (no return-format text), `validation-cases/orchestrate-gates.md` (see Non-goals), `tests/test_orchestrate_host_dispatch.py` (its phrases are kept).

## Assumptions
- A1. Role mapping into `status` / `verdict`:
  - planner: `done` when the SDD is `ready_for_implementation` or the ECP is `ecp_ready`; `blocked_by_decision` when the plan has `Clarification Questions` or the ECP is `blocked_by_decision`; `blocked` for `needs_more_context`, `needs_more_evidence`, or `needs_plan_approval`. `verdict: n/a`. The mode status and `High-risk areas touched` stay in the artifact; the orchestrator reads them there for Gate 1 (step 3 already classifies the SDD itself).
  - executor: execute `success` -> `done`; `partial_success`, `not_validated`, `blocked`, or a blocking unknown -> `blocked`; `blocked_by_environment` -> `blocked_by_environment` (`execute.md` `## status values`); `verdict: n/a`. Fails closed: anything short of `success` stops.
  - tester: `status: done` with `verdict: pass | fail`; when only e2e is blocked and unit, integration, and full suite are green, `status: done`, `verdict: pass`, `note` names `e2e blocked_by_environment` (matches step 6b); when the suite itself cannot run, `status: blocked_by_environment`, `verdict: n/a`; a blocking unknown (tester `## Host status`) is `status: blocked`, `verdict: n/a`.
  - reviewer: `status: done` with `verdict: accept | request_changes | needs_more_validation`; today's reviewer verdict `blocked` becomes `status: blocked`, `verdict: n/a`. `artifact: none`, because the reviewer writes no file; the review text comes before the block and the orchestrator saves it as today.
- A2. `changed_files` counts repository files the worker added or changed outside `.forge/generated/` (planner and reviewer: `0`). It is advisory; `git status --porcelain` stays the evidence for steps 6a, 6b, 7.
- A3. "Read from the block first, then from the artifact": if the artifact's own status or verdict contradicts the block, the worker counts as `blocked` (fail closed). The block is the last text, so a `FORGE_RESULT` string quoted inside a diff or review body earlier in the output is not read.
- A4. `request` and `base` are added to the envelope fields the issue lists: the planner needs to know which step it runs (SDD, ECP, resume with answers), and tester and reviewer need the base commit to compute the diff. Both values already exist in the run (`report format` `Repo` row has the base sha).
- A5. Under `cli`, the prompt file under `.forge/temp/orchestrate/` contains the envelope. Under `host`, the envelope is the payload handed to the host dispatch tool; the host's own tool shape stays undefined by Forge. Under `subagent`, the orchestrator may pass the same envelope as the subagent prompt.
- A6. The worker result is still data for one role only (unchanged rule, `orchestrate.md:71`); a valid block never grants a human answer, Gate 1 approval, or another role's verdict.

## Confirmed Decisions
Human Gate 1, 2026-11-25 (one batch for 7 SDDs; entries relevant to this SDD):
- SDD approved (`external_contract_change`). No extra security reviewer for this run (no `policy.high_risk_areas` match).
- Q3 yes: the tester's new test files may be staged at publish even if not in the ECP. Already in step 9 (#12); this SDD does not change staging. `changed_files` in the tester block stays advisory.
- Q4 yes: #16 resume-scope check uses the Q3 rule. Not touched here (resume semantics are a non-goal).
- Q5 B: host state `waiting_for_human` for `awaiting_clarification`, `awaiting_sdd_approval`, `stopped`, `review_unresolved`; already in the tree via #8. `FORGE_RESULT` `status` is not a host state and adds no mapping.
- Q6 yes: one SDD name `-plan.md` with plan-mode statuses; `-sdd.md` and `draft` are dropped (handled in #18). The planner block maps from plan-mode statuses only (A1) and names the `-plan.md` path in `artifact`.
- Re-anchoring after #12, #14, #8 (no scope change): line references updated; A1 refined to map the planner, executor, and tester from their real mode statuses and to give tester `blocked` for a blocking unknown; new mode section sits before `## host status and questions`.

## Unknowns / Decisions Needed
- None blocking. A1 and A3 carry the only code-level choices; both follow existing mode text (step 6b, existing `blocked` stop) and fail closed. They can be corrected at Gate 1.

## Architecture / System Impact
- Text contract in shipped runtime templates; no Python runtime code changes. Installed repos get it on `forge update`.
- Hosts and `cli` wrappers gain a stable, parseable shape. Hosts that already pass free text will now cause `blocked` until their workers end with the block; this is the intended fail-closed behaviour and should be named in the release note.
- Conflict surface with the stack: #12 edits step 9 and `## stop conditions` of the same mode file and adds validation scenario 19; #8 likely edits the `host` bullet or adds a host-status section. This SDD touches only the `cli` / `host` bullets (one appended sentence each), a new `## worker handoff` section, and the agents' `## Return to orchestrator`. Expect textual rebase conflicts only if #8 rewrites lines 69-70.

## Risk Areas
- Drift between the five places that state field names (mode + four prompts) x two copies. Mitigation: R5 tests plus the existing byte-identity test.
- Breaking existing host-dispatch phrase tests. Mitigation: append sentences; do not reword asserted phrases.
- Spoofed result via quoted text. Mitigation: last-text rule (A3).
- Over-long block. Mitigation: 1000-character rule; over-long = `blocked`.

## Proposed Approach
1. Mode (both copies), new section after `## worker dispatch`:
   `## worker handoff` with the R1 envelope, the R2 block, and these rules: `cli` and `host` dispatch send the envelope, `subagent` may; tester and reviewer get `fresh_context: true`; every worker ends with the block; read the result from the block first, then from the artifact it names; a missing block, a block that is not the last text, a value outside the listed ones, a block over 1000 characters, or a block that contradicts its artifact counts as `blocked`; `changed_files` is advisory and `git status --porcelain` stays the evidence.
2. Mode `cli` bullet: replace "Read the worker result from the artifact path it reports." with "The prompt file holds the `FORGE_HANDOFF` envelope; read the worker result as defined in `worker handoff`." Mode `host` bullet: append "Send the `FORGE_HANDOFF` envelope; the worker result is the `FORGE_RESULT` block (`worker handoff`)." Keep every phrase asserted in `tests/test_orchestrate_host_dispatch.py`.
3. Each worker prompt (both copies): `## Return to orchestrator` becomes: "End your output with this block, at most 1000 characters, nothing after it. Details stay in the artifact." followed by the block with that role's allowed values from A1 (reviewer: "Put the full review text before the block; `artifact: none`.").
4. `specs/orchestrate.md` section 8: one paragraph after the `host` bullet naming `FORGE_HANDOFF` / `FORGE_RESULT`, their fields, and the `blocked` rule; points to the mode for the exact shape.
5. `docs/release-notes.md` Unreleased: one bullet: worker handoff envelope and `FORGE_RESULT` block for `forge-orchestrate`; a worker result without a valid block counts as `blocked`.
6. Tests in `tests/test_orchestrate.py` (`OrchestrateContractTests`, read from `iter_template_files("base")`):
   - every worker prompt's `## Return to orchestrator` contains `FORGE_RESULT`, `END_FORGE_RESULT`, and the six field names `role:`, `status:`, `verdict:`, `artifact:`, `changed_files:`, `note:`, in that order, plus `1000 characters`;
   - each prompt's `role:` line names its own role; reviewer's has `artifact: none`;
   - the mode's `## worker handoff` contains the same six result fields and the envelope fields `role`, `prompt`, `specialties`, `request`, `inputs`, `fix_scope`, `fresh_context`, `branch`, `base`, and the `blocked` rule phrase;
   - failure path: the mode's `## status values` gains no new value and `## stop conditions` gains no new bullet (count unchanged), so a malformed block routes to the existing `blocked` stop.

## MVP Path
Same as full: text plus phrase tests in one batch.

## Full-Version Path
Later, outside this request: a parser or validator script for the block (non-goal in #13), and host status events from #8 referencing `role` values.

## Acceptance Criteria
1. Both mode copies contain `## worker handoff` with the envelope (9 fields) and the result block (6 fields), and are byte-identical.
2. All four worker prompts (both copies) end `## Return to orchestrator` with a `FORGE_RESULT` ... `END_FORGE_RESULT` block using the same six field names as the mode, with role-specific values per A1.
3. The mode states: block first, then artifact; missing, not-last, out-of-range, over 1000 characters, or contradicting its artifact = `blocked`.
4. Failure path: no new status value and no new stop-condition bullet; `tests/test_orchestrate_host_dispatch.py` passes unchanged.
5. `specs/orchestrate.md` section 8 names both markers; the `host` bullet text is unchanged.
6. `OrchestrateSourceSyncTests.test_runtime_copies_match_templates` passes.
7. Full suite green.

## Validation Commands
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `for r in planner executor tester reviewer; do diff runtime/.forge/runtime/agents/forge-$r.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-$r.md; done`
- `git status --porcelain` (must list only the files in the Affected Surface Inventory plus this run's artifacts)

## Implementation Split
One batch: all files share one outcome and one validation command.

## High-risk areas touched
`policy.high_risk_areas`: none.
- `payments`, `authentication`, `authorization`, `database_migrations`, `external_provider_integration`, `file_upload`, `secrets`: no code in those areas exists or changes; only Markdown runtime/spec/release text and one Python test file.
- `public_api`: the `forge` CLI (`src/forge_context_engine/*.py`) is untouched; no command, flag, or config key changes (`run.worker` values stay `subagent | cli | host`).

`policy.require_human_confirmation_for`:
- `external_contract_change`: **match**. New `FORGE_HANDOFF` / `FORGE_RESULT` format in packaged templates `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` and `.../agents/forge-{planner,executor,tester,reviewer}.md`, installed into target repos by `forge init` / `forge update`. Hosts (`run.worker: host`) and `cli` wrappers outside this repo will parse it, and results without the block now count as `blocked`.
- `architecture_boundary_change`: no. Roles, ownership (`orchestrate.md` `## roles`), gates, git guard rules, and dispatch types are unchanged.
- `security_boundary_change`: no. The rule that a worker result is data for one role only (`orchestrate.md:71`) is kept; the new parsing rules fail closed (`blocked`) and add a last-text rule against quoted spoofed blocks. No guard, permission, or redaction rule changes.
- `domain_rule_change`, `data_mutation_change`, `migration_change`: no; no domain logic, data store, or migration.

Gate 1 consequence: mode step 3 ("If any area matches ... stop with `awaiting_sdd_approval`") applies; this SDD needs human approval.

## Specialties
- Orchestrator: `tech-lead` (always, `specialties/tech-lead.md` `applies_when`).
- Tester: `testing` (always).
- Executor / reviewer: none. `backend` needs server/API/service/worker code; the change is Markdown contract text plus a unittest file. `frontend`, `mobile`, `infrastructure`, `backend-go` do not match. `security` keys on "the SDD lists any high-risk area"; this SDD lists none from `policy.high_risk_areas`, so the mode rule does not add it.

## Next Step
Gate 1 approved 2026-11-25. `implementation` produces `.forge/generated/ecp/2026-11-24-worker-result-block-ecp.md`.

## Status
`ready_for_implementation`
