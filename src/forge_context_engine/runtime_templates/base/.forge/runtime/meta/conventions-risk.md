---
id: meta.conventions-risk
title: Risk, Governance & Secret Safety Conventions
type: meta
status: confirmed
confidence: high
source: human
evidence:
  - { type: doc, ref: ../../../../specs/mode-invocation.md }
  - { type: doc, ref: ../../../FORGE-CONTEXT-ARCHITECTURE.md }
owner: forge-context-engine
updated: 2026-06-03
---

# Risk, Governance & Secret Safety Conventions

Load this file when the task involves risk classification, governance checks, approval-sensitive decisions, safety boundaries, or secret handling.

---

## Intelligence & Governance Semantics

### Cognition Drift

Forge must detect and report drift when stale assumptions, outdated decisions, context contradicting code, artifacts contradicting repository evidence, or generated artifacts older than code reality affect the task.

- Prefer current code, repository docs, ADRs, and human confirmations over generated artifacts and inferred context.
- Do not silently trust stale artifacts, stale context, or old generated output.
- Use `DRIFT_DETECTED`, `DRIFT_RISK`, or `NO_DRIFT_FOUND` when drift materially affects the answer, plan, implementation, execute, review, or context verification.
- Keep drift wording operational, not alarming: state the mismatch, newer evidence, and affected decision.
- Mark stale artifacts as stale, partial, or superseded; do not let them override repository evidence.

### Cross-Repo Awareness

Forge may identify referenced external or shared repositories and report dependency, ownership, or contract uncertainty.

- Compare cross-repo contracts only when evidence from both sides is available.
- Do not assume another repository's behavior, runtime topology, release state, or ownership from references alone.
- Do not modify multiple repositories automatically.
- Do not introduce cross-repo orchestration, shared runtime assumptions, deploy workflows, or autonomous synchronization.

### Fintech-Grade Governance Checks

Governance checks are concise risk signals, not bureaucracy.

Relevant modes should surface risk in these areas when the task touches them: PII/sensitive data, secrets/credentials, financial correctness, idempotency, retry safety, replay safety, rollback safety, transaction consistency, auditability, observability, and blast radius.

- HIGH-risk governance decisions require human approval.
- Never log, persist, or quote raw secrets or raw PII.
- Never classify payment, balance, ledger, settlement, reconciliation, or transaction correctness as LOW risk.
- Governance output must be operational, evidence-based, and concise: risk, evidence, impact, required decision or next check.
- Avoid generic security/compliance checklists, audit essays, and bureaucratic language.

### Decision Risk Levels

| Risk | Meaning | Runtime behavior |
|---|---|---|
| `LOW` | Reversible, local, no contract/security/data correctness impact. | AI may continue with a proposed default. |
| `MEDIUM` | Operational behavior, config, or runtime behavior. | Orchestrator may choose only when configured; otherwise needs confirmation. |
| `HIGH` | Security/compliance, PII/secrets, financial correctness, destructive migration, production topology, contract authority, or rollback-risky change. | Requires human confirmation; automation stops with `NEEDS_HUMAN_APPROVAL`. |

---

## Secret Safety

Forge must never print, copy, summarize, or expose raw secrets discovered during init, audit, plan, implementation, execute, review, verify-context, migration, or platform discovery.

Sensitive values include API keys, access tokens, refresh tokens, passwords, private keys, JWTs, session cookies, webhook secrets, database URLs with credentials, Kafka/SASL credentials, cloud credentials, and OAuth client secrets.

When a secret is detected:

- Redact the raw value before output or context write.
- Report only secret type, file path, line/reference when available, and safe masked preview such as `<REDACTED_SECRET>`, `<REDACTED_PRIVATE_KEY>`, or `****a91f`.
- Do not copy the raw value into `.forge/context`, `.forge/context-patches/`, `.forge/generated/`, decisions, modes, reports, validation-cases, or platform context.
- Classify it as a security finding.
- Recommend rotation if the secret may have been committed, logged, displayed, copied, or otherwise exposed.
- Preserve enough evidence for remediation without revealing the value.
