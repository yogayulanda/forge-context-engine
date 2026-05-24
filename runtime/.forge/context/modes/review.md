---
id: mode.review
title: "Mode: Review"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-24
---

# Mode: Review
## include
- `layers/<related>`
- `knowledge/decisions/`
## on_demand
- `systems/<related>`
- `knowledge/inferred.md`
- `knowledge/assumptions.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
6000
## notes
- Review correctness, regressions, risks, and consistency against evidence, decisions, and task-scoped context.
- Verify execute results against approved tasks, architecture/runtime consistency, and reported validation evidence.
- Do not replace testing mode; reference test evidence when assessing regression risk and coverage gaps.
- Check topology, runtime behavior, data flow, contracts, and layer/system boundaries only when relevant evidence is loaded.
- Lead with evidence-based critique; keep unevidenced concerns as uncertainty, not confirmed defects.
- Identify unconfirmed proposed defaults and flag any accidental promotion of proposed assumptions into confirmed behavior.
- Treat raw secret exposure in diffs, reports, generated context, or comments as a security finding requiring redaction.
- Report reviewed areas, loaded context, missing evidence or ambiguity, risk severity, and whether review mode was sufficient.
