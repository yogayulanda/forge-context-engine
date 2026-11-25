# Execution Report: Worker handoff envelope and result block

| Field | Value |
|---|---|
| Artifact | execution report |
| Date | 2026-11-25 |
| Slug | `worker-result-block` |
| ECP | `.forge/generated/ecp/2026-11-24-worker-result-block-ecp.md` |
| SDD | `.forge/generated/plans/2026-11-24-worker-result-block-plan.md` (issue #13) |
| Branch | `forge/2026-11-24-worker-result-block` |
| Execute status | `success` |

## Pre-edit check
- The working tree was clean on the expected branch.
- Before editing, the runtime and template copies of the mode and the four agent prompts were byte-identical (`diff` showed no output).

## Tasks applied
- T1: Replaced the result sentence in the mode `run.worker: cli` bullet.
- T2: Added the envelope and result-block sentence to the mode `run.worker: host` bullet. The other sentences are unchanged.
- T3: Added a new `## worker handoff` section between `## worker dispatch` and `## host status and questions`.
- T4: Replaced the `## Return to orchestrator` body in the planner, executor, tester, and reviewer prompts with the exact ECP text.
- T5: Added a worker handoff paragraph to `specs/orchestrate.md` section 8, after the `host` bullet and before section 8a.
- T6: Added a release-notes bullet under `## Unreleased`.
- T7: Added three tests to `OrchestrateContractTests`, after `test_publish_force_adds_listed_artifacts_with_preflight`.
- Each runtime file was edited first, then copied to its template path with `cp`.

## Changed files
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

This report is the only other file written. It is under `.forge/generated/`, which is gitignored.

## Validation
- `uv run python -m unittest discover -s tests -q`: `Ran 180 tests ... OK`.
- `diff` of the mode pair: identical, no output.
- `diff` loop over the planner, executor, tester, and reviewer pairs: all identical, no output.
- `git status --porcelain`: exactly the 13 files listed above, all modified (`M`). No untracked files.
- Security or static scan: the repository has no security or static-analysis command in a Makefile or CI config, so no scan was run.

## Deviations
None. Each text edit uses the exact ECP strings, and the tests match the ECP reference code.

## Decisions taken (non-blocking)
- `_block` is a `@staticmethod` on `OrchestrateContractTests`.
- `RESULT_FIELDS` and `ENVELOPE_FIELDS` are class attributes, as in the ECP reference.
- Test names follow the ECP reference.

## Blockers
None.

## Risks
- This is an external contract change: `cli` and `host` workers that return free text without a `FORGE_RESULT` block now stop as `blocked`. The release note states this.
- The new tests were not run against the pre-change tree, because no git state-changing commands were allowed. They depend on the new `## worker handoff` section and the `FORGE_RESULT` blocks, so they fail without the change.

## Next mode
`review`
