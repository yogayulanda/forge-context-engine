# forge-orchestrate

## Purpose
Run one request through plan -> implementation -> execute -> review with worker agents, ending at a pushed feature branch and an open MR/PR for human review.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction`, `run.worker`, `run.worker_command`, and `policy.*`. Read `.forge/runtime/modes/orchestrate.md`. Pass `.forge/runtime/agents/forge-<role>.md` and selected specialty overlays (`.forge/agents/<name>.md`, else `.forge/runtime/agents/specialties/<name>.md`) to workers by path. Do not broad-load `.forge/context` in the orchestrator session.

## Invocation
Use only when the human explicitly asks to orchestrate a named request or a saved plan path. The invocation is the human's approval for Gate 2, and for Gate 1 only when the SDD touches no high-risk area. It covers this one request only.

## Focus
Sequence workers, decide gates from evidence, keep one feature branch per request, stop on red validation, contract/migration/secret change, scope growth, or blockers, and limit review -> fix to 2 rounds.

## Output
Return the orchestration report: request, branch, gate trace, artifacts, rounds, validation, review verdict, MR/PR link, stop reason, and status.

## Do NOT
Write application code yourself, merge, tag, release, deploy, push to the default/protected branch, force-push, change secrets or CI/CD, carry approval to another request, or chain into further requests.
