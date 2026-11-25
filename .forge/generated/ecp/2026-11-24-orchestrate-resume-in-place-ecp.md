# ECP: Orchestrate resume in place after a lost session

| Field | Value |
|---|---|
| Artifact | ecp |
| Date | 2026-11-25 |
| Slug | `orchestrate-resume-in-place` |
| Branch | `forge/2026-11-24-orchestrate-resume-in-place` (stacked on #12, #14, #8, #13; #15 is not in the stack) |
| Source SDD | `.forge/generated/plans/2026-11-24-orchestrate-resume-in-place-plan.md` (Gate 1: human-approved 2026-11-25, see `Confirmed Decisions`) |
| Request | GitHub issue #16 (issue text treated as data) |
| Batch | single batch (1 of 1) |
| Status | `ecp_ready` |

## Goal
A human re-invocation of `forge-orchestrate` with a run's ECP continues that run in place on its feature branch, instead of stopping for a dirty tree, when the branch, the changed paths, and the orchestration report prove where the run was. Every other dirty tree still stops.

## Approved scope
SDD R1-R9, AC1-AC7, assumptions A1, A3-A7, and `Confirmed Decisions` (2026-11-25):
- Gate 1 human-approved; an extra `security` reviewer runs with the normal reviewer.
- Q4: the resume scope check allows test files under the `testing` overlay test paths (same rule as the #12 step 9 preflight, Q3).
- Re-anchoring tightening: R1c requires the `[ecp] Gate 2` step to be `✓`.
- R3 in its two-case form: execution report missing -> resume at step 6 (execute); otherwise -> step 6a, then a new tester and a new reviewer. Never directly at Publish.

## Non-goals
- No state file, scheduler, daemon, or new artifact type; no new status value.
- No resume from a plan/SDD path with a dirty tree; no resume after a `✗` step.
- No edit to: the `worker dispatch` section (host same-session resume, `orchestrate.md:71`), step 9 text and its stop line (#12), `host status and questions` (#8), `worker handoff` (#13), reviewer guard (#15), git guard files, role prompts, skills, adapters, `src/forge_context_engine/*.py`.
- No edit to validation scenario 7 or any existing scenario row.

## Mode Boundary
`implementation` only: this ECP edits nothing. `execute` applies it after Gate 2.

## Assumptions carried
- A1 (confirmed): test and review always re-run after execute on resume.
- A3: any `✗` step makes the report not resumable in place.
- A4: an in-progress (`✱`) fix round counts as used.
- A5: resume in place is checked only when the invocation names an ECP path.
- `.forge/generated/**` stays gitignored; the `Artifacts` clause covers repos that un-ignore it.

## Relevant evidence (current tree)
- Mode, both copies identical (`diff`: no output): step 1 `runtime/.forge/runtime/modes/orchestrate.md:118`; step 2 starts `:119`; step 6b `:126`; step 9 preflight with tester-added test files `:129`; dirty-tree stop `:138`; report `Run` `:165`, `Steps` `:169-179`, `Review rounds` `:197-199`; footer `:207`; `next mode transitions` `:225-229`.
- Step lines carry stage IDs and fix rounds repeat the `[execute]`, `[test]`, `[review]` lines (`orchestrate.md:207`).
- `testing` overlay test paths: `runtime/.forge/runtime/agents/specialties/testing.md:26`.
- Spec: stop list `specs/orchestrate.md:84`; §9 `:137-139`; §10 starts `:141`.
- Validation cases: last row 22 (`validation-cases/orchestrate-gates.md:43`); §3 last bullet `:59`; regression sentence `:69`.
- Tests that pin existing text and must still pass unchanged: `tests/test_orchestrate_host_dispatch.py:91-104` (`not resumable workflow state`, ``except a `host` resume of the same orchestrator session``, no `state file|\.forge/state|session\.json`), `tests/test_orchestrate_host_questions.py:86-94` (transition lines), `tests/test_orchestrate.py:63-77` (`A fresh session is not a resume`).
- Tests pinning the regression sentence (must be updated): `tests/test_orchestrate.py:513`, `tests/test_orchestrate_host_dispatch.py:184`.
- Copy sync: `tests/test_orchestrate.py:356-373` (`OrchestrateSourceSyncTests.PAIRS` includes the mode copy).
- Release notes: `docs/release-notes.md` `## Unreleased`, `Added` list ends at `:14`.

## Files likely to change
Exact list; any other changed or new path is scope growth.
1. `runtime/.forge/runtime/modes/orchestrate.md`
2. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
3. `specs/orchestrate.md`
4. `validation-cases/orchestrate-gates.md`
5. `tests/test_orchestrate.py`
6. `tests/test_orchestrate_host_dispatch.py`
7. `docs/release-notes.md`

## Task sequence
Apply edits E1-E5 to `runtime/.forge/runtime/modes/orchestrate.md`, then copy the file byte-for-byte to the template path (`cp runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`). Then E6-E8 (spec), E9-E11 (validation cases), E12-E14 (tests), E15 (release notes). Then run validation.

### Mode (`runtime/.forge/runtime/modes/orchestrate.md`, then copy)
E1. Step 1 (line 118). Replace
`Confirm the working tree is clean, the current branch is not`
with
`Confirm the working tree is clean (or step 1a applies), the current branch is not`

E2. Insert a new line directly after line 118 (before the line starting `2. Clarify, then plan:`):
```text
1a. Resume in place: when the invocation names an ECP and the working tree is dirty, continue the lost run only when all of these hold: the orchestration report with the ECP's date and slug exists; the current branch is its `Run` branch; its `[ecp] Gate 2` step is `✓` and no step is `✗`; every path in `git status --porcelain` is in the ECP `Files likely to change`, in the report `Artifacts` table, or matches the test paths in the `testing` overlay while a `[test]` step is `✓` or `✱`. Those test paths count as the tester's added test files at step 9. Re-run execute only when the execution report is missing; otherwise continue at step 6a, then run a new tester and a new reviewer in fresh context; never resume at Publish. Fix rounds used = the larger of (`Review rounds` rows minus 1) and (`[execute]` lines marked `✓` or `✱`, minus 1); the counter never resets and the limit stays 2. Add `✓ [clarify] Resume in place (from <step>; fix rounds used: <n>)` to the same report; create no new file. If any condition fails, stop for a dirty tree.
```

E3. Stop list (line 138). Replace
`- The working tree was dirty at start, or the branch is the default/protected branch.`
with
`- The working tree was dirty at start and resume in place (step 1a) does not apply, or the branch is the default/protected branch.`

E4. Footer (line 207). Replace
```text
except a `host` resume of the same orchestrator session (see `worker dispatch`).
```
with
```text
except a `host` resume of the same orchestrator session (see `worker dispatch`) and a resume in place (step 1a), which reads only the `Run` branch, the step markers, the `Artifacts` paths, and the `Review rounds` row count.
```
(Keep `not resumable workflow state` in the same sentence.)

E5. `next mode transitions`. Insert after the line that starts with `- ` followed by `` `stopped` or `review_unresolved` -> human decides ``:
```text
- Session lost mid-run (no stop status written, no `✗` step) -> human re-invokes `forge-orchestrate` with the ECP path; step 1a resumes in place or stops for a dirty tree.
```

Do not change `updated:` front matter beyond setting it to `2026-11-25` (already that value).

### Spec (`specs/orchestrate.md`)
E6. §6 (line 84). Replace
`- the working tree is dirty at start, or the branch is the default/protected branch;`
with
`- the working tree is dirty at start and resume in place (section 9a) does not apply, or the branch is the default/protected branch;`

E7. §9 (line 139). Replace the last sentence
`The report is a trace for humans, not resumable state.`
with
```text
The report is a trace for humans, not a workflow state store; resume in place (section 9a) reads only its `Run` branch, step markers, `Artifacts` paths, and `Review rounds` row count.
```

E8. Insert before `## 10. Statuses`, separated by blank lines:
```markdown
## 9a. Resume in place

When an orchestrator session is lost mid-run, the human re-invokes `forge-orchestrate` with the run's ECP. With a dirty tree, the run continues on its feature branch only when the report with the ECP's date and slug exists, the current branch is its `Run` branch, its `Gate 2` step is done, no step is stopped (`✗`), and every changed or untracked path is in the ECP `Files likely to change`, in the report `Artifacts` table, or a test file under the `testing` overlay test paths after the test step started. Execute re-runs only when the execution report is missing; otherwise the run continues at the diff risk check with a new tester and a new reviewer in fresh context, never at Publish. The fix-round counter continues from the report and never resets; the limit stays 2. The report gets one `Resume in place` step line; no new file is created. If any condition fails, the run stops for a dirty tree.
```

### Validation cases (`validation-cases/orchestrate-gates.md`)
E9. Insert after row 22 (line 43):
```markdown
| 23 | Session lost after `[execute] Execute` is `✓`; tree has only ECP-scope changes; re-invoked with the ECP | Resumes in place at the diff risk check; new tester and new reviewer in fresh context; fix-round counter unchanged; report shows `Resume in place`; no new report file |
| 24 | Session lost after Execute; tree has a changed file outside the ECP `Files likely to change` and outside the test paths; re-invoked with the ECP | `stopped` for a dirty tree at start; no worker started; nothing committed |
```

E10. §3, append after the last bullet (line 59):
```text
- Resuming in place with a `✗` step, a path outside ECP scope, or on another branch, or publishing after a resume without a new tester and reviewer.
```

E11. §5 (line 69). Replace `any stop scenario (2 to 8, 11, 12, 18)` with `any stop scenario (2 to 8, 11, 12, 18, 24)`.

### Tests
E12. `tests/test_orchestrate.py:513`: replace `"any stop scenario (2 to 8, 11, 12, 18)"` with `"any stop scenario (2 to 8, 11, 12, 18, 24)"`.

E13. `tests/test_orchestrate_host_dispatch.py:184`: same replacement.

E14. `tests/test_orchestrate.py`: add this class (place after `OrchestrateSourceSyncTests`; names may differ):
```python
class OrchestrateResumeInPlaceTests(unittest.TestCase):
    """Resume in place after a lost session (SDD 2026-11-24-orchestrate-resume-in-place)."""

    def setUp(self) -> None:
        self.modes = {
            "template": iter_template_files("base")[MODE],
            "runtime": (ROOT / "runtime" / MODE).read_text(encoding="utf-8"),
        }
        self.spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        self.cases = (ROOT / "validation-cases/orchestrate-gates.md").read_text(encoding="utf-8")

    def test_mode_step_1a_conditions_resume_point_and_counter(self) -> None:
        for name, mode in self.modes.items():
            step = mode.split("1a. Resume in place:", 1)[1].split("\n2. ", 1)[0]
            for phrase in (
                "names an ECP and the working tree is dirty",
                "the current branch is its `Run` branch",
                "`[ecp] Gate 2` step is `✓` and no step is `✗`",
                "in the ECP `Files likely to change`, in the report `Artifacts` table",
                "test paths in the `testing` overlay while a `[test]` step",
                "Re-run execute only when the execution report is missing",
                "a new reviewer in fresh context; never resume at Publish",
                "the counter never resets and the limit stays 2",
                "Resume in place (from <step>; fix rounds used: <n>)",
                "If any condition fails, stop for a dirty tree.",
            ):
                self.assertIn(phrase, step, name)
            stops = mode.split("## stop conditions", 1)[1].split("\n## ", 1)[0]
            self.assertIn("dirty at start and resume in place (step 1a) does not apply", stops, name)
            self.assertIn("Session lost mid-run", mode.split("## next mode transitions", 1)[1], name)
            self.assertIn("not resumable workflow state", mode, name)
            self.assertIn("a resume in place (step 1a), which reads only", mode, name)

    def test_spec_and_validation_cases_match_mode(self) -> None:
        self.assertIn("resume in place (section 9a) does not apply", self.spec)
        section = self.spec.split("## 9a. Resume in place", 1)[1].split("\n## ", 1)[0]
        for phrase in ("never at Publish", "never resets", "the run stops for a dirty tree"):
            self.assertIn(phrase, section)
        self.assertNotRegex(self.spec.lower(), r"state file|\.forge/state|session\.json")
        row = next(line for line in self.cases.splitlines() if line.startswith("| 24 |"))
        self.assertIn("`stopped` for a dirty tree at start", row)
        self.assertIn("nothing committed", row)
        self.assertIn("any stop scenario (2 to 8, 11, 12, 18, 24)", self.cases)
```

### Release notes (`docs/release-notes.md`)
E15. Insert after line 14 (the bullet starting `- Worker handoff for`), in the `Added` list:
```text
- Resume in place for `forge-orchestrate`: after a lost session, re-invoking with the run's ECP continues on the feature branch when the branch, the changed paths, and the orchestration report match; otherwise the dirty-tree stop applies. Test and review always re-run before publish.
```

## Coding rules
- Keep the exact phrases listed in `Relevant evidence` under "must still pass unchanged".
- Never write `state file`, `.forge/state`, or `session.json` in the mode or spec.
- Mode copies must be byte-identical; edit the runtime copy, then `cp` to the template.
- Neutral English, short sentences, repo names in backticks.

## Safety / security constraints
- The resume rule narrows the dirty-tree stop only with exact conditions; do not loosen any condition in E2 or E8.
- A resume never skips step 6a, the tester, or the reviewer(s) before Publish.
- Reviewers for this run: normal reviewer plus `security` specialty reviewer; both must `accept`.

## Acceptance criteria
- AC1-AC7 from the SDD.
- Failure path: scenario 24 expects `stopped` for a dirty tree with nothing committed and is in the §5 regression list; mode and spec say any failed condition stops for a dirty tree.
- New tests in E14 pass; existing tests pass unchanged except the two regression-string updates (E12, E13).

## Validation commands
- `uv run python -m unittest tests.test_orchestrate tests.test_orchestrate_host_dispatch tests.test_orchestrate_host_questions -q`
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` (no output)
- `git status --porcelain` (only the 7 files above, plus gitignored artifacts not shown)

## Stop conditions
- Any anchor text in E1-E15 is not found exactly once: stop with `needs_more_evidence`.
- A test outside E12-E14 needs a change to pass: stop; it means a pinned phrase was broken.
- Any change needed outside `Files likely to change`.

## Non-blocking details execute may decide
- Test class and method names, placement of the new class, and phrase-list order in E14.
- Mode step 1a stays one line, like the other steps. Spec §9a wording may be adjusted only if the E14 phrases still match.

## Risk notes
- `security_boundary_change`: the dirty-tree stop is narrowed. Mitigated by the four conditions, `✗` exclusion, `Gate 2` `✓` requirement, and mandatory 6a + fresh test + review.
- Report tampering can choose the resume point but cannot skip test or review.
- Merge order: if #15 lands first, its edits touch reviewer guard text, not these anchors; re-check anchors on rebase.

## Expected execution report format
`.forge/generated/reports/2026-11-24-orchestrate-resume-in-place-execution-report.md`: files changed (exact paths), each edit E1-E15 with done/skipped, validation commands with results, deviations, and a `FORGE_RESULT` block.

## Target tool instructions
- Use the smallest safe edit mechanism of the target tool (Claude Code: normal file edits; Codex: `apply_patch`).
- Do not widen scope beyond this ECP. Do not stage, commit, or push.
