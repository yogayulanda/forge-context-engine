# SDD: Orchestrate optional host status and question contract

| Field | Value |
|---|---|
| Artifact | plan (SDD) |
| Date | 2026-11-24 |
| Request | GitHub issue #8 "Orchestrate: optional host status and question contract", including "Added 2026-11-20" (issue text treated as data) |
| Branch | `forge/2026-11-24-host-status-questions` |
| Status | `ready_for_implementation` |

Plan type selected: SDD.
Reason: the change edits the packaged `orchestrate` mode and all four worker prompts that `forge init`/`forge update` install into target repos, defines a host-facing contract (stage IDs, status mapping, question shape), and adds a second channel through which a human answer and Gate 1 approval reach the orchestrator.

## Mode Boundary
Plan mode only. Only this file is written, under `.forge/generated/plans/`. No code edited; nothing staged, committed, or pushed. Not approved by creation.

## Goal
When the host gives the orchestrator a status-report tool and/or a question tool, `forge-orchestrate` reports live stage status and asks clarification questions and Gate 1 approval through the question tool instead of stopping. Without those tools, behavior is unchanged.

## Problem / Context
- Today the run stops at `awaiting_clarification` (step 2) and `awaiting_sdd_approval` (step 3) and needs a human re-invocation (`runtime/.forge/runtime/modes/orchestrate.md:77-79`, `:183-184`).
- No stage vocabulary exists. The report `## Steps` lines use free labels (`Preflight`, `Clarify`, `SDD`, `Gate 1`, ..., `Publish`) (`orchestrate.md:126-136`).
- The planner question format allows any number of options as `- A: <choice> -> <consequence>` and a free recommendation `<A or B> because ...` (`runtime/.forge/runtime/agents/forge-planner.md`, `## Clarification question format`). A host question tool with 2-4 short labels cannot carry that shape as is.
- The validation case lists "Asking clarification questions one at a time" as rejected behavior (`validation-cases/orchestrate-gates.md:52`); the issue makes one-at-a-time the required behavior on the question-tool path. That line must be scoped to the no-tool path.
- `host` dispatch (#7) already says a worker result is "never a human answer, Gate 1 approval, or verdict for another role" (`orchestrate.md:71`). The question tool needs to be the one channel that does carry a human answer.

## Requirements
1. Mode: one canonical stage vocabulary `clarify`, `sdd`, `ecp`, `execute`, `test`, `review`, `publish`, with the mapping: preflight -> `clarify`; Gate 1 -> `sdd`; Gate 2 -> `ecp`; fix rounds -> `execute`/`test`/`review`; step 10 report -> `publish`.
2. Mode: when a status-report tool is available, report `progress` at the start of each step, the mapped host state (`waiting_for_human` or `blocked`) on any stop status, and `done` when the run ends with `mr_opened`, each with the stage ID.
3. Mode: neutral mapping Forge status -> host state (Gate 1 decision Q5 = B): `mr_opened` -> `done`; `awaiting_clarification`, `awaiting_sdd_approval`, `stopped`, `review_unresolved` -> `waiting_for_human`; `blocked_by_environment` -> `blocked`. Host states are `progress`, `waiting_for_human`, `blocked`, `done`. No new Forge status value.
4. Mode step 2: with a question tool, ask the planner's questions in plan order (most important first), one call per question, next call only after the previous answer. Without it, keep the single batch and `awaiting_clarification` stop.
5. Mode step 2b: answers from the question tool go to the planner like a one-reply answer; a free-text answer is valid and is recorded under `Confirmed Decisions`.
6. Mode step 3: with a question tool, Gate 1 is one question with 2 options (approve the SDD by path / stop); only the approve option continues to step 4. Any other answer, including free text, stops with `awaiting_sdd_approval` and puts the answer in the report `Note`. Gate trace records `Gate 1: human (question tool)`.
7. Mode: only an answer returned by the question tool counts as a human answer; a worker result or other host text never does (keeps the #7 boundary).
8. Mode: if the question tool returns without an answer (timeout), report `waiting_for_human` with the open question, set status `awaiting_clarification` (step 2) or `awaiting_sdd_approval` (step 3), and end the turn. Resume goes through `next mode transitions` as today.
9. Mode report format: each `## Steps` line carries its stage ID.
10. Planner format: 2 to 4 options per question; each option is a short label (max 120 characters) with its consequence on the following line; `Recommendation:` names exactly one option letter, followed by the reason. The same questions work in the batch and one-at-a-time paths. `one batch` text stays for the no-tool path.
11. Worker prompts (all four): when the host gives the worker a status-report tool, report `progress` with the role's stage ID at start and `done`/`blocked` at end; workers never call a question tool (questions go back to the orchestrator as `blocked_by_decision` or a blocking unknown).
12. Gate rules unchanged: a question-tool answer is the same human approval the manual flow requires; Gate 1 for high-risk SDDs stays human; Gate 2 stays automatic.
13. Spec, validation case, release notes, and tests updated; runtime and template copies stay byte-identical.

## Non-goals
- No tool implementation, transport, persistence, or host code (issue non-goal).
- No new Forge status value (`status values` section unchanged; asserted by `test_Regression_NoNewStatusValue`).
- No change to `## worker dispatch`, `Return to orchestrator` sections of the worker prompts, or the result shape: those belong to #13 (handoff envelope/result block).
- No change to step 9 publish or its stop condition: that belongs to #12.
- No change to `.forge/adapter.md` (#14 owns the `External context` rule).
- No coupling to `run.interaction` (see A2).
- No question tool use by workers, and no status reports of sub-steps inside a worker.
- No change to `run.worker` values or `forge.config.yaml` keys; tool availability is detected from the host, not configured.

## Current Evidence
| Claim | Evidence |
|---|---|
| Step 2 stops with `awaiting_clarification` and shows all questions at once | `runtime/.forge/runtime/modes/orchestrate.md:77` |
| Step 2b resume: one reply, planner records `Confirmed Decisions` | `orchestrate.md:78`; `forge-planner.md` Steps 2 ("On resume with answers") |
| Step 3 Gate 1 stops with `awaiting_sdd_approval` | `orchestrate.md:79` |
| Worker result is never a human answer or Gate 1 approval | `orchestrate.md:71`; asserted in `tests/test_orchestrate_host_dispatch.py:106-122` (also: `Gate 1 approval` must not appear in `## stop conditions`) |
| Report steps use free labels, no stage IDs | `orchestrate.md:126-136` |
| Status values (no `host`-word allowed in that section) | `orchestrate.md:166-172`; `tests/test_orchestrate_host_dispatch.py:150-152` |
| Next transitions require re-invocation | `orchestrate.md:183-184` |
| Planner question format: open option count, recommendation `<A or B>` | `runtime/.forge/runtime/agents/forge-planner.md`, `## Clarification question format` |
| Planner test asserts `one batch`, `Recommendation:`, `Do not ask what the repo already answers`, `contradicts the code`, `` `ui.language` ``, `Never "the system"` | `tests/test_orchestrate.py:121-132` |
| Worker prompts have no status reporting and no question rule | `runtime/.forge/runtime/agents/forge-executor.md`, `forge-tester.md`, `forge-reviewer.md`, `forge-planner.md` (grep: no "status-report", "question tool") |
| Runtime and template copies of the mode and the four role prompts must be byte-identical | `tests/test_orchestrate.py:257-277` (`OrchestrateSourceSyncTests.PAIRS`); `diff` of the planner copies: identical today |
| Spec says all questions go in one batch | `specs/orchestrate.md:63` (section 4b) |
| Validation case rejects one-at-a-time questions | `validation-cases/orchestrate-gates.md:52` |
| Validation regression list asserted verbatim | `tests/test_orchestrate_host_dispatch.py:184` (`any stop scenario (2 to 8, 11, 12, 18)`) |
| #12 plan adds validation scenario 19 | `.forge/generated/plans/2026-11-24-publish-force-add-artifacts-plan.md` (Proposed Approach) |
| `run.interaction: auto` forbids conversational questions; orchestrate mode does not read `run.interaction` | `runtime/.forge/runtime/meta/conventions.md:224-227`; grep of `orchestrate.md`: no `interaction`; `runtime/skills/forge-orchestrate/SKILL.md:7` applies it generally |
| Mode files must keep the schema heading prefix | `tests/test_orchestrate.py:79-83` |
| `.forge/context` has no facts on orchestrate host contracts | `.forge/context/04-interfaces-and-contracts.md`, `99-open-questions.md` (bounded-init placeholders); no ADR beyond `ADR-0000-template.md` |

## Affected Surface Inventory
- `runtime/.forge/runtime/modes/orchestrate.md` and `src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md` (identical): new `## host status and questions` section placed after `## worker dispatch`; steps 2, 2b, 3; report `## Steps` lines; `## next mode transitions` lines for `awaiting_clarification` / `awaiting_sdd_approval` (one clause each: also reached on a question-tool timeout).
- `runtime/.forge/runtime/agents/forge-planner.md` + template copy: `## Clarification question format` (bounded options, recommendation, free-text rule); one line in Steps 2 that answers may arrive one at a time and free text is valid; one host-status line.
- `runtime/.forge/runtime/agents/forge-executor.md`, `forge-tester.md`, `forge-reviewer.md` + template copies: one short `## Host status` section each (stage ID, no question tool). Placed after `## Specialty overlays`, away from `## Return to orchestrator` (#13).
- `specs/orchestrate.md`: section 4b (batch vs one-at-a-time), new section 8a "Host status and questions" (stage IDs, mapping, question shape, timeout, gate rule unchanged).
- `validation-cases/orchestrate-gates.md`: new scenarios 20-22; scope the line-52 rejected behavior to the no-tool path; add rejected behaviors for the question-tool path.
- `tests/test_orchestrate.py`: new `OrchestrateHostInteractionTests` phrase class over both mode copies and the planner/worker templates.
- `docs/release-notes.md`: one `Added` line under `Unreleased`.
- Checked, no change needed: `runtime/skills/forge-orchestrate/SKILL.md` and `runtime/adapters/claude/commands/forge-orchestrate.md` (no clarification or stage text); `runtime/adapters/claude/agents/forge-*.md` wrappers (point to role prompts only); `.forge/forge.config.yaml` templates (no new key); `docs/workflow.md:138-142` (describes the manual approval path, still valid); `runtime/.forge/runtime/meta/conventions.md` (see A2).

## Assumptions
- A1. Each tool is optional on its own: a status-report tool alone enables status reports; a question tool alone enables in-run questions. The issue's "and" describes the full case, and each behavior needs only its own tool.
- A2. The question-tool path does not depend on `run.interaction`. Reason: `orchestrate.md` does not read `run.interaction` today, and a question tool returns a structured decision with options, which `conventions.md:227` allows under `auto` ("emit structured required decisions"). Correct me at Gate 1 if `auto` should keep the stop.
- A3. Option labels in the planner format are the text after `A:`/`B:`/...; `Recommendation:` names one letter, and the orchestrator sends that option's label as the recommended choice. This satisfies "exactly one of the option labels" without repeating the label text.
- A4. Timeout in the middle of a batch: answers already received are listed in the report `Note`; the human's re-invocation reply must still answer every question (it may restate them). The report stays a trace, not resumable state (`orchestrate.md:164`, asserted by `test_HostResume_IsSameSessionOnly_FreshSessionRestartsFromArtifact`).
- A5. Superseded by Confirmed Decision Q5 = B: `stopped` and `review_unresolved` map to host `waiting_for_human` (a human decides the next action); only `blocked_by_environment` maps to `blocked`; only `mr_opened` maps to `done`.
- A6. The 120-character label limit is written as "max 120 characters" (the issue says "max ~120"); the consequence moves to the line under the option.
- A7. Validation scenarios are numbered 20-22, after #12's scenario 19. If #12 merges later or not at all, the executor renumbers to the next free numbers; the regression sentence `any stop scenario (2 to 8, 11, 12, 18)` stays verbatim because none of the new scenarios ends with a commit.

## Unknowns / Decisions Needed
- None blocking. A2 and A4 have a code consequence; their defaults stand (Gate 1 approved the SDD without correcting them).

## Confirmed Decisions
Human Gate 1, 2026-11-25 (batch approval of 7 SDDs; entries that concern this SDD):
- SDD approved for implementation.
- An extra `security` reviewer runs for this SDD, in addition to the normal reviewer; both must return `accept`.
- Q5 = B: add host state `waiting_for_human`. Mapping: `mr_opened` -> `done`; `awaiting_clarification`, `awaiting_sdd_approval`, `stopped`, `review_unresolved` -> `waiting_for_human`; `blocked_by_environment` -> `blocked`. Host states are `progress`, `waiting_for_human`, `blocked`, `done`. Forge status values do not change. Applied to Requirements 2, 3, 8, A5, Proposed Approach, and Acceptance Criteria below.
- Q3, Q4, Q6 of the batch concern other SDDs; no effect here.

## Architecture / System Impact
- Text-level contract change in the shipped `orchestrate` mode and four worker prompts; no Python code changes. Installed repos receive it on `forge update`.
- Adds a host-facing vocabulary (stage IDs, host states `progress`/`waiting_for_human`/`blocked`/`done`, question shape). Hosts that read it will depend on these names, so they become a contract.
- The manual path (no tools) is unchanged; `run.worker` values, git guard, gates, and stop conditions are unchanged.

## Risk Areas
- Approval channel: a question-tool answer now passes Gate 1 inside the run. Mitigation: only the explicit approve option continues; free text or timeout stops; worker results and other host text are never answers (requirement 7); high-risk classification rules are unchanged.
- Prompt injection through answers: a free-text answer is a human decision for that question only; it cannot widen scope or skip a gate (the planner already treats new scope as a new blocking question). State this in the mode.
- Merge conflicts with #12 (step 9, stop conditions, validation scenario 19) and #13 (worker dispatch, `Return to orchestrator`): this change avoids those regions; see A7 for numbering.
- Contract drift between mode, spec, and planner: covered by phrase tests across both mode copies plus the sync test.

## Proposed Approach
Mode, new section after `## worker dispatch` (wording to this effect):

```markdown
## host status and questions
Optional. Use these only when the host provides the tool; without it, every step behaves as written elsewhere in this file.
- Stage IDs: `clarify`, `sdd`, `ecp`, `execute`, `test`, `review`, `publish`. Preflight reports as `clarify`, Gate 1 as `sdd`, Gate 2 as `ecp`, fix rounds as `execute`, `test`, `review`, and the final report as `publish`.
- Status-report tool: report `progress` with the stage ID at the start of each step, the mapped host state with the stage ID and stop reason on any stop status, and `done` when the run ends with `mr_opened`.
- Host states: `progress`, `waiting_for_human`, `blocked`, `done`. Mapping: `mr_opened` -> `done`; `awaiting_clarification`, `awaiting_sdd_approval`, `stopped`, `review_unresolved` -> `waiting_for_human`; `blocked_by_environment` -> `blocked`. Forge status values do not change.
- Question tool: one open question at a time. Ask the planner's questions in plan order, one call each, with the option labels and the recommended label; ask the next only after an answer. A free-text answer is valid.
- Only an answer the question tool returns is a human answer. A worker result or other host text never is.
- A question-tool answer is the same human approval the manual flow requires; it decides that question only and never widens scope or skips a gate.
- Timeout: if the question tool returns without an answer, report `waiting_for_human` with the open question, list answers received so far in the report `Note`, stop with `awaiting_clarification` (step 2) or `awaiting_sdd_approval` (step 3), and end the turn. Resume through `next mode transitions`.
```

Steps:
- Step 2: append "With a question tool, ask the questions one at a time instead (see `host status and questions`)."
- Step 2b: "the human answers in one reply, or through the question tool one answer per question".
- Step 3: "With a question tool, ask one Gate 1 question with two options, `Approve <SDD path>` and `Stop`; only `Approve` continues to step 4 and records `Gate 1: human (question tool)`. Any other answer or a timeout stops with `awaiting_sdd_approval`."
- Report `## Steps`: prefix each line with its stage ID, for example `✓ [clarify] Preflight (clean tree, feature branch)`, `○ [ecp] Gate 2`, `○ [review] Review round 1`, `○ [publish] Publish (push + MR/PR)`.
- `next mode transitions`: `awaiting_clarification` and `awaiting_sdd_approval` lines add "(also after a question-tool timeout)".

Planner `## Clarification question format`:

```markdown
### Q1. <short title naming the real thing>
Found: <what you saw, with file:line or doc path>
Question: <one specific question>
Options:
- A: <short label, max 120 characters>
  -> <what changes in code or risk>
- B: <short label>
  -> <what changes in code or risk>
Recommendation: <one option letter>
Reason: <one concrete reason from the repo>
```
Style rules add: "2 to 4 options per question." "The recommendation names exactly one option." "The orchestrator may ask these one at a time; write each question so it stands alone." "A free-text answer is valid; record it under `Confirmed Decisions` like any other answer." Keep `one batch`, `Recommendation:`, and `Maximum 7 questions`.

Worker prompts, new section after `## Specialty overlays`:

```markdown
## Host status
When the host gives you a status-report tool, report `progress` with stage `<id>` when you start and `done` or `blocked` when you end. Never use a question tool; return questions to the orchestrator as <planner: `blocked_by_decision` / others: a blocking unknown>.
```
Stage per role: planner `clarify`, `sdd`, or `ecp` by its current step; executor `execute`; tester `test`; reviewer `review`.

Spec:
- 4b: "All questions go to the human in one batch, or one at a time when the host provides a question tool (section 8a)".
- New 8a "Host status and questions": stage IDs, host states and mapping, question shape (2-4 labels, one recommended), timeout -> `waiting_for_human`, gate rules unchanged, Forge ships no tool code.

Validation case:
- `| 20 | Host provides a question tool; planner returns 3 clarification questions | 3 sequential question calls in plan order, each with 2 to 4 option labels and exactly one recommended label; the SDD is written after the third answer; status never shows \`awaiting_clarification\` |`
- `| 21 | Host question tool times out on the second of 3 questions | Status report \`waiting_for_human\` with stage \`clarify\` and the open question; status \`awaiting_clarification\`; answer 1 listed in the report \`Note\`; turn ends; nothing committed |`
- `| 22 | High-risk SDD, host question tool; human answers with free text instead of \`Approve\` | \`awaiting_sdd_approval\`; no ECP; answer in report \`Note\`; status report \`waiting_for_human\` with stage \`sdd\` |`
- Line 52 becomes: "Asking clarification questions one at a time without a host question tool, or more than one at a time with it; asking what the repo already answers; or asking without options and a recommendation."
- Add rejected behavior: "Treating a worker result, free text at Gate 1, or a question-tool timeout as Gate 1 approval."

Release notes `Unreleased` / `Added`: "Optional host status and question tools for `forge-orchestrate`: stage IDs, status mapping, one question at a time with 2 to 4 options; without them the run stops and waits as before."

## MVP Path
Same as the full path; the change is text plus phrase tests.

## Full-Version Path
Later, out of scope: a machine-readable stage/status schema file (like `git-guard-rules.json`) that hosts can read; the #13 result block may carry the stage ID.

## Acceptance Criteria
1. Both mode copies contain the `## host status and questions` section with the seven stage IDs, the four host states (`progress`, `waiting_for_human`, `blocked`, `done`), the Q5 = B mapping of all six Forge status values, "one open question at a time", "Only an answer the question tool returns is a human answer", and the timeout rule; the copies are byte-identical.
2. `## status values` is unchanged (no `host`, `progress`, `waiting_for_human`, `done` there); `## stop conditions` gains no line and still has no `Gate 1 approval`.
3. Step 3 says only the approve option continues and free text or timeout stops with `awaiting_sdd_approval`.
4. Every `## Steps` line in the report format starts with a stage ID from the vocabulary.
5. Planner format states 2 to 4 options, label max 120 characters, exactly one recommended option, and free-text answers under `Confirmed Decisions`; the existing planner phrases in `test_planner_clarifies_before_sdd_in_one_batch` still pass.
6. Each of the four worker prompts has `## Host status` with its stage ID and "Never use a question tool"; `## Return to orchestrator` sections are unchanged (diff check).
7. Failure paths: validation scenarios 21 and 22 exist (timeout -> host `waiting_for_human` and `awaiting_clarification`; free text at Gate 1 -> `awaiting_sdd_approval` and host `waiting_for_human`); the rejected-behavior list covers one-at-a-time without a tool and batch with a tool.
8. `specs/orchestrate.md` 4b and 8a match the mode; `any stop scenario (2 to 8, 11, 12, 18)` and scenario 18 row still verbatim.
9. Full suite green, including `OrchestrateSourceSyncTests` and `tests/test_orchestrate_host_dispatch.py`.

## Validation Commands
- `uv run python -m unittest discover -s tests -q`
- `diff runtime/.forge/runtime/modes/orchestrate.md src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`
- `for r in planner executor tester reviewer; do diff runtime/.forge/runtime/agents/forge-$r.md src/forge_context_engine/runtime_templates/base/.forge/runtime/agents/forge-$r.md; done`
- `git diff --name-only` (only files in the Affected Surface Inventory)

## Implementation Split
One batch: all files share one outcome, one test run, and the sync test ties the copies together.

## High-risk areas touched
`policy.high_risk_areas`: none.
- `payments`, `authentication`, `database_migrations`, `external_provider_integration`, `file_upload`: no code in these areas exists in the touched files (Markdown mode/agent/spec/validation text, one test file, release notes).
- `authorization`: no code-level access control changes. The Gate 1 approval channel is a process rule, classified under `security_boundary_change` below.
- `public_api`: `forge` CLI code (`src/forge_context_engine/*.py`) and config keys untouched.
- `secrets`: no secret handling changes.

`policy.require_human_confirmation_for`:
- `external_contract_change`: **match**. `orchestrate.md` and the four role prompts are packaged templates (`src/forge_context_engine/runtime_templates/base/.forge/runtime/modes/orchestrate.md`, `.../agents/forge-*.md`) installed into target repos. The change defines a new host-facing contract: stage IDs, host state mapping, question shape (2-4 labels, one recommended), and timeout behavior. Hosts will build against these names. The planner question format also changes shape.
- `security_boundary_change`: **match (uncertain, treated as match)**. Gate 1 approval for high-risk SDDs can now arrive through a host question tool inside the same run (`orchestrate.md:79` today requires re-invocation). The SDD keeps the boundary tight (only the explicit approve option counts; worker results, free text, and timeouts never do), but who can approve and through which channel is a boundary a human should confirm.
- `architecture_boundary_change`: no. Roles, worker dispatch, git guard rules, and ownership are unchanged; no new component. The orchestrator already owns gates (`orchestrate.md:46`).
- `domain_rule_change`: no product domain logic.
- `data_mutation_change`: no data store; no new persisted state (report stays a trace, A4).
- `migration_change`: no migrations.

Gate 1 consequence: two matches, so per mode step 3 this SDD stops with `awaiting_sdd_approval`.

## Specialties
- Orchestrator: `tech-lead` (always).
- Tester: `testing` (always).
- Executor / reviewer: none by `applies_when`. The change is Markdown contract text and Python unittest phrase tests; no backend service, frontend, mobile, or infrastructure layer is touched.
- Security reviewer: the mode rule keys on "the SDD lists any high-risk area"; `policy.high_risk_areas` is `none`. Confirmed at Gate 1 (2026-11-25): run the extra `security` reviewer, because the change adds a Gate 1 approval channel (`security_boundary_change` above).

## Next Step
Gate 1 approved by human (2026-11-25). Next: `implementation` (ECP at `.forge/generated/ecp/2026-11-24-host-status-questions-ecp.md`).

## Status
`ready_for_implementation`
