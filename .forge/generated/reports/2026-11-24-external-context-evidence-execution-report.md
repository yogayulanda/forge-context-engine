# Execution Report: Evidence rules for external context

| Field | Value |
|---|---|
| Artifact | execution-report |
| Date | 2026-11-25 |
| Slug | `external-context-evidence` |
| Branch | `forge/2026-11-24-external-context-evidence` |
| ECP | `.forge/generated/ecp/2026-11-24-external-context-evidence-ecp.md` (accepted at Gate 2, task 7 dropped) |
| SDD | `.forge/generated/plans/2026-11-24-external-context-evidence-plan.md` (issue #14) |
| Status | `success` |

## Files changed
1. `src/forge_context_engine/runtime_templates/base/.forge/adapter.md` (new `## External context` section before `## Cross-tool output expectations`)
2. `runtime/.forge/adapter.md` (same block, same anchor)
3. `src/forge_context_engine/runtime_templates/base/.forge/runtime/meta/conventions-evidence.md` (new `## External Context Evidence` section before `## Implicit Constraint Extraction`)
4. `runtime/.forge/runtime/meta/conventions-evidence.md` (same block, same anchor)
5. `validation-cases/external-context-evidence.md` (new, ECP full content)
6. `tests/test_orchestrate.py` (new `OrchestrateContractTests.test_external_context_is_cited_and_never_authoritative`, after `test_output_redaction_is_shared_and_checked_before_publish`)

`docs/release-notes.md` not edited (task 7 dropped at Gate 2).

## Per-task result
| Task | Result |
|---|---|
| 1-4 | Done. Identical blocks inserted by anchor match (each anchor found exactly once); whole files were not copied, old drift kept. |
| 5 | Done. |
| 6 | Done. Test code as given in the ECP. |
| 7 | Dropped (Gate 2). |

## Validation
| Command | Exit | Result |
|---|---|---|
| `uv run python -m unittest discover -s tests -q` (baseline before edits) | 0 | 148 tests OK |
| `uv run python -m unittest discover -s tests -q` (after edits) | 0 | 149 tests OK (baseline + 1) |
| `diff <(sed -n '/^## External context/,/^## /p' runtime/...adapter.md) <(... template adapter.md)` | 0 | no output |
| `diff <(sed -n '/^## External Context Evidence/,/^## /p' runtime/...conventions-evidence.md) <(... template)` | 0 | no output |
| `diff runtime/.forge/adapter.md src/.../base/.forge/adapter.md` | 1 | only the old lifecycle hunks (`33c33,34`, `46a48`) |
| `git diff --name-only` / `git status --short` | 0 | files 1-4 and 6 modified, file 5 untracked; nothing else (report under `.forge/generated/` is ignored) |
| AC4 failure path: changed `the repository wins` in `runtime/.forge/adapter.md`, ran `tests.test_orchestrate`, restored file | - | `FAILED (failures=1)`; file restored, section text verified back |
| Legacy marker grep (`knowledge/`, `01-core/`) in new text | - | none (also asserted in the test for the conventions section) |
| Repo security checks | - | none found (no Makefile, no CI workflows, no audit tool in `pyproject.toml`) |

## Decisions taken (non-blocking)
- Front-matter `updated:` in files 3/4 left unchanged (kept identical in both).
- Example ref kept as `external:memory/search`.
- Test helper names and phrase order kept as in the ECP.

## Deviations
None. Task 7 dropped as instructed by the Gate 2 note.

## Blockers
None.

## Next mode
`review`
