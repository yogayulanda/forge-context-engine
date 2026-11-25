# Review Report: Orchestrate optional host status and question contract (issue #8)

| Field | Value |
|---|---|
| Artifact | review |
| Date | 2026-11-25 |
| Slug | `host-status-questions` |
| Rounds | 2 |
| Reviewers | normal reviewer + `security` reviewer, fresh read-only subagents each round |
| Verdict | `accept` (both reviewers, round 2) |

## Round 1
### Normal reviewer: `accept`
All 9 ACs pass; 170 tests OK; copies identical; scope inside ECP plus tester file. Minor:
1. `specialties/tech-lead.md:31` still says all questions go in one batch (outside ECP; follow-up).
2. `specs/orchestrate.md` 8a Timeout bullet missed "answers received so far in the report `Note`".
3. Mode step 3 said a timeout "puts the answer" in the `Note`.

### Security reviewer: `request_changes`
1. MAJOR `specs/orchestrate.md` 8a, mode step 3: the Gate 1 question inherited "exactly one recommended label"; a host that preselects or auto-submits the recommended option on expiry could pass Gate 1 without a human choice. Fix: no recommended/default option at Gate 1; default, preselected, or expired answers count as a timeout.
2. MINOR: `Approve` must be matched by the selected option, not by text.
3. MINOR: worker `done` could be read as run-level `done`.
4. MINOR: clarification options must never show `Approve <SDD path>` and never count as Gate 1 approval.
5. MINOR: reports must state no security/static scan command exists.

## Fix round 1
Executor fixed security 1-5 and normal 2-3 in the mode (both copies), four worker prompts (both copies), spec 8a, and `tests/test_orchestrate.py`. Tester added 7 tests in `tests/test_orchestrate_host_questions.py`. Suite: 177 tests OK.

## Round 2
### Normal reviewer: `accept`
All 9 ACs pass; all round 1 findings resolved. Minor (open):
1. `specs/orchestrate.md:130`: spec 8a Gate 1 bullet is shorter than mode step 3 (does not name `Stop`, the `Note` entry, or the `Gate 1: human (question tool)` trace).
2. `validation-cases/orchestrate-gates.md:59`: rejected-behavior bullet does not list a default/preselected/expired answer as non-approval (unit tests cover it).
3. `specialties/tech-lead.md:31` one-batch wording (known follow-up, out of scope).

### Security reviewer: `accept`
All five round 1 findings resolved; no bypass through worker output, free text, timeout, or injected labels; stop conditions and high-risk classification unchanged; Gate 2 unchanged. Minor (open):
1. Mode `## host status and questions` Timeout bullet and spec 8a: the default/preselected/expired rule covers only Gate 1. For clarification questions, an auto-selected answer would be recorded as a Confirmed Decision. Not an approval bypass (Gate 1 still classifies the SDD). Fix: apply the rule to every question.

## Validation
- `uv run python -m unittest discover -s tests -q`: 177 tests OK (re-run by both round 2 reviewers).
- Mode and four worker prompt copy pairs identical.
- No security/static scan command exists in the repo; none ran.

## Risk flags
- `external_contract_change`, `security_boundary_change`: declared in the SDD, human-approved at Gate 1.
- Rules are prompt-level; each host must implement them. Forge cannot verify that a human, not host automation, answered.

## Context impact
`update_needed: false`: spec 8a is the durable record of this contract.

**Verdict: `accept`**
