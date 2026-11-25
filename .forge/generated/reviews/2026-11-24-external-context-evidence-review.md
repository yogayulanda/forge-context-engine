# Review Report: Evidence rules for external context (issue #14)

| Field | Value |
|---|---|
| Artifact | review |
| Date | 2026-11-25 |
| Slug | `external-context-evidence` |
| Round | 1 |
| Reviewer | fresh-context subagent, read-only |
| Verdict | `accept` |

## Diff reviewed
`git diff HEAD` plus untracked files: both `adapter.md` copies, both `conventions-evidence.md` copies, `tests/test_orchestrate.py`, new `validation-cases/external-context-evidence.md`, new `tests/test_external_context_evidence.py` (tester).

## Summary
Adds the five-rule `## External context` section to both adapter copies after `Source of truth`, a matching `## External Context Evidence` section to both `conventions-evidence.md` copies, one validation case, and guard tests. Text matches SDD Proposed Approach 1-4. Release notes dropped per the Gate 2 note; existing drift between copies unchanged.

## Acceptance criteria
| AC | Result | Evidence |
|---|---|---|
| AC1 | pass | Section diff empty; test checks phrases and copy equality |
| AC2 | pass | Section diff empty; test checks ref form, never `confirmed`, promotion entry types |
| AC3 | pass | Five scenarios incl. contradiction (2) and injected instruction (3); tester checks each row |
| AC4 | pass | Heading asserted and copies compared; tester mutation runs M1-M3 failed as required |
| AC5 | pass | 157 tests OK; no `knowledge/` or `01-core/` in new text |
| AC6 | pass | 6 ECP files plus tester's test file (allowed under test paths) |

## Findings
Critical: none. Major: none.

Minor:
1. `tests/test_external_context_evidence.py:13`: `_section` does not assert the heading exists before splitting; a missing heading gives an `IndexError` instead of a clean failure. Fix: assert the heading is present first.
2. `tests/test_external_context_evidence.py:10-14`, `tests/test_orchestrate.py:168-170`: two near-duplicate section helpers and overlapping AC1/AC2 checks. Optional cleanup.

## Validation
- `uv run python -m unittest discover -s tests -q`: 157 tests OK (148 + 1 executor + 8 tester).
- Both section diffs empty; full adapter diff shows only the pre-existing hunks `33c33,34`, `46a48`.
- The `Untrusted input` heading referenced by the new text exists in both planner copies.

## Risk flags
- `external_contract_change`: managed adapter template ships to target repos; approved at Gate 1.
- `security_boundary_change`: untrusted-input rule extended to all tools, writes to external stores forbidden; approved at Gate 1, no security reviewer by human decision.
- No migration, secret, CLI, config, or install manifest change. Neutral English confirmed.

## Context impact
`update_needed: false`: the rule lives in the managed runtime/template files.

## Not checked
AC4 mutation runs were not repeated (read-only review).

**Verdict: `accept`**
