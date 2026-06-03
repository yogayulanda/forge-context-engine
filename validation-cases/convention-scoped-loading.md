# Convention Scoped Loading

| Field | Value |
|---|---|
| Pattern | `convention-scoped-loading` |
| Lifecycle state | `benchmarked` |
| Coverage category | Context load optimization, scoped convention retrieval, redundancy reduction |
| Scope | Repository-neutral cognition benchmark |

---

## 1. Pattern Name

`convention-scoped-loading`

Forge must use `conventions.md` as a short index and load scoped convention files only when the task requires them — not for every task.

---

## 2. Lifecycle State

`benchmarked`

This case represents a validated cognition pattern for context-load efficiency. It does not imply the pattern is `stable` across all repository diversity.

---

## 3. Topology Shape

```text
task arrives
→ conventions.md loaded (always-loaded, short index)
→ assistant checks task type
→ loads only the scoped convention file relevant to the task
→ proceeds without loading unrelated scoped convention files
```

---

## 4. Expected Behavior

- `conventions.md` acts as a short index and global convention entrypoint.
- Assistants load scoped convention files based on task need, not by default.
- Output formatting and style questions load `conventions-language.md`.
- Evidence, citation, or constraint extraction questions load `conventions-evidence.md`.
- Risk-sensitive, governance, approval, or secret-handling questions load `conventions-risk.md`.
- Testing, validation, review evidence, or prerequisite checks load `conventions-validation.md`.
- Assistants do not load all scoped convention files for every task.
- Scoped convention files are referenced via the Scoped Convention Files table in `conventions.md`.

---

## 5. Incorrect Behaviors Forge Must Reject

- Always loading every scoped convention file regardless of task type.
- Keeping `conventions.md` as a giant duplicated full manual (defeats scoped loading).
- Losing important conventions during extraction (conventions must be findable via references).
- Reintroducing long convention blocks inside `specs/mode-invocation.md`.
- Loading `conventions-evidence.md` for a pure output formatting task.
- Loading `conventions-risk.md` for a read-only ask query with no governance signals.

---

## 6. Evidence Shape Required

- `conventions.md` is short (index + global rules only).
- Scoped convention files exist with real content for their category.
- At least one scoped file is referenced from the Scoped Convention Files table in `conventions.md`.
- Task-type-to-file mapping is explicit and navigable.

---

## 7. Known Incorrect Interpretations

- "Always-loaded means every file in `00-meta/` is always loaded." — Scoped convention files in `00-meta/` are loaded on demand, not automatically.
- "Scoped files are optional extras." — They contain required conventions; they are just loaded selectively.
- "conventions.md should still contain all rules for completeness." — After Batch B, full rules live in scoped files; conventions.md is the index.

---

## 8. Hallucination Boundary

Forge must not:
- Claim a convention applies without checking the relevant scoped file.
- Describe validation statuses from memory when `conventions-validation.md` is not loaded.
- Report governance rules without loading `conventions-risk.md` for governance-sensitive tasks.

---

## 9. Regression Signals

This case regresses if:

- `conventions.md` grows back into a large always-loaded full manual.
- `specs/mode-invocation.md` reintroduces long convention blocks from scoped files.
- Scoped convention files exist but are never referenced or loaded.
- Important conventions are silently missing from both `conventions.md` and scoped files.
- References in scoped files or `conventions.md` point to missing files.
