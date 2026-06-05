# Artifact Lifecycle Specification

| Field | Value |
|---|---|
| Document | Forge Artifact Lifecycle Specification |
| Version | 1.3 |
| Date | 2026-06-05 |
| Status | `decision` |
| Scope | Minimal lifecycle artifacts for mode continuity |
| Dependency | `specs/mode-invocation.md`, `specs/context-validation.md`, `runtime/.forge/context/00-meta/conventions.md` |

---

## 0. Purpose

This document defines small, human-readable lifecycle artifacts that preserve engineering continuity across Forge modes and sessions.

Artifacts are supporting engineering records. They help engineers and assistants connect plan, implementation, execution, review, verify-context, and scenario work without reconstructing the same context repeatedly.

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
- The artifact is stale, partial, or superseded.
- The conflict must be surfaced as a validation or review concern when it affects execution safety.

Artifacts may summarize approved intent and results, but they never override repository truth.

---

## 2. Persistence Boundary

Artifacts are persisted only when useful for lifecycle continuity.

Default behavior is chat output first. Forge should not auto-write a Markdown artifact for every small answer.

Default persisted location:

```
.forge/generated/
```

The folder is created on demand. Artifact files use Markdown with front matter and concise sections. They are append-friendly, reviewable in diffs, and replaceable/discardable.

Artifact storage policy:

| Path | Policy |
|---|---|
| `.forge/context` | Committed curated context source of truth |
| `.forge/context-patches` | Reviewable context update proposals |
| `.forge/generated` | Generated artifacts committed manually when relevant |
| `.forge/temp` | Ignored local-only scratch |
| `.forge/cache` | Ignored local-only cache |

Generated artifacts must never be confused with curated context. Context changes that should become durable source of truth go through `.forge/context-patches` review before promotion to `.forge/context`.

Context quality boundary:
- `.forge/context` is for durable, repo-specific, evidence-backed, compact knowledge that remains useful beyond one task.
- `.forge/generated/...` is for working artifacts such as plans, ECPs, execution reports, review reports, and other temporary continuity records.
- `.forge/context-patches/...` is for proposed durable context updates that still require review.
- A generated artifact is not automatically promoted into `.forge/context`.
- A context patch is not accepted context until it is reviewed and promoted.
- Raw logs, scratchpads, one-off plans, temporary ECPs, and long reports stay out of curated context unless reduced into durable evidence-backed context.

Persist only when one of these is true:
- The user explicitly asks to save or create the artifact.
- The work is medium/large and the user approves saving for continuity.
- The artifact is needed for multi-session or multi-agent continuation.

Do not persist artifacts during read-only modes by default. If a read-only mode is explicitly asked to save its output, save only to `.forge/generated/...` and keep the mode's no-code-change boundary intact.

Recommended persisted paths:

```text
.forge/generated/plans/<date>-<slug>.md
.forge/generated/ecp/<date>-<slug>.md
.forge/generated/reports/<date>-<slug>-execution.md
.forge/generated/reviews/<date>-<slug>-review.md
```

Recommended filename:

```
<artifact-type>-<short-topic>-<revision>.md
```

Recommended artifact ID:

```
artifact.<type>.<short-topic>.r<N>
```

`.forge/generated/*` remains generated artifact output. It is loaded only by explicit reference, mode handoff, or task relevance.

---

## 3. Common Artifact Fields

Every persisted artifact should include:

- `artifact_id`
- `artifact_type`
- `status`
- `produced_by_mode`
- `derived_from`
- `created_at` or `updated_at`
- `repo_reference`
- `summary`
- `boundaries`
- `links`

Statuses should be operational and mode-specific. Avoid broad lifecycle vocabulary that implies autonomous state management.

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
- Preserve risks, options, boundaries, and blockers.

Minimum contents:
- Title.
- Status.
- Plan type: Quick Plan or SDD.
- Reason for chosen type.
- Required decisions.
- Blockers.
- Boundaries.
- Linked systems/layers.
- Revision timestamp or reference.

**Plan status vocabulary:**

| Status | Meaning |
|---|---|
| `proposed` | Plan output produced; awaiting human review and approval |
| `approved` | Human has explicitly accepted this as the basis for implementation mode |
| `superseded` | Replaced by a newer revision |
| `rejected` | Human declined this direction |

Rules:
- A newly produced Plan artifact must use `status: proposed`.
- Only the human may transition a Plan artifact to `approved`.
- An AI assistant must not self-promote a Plan artifact from `proposed` to `approved`.

### 4.2 ECP Artifact

Produced by: implementation mode.

Default behavior:
- Emit the ECP/readiness package in chat.
- Persist only when requested or approved for continuity.

Purpose:
- Persist the execution-ready context package produced from an approved plan.

Minimum contents:
- Readiness status.
- Task cards.
- Dependency order.
- Stop conditions.
- Do-not-change boundaries.
- Acceptance criteria.
- Validation requirements.
- Security constraints.
- Derived-from approved Plan reference.

**ECP status vocabulary:**

