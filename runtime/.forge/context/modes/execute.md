---
id: mode.execute
title: "Mode: Execute"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---
# Mode: Execute
## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`
## on_demand
- Approved implementation task list or ECP/phases
- `knowledge/assumptions.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
8000
## notes
- Implement only approved tasks or approved task subsets using scoped execution context; preserve repository conventions, nearby code style, natural operational names, and proposed vs confirmed boundaries.
- When persistence helps continuity, write or reference an Execute Result Artifact with result, changed file groups, validation status, manual follow-up, rollback notes, and unchanged boundaries.
- Do not redesign architecture, invent topology/contracts, broad-load unrelated context, silently redefine approved plans, introduce competing paradigms, or mass-refactor unrelated code.
- Ask before dangerous/destructive/runtime-impacting changes; in non-interactive repos stop safely, run narrow verification when relevant, and never copy raw secrets into code/context.
- If execution needs more/fresher scoped evidence, stop or narrow scope with `CONTEXT_BUDGET_LIMITED`, `DRIFT_DETECTED`, or `DRIFT_RISK`; never assume external repo behavior or modify multiple repos automatically.
- Treat governance risks operationally: never auto-approve HIGH-risk PII/secrets, financial correctness, transaction consistency, idempotency, retry/replay, rollback, or blast-radius changes; payment correctness is never LOW risk.
- Execute report order: `Execution Result`, `Yang berhasil diubah`, `File yang berubah`, `Validasi`, `Yang belum tervalidasi`, `Yang masih perlu dicek manual`, `Cara rollback perubahan ini`, `Yang sengaja tidak diubah`, `Reviewer perlu fokus ke`, `Hidden change check`.
- `Execution Result` must use one clear status: `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_VALIDATED`; `SUCCESS` requires reliable validation evidence.
- Before validation, check prerequisites; report missing tooling/infra as `BLOCKED_BY_ENVIRONMENT`, contract/runtime/approval blockers as `BLOCKED`, and changed code without validation as `NOT_VALIDATED`.
- `File yang berubah` must group files by responsibility: Runtime / Bootstrap, Adapter / Handler, Service / Domain, Persistence, Config / Docs, and Tests; omit empty groups.
- `Validasi` must separate prerequisites checked, executed checks, failures, and checks that could not run; `Yang belum tervalidasi` lists changed or risky scope without reliable validation evidence.
- `Yang masih perlu dicek manual` is operational; rollback and reviewer focus use concrete risks such as disable flag, replay, idempotency, retry vs DLQ, lifecycle/shutdown, secret-safe logging, and boundary preservation.
- `Hidden change check` reports no unexpected database schema, deployment pipeline, shared runtime contract, or unrelated context/runtime changes; keep runtime/bootstrap/loading details quiet unless debug detail affects the result.
