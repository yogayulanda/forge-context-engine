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
- Promote durable context only through reviewed `.forge/context-patches/...`.
- Do not force artifact-save status into every response; mention persistence status only when the user asks or when save behavior is part of the workflow.

## Incorrect Behaviors Forge Must Reject

- Treating `.forge/generated` as always ignored or always committed.
- Auto-writing Markdown artifacts for every small answer.
- Treating `.forge/generated` as authoritative over source code, ADRs, or `.forge/context`.
- Treating a generated artifact as automatically accepted curated context.
- Writing durable context updates directly into `.forge/context` instead of `.forge/context-patches`.
- Treating `.forge/context-patches` proposals as already accepted context.
- Treating a review `Context Impact` result as permission to auto-write curated context.
- Storing raw logs, one-off task artifacts, or scratchpad notes in `.forge/context`.
- Committing `.forge/temp` or `.forge/cache`.
- Storing raw secrets, hidden chain-of-thought, or broad conversation history in artifacts.

## Regression Signals

This case regresses if artifact paths drift back to `.forge/context/generated` as the current policy or if temp/cache are not local-only.