| Status | Meaning |
|---|---|
| `proposed` | Task cards produced by implementation mode; awaiting human review |
| `approved` | Human has confirmed the ECP is safe to execute |
| `blocked` | Blockers remain unresolved; not execution-ready |
| `superseded` | Replaced by a revised contract |

Rules:
- A newly produced ECP must use `status: proposed`.
- Only the human may transition it to `approved`.
- An AI assistant must not self-promote from `proposed` to `approved`.

### 4.3 Execute Result Artifact

Produced by: execute mode.

Default behavior:
- Report execution in chat.
- Persist when requested, approved, or useful for follow-up review/continuity.

Purpose:
- Preserve the actual implementation result.

Minimum contents:
- Execution result.
- Changed file groups.
- Validation status.
- Manual follow-up.
- Rollback notes.
- Unchanged boundaries.

### 4.4 Validation Result Artifact

Produced by: execute/review workflow when scoped validation evidence needs a separate handoff record.

Purpose:
- Preserve validation evidence.

Minimum contents:
- Validation result.
- Validated scope.
- Blockers.
- Automated/manual validation.
- Coverage gaps.
- Runtime-sensitive validation.

### 4.5 Review Result Artifact

Produced by: review mode.

Default behavior:
- Report review findings in chat.
- Persist only when requested or approved.

Purpose:
- Preserve MR/review findings.

Minimum contents:
- Review Report.
- Verdict.
- Mode Boundary.
- Diff Reviewed.
- Summary.
- Critical/major findings.
- Validation result assessment.
- Lifecycle boundary assessment.
- Security / risk assessment.
- Context impact.
- Recommended next step.

Review result artifacts must name the diff surface reviewed. If no diff or changed-file evidence is available, the artifact must say so explicitly and should usually preserve a `needs_more_validation` outcome rather than imply complete review coverage.

Recommended next-step wording must preserve human control. It must not imply that Forge will commit, push, merge, or open MR/PR actions automatically.

### 4.6 Incident Scenario Artifact

Produced by: incident workflow scenario when diagnosis and mitigation need a separate handoff record.

Purpose:
- Preserve diagnosis and mitigation flow.

Minimum contents:
- Incident summary.
- Likely root cause.
- Affected systems.
- Mitigation.
- Rollback possibility.
- Next checks.

### 4.7 Refactor Scenario Artifact

Produced by: refactor workflow scenario when technical-debt intent needs a separate handoff record.

Purpose:
- Preserve technical debt proposal or refactor intent.

Minimum contents:
- Problem areas.
- Proposed safe improvements.
- Risk areas.
- Out-of-scope redesigns.
- Recommended execution boundaries.

---

## 5. Linking Rules

Artifacts may reference:
- Previous artifact IDs.
- Plan artifact IDs.
- ECP artifact IDs.
- Execute, review, verify-context, or scenario result references.
- Repository evidence paths, commits, PR/MR IDs, ADRs, or human confirmation references.

Artifact links are trace references only.

They must NOT:
- Define dependency graphs.
- Encode orchestration semantics.
- Create DAGs or workflow state machines.
- Trigger execution.
- Replace task approval.

Use shallow links. Prefer direct parent/current-result links over long chains.

---

## 6. Lifecycle Semantics

Artifacts are lifecycle helpers with these semantics:

- Append-friendly: revisions may add clearer status, result, or follow-up.
- Reviewable: engineers can inspect and diff them.
- Replaceable: a newer artifact may supersede an older one.
- Discardable: deleting an artifact must not remove repository truth.
- Bounded: no long conversational dumps or broad historical summaries.
- Explicitly non-authoritative over repository evidence.
- Producing an artifact does not imply approval. A newly produced Plan or ECP is `proposed` until the human explicitly approves it.
- Artifact status promotion from `proposed` to `approved` requires explicit human confirmation; it is not a side-effect of artifact creation or assistant output.

Revision references may use `r1`, `r2`, or date-based references. Revisions should preserve the reason for change when it affects execution or review continuity.

---

## 7. Content Boundaries

Artifacts must NOT contain:
- Hidden chain-of-thought.
- Raw secrets.
- Unnecessary conversational history.
- Generic long-form summaries.
- Broad repository audits unrelated to the lifecycle handoff.
- Knowledge graph terminology or structure.
- Agent memory, autonomous memory, workflow engine, or orchestration concepts.

Artifacts should use concise engineering language, stable references, and direct evidence/status wording. Avoid abstract lifecycle commentary when a blocker, decision, validation result, or changed boundary is enough.

---

## 8. Mode Ownership

| Mode | Artifact |
|---|---|
| `plan` | Quick Plan or SDD |
| `implementation` | Execution Context Package |
| `execute` | Execute Result Artifact |
| `review` | Review Result Artifact |
| `verify-context` | Context Verification Result |

Ask mode does not produce lifecycle artifacts by default. It may reference existing artifacts when directly relevant to a lightweight question.

---

## 9. Future Compatibility Boundary

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
