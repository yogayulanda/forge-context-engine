# Artifact Lifecycle Specification

| Field | Value |
|---|---|
| Document | Forge Artifact Lifecycle Specification |
| Version | 1.1 |
| Date | 2026-05-25 |
| Status | `decision` |
| Scope | Minimal lifecycle artifacts for mode continuity |
| Dependency | `specs/mode-invocation.md`, `specs/context-validation.md`, `runtime/.forge/context/00-meta/conventions.md` |

---

## 0. Purpose

This document defines small, human-readable lifecycle artifacts that preserve engineering continuity across Forge modes and sessions.

Artifacts are supporting engineering records. They help engineers and assistants connect planning, implementation, execution, testing, review, incident, and refactor work without reconstructing the same context repeatedly.

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

Default location:

```
.forge/context/generated/artifacts/
```

The folder is created on demand. Artifact files use Markdown with front matter and concise sections. They are append-friendly, reviewable in diffs, and replaceable/discardable.

Recommended filename:

```
<artifact-type>-<short-topic>-<revision>.md
```

Recommended artifact ID:

```
artifact.<type>.<short-topic>.r<N>
```

`generated/artifacts/*` remains generated context. It is loaded only by explicit reference, mode handoff, or task relevance.

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

### 4.1 ECP Artifact

Produced by: planning mode.

Purpose:
- Preserve approved engineering intent.
- Preserve confirmed decisions.
- Preserve boundaries and blockers.

Minimum contents:
- Title.
- Status.
- Confirmed decisions.
- Blockers.
- Approved boundaries.
- Linked systems/layers.
- Revision timestamp or reference.

**ECP status vocabulary:**

| Status | Meaning |
|---|---|
| `proposed` | Planning output produced; awaiting human review and approval |
| `approved` | Human has explicitly accepted this as the basis for implementation |
| `superseded` | Replaced by a newer revision |
| `rejected` | Human declined this direction |

Rules:
- A newly produced ECP artifact must use `status: proposed`.
- Only the human may transition an ECP to `approved`.
- An AI assistant must not self-promote an ECP from `proposed` to `approved`.

### 4.2 Execution Contract Artifact

Produced by: implementation mode.

Purpose:
- Persist the execution-ready task contract.

Minimum contents:
- Readiness status.
- Task cards.
- Dependency order.
- Stop conditions.
- Do-not-change boundaries.
- Acceptance criteria.
- Derived-from ECP reference.

**Execution Contract status vocabulary:**

| Status | Meaning |
|---|---|
| `proposed` | Task cards produced by implementation mode; awaiting human review |
| `approved` | Human has confirmed these task cards are safe to execute |
| `blocked` | Blockers remain unresolved; not execution-ready |
| `superseded` | Replaced by a revised contract |

Rules:
- A newly produced Execution Contract must use `status: proposed`.
- Only the human may transition it to `approved`.
- An AI assistant must not self-promote from `proposed` to `approved`.

### 4.3 Execute Result Artifact

Produced by: execute mode.

Purpose:
- Preserve the actual implementation result.

Minimum contents:
- Execution result.
- Changed file groups.
- Validation status.
- Manual follow-up.
- Rollback notes.
- Unchanged boundaries.

### 4.4 Testing Result Artifact

Produced by: testing mode.

Purpose:
- Preserve validation evidence.

Minimum contents:
- Testing result.
- Validated scope.
- Blockers.
- Automated/manual validation.
- Coverage gaps.
- Runtime-sensitive validation.

### 4.5 Review Result Artifact

Produced by: review mode.

Purpose:
- Preserve MR/review findings.

Minimum contents:
- Review result.
- MR readiness.
- Critical/major findings.
- Reviewer focus.
- Rollback/safety notes.
- Suggested next action.

### 4.6 Incident Artifact

Produced by: incident mode.

Purpose:
- Preserve diagnosis and mitigation flow.

Minimum contents:
- Incident summary.
- Likely root cause.
- Affected systems.
- Mitigation.
- Rollback possibility.
- Next checks.

### 4.7 Refactor Artifact

Produced by: refactor mode.

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
- ECP artifact IDs.
- Execution contract artifact IDs.
- Execute, testing, review, incident, or refactor result references.
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
- Producing an artifact does not imply approval. A newly produced ECP or Execution Contract is `proposed` until the human explicitly approves it.
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
| `planning` | ECP Artifact |
| `implementation` | Execution Contract Artifact |
| `execute` | Execute Result Artifact |
| `testing` | Testing Result Artifact |
| `review` | Review Result Artifact |
| `incident` | Incident Artifact |
| `refactor` | Refactor Artifact |

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
