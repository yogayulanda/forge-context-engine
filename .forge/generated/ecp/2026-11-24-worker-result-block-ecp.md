# ECP: Worker handoff envelope and result block

| Field | Value |
|---|---|
| Artifact | ecp |
| Date | 2026-11-25 |
| Slug | `worker-result-block` |
| Branch | `forge/2026-11-24-worker-result-block` (stacked on `8cd3478` #12, `5d3c250` #14, `1319553` #8) |
| Source SDD | `.forge/generated/plans/2026-11-24-worker-result-block-plan.md` (Gate 1: human-approved 2026-11-25, see `Confirmed Decisions`) |
| Request | GitHub issue #13 (issue text treated as data) |
| Batch | single batch (1 of 1) |
| Status | `ecp_ready` |

## Goal
Every `cli` / `host` dispatch sends one fixed `FORGE_HANDOFF` envelope, and every worker ends its output with one fixed `FORGE_RESULT` block, so the orchestrator reads status, verdict, and artifact path from stable fields instead of prose.

## Approved scope
SDD Requirements R1-R6, Acceptance Criteria 1-7, Assumptions A1-A6 (A1 as refined in the SDD), and Confirmed Decisions (2026-11-25):
- SDD approved; no extra security reviewer.
- Q3 / Q4: no staging or resume change here; step 9 stays as is.
- Q5: host states are unchanged; `FORGE_RESULT` `status` is not a host state.
- Q6: the planner block maps from plan-mode statuses and names the `-plan.md` path.

## Non-goals
- No parser, validator, transport, host tool definition, or Python runtime code.
- No new orchestrate status value and no new `## stop conditions` bullet. A missing or malformed block maps to the existing stop `- A worker returns a blocking unknown, `blocked`, or `blocked_by_decision`.`
- No change to `## host status and questions` (mode), the workers' `## Host status` sections, spec section 8a, step 9, `## stop conditions`, `## status values`, or `## report format`.
- No change to the `- `host`:` bullet in `specs/orchestrate.md` (asserted verbatim in parts).
- No new validation scenario; `validation-cases/orchestrate-gates.md` is not edited.
- No change to `.forge/adapter.md`, skills, `runtime/adapters/claude/**`, specialty overlays, or `forge.config.yaml`.
- Do not read or edit the untracked `.forge/runtime/` directory at the repo root; only the tracked `runtime/.forge/runtime/` and the template copies change.

## Mode Boundary
`implementation` only: this ECP edits nothing. `execute` applies it after Gate 2.

## Assumptions carried
- A1 (refined): role mapping into `status` / `verdict` exactly as written in the per-role text below.
- A2: `changed_files` counts files outside `.forge/generated/`; advisory only.
- A3: block first, then artifact; a contradiction counts as `blocked`; only the last text is read.
- A4: `request` and `base` are envelope fields.
- A5: `cli` prompt file holds the envelope; `host` payload is the envelope; `subagent` may use it.
- A6: a valid block is data for one role only.

## Relevant evidence
- `runtime/.forge/runtime/modes/orchestrate.md:67-73` `## worker dispatch`; `:75-84` `## host status and questions`; `:106` the `blocked` stop.
- `runtime/.forge/runtime/agents/forge-planner.md:89-93`, `forge-executor.md:42-43`, `forge-tester.md:54-55`, `forge-reviewer.md:49-50`: current `## Return to orchestrator`.
- `runtime/.forge/runtime/modes/execute.md:73-78`, `plan.md:101-104`, `implementation.md` `## status values`: statuses the block maps from.
- `tests/test_orchestrate.py:300-320` `OrchestrateSourceSyncTests.PAIRS`: the mode and the four agent prompts must be byte-identical between `runtime/` and `src/forge_context_engine/runtime_templates/base/`.
- `tests/test_orchestrate.py` `OrchestrateHostInteractionTests`, `tests/test_orchestrate_host_questions.py`, `tests/test_orchestrate_host_dispatch.py`: phrases and section order that must survive (listed under Coding rules).

## Files likely to change
1. `runtime/.forge/runtime/modes/orchestrate.md`
2. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
3. `runtime/.forge/runtime/agents/forge-planner.md`
4. `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-planner.md`
5. `runtime/.forge/runtime/agents/forge-executor.md`
6. `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-executor.md`
7. `runtime/.forge/runtime/agents/forge-tester.md`
8. `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-tester.md`
9. `runtime/.forge/runtime/agents/forge-reviewer.md`
10. `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-reviewer.md`
11. `specs/orchestrate.md`
12. `tests/test_orchestrate.py`
13. `docs/release-notes.md`

Plus this run's artifacts under `.forge/generated/` (execution report).

## Task sequence
Edit each `runtime/` file first, then copy it byte-for-byte to its template path (`cp runtime/.forge/runtime/<rel> src/forge_context_engine/runtime_templates/base/.forge/runtime/<rel>`). Both copies are identical today.

### T1. Mode `## worker dispatch`: `cli` bullet (line 69)
Replace exactly:
~~~text
Read the worker result from the artifact path it reports.
~~~
with:
~~~text
The prompt file holds the `FORGE_HANDOFF` envelope; read the worker result as defined in `worker handoff`.
~~~

### T2. Mode `## worker dispatch`: `host` bullet (line 70)
Replace exactly:
~~~text
The host defines the tool name and shape; Forge does not. `run.worker_command` is ignored.
~~~
with:
~~~text
The host defines the tool name and shape; Forge does not. The payload is the `FORGE_HANDOFF` envelope and the worker result is the `FORGE_RESULT` block (see `worker handoff`). `run.worker_command` is ignored.
~~~
Every other sentence of the bullet stays unchanged.

### T3. Mode: new section `## worker handoff`
Insert after the last `## worker dispatch` bullet (`- The orchestrator may run the planner, tester, and reviewer as subagents ...`) and its following blank line, directly before `## host status and questions`. Exact text (followed by one blank line):
~~~markdown
## worker handoff
- `cli` and `host` dispatch send this envelope; `subagent` dispatch may send it as the subagent prompt.
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
- `fresh_context` is always `true` for the tester and reviewer. `fix_scope` is `none` outside a fix round (step 8).
- Every worker ends its output with this block, at most 1000 characters, with nothing after it. Details stay in the artifact.
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
- Read the worker result from the block first, then from the artifact it names (for the reviewer: the review text before the block). A missing block, a block that is not the last text, a value outside the listed ones, a block over 1000 characters, or a block that contradicts its artifact counts as `blocked`.
- `changed_files` is advisory; `git status --porcelain` stays the evidence for steps 6a, 6b, and 7.
- A valid block is still data for that one role (see `worker dispatch`); it never grants a human answer, Gate 1 approval, or another role's verdict.
~~~

### T4. Worker prompts: replace the body of `## Return to orchestrator`
In each prompt, replace everything between the `## Return to orchestrator` heading and the next `## ` heading (keep one blank line before the next heading). Section position is unchanged. Exact bodies:

Planner (`forge-planner.md`, replaces the 4 bullets starting `- Artifact path.`):
~~~markdown
End your output with this block, at most 1000 characters, with nothing after it. Details stay in the artifact (`worker handoff` in `.forge/runtime/modes/orchestrate.md`).
```text
FORGE_RESULT
role: planner
status: done | blocked | blocked_by_decision
verdict: n/a
artifact: <the -plan.md or -ecp.md path under .forge/generated/>
changed_files: 0
note: <one line>
END_FORGE_RESULT
```
- `status`: `done` when the SDD is `ready_for_implementation` or the ECP is `ecp_ready`; `blocked_by_decision` when the plan has `Clarification Questions` or the ECP is `blocked_by_decision`; `blocked` for `needs_more_context`, `needs_more_evidence`, or `needs_plan_approval`.
- The mode status, `High-risk areas touched`, and blocking unknowns stay in the artifact.
~~~

Executor (`forge-executor.md`, replaces `- Report path, execute status, ...`):
~~~markdown
End your output with this block, at most 1000 characters, with nothing after it. Details stay in the artifact (`worker handoff` in `.forge/runtime/modes/orchestrate.md`).
```text
FORGE_RESULT
role: executor
status: done | blocked | blocked_by_environment
verdict: n/a
artifact: <execution report path under .forge/generated/>
changed_files: <count of files you added or changed outside .forge/generated/>
note: <one line>
END_FORGE_RESULT
```
- `status`: execute `success` is `done`; `partial_success`, `not_validated`, `blocked`, a blocking unknown, or new scope is `blocked`; `blocked_by_environment` stays `blocked_by_environment`.
- Changed files, validation commands and results, deviations, and blockers stay in the report.
~~~

Tester (`forge-tester.md`, replaces `- Test report path, verdict ...`):
~~~markdown
End your output with this block, at most 1000 characters, with nothing after it. Details stay in the artifact (`worker handoff` in `.forge/runtime/modes/orchestrate.md`).
```text
FORGE_RESULT
role: tester
status: done | blocked | blocked_by_environment
verdict: pass | fail | n/a
artifact: <test report path under .forge/generated/>
changed_files: <count of test files you added or changed>
note: <one line>
END_FORGE_RESULT
```
- `status: done` with `verdict: pass` or `fail`. When only e2e cannot run and unit, integration, and full-suite runs are green: `status: done`, `verdict: pass`, and `note` names `e2e blocked_by_environment`. When the suite itself cannot run: `status: blocked_by_environment`, `verdict: n/a`. A blocking unknown: `status: blocked`, `verdict: n/a`.
- Failing scenarios mapped to acceptance criteria, the full-suite result, and files added stay in the report.
~~~

Reviewer (`forge-reviewer.md`, replaces `- Review text, verdict ...`):
~~~markdown
Put the full review text first; the orchestrator saves it. End your output with this block, at most 1000 characters, with nothing after it (`worker handoff` in `.forge/runtime/modes/orchestrate.md`).
```text
FORGE_RESULT
role: reviewer
status: done | blocked
verdict: accept | request_changes | needs_more_validation | n/a
artifact: none
changed_files: 0
note: <one line>
END_FORGE_RESULT
```
- `status: done` with `verdict: accept`, `request_changes`, or `needs_more_validation`. A review that cannot complete: `status: blocked`, `verdict: n/a`.
- Severity-grouped findings and scope, contract, migration, or secret flags stay in the review text.
~~~
Do not touch `## Host status`, `## Do NOT`, or frontmatter in any prompt.

### T5. `specs/orchestrate.md` section 8
Insert one paragraph after the `- `host`:` bullet line and a blank line, before `## 8a. Host status and questions` (keep one blank line before the heading). The `host` bullet text is unchanged. Exact text:
~~~markdown
Worker handoff (all `run.worker` values): `cli` and `host` dispatch send a `FORGE_HANDOFF` envelope (`role`, `prompt`, `specialties`, `request`, `inputs`, `fix_scope`, `fresh_context`, `branch`, `base`); `subagent` may. Every worker ends its output with a `FORGE_RESULT` block (`role`, `status`, `verdict`, `artifact`, `changed_files`, `note`), at most 1000 characters and the last text of the output. The orchestrator reads the block first, then the artifact it names; a missing, not-last, out-of-range, over-long, or contradicting block counts as `blocked`. The exact shape is in the mode's `worker handoff` section.
~~~

### T6. `docs/release-notes.md` `## Unreleased`
Insert after the bullet starting `- Optional host status and question tools for `forge-orchestrate`` (line 13):
~~~markdown
- Worker handoff for `forge-orchestrate`: a `FORGE_HANDOFF` envelope for `cli` and `host` dispatch and a `FORGE_RESULT` block every worker ends with. A worker result without a valid block counts as `blocked`, so `cli` and `host` workers must end with the block.
~~~

### T7. Tests in `tests/test_orchestrate.py`, class `OrchestrateContractTests`
Add after `test_publish_force_adds_listed_artifacts_with_preflight`. Reference code (names and helper layout may differ; assertions must not be weaker):
~~~python
    RESULT_FIELDS = ("role:", "status:", "verdict:", "artifact:", "changed_files:", "note:")
    ENVELOPE_FIELDS = ("role", "prompt", "specialties", "request", "inputs", "fix_scope", "fresh_context", "branch", "base")

    @staticmethod
    def _block(text: str, marker: str) -> list[str]:
        return text.split(f"\n{marker}\n", 1)[1].split(f"END_{marker}", 1)[0].splitlines()

    def test_mode_defines_handoff_envelope_and_result_block(self) -> None:
        self.assertLess(self.mode.index("\n## worker dispatch\n"), self.mode.index("\n## worker handoff\n"))
        self.assertLess(self.mode.index("\n## worker handoff\n"), self.mode.index("\n## host status and questions\n"))
        handoff = self.mode.split("\n## worker handoff\n", 1)[1].split("\n## ", 1)[0]
        envelope = self._block(handoff, "FORGE_HANDOFF")
        self.assertEqual([line.split(":", 1)[0] for line in envelope], list(self.ENVELOPE_FIELDS))
        result = self._block(handoff, "FORGE_RESULT")
        self.assertEqual([line.split(" ", 1)[0] for line in result], list(self.RESULT_FIELDS))
        for phrase in (
            "at most 1000 characters",
            "block first, then from the artifact it names",
            "a block that is not the last text",
            "a block over 1000 characters",
            "contradicts its artifact counts as `blocked`",
            "`fresh_context` is always `true` for the tester and reviewer",
            "`git status --porcelain` stays the evidence",
        ):
            self.assertIn(phrase, handoff)
        dispatch = self.mode.split("\n## worker dispatch\n", 1)[1].split("\n## ", 1)[0]
        cli = next(line for line in dispatch.splitlines() if line.startswith("- `run.worker: cli`"))
        host = next(line for line in dispatch.splitlines() if line.startswith("- `run.worker: host`"))
        self.assertIn("`FORGE_HANDOFF`", cli)
        self.assertIn("`FORGE_RESULT`", host)

    def test_worker_prompts_end_with_result_block(self) -> None:
        for role in ROLES:
            prompt = self.templates[f".forge/runtime/agents/{role}.md"]
            ret = prompt.split("\n## Return to orchestrator\n", 1)[1].split("\n## ", 1)[0]
            self.assertIn("at most 1000 characters, with nothing after it", ret, role)
            block = self._block(ret, "FORGE_RESULT")
            self.assertEqual([line.split(" ", 1)[0] for line in block], list(self.RESULT_FIELDS), role)
            self.assertEqual(block[0], f"role: {role.split('-')[1]}", role)
        reviewer = self.templates[".forge/runtime/agents/forge-reviewer.md"]
        self.assertIn("\nartifact: none\n", reviewer)

    def test_malformed_result_uses_existing_blocked_stop(self) -> None:
        # Failure path: no new stop or status; a bad block routes to the existing `blocked` stop.
        stops = self.mode.split("## stop conditions", 1)[1].split("\n## ", 1)[0]
        self.assertIn("- A worker returns a blocking unknown, `blocked`, or `blocked_by_decision`.", stops)
        self.assertNotIn("FORGE_RESULT", stops)
        self.assertNotIn("FORGE_RESULT", self.mode.split("## status values", 1)[1].split("\n## ", 1)[0])
        spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        section8 = spec.split("## 8. Worker configuration", 1)[1].split("\n## ", 1)[0]
        for phrase in ("`FORGE_HANDOFF`", "`FORGE_RESULT`", "counts as `blocked`"):
            self.assertIn(phrase, section8)
~~~
No change to `OrchestrateSourceSyncTests.PAIRS`: the mode and the four agent prompts are already in it. No edit to any other test file.

## Coding rules
- Byte-identical pairs (enforced by `OrchestrateSourceSyncTests.test_runtime_copies_match_templates`): the mode and the four agent prompts, `runtime/` vs `src/forge_context_engine/runtime_templates/base/`.
- Keep these asserted phrases intact in `## worker dispatch`: "hand every role to the dispatch tool the host provides", "The host defines the tool name and shape; Forge does not.", "`run.worker_command` is ignored.", "The tester and reviewer are always new workers with fresh context", "a worker that ends without a complete report counts as `blocked`", "After each dispatch, end the turn.", "artifacts under `.forge/generated/` plus the worker result the host passes in", "Flags for any specific CLI are not defined by Forge and must be verified by the user.", "while only the executor uses `cli`; it reports which worker ran each role.", and the resume boundary sentence.
- Keep `## host status and questions` after `## worker dispatch` and before `## behavior` (`test_mode_host_section_defines_stages_states_and_mapping`); the new section sits between `## worker dispatch` and it.
- Keep each worker's `## Host status` between `## Specialty overlays` and `## Role` (`test_workers_report_status_and_never_ask`).
- `## status values` and `## stop conditions` stay byte-identical (`test_mode_status_values_and_stop_conditions_unchanged`, `test_StopConditions_HostWithoutDispatchTool_AddsExactlyOneHostStop`).
- No `## ` line inside the new fenced blocks (section splitting uses `"\n## "`).
- Do not change the `updated:` frontmatter of the agent prompts or the mode (mode is already `2026-11-25`).
- Neutral English; no issue-text quoting beyond field names.

## Safety / security constraints
- Fail closed: every malformed, missing, over-long, not-last, or contradicting block is `blocked`.
- The last-text rule prevents a `FORGE_RESULT` string quoted inside a diff or review body from being read.
- A worker result is never a human answer or Gate 1 approval (unchanged; restated in `worker handoff`).
- No secrets, production identifiers, or external URLs in any added text.

## Acceptance criteria
1. Both mode copies contain `## worker handoff` with the 9-field envelope and the 6-field result block, and are byte-identical.
2. All four worker prompts (both copies) have a `FORGE_RESULT` ... `END_FORGE_RESULT` block in `## Return to orchestrator` with the same six field names in order and their own `role:` value; reviewer has `artifact: none`.
3. The mode states block first, then artifact, and the five `blocked` cases.
4. Failure path: no new status value, no new stop-condition bullet; the existing `blocked` stop is unchanged; `tests/test_orchestrate_host_dispatch.py` and `tests/test_orchestrate_host_questions.py` pass unchanged.
5. `specs/orchestrate.md` section 8 names both markers and the `blocked` rule; the `host` bullet and section 8a are unchanged.
6. `docs/release-notes.md` `## Unreleased` has the new bullet; existing asserted bullets unchanged.
7. Full suite green.

## Validation commands
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `for r in planner executor tester reviewer; do diff runtime/.forge/runtime/agents/forge-$r.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-$r.md; done`
- `git status --porcelain` (only the 13 files above plus `.forge/generated/` artifacts; `.forge/generated/` is gitignored, so artifacts may not appear)

## Stop conditions
- Any validation command red after 3 attempts on the same check.
- A needed edit outside the 13 files (for example `validation-cases/orchestrate-gates.md`, another test file, or a Claude wrapper).
- An existing asserted phrase would have to change to fit the new text.
- The runtime and template copies of a pair differ before editing (means the tree moved; re-plan).

## Expected execution report format
`.forge/generated/reports/2026-11-24-worker-result-block-execution-report.md` with: execute status, changed files (exact paths), validation commands with real output summary, deviations from this ECP, non-blocking decisions, blockers. End the worker output with the executor `FORGE_RESULT` block only if T4 is already applied; otherwise the current return list.

## Non-blocking details execute may decide
- Test method names and whether `_block` is a static method or a module helper.
- Exact placement of the new tests inside `OrchestrateContractTests`.

## Risk notes
- External contract (`external_contract_change`, approved at Gate 1): hosts and `cli` wrappers that pass free-text results will now stop as `blocked`. The release note says so.
- Rebase surface: later stacked SDDs (#16, #18) may edit `## worker dispatch` or the planner prompt; this ECP touches only the `cli`/`host` bullets, one new section, and `## Return to orchestrator`.

## Target Tool Instructions
- Use the smallest safe edit mechanism available in the target tool.
- For Codex, prefer `apply_patch` for scoped edits.
- For Claude Code, use its normal file-edit workflow; copy runtime files to template paths with `cp` after editing.
- For Copilot, produce the smallest reviewable patch.
- Do not widen scope beyond this ECP.
- Do not stage, commit, or push.
