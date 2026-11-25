# Execution Report: Orchestrate optional host status and question contract

| Field | Value |
|---|---|
| Artifact | execution report |
| Date | 2026-11-25 |
| ECP | `.forge/generated/ecp/2026-11-24-host-status-questions-ecp.md` (accepted at Gate 2 by the orchestrator) |
| SDD | `.forge/generated/plans/2026-11-24-host-status-questions-plan.md` (issue #8) |
| Branch | `forge/2026-11-24-host-status-questions` |
| Status | `success` |

## Changed files
Equal to the ECP `Files likely to change` (14 paths):
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
12. `validation-cases/orchestrate-gates.md`
13. `tests/test_orchestrate.py`
14. `docs/release-notes.md`

Plus this report.

## Tasks
- T1 mode: E1-E8 applied verbatim (new `## host status and questions` section between `## worker dispatch` and `## behavior`; steps 2, 2b, 3; report `## Steps` stage IDs; Gate trace; step-marker line; `next mode transitions`).
- T2 planner: P1-P5 applied verbatim.
- T3 executor, tester, reviewer: `## Host status` inserted between `## Specialty overlays` and `## Role` with stages `execute`, `test`, `review`.
- T4 spec: 4b wording (S1) and new section 8a (S2). No new line in 8a starts with `- `host`:`.
- T5 validation case: rows 20-22 after row 19; rejected-behavior line scoped; new last bullet added. Row 18 and the regression sentence unchanged.
- T6 release notes: one bullet after the `run.worker` bullet.
- T7 tests: `OrchestrateHostInteractionTests` inserted verbatim from the ECP after `OrchestrateSourceSyncTests`.

Every anchor was matched exactly once (edits were applied by a script that asserted a single match per anchor).

## Copy sync (files 1-10)
| Pair | `diff` before | `diff` after |
|---|---|---|
| `modes/orchestrate.md` | no output | no output |
| `agents/forge-planner.md` | no output | no output |
| `agents/forge-executor.md` | no output | no output |
| `agents/forge-tester.md` | no output | no output |
| `agents/forge-reviewer.md` | no output | no output |

Runtime copies edited, then copied to the template copies (Copy sync rule step 2).

## Validation
| Command | Result |
|---|---|
| `uv run python -m unittest discover -s tests -q` | `Ran 164 tests` - `OK` |
| `diff runtime/.forge/runtime/modes/orchestrate.md src/.../modes/orchestrate.md` | no output |
| `for r in planner executor tester reviewer; do diff ...; done` | no output |
| `git diff -- runtime/.forge/runtime/agents/ \| grep -n "Return to orchestrator"` | no output (exit 1) |
| `git status --porcelain` | exactly the 14 ECP paths (`M`); this report is under ignored `.forge/generated/` |

Fails-without-change check: the new test file was run against a `git archive HEAD` export in the scratchpad: 7 tests, 4 failures and 2 errors. The one passing test (`test_mode_status_values_and_stop_conditions_unchanged`) is a regression guard and is expected to pass before and after.

Security checks: the repo defines no vulnerability or static-analysis command (no Makefile, no such entry in `pyproject.toml` or `.github`).

## Deviations
None.

## Decisions taken (non-blocking)
- `updated:` frontmatter of the four role prompts not bumped (keeps diffs minimal; ECP left it optional).
- Test class kept in ECP order and wording; two blank lines between classes as in the file.

## Blockers
None.

## Risks
- `runtime/.forge/runtime/agents/specialties/tech-lead.md:31` still says all questions go in one batch at the start; correct for the no-tool path, out of scope (ECP risk note).

## Next mode
`review` (normal reviewer plus `security` reviewer).

## Fix round 1

| Finding | Change | Status |
|---|---|---|
| S1 (major, security) | Mode step 3 and spec 8a: the Gate 1 question has no recommended or default option; an answer the host picked by default, by preselection, or on expiry counts as a timeout, never as `Approve`. New asserts in `tests/test_orchestrate.py::test_steps_2_and_3_question_tool_path` (fail without the change). | resolved |
| S2 | Mode step 3 and spec 8a: `Approve` means the selected `Approve <SDD path>` option, never free text that reads like approval. | resolved |
| S3 | `## Host status` in all four worker prompts: a worker's `done` covers only its own stage; only the orchestrator reports run-level `done`, with stage `publish`. Same rule added to spec 8a workers bullet; mode status-report bullet now says `done` with stage `publish`. | resolved |
| S4 | Mode host questions part: a clarification question never shows an `Approve <SDD path>` option, and a clarification answer is never Gate 1 approval. Same sentence in spec 8a. | resolved |
| R2 | Spec 8a Timeout bullet: lists the answers received so far in the report `Note`. | resolved |
| R3 | Mode step 3: puts the answer, or `timeout` for a timeout, in the report `Note` (both copies). | resolved |

Wording kept compatible with existing asserts (`only \`Approve\` continues to step 4`, `any other answer, including free text, or a timeout stops with \`awaiting_sdd_approval\``); no existing assert was edited. `specialties/tech-lead.md` untouched (follow-up).

Changed in this round: `runtime/.forge/runtime/modes/orchestrate.md`, `runtime/.forge/runtime/agents/forge-{planner,executor,tester,reviewer}.md`, their template copies under `src/forge_context_engine/runtime_templates/base/.forge/runtime/`, `specs/orchestrate.md`, `tests/test_orchestrate.py`. All inside `Files likely to change`.

Validation:
- Copy pairs: identical before editing; after edit + `cp`, `diff -q` on all 5 pairs: identical.
- `uv run python -m unittest discover -s tests -q`: Ran 170 tests, OK (first two runs failed on my own step 3 wording vs existing asserts; wording fixed, test unchanged).
- Security/static scan: the repo has no security or static-analysis command, so none ran.
