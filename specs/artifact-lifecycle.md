# Artifact Lifecycle Specification

| Field | Value |
|---|---|
| Document | Forge Artifact Lifecycle Specification |
| Version | 1.5 |
| Date | 2026-06-05 |
| Status | `decision` |
| Scope | Minimal generated artifact continuity for lifecycle handoff |
| Dependency | `specs/mode-invocation.md`, `specs/context-validation.md`, `runtime/.forge/context/00-meta/conventions.md` |

---

## 0. Purpose

This document defines small, human-readable generated artifacts that preserve engineering continuity across Forge modes, sessions, and tools.

Artifacts are supporting engineering records. They help engineers and assistants connect plan, implementation, execution, and review work without reconstructing the same context repeatedly.

Artifacts are NOT:
- Source of truth over code, repository docs, ADRs, or human confirmations.
- Persistent AI memory.
- Conversational history.
- Chain-of-thought storage.
- Workflow, DAG, agent, scheduler, CI/CD, deploy, or runtime execution state.

---

## 1. Repository-First Rule

Repository evidence remains authoritative.

When an artifact conflicts with code, repository docs, ADRs, or explicit human confirmation:
- Code wins for implementation facts.
- ADRs or human confirmations win for approved intent.
- The artifact is stale, partial, ambiguous, or superseded.
- The conflict must be surfaced as a validation or review concern when it affects execution safety.

Artifacts may summarize approved intent and results, but they never override repository truth.

---

## 2. Persistence Boundary

Artifacts are persisted only when useful for lifecycle continuity.

Default behavior is chat output first. Forge should not auto-write a Markdown artifact for every small answer.

Default persisted location:

```text
.forge/generated/
```

The folder is created on demand. Artifact files use Markdown with a small metadata header and concise sections. They are human-readable, append-friendly, reviewable in diffs, and replaceable or discardable.

Artifact storage policy:

| Path | Policy |
|---|---|
| `.forge/context` | Committed curated context source of truth |
| `.forge/context-patches` | Reviewable context update proposals |
| `.forge/generated` | Generated working artifacts committed manually when relevant |
| `.forge/temp` | Ignored local-only scratch |
| `.forge/cache` | Ignored local-only cache |

Generated artifacts must never be confused with curated context. Context changes that should become durable source of truth go through `.forge/context-patches` review before promotion to `.forge/context`.

Context quality boundary:
- `.forge/context` is for durable, repo-specific, evidence-backed, compact knowledge that remains useful beyond one task.
- `.forge/generated/...` is for working artifacts such as plans, ECPs, execution reports, and review reports.
- `.forge/context-patches/...` is for proposed durable context updates that still require review.
- A generated artifact is not automatically promoted into `.forge/context`.
- A context patch is not accepted context until it is reviewed and promoted.
- Raw logs, scratchpads, one-off plans, temporary ECPs, and long reports stay out of curated context unless reduced into durable evidence-backed context.

Persist only when one of these is true:
- The user explicitly asks to save or create the artifact.
- The work is medium or large and the user approves saving for continuity.
- The artifact is needed for multi-session or multi-tool continuation.

Do not persist artifacts during read-only modes by default. If a read-only mode is explicitly asked to save its output, save only to `.forge/generated/...` and keep the mode's no-code-change boundary intact.

Saved artifact directories:

```text
.forge/generated/plans/
.forge/generated/ecp/
.forge/generated/reports/
.forge/generated/reviews/
```

Generated artifact types:
- `plan`
- `ecp`
- `execution_report`
- `review_report`

Recommended naming pattern:

```text
.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md
.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md
.forge/generated/reports/YYYY-MM-DD-<slug>-execution-report.md
.forge/generated/reviews/YYYY-MM-DD-<slug>-review.md
```

Naming rules:
- Use lowercase kebab-case for `<slug>`.
- Include the creation date in `YYYY-MM-DD` format.
- Include the artifact type suffix in the filename.
- Avoid ambiguous names such as `latest.md`, `current.md`, or `final.md`.
- Do not overwrite an existing generated artifact without explicit human approval.

