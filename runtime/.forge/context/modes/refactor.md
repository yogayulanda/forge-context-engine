---
id: mode.refactor
title: "Mode: Refactor"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---
# Mode: Refactor
## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
## on_demand
- `knowledge/inferred.md`, `knowledge/assumptions.md`, `generated/<relevant>`
- Tests, coverage, contracts, and call sites needed to prove behavior preservation
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
7000
## notes
- Improve technical debt conservatively within a bounded scope while preserving behavior.
- When persistence helps continuity, write or reference a Refactor Artifact with problem areas, safe improvements, risk areas, out-of-scope redesigns, and execution boundaries.
- Prefer local simplification, duplication removal, naming cleanup, and structure alignment already supported by repo conventions.
- Use natural engineering names and explicit flow; remove abstraction only when it reduces real complexity or restores repository-native style.
- Classify refactor risk as `LOW`, `MEDIUM`, or `HIGH`; prioritize LOW-risk behavior-preserving improvements and require a planning/implementation path for HIGH risk.
- Do not perform architecture rewrites, paradigm migrations, hidden behavior changes, or unrelated cleanup.
- Do not replace one local style with a new competing style unless the approved refactor explicitly calls for it.
- Identify behavior-preservation evidence and required tests before or during changes.
- Report drift when context/artifacts describe debt or behavior that current code no longer supports; current code evidence wins.
- Use `CONTEXT_BUDGET_LIMITED` if safe refactor classification needs more call-site/contract/test evidence than the normal budget; name the missing evidence and affected behavior-preservation claim.
- Do not assume external repo contracts or modify multiple repos as part of refactor.
- For fintech-sensitive code, treat financial correctness, transaction consistency, idempotency, retry/replay, rollback, auditability, observability, and blast radius as governance risks; payment correctness is never LOW risk.
- Ask or stop before broad, risky, destructive, contract-changing, or runtime-impacting refactors.
- Report `Yang dirapikan`, changed files grouped by responsibility, behavior-preservation checks, validation run or skipped, risks, and rollback.
- Keep output operational and avoid architecture-heavy justification unless the refactor needs it.
