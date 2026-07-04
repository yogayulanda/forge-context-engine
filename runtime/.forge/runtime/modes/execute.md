---
id: mode.execute
title: "Mode: Execute"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-04
---

# Mode: Execute

## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`

## on_demand
- Approved ECP
- `knowledge/assumptions.md`
- `.forge/generated/<relevant>`

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
8000

## purpose
Apply an approved ECP into code within explicit boundaries.

## inputs
- Approved ECP.
- Allowed files and scope.
- Task sequence.
- Coding rules.
- Validation commands.
- Stop conditions.
- `run.write_behavior`.

## behavior
- If the user references a saved ECP artifact, read it first and verify it is an ECP artifact before continuing.
- Check whether the saved ECP still has enough evidence and whether current repository/context evidence materially contradicts it; if so, stop with `blocked`, `blocked_by_environment`, or `not_validated` instead of guessing.
- Execute task by task with minimal diffs and repository-native style.
- Run scoped validation after each task for the changed area.
- Fix ordinary in-scope failures such as typos, formatting issues, missing imports, small logic bugs, or assertion mismatches.
- Stop on scope, domain, security, contract, migration, infra, evidence, or environment blockers.
- Run final validation after all approved tasks complete.
- Preserve validation honesty: changed code without reliable validation is `not_validated`.
- Default to chat output; save an execution report only when the user explicitly asks or approves persistence.
- When saving, use `.forge/generated/reports/YYYY-MM-DD-<slug>-execution-report.md` and avoid overwriting an existing artifact without explicit approval.

## outputs
- Execution Report.
- Status.
- Changed files.
- Commands run.
- Validation results.
- Fixes made during execute.
- Deviations from ECP.
- Blocked items.
- Risks.
- Next mode: `review`.

## status values
- `success`
- `partial_success`
- `blocked`
- `blocked_by_environment`
- `not_validated`

## boundaries
- Execute is the only core mode that may edit files, and only within the approved ECP/scope boundary.
- Do not execute from a saved plan artifact directly; execution still requires an approved ECP.
- Do not expand scope silently.
- Do not commit, push, merge, deploy, change secrets, or change CI/CD/infra unless explicitly approved in the ECP.
- Do not ignore failed validation.
- Do not continue when code evidence contradicts the approved ECP.

## next mode transitions
- Use `review` after execution.
- Return to `implementation` when the ECP needs correction.
- Return to `plan` when a new decision or scope change is required.