`.forge/generated/*` remains generated artifact output. It is loaded only by explicit reference, mode handoff, or task relevance.

Context patch proposals live under `.forge/context-patches/...`, not `.forge/generated/...`, when the workflow needs a reviewable durable-context update proposal.

Recommended context patch path:

```text
.forge/context-patches/<date>-<slug>.md
```

---

## 3. Metadata Header Contract

Persisted artifacts should include a small metadata header. This is recommended for saved artifacts and unnecessary for normal chat-only responses.

Recommended shape:

```yaml
---
forge_artifact:
  type: plan | ecp | execution_report | review_report
  lifecycle_mode: plan | implementation | execute | review
  status: ready_for_implementation | ecp_ready | completed | accepted | needs_follow_up | blocked
  created_for: "<short task title>"
  source_context:
    - ".forge/context/..."
  source_artifacts:
    - ".forge/generated/..."
  next_mode: implementation | execute | review | none
  context_impact: true | false | unknown
---
```

Metadata guidance:
- Keep the block minimal and readable.
- `source_context` and `source_artifacts` may be empty lists when there is nothing relevant to cite.
- Status values should remain operational and mode-specific. They must not imply autonomous workflow state.
- Use `context_impact: unknown` when the saved artifact does not carry enough evidence to conclude whether durable context should change.

Artifacts must stay concise. Store decisions, blockers, boundaries, evidence references, validation results, and follow-up actions only when they are needed for engineering continuity.

---

## 4. Artifact Types

### 4.1 Plan Artifact

Produced by: plan mode.

Default behavior:
- Emit the Forge Plan in chat.
- Persist only when requested or approved for continuity.

Purpose:
- Preserve reviewable engineering intent before implementation.
- Preserve plan shape: Quick Plan or SDD.
- Preserve risks, boundaries, and blockers.

Recommended save path:

```text
.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md
```

Minimum contents:
- Title.
- Status.
- Plan type: Quick Plan or SDD.
- Reason for chosen type.
- Required decisions.
- Blockers.
- Boundaries.
- Linked systems or layers.
- Revision timestamp or reference.

### 4.2 ECP Artifact

Produced by: implementation mode.

Default behavior:
- Emit the ECP or readiness package in chat.
- Persist only when requested or approved for continuity.

Purpose:
- Preserve the execution-ready context package produced from an approved plan.

Recommended save path:

```text
.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md
```

Minimum contents:
- Readiness status.
- Task sequence.
- Stop conditions.
- Do-not-change boundaries.
- Acceptance criteria.
- Validation requirements.
- Security constraints.
- Derived-from approved plan reference.

### 4.3 Execution Report Artifact

Produced by: execute mode.

Default behavior:
- Report execution in chat.
- Persist when requested, approved, or useful for follow-up review continuity.

Purpose:
- Preserve the actual implementation result.

Recommended save path:

```text
.forge/generated/reports/YYYY-MM-DD-<slug>-execution-report.md
```

Minimum contents:
- Execution result.
- Changed file groups.
- Validation status.
- Manual follow-up.
- Rollback notes.
- Unchanged boundaries.

### 4.4 Review Report Artifact

Produced by: review mode.

Default behavior:
- Report review findings in chat.
- Persist only when requested or approved.

Purpose:
- Preserve review findings for follow-up work.

Recommended save path:

```text
.forge/generated/reviews/YYYY-MM-DD-<slug>-review.md
```

Minimum contents:
- Review Report.
- Verdict.
- Mode Boundary.
- Diff Reviewed.
- Summary.
- Critical, major, or minor findings.
- Validation result assessment.
- Lifecycle boundary assessment.
- Security or risk assessment.
- Context impact.
- Recommended next step.

Review report artifacts must name the diff surface reviewed. If no diff or changed-file evidence is available, the artifact must say so explicitly and should usually preserve a `needs_more_validation` style outcome rather than imply complete review coverage.

