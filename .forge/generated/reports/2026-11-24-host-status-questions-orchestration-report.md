# Orchestration Report: Optional host status and question contract

| Field | Value |
|---|---|
| Artifact | orchestration_report |
| Repo | forge-context-engine @ base `forge/2026-11-24-external-context-evidence` |
| Date | 2026-11-25 |
| Target tool | orchestrator=claude-code; planner=subagent; executor=subagent; tester=subagent; reviewer=subagent (+ security subagent) |
| Specialties | orchestrator=tech-lead; executor=none; tester=testing; reviewer=none, security |
| Status | mr_opened |
| Run | host-status-questions on branch `forge/2026-11-24-host-status-questions` |
| Goal | Let a host with status and question tools receive live stage status and ask clarification and Gate 1 questions one at a time (issue #8). |
| Note | Stacked on the #14 branch. git guard hook missing (no `.claude/settings.json`); worker git guard not confirmed (general-purpose subagents with tracked role prompts). |

## Steps
✓ Preflight (feature branch from previous run)
✓ Clarify: 0 questions
✓ SDD -> .forge/generated/plans/2026-11-24-host-status-questions-plan.md
✓ Gate 1: human (approved 2026-11-25; Q5 = B recorded under Confirmed Decisions)
✓ ECP
✓ Gate 2
✓ Execute
✓ Test (scenarios: 9 acceptance criteria + 7 fix-round scenarios, full suite)
✓ Review round 1 (security: request_changes)
✓ Fix round 1
✓ Review round 2 (both accept)
✓ Publish (push + MR/PR)

## Artifacts
| Type | Path | Status |
|---|---|---|
| SDD | `.forge/generated/plans/2026-11-24-host-status-questions-plan.md` | ready_for_implementation |
| ECP | `.forge/generated/ecp/2026-11-24-host-status-questions-ecp.md` | accepted |
| Execution report | `.forge/generated/reports/2026-11-24-host-status-questions-execution-report.md` | complete (incl. fix round 1) |
| Test report | `.forge/generated/reports/2026-11-24-host-status-questions-test-report.md` | pass (round 2) |
| Review | `.forge/generated/reviews/2026-11-24-host-status-questions-review.md` | accept |
| Orchestration report | `.forge/generated/reports/2026-11-24-host-status-questions-orchestration-report.md` | mr_opened |

## Gate trace
- Gate 1: human - `external_contract_change`, `security_boundary_change` (uncertain, treated as match); approved 2026-11-25 with Q5 = B (host state `waiting_for_human`) and an extra security reviewer.
- Gate 2: auto - ECP scope matches the SDD; one concretization (Gate trace template gains `human (question tool)`).

## Validation
| Command | Result |
|---|---|
| `uv run python -m unittest discover -s tests -q` | 177 tests OK |
| mode and four worker prompt copy diffs | identical |
| security/static scan | none exists in the repo |

## Test scenarios
| Entry point | Category | Scenario | Result |
|---|---|---|---|
| mode host section | Contract | stage IDs, host states, Q5 B mapping, one question at a time | pass |
| mode step 3 | Failure path | free text, `Stop`, timeout, default/preselected/expired answer never approve | pass |
| worker prompts | Contract | `## Host status`, never use a question tool, `done` only own stage | pass |
| planner | Contract | 2-4 options, one recommendation, free text recorded | pass |
| boundary | Security | worker result never a human answer or Gate 1 approval | pass |
| e2e | n/a | no e2e harness | n/a |

## Review rounds
| Round | Tester | Reviewer | Open findings |
|---|---|---|---|
| 1 | pass | normal accept; security request_changes | 1 major, 7 minor |
| 2 | pass | normal accept; security accept | 4 minor (spec 8a Gate 1 wording; validation case bullet; tech-lead one-batch line; default-answer rule for clarification questions) |

## MR/PR
See the pull request for branch `forge/2026-11-24-host-status-questions`.

## Lessons (proposals only)
- Planner: when a contract inherits a general rule ("one recommended option"), check whether an approval question must be excluded from it.
- Follow-up: `specialties/tech-lead.md:31` should allow one-at-a-time questions when a host question tool exists.
