# forge-autopilot

## Purpose
Drive one request or spec through the Forge lifecycle to a reviewable pull/merge request using the opt-in `forge run` control plane (`specs/autopilot.md` in forge-context-engine). You are the orchestrator; Forge owns state, gates, and the PR.

## Load
Read `.forge/forge.config.yaml` and `.forge/autopilot.json` first. Load `.forge/runtime/modes/<mode>.md` only for the stage you are working on.

## Invocation
Use when the user asks to run, implement, or ship a spec or a free-text request end to end, for example `/forge-autopilot <spec path or request>`.

## Loop
1. Free text: write the request as a spec file, then `forge run start text:<file>`. Existing spec: `forge run start md:<path>`.
2. Repeat until `forge run status --json` shows `done` or `blocked`:
   - Read the current `stage`.
   - Role `self` (default for `spec`, `plan`, `ecp`): do the stage yourself under its Forge mode, write the artifact, then `forge run submit <run> --stage <stage> --file <artifact>`.
   - Other roles: write a stage prompt with the context the agent needs, then `forge run dispatch <run> --stage <stage> --prompt-file <prompt>`.
   - Stages `validate` and `pr` are run by Forge: call the gate directly.
   - Call `forge run gate <run> --stage <stage> --json`. On fail, read the reasons and fix within limits.
3. Spec stage: check the spec against the repository. Resolve each ambiguity with a recommended option and list it under `## Decisions taken by autopilot`. Use `status: blocked` only when no reasonable recommendation exists.
4. ECP stage: include `## Allowed files` with each path or glob as a backticked bullet.
5. Report to the user only when a PR is open, the run is blocked, or they ask.

## Output
The PR link, the decisions taken, the risk level, and the validation table from `forge run report`.

## Do NOT
Do not edit code, commit, push, or open PRs yourself. Do not bypass or retry a gate by changing state files. Do not merge. Do not delete `.forge/runs/STOP`.
