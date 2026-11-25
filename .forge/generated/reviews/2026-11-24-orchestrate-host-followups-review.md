# Review Report: Orchestrate follow-ups from the host dispatch run (issue #18)

| Field | Value |
|---|---|
| Artifact | review |
| Date | 2026-11-25 |
| Slug | `orchestrate-host-followups` |
| Round | 1 |
| Reviewer | fresh-context subagent, read-only |
| Verdict | `accept` |

## Scope
The 10 tracked files match the SDD inventory; `tests/test_orchestrate_host_followups.py` was added by the tester (allowed by D3). No Python runtime or CLI change, no migration, no secret. D4 (`waiting_for_human` untouched) and D5 (historical `-sdd.md` artifact not renamed) honoured.

## Acceptance criteria
| AC | Result | Evidence |
|---|---|---|
| AC1 | pass | Step 1 in both mode copies names the rules file, role `orchestrator`, and the advisory note; stop conditions clean |
| AC2 | pass | Mode `Git guard under host` bullet and spec `host` bullet carry both notes; §6a covers role `orchestrator` |
| AC3 | pass | Planner, mode, and spec name `-plan.md` and the `plan` statuses; no shipped file contains `-sdd.md` |
| AC4 | pass | Failure-path tests break a copy and check the message names it |
| AC5 | pass | No `. ` in asserted literals; no `"Gate 1 approval"` assert; copy loops pass `name` |
| AC6 | pass | 228 tests OK (baseline 214); sync test passes |
| AC7 | pass | Porcelain shows the inventory plus the tester file |

## Findings
Critical: none. Major: none.

Minor:
1. `.forge/generated/ecp/2026-11-24-orchestrate-host-followups-ecp.md:385`: the `-sdd.md` grep check expects no output but matches the new negative assert at `tests/test_orchestrate.py:312`. Artifact gap only; exclude `tests` from the check.
2. `tests/test_orchestrate.py:314,317`: two template-only asserts have no copy-naming message. Fix: pass `"orchestrate.md (template)"`.
3. `specs/orchestrate.md:121`: the `host` bullet does not name `git-guard-rules.json` (section 6a does). Optional: add "(section 6a)".

## Validation
- `uv run python -m unittest discover -s tests -q`: 228 tests OK (re-run).
- Runtime vs template copies of `orchestrate.md`, `forge-planner.md`, `specialties/testing.md`: identical.
- Remaining `draft` hits are unrelated (`write_behavior`, document statuses in other specs).
- No security/static scan command exists in the repo.

## Risk flags
- `external_contract_change`: packaged mode/planner text gains an advisory `Note` value; approved at Gate 1 (D1).
- Orchestrator guard for non-Claude hosts is advisory wording only; hook and rules JSON unchanged.

**Verdict: `accept`**
