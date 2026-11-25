# Review Report: Orchestrate resume in place after a lost session (issue #16)

| Field | Value |
|---|---|
| Artifact | review |
| Date | 2026-11-25 |
| Slug | `orchestrate-resume-in-place` |
| Rounds | 3 (2 fix rounds) |
| Reviewers | normal reviewer + `security` reviewer, fresh read-only subagents each round |
| Verdict | `accept` (both reviewers, round 3) |

## Round 1
- Normal: `accept`. AC1-7 pass, 207 tests OK. Planner refinements accepted (Gate 2 `✓` required; tester test paths only after a `[test]` step per Q4; fix-round counter from `[execute]` lines; never resumes at Publish). Minor: ambiguous "ECP's date and slug"; a crash during a fix-round `[execute]` skipped the fix; execution-report lookup not tied to `Artifacts`.
- Security: `request_changes`. MAJOR: the scope check accepted any `Artifacts` table path from the editable, gitignored report (e.g. `src/x.py`), which step 9 then force-adds. Notes (no fix required): Gate 1 not re-checked on resume; fix-round count read from the editable report; adopted test-path files run as code before review; "Scope grows" wording predates this change.

## Fix round 1
Step 1a and spec §9a: `Artifacts` paths accepted only under `.forge/generated/` with the ECP's `<YYYY-MM-DD>-<slug>` prefix; report located by the ECP file's date and slug; `✱` `[execute]` re-runs execute in the same round; execution report lookup per `Artifacts`.

## Round 2
- Normal: `accept`, no findings. 212 tests OK.
- Security: `request_changes`. MAJOR: the filter applied only to porcelain-visible paths; a gitignored file (e.g. `.env`) added to `Artifacts` never shows in porcelain but would be force-added at step 9. Minor: R2 wording when no review findings exist yet.

## Fix round 2
Every `Artifacts` table path must be under `.forge/generated/` with the ECP's `<YYYY-MM-DD>-<slug>` prefix, else stop for a dirty tree, with the reason stated; R2 wording "the ECP, plus the last review findings if any".

## Round 3
- Normal: `accept`. Minor (open): no validation scenario for the all-`Artifacts`-paths stop; the prefix rule assumes all artifacts share the ECP's date (fails closed).
- Security: `accept`. Low notes (open): prefix collision with a same-date slug that extends this one (`<slug>-v2`); `..` segments not explicitly forbidden (step 9 cached-name preflight would likely flag). Earlier notes not worsened.

## Validation
`uv run python -m unittest discover -s tests -q`: 214 tests OK. Mode copies identical. No security/static scan command exists in the repo.

## Risk flags
- Narrows the dirty-tree stop: `security_boundary_change`, `external_contract_change`; human-approved at Gate 1 with an extra security reviewer.
- Tests check contract text only; the SDD's full-version deterministic scope script remains the stronger safeguard.

**Verdict: `accept`**
