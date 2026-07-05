---
id: meta.conventions-validation
title: Validation & Testing Conventions
type: meta
status: confirmed
confidence: high
source: human
evidence:
  - { type: doc, ref: ../../../../specs/mode-invocation.md }
  - { type: doc, ref: ../../../../specs/artifact-lifecycle.md }
owner: forge-context-engine
updated: 2026-06-03
---

# Validation & Testing Conventions

Load this file when the task involves validation reporting, test expectations, review evidence, prerequisite checks, or missing validation behavior.

---

## Runtime Validation Semantics

Validation reporting must never imply success without evidence.

### Canonical Operational Statuses

| Mode | Allowed statuses |
|---|---|
| Execute | `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, `NOT_VALIDATED` |
| Review | `APPROVED`, `NEEDS_CHANGES`, `BLOCKED`, `PARTIAL_REVIEW` |
| Implementation | `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, `READY_FOR_EXECUTION` |

### Status Meanings

Execute:
- `SUCCESS`: approved scope completed and reliable validation evidence exists.
- `PARTIAL_SUCCESS`: implementation completed partially, or implementation finished but validation is incomplete.
- `BLOCKED`: contract, approval, runtime behavior, ownership, security, or other non-environment prerequisites are unresolved.
- `BLOCKED_BY_ENVIRONMENT`: required runtime/tooling/infra is unavailable.
- `NOT_VALIDATED`: code changed, but no reliable validation executed.

Review:
- `APPROVED`: sufficient implementation and validation evidence; no blocking findings.
- `NEEDS_CHANGES`: implementation, test, or documentation changes required before approval.
- `BLOCKED`: required contract/runtime evidence is missing.
- `PARTIAL_REVIEW`: review covered only part of the changed scope.

### Prerequisite Checks

Before running validation or tests, check required prerequisites for the attempted command: language/runtime tools (`go`, `node`), formatters (`gofmt`), package managers (`npm`, `pnpm`, `yarn`), dependency/codegen/protobuf tools, Docker/compose, and explicitly required broker/database/test infra.

- Missing tooling or infra is `BLOCKED_BY_ENVIRONMENT`; it is not an implementation failure.
- Contract, schema, runtime behavior, approval, or ownership gaps are `BLOCKED`; they are not environment failures.
- Code changes without reliable validation are `NOT_VALIDATED`, even if implementation work appears complete.

### Validation Section Structure

Validation sections must separate:
- Prerequisites checked.
- Commands or checks executed.
- What failed.
- What could not run.
- What remains unvalidated.

Manual actions must be explicit and operational, e.g. `Jalankan go test ./... setelah Go toolchain tersedia`, `Validasi Kafka integration membutuhkan broker aktif`, or `Replay/DLQ flow belum tervalidasi manual`.

### Validation Scope Grouping

Validation reporting must group validated scope by applicable category: unit, integration, e2e, smoke, rollback, migration, runtime validation, and contract validation.

Validation reporting must separate automated checks, manual validation, infra-dependent validation, and production-like verification.

Runtime-sensitive testing must explicitly address retryable failures, non-retryable failures, DLQ expectations, duplicate/idempotent replay, and partial replay when relevant.

Validation reports must surface unvalidated risk areas and must not imply full validation, production readiness, or complete coverage without evidence.

### Ownership Boundaries

- Execute performs scoped validation for the implemented scope.
- Review evaluates correctness, risk, and whether implementation/validation evidence supports the claimed status.
- Review performs a small per-task Context Impact Check and may propose a reviewable context patch when durable repository knowledge changes.
- Verify-context evaluates curated context health and reviewable patch quality; it is not a general code-review or testing mode.
- Deeper test planning is a validation activity inside execute/review workflows, not a core lifecycle mode.

---

## Validation Semantics Rule

Validation lives in **multiple layers**. Context must preserve where each rule is enforced — never flatten everything into "required fields".

### Validation Layers

| Layer | Where | What it does | How to read in code |
|---|---|---|---|
| Handler / API | `internal/handler/*` (or routes) | Transport-level shape, format, range | Validators on request DTOs, OpenAPI/proto annotations |
| Service | `internal/service/*` (or use-cases) | Business validation, empty-checks, normalization | Functions like `sanitize<X>Input`, explicit `if x == "" return error` |
| Database | `migrations/*`, schema | `NOT NULL`, `CHECK`, `UNIQUE`, FK | SQL DDL + index definitions |
| Repository | `internal/repository/*` | Persistence-time fallback, defaults, transaction boundary | Code paths like `if x.IsZero() { x = now }` |
| Business intent | ADRs, product spec | Why a rule exists | Cross-reference between code and `.forge/context/06-business-rules-and-flows.md` |
| Inferred | active `.forge/context/*.md` entries labeled `inferred` | AI-derived guesses (still needs validation) | — |

### Mandatory Distinctions

When documenting a field constraint, the context must state:

1. **At which layer is it enforced?** (service / handler / DB / repository)
2. **What is the failure mode?** (returns error, demoted to default, DB-rejected)
3. **Is it consistent across layers?** (e.g. service-required + DB-NOT NULL = aligned; service-optional + DB-CHECK = different concerns)

### Anti-Pattern

```
❌ "required: user_id, channel, direction, transaction_time"
   (flattens 4 different validation realities into one false claim)

✅ Service-required (empty-check): user_id, channel
   DB-constrained (CHECK): direction (∈ debit|credit)
   Repository fallback: transaction_time (zero → now)
```

### Source-of-Truth Order

When validation evidence conflicts:
1. **Code** wins (service code, schema DDL, repository code).
2. **ADR** for intent ("why").
3. **Existing context** is least authoritative — corrected against #1 and #2.

If business intent is unclear (a field is DB-constrained but never service-validated, and no ADR explains why), record an unknown with priority `important`.