---

## 5. Continue-From-Artifact Workflow

Saved artifacts are continuity helpers, not autonomous instructions.

Supported mode mapping:
- Saved `plan` artifact -> `implementation` mode may continue from it and produce an ECP.
- Saved `ecp` artifact -> `execute` mode may continue from it and implement the approved scope.
- Saved `execution_report` artifact -> `review` mode may continue from it and assess the result.
- Saved `review_report` artifact -> may guide follow-up planning or a `.forge/context-patches/...` proposal, but it must not auto-apply context changes.

Continuation examples:

```text
Use Forge implementation mode from .forge/generated/plans/2026-06-05-add-export-plan.md
Use Forge execute mode from .forge/generated/ecp/2026-06-05-add-export-ecp.md
Use Forge review mode from .forge/generated/reports/2026-06-05-add-export-execution-report.md
```

Required continuation checks:
- Read the referenced artifact first.
- Verify the artifact type matches the requested lifecycle mode.
- Verify the artifact still has enough evidence, scope, and approval context for safe continuation.
- Check for material repository or context drift when evidence is available.
- Stay inside the artifact's approved scope.
- Do not silently expand scope.
- Do not execute from a plan artifact directly; execution still requires an approved ECP.
- Do not mutate `.forge/context` based only on generated artifact content.

When a saved artifact is stale, ambiguous, contradicted by current evidence, or lacks required approval state:
- Return a blocked or needs-more-context style outcome for the current mode.
- Explain what evidence, approval, or refreshed artifact is missing.

---

## 6. Save Behavior

Default behavior:
- Respond in chat.

Save only when:
- The user explicitly asks to save.
- The user asks for a saved artifact such as a saved plan, saved ECP, saved execution report, or saved review report.
- The user asks for `write this to .forge/generated/...` or equivalent wording.
- The workflow needs a saved artifact for continuity and the user approves that persistence.

Do not:
- Auto-save every plan, ECP, execution report, or review report.
- Save temporary scratchpads as generated artifacts.
- Save raw logs as artifacts unless they are summarized into a human-readable report.
- Overwrite an existing generated artifact without explicit approval.
- Promote saved artifacts into `.forge/context`.

---

## 7. Linking Rules

Artifacts may reference:
- Previous artifact paths.
- Plan, ECP, execution report, or review report artifact paths.
- Repository evidence paths, commits, PR or MR IDs, ADRs, or human confirmation references.

Artifact links are trace references only.

They must NOT:
- Define dependency graphs.
- Encode orchestration semantics.
- Create DAGs or workflow state machines.
- Trigger execution.
- Replace task approval.

Use shallow links. Prefer direct parent or current-result links over long chains.

---

## 8. Content Boundaries

Artifacts must NOT contain:
- Hidden chain-of-thought.
- Raw secrets.
- Unnecessary conversational history.
- Generic long-form summaries.
- Broad repository audits unrelated to the lifecycle handoff.
- Knowledge graph terminology or structure.
- Agent memory, autonomous memory, workflow engine, or orchestration concepts.

Artifacts should use concise engineering language, stable references, and direct evidence or status wording. Avoid abstract lifecycle commentary when a blocker, decision, validation result, or changed boundary is enough.

---

## 9. Mode Ownership

| Mode | Saved artifact type |
|---|---|
| `plan` | `plan` |
| `implementation` | `ecp` |
| `execute` | `execution_report` |
| `review` | `review_report` |

Ask mode does not produce lifecycle artifacts by default. It may reference existing artifacts when directly relevant to a lightweight question.

---

## 10. Future Compatibility Boundary

This specification gives future automation stable artifact boundaries, but it does not implement automation.

It does not add:
- Orchestration.
- Agents.
- Workflow engines.
- DAG systems.
- CI/CD logic.
- Deploy workflows.
- Runtime executors.
- Persistent AI memory systems.
- Knowledge graph systems.
