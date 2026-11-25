# Review Report: Worker handoff envelope and result block (issue #13)

| Field | Value |
|---|---|
| Artifact | review |
| Date | 2026-11-25 |
| Slug | `worker-result-block` |
| Round | 1 |
| Reviewer | fresh-context subagent, read-only |
| Verdict | `accept` |

## Summary
Adds `## worker handoff` to both mode copies with the 9-field `FORGE_HANDOFF` envelope and the 6-field `FORGE_RESULT` block. All four worker prompts end with a role-specific `FORGE_RESULT` block; spec section 8 gains one paragraph; one release-notes line. Tests: 3 in `tests/test_orchestrate.py`, 17 in new `tests/test_worker_result_block.py`. Copies byte-identical; changes inside ECP scope.

## Acceptance criteria
| AC | Result | Evidence |
|---|---|---|
| 1 Mode section, 9 + 6 fields, copies identical | pass | `diff -q` clean; `test_mode_defines_handoff_envelope_and_result_block` |
| 2 Four prompts end with block, values per role | pass | `test_worker_prompts_end_with_result_block`, `test_each_role_lists_exactly_its_a1_status_and_verdict_values` |
| 3 Block first, then artifact; five `blocked` cases | pass | `orchestrate.md:102`; phrase asserts |
| 4 No new status or stop condition | pass | `test_status_values_and_stop_conditions_are_unchanged`; host dispatch tests unchanged |
| 5 Spec section 8 names both markers; `host` bullet unchanged | pass | spec diff adds lines only |
| 6 Sync test | pass | suite run |
| 7 Full suite green | pass | 197 tests OK |

## Findings
Critical: none. Major: none.

Minor:
1. `runtime/.forge/runtime/modes/orchestrate.md:102` (and template copy): "a value outside the listed ones" does not say which list counts; the mode block merges all roles' values, so a reviewer `verdict: pass` passes the mode-level check. Cannot cause a false accept (step 9 needs `accept`), but the resulting flow is undefined. Fix: "a value outside the ones listed for that role", plus a test where reviewer `verdict: pass` is `blocked`.
2. `orchestrate.md:126` (step 6b, outside this change): "`blocked_by_environment` for e2e is reported" reads like a verdict value; the tester now signals it in `note`. Fix later: "the tester `note` names e2e `blocked_by_environment`".

## Validation
- `uv run python -m unittest discover -s tests -q`: 197 tests OK (re-run).
- Mode and four agent copy pairs identical.
- Changed files match the ECP inventory plus the tester's new test file.
- No security/static scan command exists in the repo.

## Risk flags
- `external_contract_change` (`FORGE_HANDOFF` / `FORGE_RESULT` in packaged templates): human-approved at Gate 1.
- Under `cli` and `host` dispatch, a result without the block now counts as `blocked`; release notes state it.
- No migration, no secret; neutral English, ASCII only.

## Context impact
`update_needed: false`. Worker prompts grow by about 12 lines each, the mode by about 30; capped results should reduce orchestrator context per worker.

**Verdict: `accept`**
