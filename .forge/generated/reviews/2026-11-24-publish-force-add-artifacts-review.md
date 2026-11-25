# Review Report: Orchestrate publish step force-adds this run's artifacts

| Field | Value |
|---|---|
| Artifact | review |
| Date | 2026-11-25 |
| Slug | `publish-force-add-artifacts` |
| Round | 1 |
| Reviewer | fresh-context subagent, read-only |
| Verdict | `accept` |

## Diff reviewed
`git diff master` on `forge/2026-11-24-publish-force-add-artifacts`, uncommitted, 7 files (+88 / -5): `docs/release-notes.md`, both `orchestrate.md` mode copies, `specs/orchestrate.md`, `validation-cases/orchestrate-gates.md`, `tests/test_orchestrate.py`, `tests/test_git_guard.py`.

## Summary
Step 9 of both mode copies (byte-identical) stages code by explicit path, force-adds only the `Artifacts` table paths (never a directory or glob), excludes `.forge/temp/` and `.forge/cache/`, and checks `git diff --cached --name-only` against the expected set. The matching stop condition is in the mode and spec section 6. Spec section 7 keeps `/generated/**` ignored and keeps "No force-push." Validation scenario 19 and a section 3 rejected behavior were added; scenario 18 and its regression sentence are unchanged. Text matches the ECP.

## Acceptance criteria
| AC | Status | Evidence |
|---|---|---|
| 1 | met | Phrases in step 9 of both copies; copies identical; `test_runtime_copies_match_templates`, `test_publish_force_adds_listed_artifacts_with_preflight` pass |
| 2 | met | Stop bullet in mode and spec section 6; `test_spec_stop_list_has_staged_set_mismatch` |
| 3 | met | Spec section 7 explicit-path force-add, preflight, `/generated/**` stays ignored; asserted |
| 4 | met | `git diff --quiet master -- runtime_ops.py ...` exit 0 |
| 5 | met | Guard unchanged; `git add -f -- <path>` allowed; `git push -f` still blocked alone and chained |
| 6 | met | Row 19 "an extra staged path stops before commit"; asserted |
| 7 | met | Scenario 18 row and regression sentence unchanged; host dispatch tests pass |
| 8 | met | Reviewer re-ran suite: 148 tests OK |

## Findings
Critical: none. Major: none.

Minor:
1. `tests/test_orchestrate.py:292-293`, `:322-323` (style): three blank lines before `PublishForceAddSpecAndValidationTests`, one before `if __name__ == "__main__":`; PEP 8 wants two in both places.
2. `runtime/.forge/runtime/modes/orchestrate.md:87`, template copy, `specs/orchestrate.md` section 7 (contract consistency, accepted by design): step 6b allows test files the tester "added or changed", step 9 preflight allows only "added". A changed existing test file outside ECP scope would stop at step 9. Fails closed and matches the Gate 1 wording; a follow-up could say "added or changed".

## Validation
- Full suite 148 tests OK (execution report's 143 predates the tester's 5 tests).
- Mode copies identical; `git diff --name-only master` equals the 7 ECP files; guard and `runtime_ops.py` unchanged.
- Test run left no files behind.

## Lifecycle and risk
- All changes inside ECP scope; tester files under test paths; nothing staged; untracked `.forge/runtime/` untouched.
- `external_contract_change` and `security_boundary_change` present and human-approved at Gate 1. No migration, no secret.
- No secrets, personal names, hostnames, or IPs in the diff; text is neutral English.

## Context impact
`update_needed: false`: the shipped mode, spec, and validation text are the source of truth for this behavior.

## Not checked
Whether orchestrator agents follow the new step 9 text; it is an instruction, not a script (SDD non-goal).

**Verdict: `accept`**
