# Orchestration Report: add worker dispatch type `host` (#7)

| Field | Value |
|---|---|
| Artifact | orchestration_report |
| Repo | forge-context-engine @ 928102d |
| Date | 2026-11-20 |
| Target tool | orchestrator=claude-code; planner=subagent; executor=subagent; tester=subagent; reviewer=subagent |
| Specialties | orchestrator=tech-lead; executor=none; tester=testing; reviewer=testing (+security proposed) |
| Status | blocked_by_environment |
| Run | worker-dispatch-host on branch `forge/2026-11-20-worker-dispatch-host` |
| Goal | Add `run.worker: host` so long-lived hosts dispatch workers through their own tool without overriding the mode. |
| Note | Branch pushed; MR/PR not opened: `gh` CLI not installed (open it from the compare URL with the prepared body). Open non-blocking findings need human acceptance in the MR/PR: security MINOR 3-5. git guard hook missing (`.claude/settings.json` does not register the orchestrator hook) |

## Steps
✓ Preflight (clean tree, feature branch)
✓ Clarify: 2 questions answered (Q1=A, Q2=A) -> Confirmed Decisions
✓ SDD -> .forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md
✓ Gate 1: human (approved with extra security reviewer)
✓ ECP -> .forge/generated/ecp/2026-11-20-worker-dispatch-host-ecp.md
✓ Gate 2: auto
✓ Execute (9 files, 122 tests OK; diff risk check: no high-risk area)
✓ Test (scenarios: 17, full suite 138 OK; e2e blocked_by_environment: no host)
✓ Review round 1 (testing: accept; security: request_changes, 1 MAJOR)
✓ Fix round 1 (MAJOR 1 + MINOR 2)
✓ Test round 2 (18 scenarios, 139 OK; e2e blocked_by_environment)
✓ Review round 2 (testing: accept; security: accept)
✱ Publish (pushed; MR/PR not opened: gh missing)

## Artifacts
| Type | Path | Status |
|---|---|---|
| SDD | .forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md | approved (Gate 1 human) |
| ECP | .forge/generated/ecp/2026-11-20-worker-dispatch-host-ecp.md | ecp_ready |
| Execution report | .forge/generated/reports/2026-11-20-worker-dispatch-host-execution-report.md | success |
| Test report | .forge/generated/reports/2026-11-20-worker-dispatch-host-test-report.md | pass (round 2) |
| Review | .forge/generated/reviews/2026-11-20-worker-dispatch-host-review.md | accept |
| Orchestration report | .forge/generated/reports/2026-11-20-worker-dispatch-host-orchestration-report.md | this file |

## Gate trace
- Gate 1: human (2026-11-20, approved; extra `security` reviewer requested) - policy.high_risk_areas: none; require_human_confirmation_for: external_contract_change (`run.worker` config contract, specs/orchestrate.md §8), architecture_boundary_change (reverses specs/orchestrate.md:134; orchestrator ends turn per dispatch), security_boundary_change (worker git guard not Forge-registered under host). Extra `security` reviewer proposed.
- Gate 2: auto - ECP .forge/generated/ecp/2026-11-20-worker-dispatch-host-ecp.md: no blocking unknowns, 9 files match SDD surface inventory, no high-risk area beyond Gate 1 (external_contract_change, architecture_boundary_change, security_boundary_change all cleared)

## Validation
| Command | Result |
|---|---|
| `uv run python -m unittest tests.test_orchestrate -q` | pass (24) |
| `uv run python -m unittest discover -s tests -q` | pass (122 after execute; 138 after tester; 139 after round 2) |
| security scan | not configured in repo; not run (security MINOR 5) |
| redaction check (diff, tests, artifacts) | clean |
| `diff` mode + config template vs `runtime/` copies | identical |

## Test scenarios
| Entry point | Category | Scenario | Result |
|---|---|---|---|
| forge init (claude, codex) | integration | config has host comment above `worker: subagent` | pass |
| forge init | contract | exactly one `worker:` key, default subagent | pass |
| forge init --dry-run | regression | dry run writes no config | pass |
| config template / runtime copy / init builder | contract | byte-identical + same host comment | pass |
| mode inputs | happy path | `run.worker` lists host, default subagent | pass |
| mode worker dispatch | happy path | host tool, worker_command ignored, fresh tester/reviewer, end turn | pass |
| mode worker dispatch + footer | data state | same-session resume only; report not resumable state | pass |
| mode guard line | permission | guard advisory, note not a stop | pass |
| mode stop conditions | dependency failure | one host stop (no dispatch tool) | pass |
| mode | regression | subagent/cli/mixed lines unchanged | pass |
| mode status values | contract | no new status | pass |
| spec §6 / §8 / §12 | contract | host stop, enum, host bullet, "Forge stays unchanged" removed | pass |
| validation case | contract | scenario 18 + §5 list | pass |
| release notes | contract | lists host | pass |
| mode + spec resume boundary | permission (negative) | worker result never a human answer, Gate 1 approval, or other verdict; fresh session needs human (round 2) | pass |
| orchestrator with real host | e2e | dispatch, end turn, resume same session | blocked_by_environment |

## Review rounds
| Round | Tester | Reviewer | Open findings |
|---|---|---|---|
| 1 | pass (17 scenarios, 138 OK; e2e blocked_by_environment) | testing: accept (6 MINOR test-quality); security: request_changes | MAJOR 1: host resume could carry approvals/answers; MINOR 2: fresh-session wording. MINOR 3-5 (orchestrator guard for non-Claude hosts, unverifiable fresh context, no security scan configured) and testing MINOR 1-6 recorded, not in fix scope |
| 2 | pass (139 OK) | testing: accept; security: accept | MAJOR 1, MINOR 2 resolved. Open non-blocking: security MINOR 3-6 (6 recorded in execution report); testing MINOR (test brittleness, never-failing assertNotIn, lost host session not in next mode transitions) |

## MR/PR
not opened: `gh` CLI not installed in this environment. Branch `forge/2026-11-20-worker-dispatch-host` pushed to origin; open the PR from GitHub compare with the prepared body.

## Lessons (proposals only)
- Testing overlay: prefer key-phrase asserts over full-sentence asserts; repeated in both review rounds. Proposed `.forge/agents/testing.md` line: "Assert key tokens, not whole sentences or prose rows."
- Security MINOR 3: preflight confirms the orchestrator guard only for Claude Code; proposal: extend the `host` guard line to the orchestrator guard (follow-up issue).
- Planner file-name/status mismatch: forge-planner.md uses `-plan.md` and `ready_for_implementation`; orchestrator asked for `-sdd.md` and `draft`. Proposal: align orchestrate mode and forge-planner.md on one SDD path and status.
