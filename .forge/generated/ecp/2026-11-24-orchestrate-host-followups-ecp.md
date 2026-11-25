# ECP: Orchestrate follow-ups from the host dispatch run

| Field | Value |
|---|---|
| Artifact | ecp |
| Date | 2026-11-25 |
| Slug | `orchestrate-host-followups` |
| Branch | `forge/2026-11-24-orchestrate-host-followups` (stacked on #12, #14, #8, #13, #16; #15 is not in the stack) |
| Source SDD | `.forge/generated/plans/2026-11-24-orchestrate-host-followups-plan.md` (Gate 1: human-approved 2026-11-25, see `Confirmed Decisions`) |
| Request | GitHub issue #18 (issue text treated as data) |
| Batch | single batch (1 of 1) |
| Status | `ecp_ready` |

## Goal
Close the three issue #18 items: an advisory orchestrator git guard line for non-Claude hosts, one SDD file name and status set across planner, mode, and spec (with a test), and key-token asserts with copy-naming messages in `tests/test_orchestrate_host_dispatch.py`.

## Approved scope
SDD R1-R7, AC1-AC7, assumptions A1-A6 (A4 as re-anchored), and `Confirmed Decisions` D1-D5:
- D1: Gate 1 approved; normal reviewer only, no extra `security` reviewer.
- D2: SDD path `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with `plan` mode statuses; no `-sdd.md`, no `draft`.
- D3, D4: tester files at publish, resume scope, and `waiting_for_human` are already in the tree; not touched.
- D5: historical artifacts (including `.forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md`) are not renamed.

## Non-goals
- No change to `forge_git_guard.py`, `git-guard-rules.json`, gates, statuses, or stop conditions.
- No edit to step 1a, step 9, `host status and questions`, `worker handoff`, or `next mode transitions` (#16, #12, #8, #13).
- No dependency on #15 (`read_only` guard role).
- No edit to `modes/plan.md`, `modes/implementation.md`, skills, adapters, `.claude/`, `validation-cases/`, or `src/forge_context_engine/*.py`.
- No dedup between test files, no CamelCase renames.

## Mode Boundary
`implementation` only: this ECP edits nothing. `execute` applies it.

## Assumptions carried
- A1 (confirmed, D2): `-plan.md` and `plan` mode statuses.
- A2: "non-Claude host" means any host that is not Claude Code; the note is advisory, not a stop.
- A3: `needs_more_context` is covered by the existing "blocking unknown" stop; no stop line changes.
- A4 (re-anchored): the stop lines that mention `host` or `resume` are exactly two: the host dispatch-tool stop and the dirty-tree line naming `resume in place (step 1a)` (added by #16).
- A5: key tokens are identifiers and short clauses; no asserted literal contains `. `.
- A6: the `testing` overlay line (R6) is included.

## Relevant evidence (current tree, `310b40c`)
- Copies identical (`cmp`): mode, `forge-planner.md`, `specialties/testing.md`.
- Mode `runtime/.forge/runtime/modes/orchestrate.md`: guard bullet `:72`; step 1 `:118`; step 2 `:120`; stop list `:133-148`, with `resume` at `:139` and `host` at `:142`; report Steps `:173` `✓ [sdd] SDD -> .forge/generated/plans/<file>`.
- Planner `runtime/.forge/runtime/agents/forge-planner.md:42` step 3; front matter `updated: 2026-11-10`.
- Overlay `runtime/.forge/runtime/agents/specialties/testing.md`: `## As reviewer` last bullet `:45`; `updated: 2026-11-10`.
- Spec `specs/orchestrate.md`: §4b `:63`; §6a `:103`; §8 `host` bullet `:121`.
- Release notes `docs/release-notes.md`: `Added` list ends at `:15` (resume in place bullet).
- Tests pinning text this ECP touches: `tests/test_orchestrate_host_dispatch.py:127-128` (old guard bullet phrases; rewritten in E11); `tests/test_orchestrate.py:63-77` (`forge_git_guard.py worker`, `worker git guard not confirmed` in `worker dispatch`; still pass); `tests/test_orchestrate.py:495-500` (10 report step lines with stage IDs; still pass).
- Sync test: `tests/test_orchestrate.py:353-373` `OrchestrateSourceSyncTests.PAIRS` covers the mode, all role prompts, and all specialties.
- No runtime, spec, or test file contains `-sdd.md`; `` `draft` `` appears only in unrelated specs (`specs/runtime-install-update.md`, `specs/platform-context.md`, `specs/context-validation.md`).
- Baseline: `uv run python -m unittest discover -s tests -q` -> `Ran 214 tests ... OK`.
- Dry run: all edits below applied to a scratch copy of the tree: `Ran 217 tests ... OK`. AC4 checks in the scratch copy: `-sdd.md` in the template mode fails `test_sdd_path_and_status_are_one_set`; an extra stop line containing `Resume` fails the A4 test with `3 != 2 : orchestrate.md (template)`; a broken runtime copy fails with message `orchestrate.md (runtime/)`.

## Files likely to change
Exact list; any other changed or new path is scope growth.
1. `runtime/.forge/runtime/modes/orchestrate.md`
2. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
3. `runtime/.forge/runtime/agents/forge-planner.md`
4. `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-planner.md`
5. `runtime/.forge/runtime/agents/specialties/testing.md`
6. `src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/specialties/testing.md`
7. `specs/orchestrate.md`
8. `tests/test_orchestrate_host_dispatch.py`
9. `tests/test_orchestrate.py`
10. `docs/release-notes.md`

## Task sequence
Edit each `runtime/` copy, then copy it byte-for-byte to the template path with `cp`. Each anchor must match exactly once.

### Mode (`runtime/.forge/runtime/modes/orchestrate.md`, then copy)
E1. Step 1 (`:118`). Replace
```text
put `git guard hook missing` in the report `Note`. Confirm the working tree
```
with
```text
put `git guard hook missing` in the report `Note`. Otherwise, the host should enforce role `orchestrator` from `.forge/runtime/meta/git-guard-rules.json` on orchestrator shell commands; if the orchestrator cannot confirm it, continue and put `orchestrator git guard not confirmed` in the report `Note`. Confirm the working tree
```

E2. `## worker dispatch` guard bullet (`:72`). Replace the whole line
```text
- Worker git guard under `host`: the host should run `.forge/runtime/hooks/forge_git_guard.py worker` before worker shell commands. If the orchestrator cannot confirm it, continue and put `worker git guard not confirmed` in the report `Note`.
```
with
```text
- Git guard under `host`: the host should run `.forge/runtime/hooks/forge_git_guard.py worker` before worker shell commands. If the orchestrator cannot confirm it, continue and put `worker git guard not confirmed` in the report `Note`. The host should also enforce role `orchestrator` from `.forge/runtime/meta/git-guard-rules.json` on orchestrator shell commands (step 1); if the orchestrator cannot confirm it, continue and put `orchestrator git guard not confirmed` in the report `Note`.
```

E3. Step 2 (`:120`). Replace
```text
before writing the SDD. If it finds any ambiguity
```
with
```text
before writing the SDD. The planner saves the SDD at `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with one `plan` mode status: `ready_for_implementation`, `blocked_by_decision`, or `needs_more_context`. If it finds any ambiguity
```

E4. Report Steps (`:173`). Replace the line
```text
✓ [sdd] SDD -> .forge/generated/plans/<file>
```
with
```text
✓ [sdd] SDD -> .forge/generated/plans/<YYYY-MM-DD>-<slug>-plan.md
```
Front matter `updated:` is already `2026-11-25`; leave it.
Then: `cp runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`

### Planner (`runtime/.forge/runtime/agents/forge-planner.md`, then copy)
E5. Step 3 (`:42`). Replace
```text
Save to `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md`.
```
with
```text
Save to `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with one `plan` mode status.
```
Set front matter `updated: 2026-11-10` to `updated: 2026-11-25`.
Then: `cp runtime/.forge/runtime/agents/forge-planner.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-planner.md`

### Testing overlay (`runtime/.forge/runtime/agents/specialties/testing.md`, then copy)
E6. After the last `## As reviewer` bullet (`:45`)
```text
- The full suite ran; a skipped full suite is a finding.
```
add the line
```text
- Assert key tokens, not whole sentences or prose rows.
```
Set front matter `updated: 2026-11-10` to `updated: 2026-11-25`.
Then: `cp runtime/.forge/runtime/agents/specialties/testing.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/specialties/testing.md`

### Spec (`specs/orchestrate.md`)
E7. §4b (`:63`). At the end of the paragraph, replace
```text
the run stops and the miss is reported so the checks can be improved.
```
with
```text
the run stops and the miss is reported so the checks can be improved. The planner saves the SDD at `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with one `plan` mode status: `ready_for_implementation`, `blocked_by_decision`, or `needs_more_context`.
```

E8. §6a (`:103`). Replace
```text
Hosts that run non-Claude workers (for example through ACP permission requests) may read the same file to enforce the same rules instead of copying the list.
```
with
```text
Hosts that run non-Claude workers or a non-Claude orchestrator (for example through ACP permission requests) may read the same file to enforce the same rules for role `worker` and role `orchestrator` instead of copying the list.
```

E9. §8 `- `host`:` bullet (`:121`). Replace
```text
the report `Note` says `worker git guard not confirmed`. A missing dispatch tool
```
with
```text
the report `Note` says `worker git guard not confirmed`. The host should also enforce role `orchestrator` on orchestrator shell commands; when the orchestrator cannot confirm it, the report `Note` says `orchestrator git guard not confirmed`. A missing dispatch tool
```

### Release notes (`docs/release-notes.md`)
E10. After the `Added` bullet ending `Test and review always re-run before publish.` (`:15`), add:
```text
- `forge-orchestrate` preflight: a host that is not Claude Code should enforce git guard role `orchestrator` from `.forge/runtime/meta/git-guard-rules.json`; when the orchestrator cannot confirm it, the report `Note` says `orchestrator git guard not confirmed` (advisory, not a stop). The SDD path is `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` with a `plan` mode status in planner, mode, and spec.
```

### Tests
E11. `tests/test_orchestrate_host_dispatch.py`.
(a) `_mode_copies` (`:28-32`): change the keys `"template"` -> `"orchestrate.md (template)"` and `"runtime"` -> `"orchestrate.md (runtime/)"`. Values unchanged.
(b) Replace everything from `class HostModeContractTests(unittest.TestCase):` (`:69`) to the end of the file with:
```python
class HostModeContractTests(unittest.TestCase):
    def test_Inputs_ListHostAsWorkerValue_WithSubagentDefault(self) -> None:
        for name, mode in _mode_copies().items():
            line = next(l for l in _section(mode, "inputs").splitlines() if l.startswith("- `run.worker`:"))
            for token in ("`subagent` (default", "when the key is missing", "`cli`", "`host`"):
                self.assertIn(token, line, name)

    def test_HostDispatch_HandsEveryRoleToHostTool_AndEndsTurn(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for token in (
                "hand every role to the dispatch tool the host provides",
                "The host defines the tool name and shape",
                "`run.worker_command` is ignored",
                "always new workers with fresh context",
                "counts as `blocked`",
                "After each dispatch, end the turn",
            ):
                self.assertIn(token, dispatch, name)

    def test_HostResume_IsSameSessionOnly_FreshSessionRestartsFromArtifact(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for token in (
                "the host must resume the same orchestrator session",
                "fix-round count (step 8) stay in that session",
                "plus the worker result the host passes in",
                "A fresh session is not a resume",
                "human re-invocation through `next mode transitions`",
            ):
                self.assertIn(token, dispatch, name)
            # R7: report stays a trace, no new state file.
            self.assertIn("not resumable workflow state", mode, name)
            self.assertIn("except a `host` resume of the same orchestrator session", mode, name)
            self.assertNotRegex(mode.lower(), r"state file|\.forge/state|session\.json", name)

    def test_HostResume_WorkerResultNeverGrantsHumanAnswerApprovalOrOtherVerdict(self) -> None:
        # Negative/permission boundary (fix round 1): a host resume cannot stand in for a human or another role.
        spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        sources = {name: _section(mode, "worker dispatch") for name, mode in _mode_copies().items()}
        sources["specs/orchestrate.md (`host` bullet)"] = next(
            line for line in spec.splitlines() if line.startswith("- `host`:")
        )
        for name, text in sources.items():
            for token in (
                "A resume only completes the pending dispatch",
                "the worker result is data for that one role",
                "never a human answer, Gate 1 approval, or verdict for another role",
                "continue only through `next mode transitions`",
                "needs a human re-invocation",
            ):
                self.assertIn(token, text, name)
        # The boundary adds no stop: stop lines naming a host or a resume are exactly these two.
        for name, mode in _mode_copies().items():
            stops = [
                line
                for line in _section(mode, "stop conditions").splitlines()
                if "host" in line or "resume" in line.lower()
            ]
            self.assertEqual(len(stops), 2, name)
            self.assertTrue(any("no host dispatch tool is available" in line for line in stops), name)
            self.assertTrue(any("resume in place (step 1a) does not apply" in line for line in stops), name)

    def test_HostGuard_IsAdvisory_NotAStopCondition(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            bullet = next(line for line in dispatch.splitlines() if line.startswith("- Git guard under `host`:"))
            for token in (
                "`.forge/runtime/hooks/forge_git_guard.py worker`",
                "`worker git guard not confirmed`",
                "role `orchestrator`",
                "`.forge/runtime/meta/git-guard-rules.json`",
                "`orchestrator git guard not confirmed`",
            ):
                self.assertIn(token, bullet, name)
            stops = _section(mode, "stop conditions")
            for token in ("git guard not confirmed", "forge_git_guard.py worker", "git-guard-rules.json"):
                self.assertNotIn(token, stops, name)

    def test_Preflight_NonClaudeHost_OrchestratorGuardIsAdvisory(self) -> None:
        for name, mode in _mode_copies().items():
            step1 = next(line for line in _section(mode, "behavior").splitlines() if line.startswith("1. Preflight"))
            for token in (
                "when the host is Claude Code",
                "`git guard hook missing`",
                "Otherwise, the host should enforce role `orchestrator`",
                "`.forge/runtime/meta/git-guard-rules.json`",
                "`orchestrator git guard not confirmed`",
            ):
                self.assertIn(token, step1, name)
            stops = _section(mode, "stop conditions")
            self.assertNotIn("orchestrator git guard", stops, name)
            self.assertNotIn("git-guard-rules.json", stops, name)

    def test_StopConditions_HostWithoutDispatchTool_AddsExactlyOneHostStop(self) -> None:
        for name, mode in _mode_copies().items():
            stops = _section(mode, "stop conditions")
            host_stops = [line for line in stops.splitlines() if "`run.worker: host`" in line]
            self.assertEqual(len(host_stops), 1, name)
            self.assertIn("no host dispatch tool is available", host_stops[0], name)

    def test_Regression_CliAndSubagentDispatchAndCliStop_Unchanged(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for token in (
                "always new subagents, never resumed ones",
                "not defined by Forge and must be verified by the user",
                "while only the executor uses `cli`",
                "reports which worker ran each role",
            ):
                self.assertIn(token, dispatch, name)
            self.assertIn(
                "`run.worker: cli` is set but `run.worker_command` is empty",
                _section(mode, "stop conditions"),
                name,
            )

    def test_Regression_NoNewStatusValue(self) -> None:
        for name, mode in _mode_copies().items():
            self.assertNotIn("host", _section(mode, "status values"), name)


class HostSpecAndValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        self.cases = (ROOT / "validation-cases/orchestrate-gates.md").read_text(encoding="utf-8")

    def test_Spec_StopsHostWithoutDispatchTool(self) -> None:
        stops = _section(self.spec, "6. Stop conditions")
        line = next(line for line in stops.splitlines() if line.startswith("- `run.worker: host`"))
        self.assertIn("no host dispatch tool is available", line)

    def test_Spec_ConfigListsHost_AndHostBulletOwnsNoHostCode(self) -> None:
        self.assertIn("# subagent | cli | host; missing key means subagent", self.spec)
        bullet = next(line for line in self.spec.splitlines() if line.startswith("- `host`:"))
        for token in (
            "Forge ships no host code",
            "resumes the same orchestrator session",
            "a fresh session needs a human re-invocation",
            "`worker git guard not confirmed`",
            "`orchestrator git guard not confirmed`",
            "`blocked_by_environment`",
        ):
            self.assertIn(token, bullet)

    def test_Spec_GitGuard_RulesFileCoversOrchestratorRoleForOtherHosts(self) -> None:
        section = _section(self.spec, "6a. Git guard")
        for token in ("may read the same file", "role `worker` and role `orchestrator`", "`.forge/runtime/meta/git-guard-rules.json`"):
            self.assertIn(token, section)

    def test_Spec_OpenItems_DropsForgeStaysUnchanged(self) -> None:
        self.assertNotIn("Forge stays unchanged", self.spec)
        self.assertIn("instead of overriding the mode's `worker dispatch` section", self.spec)

    def test_ValidationCase18_ExpectsBlockedByEnvironment_AndIsInRegressionList(self) -> None:
        row = next(line for line in self.cases.splitlines() if line.startswith("| 18 |"))
        for token in ("`run.worker: host`", "no host dispatch tool", "`blocked_by_environment`", "nothing committed"):
            self.assertIn(token, row)
        self.assertRegex(self.cases, r"any stop scenario \([^)]*\b18\b")

    def test_ReleaseNotes_ListHostWorker(self) -> None:
        notes = (ROOT / "docs/release-notes.md").read_text(encoding="utf-8")
        self.assertIn("`run.worker` (`subagent` | `cli` | `host`)", notes)


if __name__ == "__main__":
    unittest.main()
```

E12. `tests/test_orchestrate.py`, class `OrchestrateContractTests`: add this method after `test_gate_exceptions_are_scoped_to_orchestrate` (after the line `        self.assertIn("only inside `forge-orchestrate`", conventions)`, `:301`):
```python
    def test_sdd_path_and_status_are_one_set(self) -> None:
        sources = {
            "forge-planner.md (template)": self.templates[".forge/runtime/agents/forge-planner.md"],
            "orchestrate.md (template)": self.mode,
            "specs/orchestrate.md": (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8"),
        }
        for name, text in sources.items():
            self.assertIn(".forge/generated/plans/YYYY-MM-DD-<slug>-plan.md", text, name)
            self.assertIn("ready_for_implementation", text, name)
            self.assertNotIn("-sdd.md", text, name)
            self.assertNotIn("`draft`", text, name)
        self.assertIn("SDD -> .forge/generated/plans/<YYYY-MM-DD>-<slug>-plan.md", self.mode)
        step2 = next(line for line in self.mode.splitlines() if line.startswith("2. Clarify"))
        for status in ("`ready_for_implementation`", "`blocked_by_decision`", "`needs_more_context`"):
            self.assertIn(status, step2)
```
The runtime copies are covered by `OrchestrateSourceSyncTests`.

## Coding rules
- Edit `runtime/` copies, then `cp` to the template; mode, planner, and overlay copies must be byte-identical.
- Keep every existing phrase in the mode, spec, and planner that other tests pin (see `Relevant evidence`); E1-E9 only add text, except E2 (bullet label `Worker git guard` -> `Git guard`) and E4 (report placeholder).
- Never write `state file`, `.forge/state`, or `session.json` in the mode or spec.
- No asserted test literal contains `. `; every assert inside a copy loop passes the copy name.
- Neutral English, short sentences, repo names in backticks.

## Safety / security constraints
- The orchestrator guard text is advisory: never add it to `## stop conditions` or spec §6.
- Do not touch `forge_git_guard.py` or `git-guard-rules.json`.
- Reviewer for this run: the normal reviewer only (D1).

## Acceptance criteria
- AC1-AC7 from the SDD.
- Failure path: `-sdd.md` in a mode copy fails `test_sdd_path_and_status_are_one_set` or the sync test; an extra `host` or `resume` stop line fails the A4 assert; a broken runtime copy fails with a message naming `orchestrate.md (runtime/)`.
- The suite count rises from 214 to 217 (3 new tests), and no existing test is deleted.

## Validation commands
- `uv run python -m unittest tests.test_orchestrate tests.test_orchestrate_host_dispatch -v`
- `uv run python -m unittest discover -s tests -q` (expected `Ran 217 tests`, `OK`)
- `cmp runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `cmp runtime/.forge/runtime/agents/forge-planner.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-planner.md`
- `cmp runtime/.forge/runtime/agents/specialties/testing.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/specialties/testing.md`
- `grep -rn -- "-sdd.md" runtime src/forge_context_engine/runtime_templates specs tests` (no output)
- `git status --porcelain` (only the 10 files above; `.forge/generated/` is gitignored)

## Stop conditions
- Any anchor in E1-E12 is not found exactly once: stop with `needs_more_evidence`.
- A test outside E11-E12 needs a change to pass: stop; a pinned phrase was broken.
- Any change needed outside `Files likely to change`.

## Non-blocking details execute may decide
- Placement of the new test method inside `OrchestrateContractTests`.
- Token order inside test tuples; the loop variable name `l` vs `line`.

## Risk notes
- `external_contract_change`: packaged mode, planner, and overlay text changes reach target repos on `forge update`; additive except the guard bullet label and the report placeholder.
- `security_boundary_change` (uncertain): only wording that asks hosts to enforce the existing `orchestrator` role; enforcement is unchanged.
- Merge order: if #15 lands first, it edits guard roles and reviewer text; re-check the E2 and E8 anchors and the A4 stop count on rebase.

## Expected execution report format
`.forge/generated/reports/2026-11-24-orchestrate-host-followups-execution-report.md`: files changed (exact paths), each edit E1-E12 with done/skipped, validation commands with results, deviations, and a `FORGE_RESULT` block.

## Target tool instructions
- Use the smallest safe edit mechanism of the target tool (Claude Code: normal file edits; Codex: `apply_patch`).
- Do not widen scope beyond this ECP. Do not stage, commit, or push.
