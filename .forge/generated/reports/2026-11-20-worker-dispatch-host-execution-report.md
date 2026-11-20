# Execution Report: Orchestrate worker dispatch type `host`

| Field | Value |
|---|---|
| Artifact | execution-report |
| Date | 2026-11-20 |
| Slug | `worker-dispatch-host` |
| ECP | `.forge/generated/ecp/2026-11-20-worker-dispatch-host-ecp.md` (Gate 2 auto-accepted) |
| SDD | `.forge/generated/plans/2026-11-20-worker-dispatch-host-sdd.md` |
| Branch | `forge/2026-11-20-worker-dispatch-host` (base `928102d`) |
| Status | `success` |

## Evidence check
All ECP anchor lines and existing wording matched before editing (no drift). Edits applied with exact single-occurrence replacements.

## Changed files
1. `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`: `run.worker` input lists `host`; three `host` bullets in `worker dispatch` (dispatch, same-session resume, advisory worker git guard); `host` stop condition; report footer resume exception.
2. `runtime/.forge/runtime/modes/orchestrate.md`: `cp` of file 1 (byte-identical).
3. `src/forge_context_engine/runtime_templates/base/.forge/forge.config.yaml`: worker comment lists `host`.
4. `runtime/.forge/forge.config.yaml`: `cp` of file 3 (byte-identical; only the comment line differs from base).
5. `src/forge_context_engine/runtime_ops.py`: init config comment string literal only.
6. `specs/orchestrate.md`: §6 `host` stop; §8 YAML comment `subagent | cli | host`; §8 `host` bullet; §12 sentence replaced.
7. `validation-cases/orchestrate-gates.md`: scenario 18 row; §5 stop list `(2 to 8, 11, 12, 18)`.
8. `tests/test_orchestrate.py`: `host` comment asserts in `test_config_defaults_worker_to_subagent`; new `OrchestrateContractTests.test_mode_host_dispatch_resume_and_guard`.
9. `docs/release-notes.md`: `run.worker` line lists `host`.

## Validation
| Command | Result |
|---|---|
| `uv run python -m unittest tests.test_orchestrate -q` | pass, 24 tests OK (baseline 23 + 1 new) |
| `uv run python -m unittest discover -s tests -q` | pass, 122 tests OK (baseline 121 + 1 new) |
| `diff runtime/.forge/runtime/modes/orchestrate.md src/.../modes/orchestrate.md` | pass, no output |
| `diff runtime/.forge/forge.config.yaml src/.../forge.config.yaml` | pass, no output |
| `git status --porcelain` | pass, exactly the 9 ECP files (` M`) |
| AC6 failure path (in-memory: mode text with the `host` stop line removed) | stop phrase absent, so the new test's final assert would fail; no file modified |

No Makefile, CI config, or security-check command exists in the repo; none run.

## Decisions taken (non-blocking)
- Test name `test_mode_host_dispatch_resume_and_guard`, placed first in `OrchestrateContractTests`; `host` variable defined after existing template assert.

## Fixes during execute
None.

## Deviations
None.

## Blocked items
None.

## Risks
- Worker git guard under `host` is advisory only, as stated in mode and spec; Forge cannot enforce it.
- `runtime_ops.py` comment string is covered by the generated-config assert; `runtime/` config is covered only by the diff command, not a test (ECP risk note).

## Next mode
`review`

## Fix round 1

Scope: security review findings only.

| Finding | Status | Change |
|---|---|---|
| MAJOR 1: host resume could carry approvals/answers | resolved | Added "A resume only completes the pending dispatch: the worker result is data for that one role, never a human answer, Gate 1 approval, or verdict for another role. After any stop status, continue only through `next mode transitions`." to the mode `Resume under host` bullet (both copies) and spec §8 `host` bullet. |
| MINOR 2: fresh session wording implied auto-restart | resolved | Mode: "it needs a human re-invocation through `next mode transitions` from the named SDD or ECP." Spec: "a fresh session needs a human re-invocation from the named SDD or ECP". |

Files changed: src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md, runtime/.forge/runtime/modes/orchestrate.md (cp), specs/orchestrate.md, tests/test_orchestrate.py (new phrase in test_mode_host_dispatch_resume_and_guard), tests/test_orchestrate_host_dispatch.py (two MINOR 2 asserts updated).

Validation:
- `uv run python -m unittest discover -s tests -q`: Ran 138 tests, OK.
- `diff` of the two mode copies: identical.
- `git status --porcelain`: same file set as round 0; no new files.

Deviations: none.

### Fix round 1: deviation note (added by orchestrator)
- Review-driven deviation from ECP text: ECP wording "a fresh session ... restarts" was replaced by "needs a human re-invocation" (security MINOR 2), and the resume-boundary sentence (security MAJOR 1) was added. Both were orchestrator-accepted fix scope; not scope growth.
