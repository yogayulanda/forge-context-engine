# Context Patch Workflow

| Field | Value |
|---|---|
| Pattern | `context-patch-review-flow` |
| Lifecycle state | `benchmarked` |
| Coverage category | Context maintenance, team workflow, source-of-truth boundary |
| Scope | Repository-neutral context benchmark |

---

## Expected Behavior

Context refresh follows this flow:

```text
changed files
-> affected context cards
-> .forge/context-patches proposal
-> human review
-> promote to .forge/context
```

Required metadata on curated context cards:
- `title`
- `status`
- `confidence`
- `source_paths`
- `source_commit`
- `last_verified`

`.forge/context` is committed curated source of truth. `.forge/context-patches` contains reviewable proposals only.

When review determines durable repo knowledge changed, it should propose a patch path such as:

```text
.forge/context-patches/<date>-<slug>.md
```

Suggested proposal contents:
- target context files
- reason
- evidence
- proposed update or diff
- confidence
- promotion notes requiring human review before promotion into `.forge/context`

## Incorrect Behaviors Forge Must Reject

- Silently overwriting `.forge/context` from code changes without a reviewable patch.
- Treating generated artifacts as curated context.
- Omitting context impact checks from execute or review when source paths changed.
- Promoting inferred or stale context without evidence and human review.

## Regression Signals

This case regresses if context updates bypass `.forge/context-patches` or if `team.require_context_impact_check` is not enforced.
