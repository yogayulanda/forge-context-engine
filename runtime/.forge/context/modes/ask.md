---
id: mode.ask
title: "Mode: Ask"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---

# Mode: Ask
## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/inferred.md`
## on_demand
- `knowledge/decisions/`, `knowledge/assumptions.md`, `knowledge/unknowns.md`
- Contracts/events/data/UI/runtime context only when needed to answer the question
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
3000
## notes
- Answer lightweight questions about current code, flow, ownership, dependencies, behavior, and loaded Forge context.
- Do not create lifecycle artifacts by default; reference existing artifacts only when directly relevant to the question.
- Keep answers evidence-based; separate confirmed facts, inference, assumptions, and unknowns.
- Do not create ECPs, task breakdowns, code changes, redesigns, or broad audits.
- Load only the minimum task-relevant context needed to answer; use on-demand context for specific edges only.
- Prefer direct repository evidence over broad Forge context; report `CONTEXT_BUDGET_LIMITED` when safe answering needs evidence beyond the normal scoped budget, naming the missing evidence and safe answer boundary.
- If loaded context or artifacts conflict with current repository evidence, report `DRIFT_DETECTED` or `DRIFT_RISK` and prefer current evidence.
- For referenced external/shared repos, state only evidenced ownership or contract facts; label unevidenced cross-repo behavior as unknown.
- Use short, scannable answers. Avoid runtime/mode internals unless they change the answer.
- If context loading matters, say `Scoped context loaded` and list only the relevant areas.
- Surface missing evidence and unresolved ambiguity in practical language.
