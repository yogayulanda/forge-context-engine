# Forge Workflow

This document is the canonical reference for the Forge end-to-end engineering workflow. For the mode selection decision guide see `docs/mode-selection.md`. For a worked example see `docs/first-workflow.md`.

---

## The Workflow

```text
forge-plan
→ human approval
→ forge-implement
→ human approval
→ forge-execute
→ optional forge-test
→ forge-review
→ scoped fix loop if needed
```

Each step produces a defined output. Each transition between planning and implementation, and between implementation and execution, requires explicit human approval. No assistant may self-approve either transition.

---

## What Each Step Produces

| Step | Output | Mutation? |
|---|---|---|
| `forge-plan` | ECP (`status: proposed`) | No |
| human approval | ECP transitions to `approved` | N/A |
| `forge-implement` | Execution Contract (`status: proposed`) | No |
| human approval | Execution Contract transitions to `approved` | N/A |
| `forge-execute` | Code changes + validation report | Yes, inside approved scope |
| `forge-test` (optional) | Structured validation result | Maybe, if test changes are in scope |
| `forge-review` | MR readiness + findings | No |
| fix loop | Bounded code fix | Yes, inside approved fix scope |

---

## Approval Gate UX

### Gate 1 — Plan approval

After `forge-plan` produces an ECP, the human must review and explicitly approve before implementation begins.

Minimal approval signals:

```
Approved. Use Forge implementation mode for the retry plan.
```

```
Approved. Use Forge implementation mode for ECP ecp.retry-plan.r1.
```

Rules:
- The human must explicitly approve.
- Invoking `forge-implement` without a prior approval signal means the assistant should treat the input as a new direct request, not a pre-approved plan.
- The assistant must not infer approval from ECP artifact creation alone.
- Affirmative language such as "looks good" or "that makes sense" is not a formal approval signal.

### Gate 2 — Task card approval

After `forge-implement` produces an Execution Contract with task cards, the human must review and explicitly approve before execution begins.

Minimal approval signals:

```
Approved. Use Forge execute mode for task cards IMP-001 and IMP-002.
```

```
Approved. Execute the confirmed execution contract from the last forge-implement output.
```

Rules:
- The human must explicitly approve task cards, an Execution Contract, or a named bounded task subset.
- A proposed Execution Contract is not sufficient for execution without human confirmation.
- The assistant must not execute immediately after producing task cards.
- `READY_FOR_EXECUTION` in implementation output is a readiness signal, not autonomous permission to execute.

---

## When to Skip Modes

| Mode | Skip when |
|---|---|
| `forge-ask` | Intent is already clear; no understanding gaps |
| `forge-plan` | Change is simple, bounded, well-understood, no architectural risk |
| `forge-test` | Lightweight validation from execute is sufficient; no new test changes needed |
| Human approval gates | **Never.** Approval between plan → implement and implement → execute is always required. |

---

## Post-Review Fix Loop

When `forge-review` returns `NEEDS_CHANGES`:

```text
forge-review (NEEDS_CHANGES)
→ human reviews findings
→ human approves fix scope
→ forge-implement for new task cards, OR forge-execute for small bounded fixes
→ optional forge-test
→ forge-review
```

Guidance:

- For `CRITICAL` or `MAJOR` findings: use `forge-implement` to produce fix task cards for the finding scope. Get human approval. Then use `forge-execute`.
- For `MINOR` findings: the human may request `forge-execute` directly with the precise fix scope named.
- The human must approve the fix scope before execute runs, the same as the main workflow.
- `forge-review` when re-invoked should verify prior findings are resolved or explicitly still open.
- Review findings do not automatically become execute tasks. The human names the fix scope.

---

## Entry Points

Not every change starts at `forge-plan`.

| Situation | Entry point |
|---|---|
| Understanding code or current state | `forge-ask` |
| Active incident or production failure | `forge-incident` |
| Behavior-preserving cleanup | `forge-refactor` |
| Clear, bounded, well-understood change | `forge-implement` directly |
| Non-trivial change needing architectural shape | `forge-plan` |

See `docs/mode-selection.md` for the full decision guide.
