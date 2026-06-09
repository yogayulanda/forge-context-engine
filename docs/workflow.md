# Forge Workflow

This document is the canonical reference for the Forge end-to-end engineering workflow. For the mode selection decision guide see `docs/mode-selection.md`. For a worked example see `docs/first-workflow.md`.

For repository setup and adoption:
- fresh repo: `forge init`
- existing or legacy Forge repo: `forge update`
- workspace repo: `forge init --workspace`
- preview before managed refresh: `forge update --dry-run`

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

Saved artifact continuity is optional:
- default behavior is chat output first
- save to `.forge/generated/...` only when requested or approved
- generated artifacts are reusable working files, not curated context
- durable context changes still go through `.forge/context-patches/...` review

Adapter parity expectations:
- `.forge/adapter.md` owns shared lifecycle, context-loading, artifact, and safety rules for every supported tool
- `AGENTS.md`, `CLAUDE.md`, and optional `.github/copilot-instructions.md` stay thin wrappers
- universal lifecycle artifacts stay tool-neutral unless a clearly labeled `Target Tool Notes` section is needed

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
| `forge-ai-readiness` | AI readiness report + remediation roadmap + proposed context updates | No |
| `forge-verify-context` | Context health/freshness result | No |
| fix loop | Bounded code fix | Yes, inside approved fix scope |

Minimum common artifact shape across tools:
- Plan: `Mode Boundary`, `Assumptions`, `Goal / Scope / Non-goals`, `Evidence`, `Risks`, `Acceptance Criteria`, `Validation Commands`, `Next Step`, `Status`
- ECP: `Approved Scope`, `Files likely to change`, `Task sequence`, `Coding rules`, `Safety constraints`, `Validation commands`, `Stop conditions`, `Expected execution report`, `Status`
- Execution Report: `Changed files`, `What changed`, `Validation run`, `Deviations`, `Remaining risks`, `Status`
- Review: `Verdict`, `Diff Reviewed`, `Findings`, `Validation assessment`, `Context Impact`, `Recommended next step`, `Status`
- AI Readiness Report: `Executive Summary`, `Verdict`, `Readiness Profile`, `Key Strengths`, `Priority Risks`, `Findings`, `Ambiguities`, `Questions For Human`, `Context Drift`, `Proposed Context Updates`, `Remediation Roadmap`, `Evidence Coverage`, `Recommended Next Step`, `Status`

Optional saved artifact paths:

```text
.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md
.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md
.forge/generated/reports/YYYY-MM-DD-<slug>-execution-report.md
.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-report.md
.forge/generated/reports/YYYY-MM-DD-<slug>-ai-readiness-roadmap.md
.forge/generated/reviews/YYYY-MM-DD-<slug>-review.md
```

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
- Continuing from a saved plan still requires checking that the artifact is a plan, that it still matches current evidence, and that approval exists.

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
- Continuing from a saved ECP still requires checking that the artifact is an ECP, that it still matches current evidence, and that approval exists.

## Continue From Saved Artifact

Supported mapping:
- plan artifact -> `forge-implementation`
- ECP artifact -> `forge-execute`
- execution report artifact -> `forge-review`
- review report artifact -> follow-up `forge-plan` work or a `.forge/context-patches/...` proposal

Guardrails:
- read the referenced artifact first
- verify the artifact type matches the requested mode
- verify the artifact still has enough evidence and approved scope
- check for material source or context drift when evidence is available
- block or request more context when the artifact is stale or ambiguous
- do not execute from a plan artifact directly
- do not mutate `.forge/context` from generated artifact content alone

---

## When to Skip Modes

| Mode | Skip when |
|---|---|
| `forge-init` | The repository already has confirmed Forge context/config. |
| `forge-ask` | Intent is already clear; no understanding gaps. |
| `forge-plan` | Change is simple, bounded, well-understood, no architectural risk. |
| `forge-ai-readiness` | The repository is already well understood and no readiness audit or remediation prioritization is needed. |
| `forge-verify-context` | No context card or source evidence could be affected. |
| Human approval gates | **Never.** Approval between plan -> implementation and implementation -> execute is always required. |

---

## Scenario Workflows

Not every task starts at `forge-plan`.

| Situation | Entry point |
|---|---|
| Understanding code or current state | `forge-ask` |
| Repository onboarding, AI safety, or context fitness audit | `forge-ai-readiness` |
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
