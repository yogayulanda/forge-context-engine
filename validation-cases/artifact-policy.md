# Artifact Policy

| Field | Value |
|---|---|
| Pattern | `final-artifact-policy` |
| Lifecycle state | `benchmarked` |
| Coverage category | Artifact lifecycle, context boundary, local-only data |
| Scope | Repository-neutral artifact benchmark |

---

## Expected Behavior

Final artifact and context paths:

```text
.forge/context = committed curated source of truth
.forge/context-patches = reviewable context update proposals
.forge/generated = generated artifacts committed manually when relevant
.forge/temp = ignored/local-only
.forge/cache = ignored/local-only
```

Generated artifacts may include Quick Plans, ECPs, execution reports, review results, and context verification results when they help reviewers understand or validate the change.
Saved continuity artifacts for v0.10 focus on:
- plans under `.forge/generated/plans/`
- ECPs under `.forge/generated/ecp/`
- execution reports under `.forge/generated/reports/`
- review reports under `.forge/generated/reviews/`

Curated context expectations:
- `.forge/context` contains durable, repo-specific, evidence-backed, compact knowledge that remains useful beyond one task.
- Generated artifacts are working records, not automatically curated context.
- Context patches are proposals only until reviewed and promoted.
- Raw logs, one-off plans, temporary ECPs, long reports, and scratchpad notes stay out of `.forge/context`.
- Review-triggered durable context updates are proposed under `.forge/context-patches/...`, not written directly into `.forge/context`.

Default persistence behavior:
- Print the Plan, ECP, Execute Report, or Review Report in chat first.
- Save Markdown only when explicitly requested, approved for continuity, or needed for multi-session/multi-agent handoff.
- Persist generated artifacts under `.forge/generated/...`, not `.forge/context`.
- Use human-readable dated kebab-case filenames with an artifact-type suffix.
- Promote durable context only through reviewed `.forge/context-patches/...`.
- Do not force artifact-save status into every response; mention persistence status only when the user asks or when save behavior is part of the workflow.
- Keep universal artifacts tool-neutral unless tool-specific hints appear only under a clearly labeled `Target Tool Notes` section.

## Incorrect Behaviors Forge Must Reject

- Treating `.forge/generated` as always ignored or always committed.
- Auto-writing Markdown artifacts for every small answer.
- Treating `.forge/generated` as authoritative over source code, ADRs, or `.forge/context`.
- Treating a generated artifact as automatically accepted curated context.
- Continuing from a saved artifact without first reading it, checking type-to-mode fit, or checking for staleness or contradiction.
- Executing directly from a saved plan artifact without an approved ECP.
- Writing durable context updates directly into `.forge/context` instead of `.forge/context-patches`.
- Treating `.forge/context-patches` proposals as already accepted context.
- Treating a review `Context Impact` result as permission to auto-write curated context.
- Overwriting an existing generated artifact without explicit approval.
- Storing raw logs, one-off task artifacts, or scratchpad notes in `.forge/context`.
- Leaking tool-specific edit mechanics into universal artifacts without explicit target-tool labeling.
- Committing `.forge/temp` or `.forge/cache`.
- Storing raw secrets, hidden chain-of-thought, or broad conversation history in artifacts.

## Regression Signals

This case regresses if artifact paths drift back to `.forge/context/generated`, if save-by-default becomes normal behavior, if stale generated artifacts are treated as authoritative, or if temp/cache are not local-only.
