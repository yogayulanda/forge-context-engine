# Forge Workflow

This document is the canonical reference for the Forge end-to-end engineering workflow. For the mode selection decision guide see `docs/mode-selection.md`. For a worked example see `docs/first-workflow.md`.

---

## The Workflow

```text
forge-init
-> forge-ask
-> forge-plan
-> human approval
-> forge-implementation
-> human approval
-> forge-execute
-> forge-review
-> forge-verify-context when context health may be affected
-> scoped fix loop if needed
```

Each step produces a defined output. Each transition between plan and implementation, and between implementation and execution, requires explicit human approval. No assistant may self-approve either transition.

For multi-repo work, this workflow still runs in bounded scope:
- repo-scoped work starts from the current service repo context
- cross-repo planning may load workspace context first, then only the relevant linked service contexts
- workspace context coordinates ownership and boundaries; it does not replace service-specific source of truth

---

## What Each Step Produces

| Step | Output | Mutation? |
|---|---|---|
| `forge-init` | Confirmed `.forge/context` and `forge.config.yaml` | Drafts context/config; finalizes only after confirmation |
| `forge-ask` | Evidence-aware answer | No |
| `forge-plan` | Quick Plan or SDD (`status: proposed`) | No |
| human approval | Plan transitions to approved implementation input | N/A |
| `forge-implementation` | Execution Context Package (`status: proposed`) | No |
| human approval | ECP transitions to approved execution input | N/A |
| `forge-execute` | Code changes + validation report | Yes, inside approved scope |
| `forge-review` | Verdict + diff reviewed + findings + validation assessment + context impact | No |
| `forge-verify-context` | Context health/freshness result | No |
| fix loop | Bounded code fix | Yes, inside approved fix scope |

---

## Approval Gate UX

### Gate 1 - Plan approval

After `forge-plan` produces a Quick Plan or SDD, the human must review and explicitly approve before implementation begins.

Minimal approval signals:

```text
Approved. Use Forge implementation mode for the retry plan.
```

```text
Approved. Use Forge implementation mode for plan retry-plan.r1.
```

Rules:
- The human must explicitly approve.
- Invoking `forge-implementation` without a prior approval signal means the assistant should treat the input as a new direct request, not a pre-approved plan.
- The assistant must not infer approval from plan artifact creation alone.
- Affirmative language such as "looks good" or "that makes sense" is not a formal approval signal.

### Gate 2 - ECP approval

After `forge-implementation` produces an Execution Context Package, the human must review and explicitly approve before execution begins.

Minimal approval signals:

```text
Approved. Use Forge execute mode for ECP ecp.retry-plan.r1.
```

```text
Approved. Execute the confirmed ECP from the last forge-implementation output.
```

Rules:
- The human must explicitly approve the ECP or a named bounded ECP subset.
- A proposed ECP is not sufficient for execution without human confirmation.
- The assistant must not execute immediately after producing an ECP.
- ECP readiness in implementation output is a readiness signal, not autonomous permission to execute.

---

## When to Skip Modes

| Mode | Skip when |
|---|---|
| `forge-init` | The repository already has confirmed Forge context/config. |
| `forge-ask` | Intent is already clear; no understanding gaps. |
| `forge-plan` | Change is simple, bounded, well-understood, no architectural risk. |
| `forge-verify-context` | No context card or source evidence could be affected. |
| Human approval gates | **Never.** Approval between plan -> implementation and implementation -> execute is always required. |

---

## Scenario Workflows

Not every task starts at `forge-plan`.

| Situation | Entry point |
|---|---|
| Understanding code or current state | `forge-ask` |
| Active incident or production failure | Incident scenario: `ask` -> `plan` -> `implementation` -> `execute` -> `review` as needed |
| Behavior-preserving cleanup | Refactor scenario: `plan` -> `implementation` -> `execute` -> `review` as needed |
| Clear, bounded, well-understood change | `forge-implementation` directly, then human approval before execute |
| Non-trivial change needing architectural shape | `forge-plan` |

Validation is a workflow activity inside `execute` and `review`, not a separate core lifecycle mode.

---

## Post-Review Fix Loop

When `forge-review` returns findings that need fixes:

```text
forge-review
-> human reviews findings
-> human approves fix scope
-> forge-implementation for new ECP, OR forge-execute for small bounded fixes
-> forge-review
-> forge-verify-context if context health may be affected
```

Guidance:

- For critical or major findings: use `forge-implementation` to produce a fix ECP for the finding scope. Get human approval. Then use `forge-execute`.
- For minor findings: the human may request `forge-execute` directly with the precise fix scope named.
- The human must approve the fix scope before execute runs, the same as the main workflow.
- `forge-review` when re-invoked should verify prior findings are resolved or explicitly still open.
- Review findings do not automatically become execute tasks. The human names the fix scope.

See `docs/mode-selection.md` for the full decision guide.
