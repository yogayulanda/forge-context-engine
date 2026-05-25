---
id: mode.incident
title: "Mode: Incident"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---

# Mode: Incident
## include
- `layers/<related>`
- `systems/<affected>`
- `knowledge/inferred.md`
## on_demand
- `knowledge/decisions/`, `knowledge/assumptions.md`, `knowledge/unknowns.md`
- Logs, traces, metrics, configs, recent changes, contracts, migrations, and runbooks when relevant
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
6000
## notes
- Diagnose bugs, issues, and incidents from evidence; identify symptom, impact, affected flow, likely root cause, mitigation, rollback, and next checks.
- When persistence helps continuity, write or reference an Incident Artifact with summary, likely root cause, affected systems, mitigation, rollback possibility, and next checks.
- Distinguish symptom from cause. Use `LIKELY_CAUSE` only with direct supporting evidence, `POSSIBLE_CAUSE` for plausible hypotheses, and `NEEDS_MORE_EVIDENCE` when cause cannot be safely stated.
- Include confidence level for cause and mitigation statements.
- Preserve uncertainty: label confirmed evidence, hypotheses, unknowns, and proposed mitigations separately.
- Check for cognition drift when old context, runbooks, incident artifacts, or assumptions contradict current code/config evidence.
- Use `CONTEXT_BUDGET_LIMITED` if diagnosis needs more scoped evidence than the normal budget; name missing evidence, affected diagnosis/mitigation, and targeted expansion. Do not broad-load unrelated context by default.
- For cross-repo dependencies, state external ownership/contract uncertainty and avoid claiming another repo's behavior without evidence.
- For fintech incidents, surface PII/secrets, financial correctness, idempotency, retry/replay, rollback, transaction consistency, auditability, observability, and blast-radius risks; never claim root cause without evidence.
- Do not redesign architecture, invent topology, or make speculative migrations as part of diagnosis.
- If execution is needed, hand off bounded remediation to execute mode after approval.
- Redact secrets from logs/configs and report security exposure only as masked findings.
- Report `Gejala`, `Dampak`, `Kemungkinan penyebab`, `Mitigasi`, `Rollback`, `Next checks`, and missing evidence.
- Keep context-loading details terse; focus on what the operator should do next.
