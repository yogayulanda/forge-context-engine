# Test Report: Orchestrate worker dispatch type `host`

| Field | Value |
|---|---|
| Artifact | test-report |
| Date | 2026-11-20 |
| Slug | `worker-dispatch-host` |
| SDD | `.forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md` |
| ECP | `.forge/generated/ecp/2026-11-20-worker-dispatch-host-ecp.md` |
| Branch | `forge/2026-11-20-worker-dispatch-host` (base `928102d`) |
| Verdict | `pass` (e2e `blocked_by_environment`: no host) |

## Entry points changed (from diff)
1. `forge init` (CLI `run_init` -> `_render_forge_config` in `runtime_ops.py`): generated `.forge/forge.config.yaml` comment.
2. Packaged config template + `runtime/` engine copy.
3. Mode `orchestrate.md` (packaged + `runtime/` copies): `inputs`, `worker dispatch`, `stop conditions`, report footer.
4. Spec `specs/orchestrate.md`, validation case `validation-cases/orchestrate-gates.md`, `docs/release-notes.md`.

No HTTP/gRPC endpoint, consumer, job, or screen. `forge update` does not change behavior here (config rendering is shared with init); covered via the init path.

## Team settings (testing overlay placeholders resolved)
- No Makefile or CI config in repo. Commands from orchestrator convention: `uv run python -m unittest ...`; full suite `uv run python -m unittest discover -s tests -q`.
- Integration/e2e command: none separate; `no e2e harness`. Integration tests run in the standard unittest suite.

## Scenario matrix
New file: `tests/test_orchestrate_host_dispatch.py` (16 tests).

| # | Entry point | Category | Scenario | AC | Result |
|---|---|---|---|---|---|
| 1 | `forge init` (claude, codex) | Happy path / integration | Generated config has host comment directly above `worker: subagent` | AC4 | pass |
| 2 | `forge init` | Boundaries / contract | Exactly one `worker:` key (default stays `subagent`, A6) | AC4 | pass |
| 3 | `forge init --dry-run` | Regression | Dry run writes no config | - | pass |
| 4 | Config template / `runtime/` copy / init builder | Contract (sync) | `runtime/` config byte-equal to template; both carry the init builder's host comment (closes SDD risk: config had no sync test) | AC4 | pass |
| 5 | Mode inputs (both copies) | Happy path | `run.worker` lists `host`, `subagent` default | AC1 | pass |
| 6 | Mode worker dispatch | Happy path | Host tool defined by host, every role, `worker_command` ignored, tester/reviewer fresh, incomplete -> `blocked`, end the turn | AC1, R2, A1, A3, A5 | pass |
| 7 | Mode worker dispatch / footer | Data state (resume) | Same-session resume; snapshots/hash/fix count in-session; fresh session restarts via `next mode transitions`; footer keeps "not resumable workflow state"; no state file wording | AC1b, R7 | pass |
| 8 | Mode guard line | Auth and permission (negative) | Guard is advisory: `forge_git_guard.py worker` + `worker git guard not confirmed` in dispatch, absent from stop conditions | AC1b, R8 | pass |
| 9 | Mode stop conditions | Dependency failure (negative) | Exactly one host stop: host set, no dispatch tool | AC2, R4 | pass |
| 10 | Mode | Regression | subagent/cli dispatch lines, mixed-dispatch line, cli stop unchanged | AC3 | pass |
| 11 | Mode status values | Contract | No new status value | Non-goal | pass |
| 12 | Spec §6 | Contract | Host stop bullet present | AC2 | pass |
| 13 | Spec §8 | Contract | `subagent \| cli \| host`; host bullet: no host code, same session, fresh restart, guard note, `blocked_by_environment` | R1, A2 | pass |
| 14 | Spec §12 | Contract | "Forge stays unchanged" removed; hosts set `run.worker: host` | R1 | pass |
| 15 | Validation case | Contract | Scenario 18 -> `blocked_by_environment`, listed in §5 regression stops | AC5, R5 | pass |
| 16 | Release notes | Contract | Lists `host` | - | pass |
| 17 | Orchestrator with real host | E2E | Dispatch via host tool, end turn, resume same session | AC1, R7 | `blocked_by_environment` (no host in repo or environment; Forge ships no host code) |

n/a categories:
- Input validation: Forge does not parse or validate `run.worker` in code; the value is read by the orchestrating agent from mode text. Unknown values have no code path to test.
- Idempotency/duplicates, Concurrency: no stateful code path; host resume is mode text only.
- Auth tokens/roles: no auth surface; guard covered as a negative scenario in row 8.

Existing executor coverage (not used as the definition of correct, rerun as regression): `tests/test_orchestrate.py` host asserts and `OrchestrateSourceSyncTests` (AC6 mode-copy drift).

AC3 (byte-unchanged elsewhere): reviewed `git diff` of the mode; only inputs line, three dispatch bullets, one stop line, and footer line changed (+6/-2). AC7: `git status --porcelain` shows the 9 ECP files plus this tester's new test file only.

## Commands
| Command | Result |
|---|---|
| `uv run python -m unittest tests.test_orchestrate_host_dispatch -v` | OK, 16 tests |
| `uv run python -m unittest tests.test_orchestrate -q` | OK, 24 tests |
| `uv run python -m unittest discover -s tests -q` | OK, 138 tests (122 before + 16 new) |
| `diff` mode copies; `diff` config copies | identical |

## Failures
None.

## Files added
- `tests/test_orchestrate_host_dispatch.py`

## Round 2 (re-test after fix round 1)

Fix round 1 added a resume boundary to the mode `Resume under host` bullet (both copies) and to the spec §8 `host` bullet. Round 2 adds one negative/permission scenario for it.

| # | Entry point | Category | Scenario | AC / risk | Result |
|---|---|---|---|---|---|
| 18 | Mode worker dispatch (template + runtime) and spec §8 `host` bullet | Auth and permission (negative) | `test_HostResume_WorkerResultNeverGrantsHumanAnswerApprovalOrOtherVerdict`: all three sources state that a resume only completes the pending dispatch, the worker result is never a human answer, Gate 1 approval, or verdict for another role, and after any stop status the run continues only through `next mode transitions`; each says a fresh session needs a human re-invocation; the boundary adds no new stop condition | AC1b, R7, fix round 1 | pass |

Rows 1 to 16 re-run: pass. Row 17 (real host E2E) stays `blocked_by_environment`.

### Commands
| Command | Result |
|---|---|
| `uv run python -m unittest tests.test_orchestrate_host_dispatch -v` | OK, 17 tests |
| `uv run python -m unittest tests.test_orchestrate -q` | OK, 24 tests |
| `uv run python -m unittest discover -s tests -q` | OK, 139 tests |
| `diff` mode copies | identical |

### Failures
None.

### Files changed
- `tests/test_orchestrate_host_dispatch.py` (one new test)
