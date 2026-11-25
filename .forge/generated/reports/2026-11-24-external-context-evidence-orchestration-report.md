# Orchestration Report: Evidence rules for external context

| Field | Value |
|---|---|
| Artifact | orchestration_report |
| Repo | forge-context-engine @ base `forge/2026-11-24-publish-force-add-artifacts` |
| Date | 2026-11-25 |
| Target tool | orchestrator=claude-code; planner=subagent; executor=subagent; tester=subagent; reviewer=subagent |
| Specialties | orchestrator=tech-lead; executor=none; tester=testing; reviewer=none |
| Status | mr_opened |
| Run | external-context-evidence on branch `forge/2026-11-24-external-context-evidence` |
| Goal | Define how external context (MCP, memory, web) may be cited as evidence and never be authoritative (issue #14). |
| Note | Stacked on the #12 branch. git guard hook missing (no `.claude/settings.json`); worker git guard not confirmed (general-purpose subagents with tracked role prompts). |

## Steps
✓ Preflight (feature branch from previous run)
✓ Clarify: 0 questions
✓ SDD -> .forge/generated/plans/2026-11-24-external-context-evidence-plan.md
✓ Gate 1: human (approved 2026-11-25)
✓ ECP
✓ Gate 2
✓ Execute
✓ Test (scenarios: 6 acceptance criteria, full suite)
✓ Review round 1
✓ Publish (push + MR/PR)

## Artifacts
| Type | Path | Status |
|---|---|---|
| SDD | `.forge/generated/plans/2026-11-24-external-context-evidence-plan.md` | ready_for_implementation |
| ECP | `.forge/generated/ecp/2026-11-24-external-context-evidence-ecp.md` | accepted with Gate 2 trim |
| Execution report | `.forge/generated/reports/2026-11-24-external-context-evidence-execution-report.md` | complete |
| Test report | `.forge/generated/reports/2026-11-24-external-context-evidence-test-report.md` | pass |
| Review | `.forge/generated/reviews/2026-11-24-external-context-evidence-review.md` | accept |
| Orchestration report | `.forge/generated/reports/2026-11-24-external-context-evidence-orchestration-report.md` | mr_opened |

## Gate trace
- Gate 1: human - SDD names `external_contract_change` and `security_boundary_change` (uncertain, treated as match); approved 2026-11-25; no extra security reviewer by human decision.
- Gate 2: auto - after the orchestrator dropped ECP task 7 (`docs/release-notes.md`), which the SDD lists as a non-goal. Remaining scope matches the SDD.

## Validation
| Command | Result |
|---|---|
| `uv run python -m unittest discover -s tests -q` | 157 tests OK |
| section diffs (adapter, conventions-evidence pairs) | empty |

## Test scenarios
| Entry point | Category | Scenario | Result |
|---|---|---|---|
| adapter section | Contract | phrases present, copies equal, placed after `Source of truth` | pass |
| conventions-evidence section | Contract | ref form, never `confirmed`, promotion entry types | pass |
| `forge init` output | Integration | both new sections installed | pass |
| validation case | Failure path | contradiction: repository wins; injected instruction ignored | pass |
| copy sync | Regression | mutation of either copy fails the test | pass |
| e2e | n/a | no e2e harness | n/a |

## Review rounds
| Round | Tester | Reviewer | Open findings |
|---|---|---|---|
| 1 | pass | accept | 2 minor (`_section` heading assert; duplicate helpers) |

## MR/PR
See the pull request for branch `forge/2026-11-24-external-context-evidence`.

## Lessons (proposals only)
- Planner added `docs/release-notes.md` against an SDD non-goal by copying the previous run; proposal: planner keeps the SDD non-goals list as a hard filter for ECP files.
