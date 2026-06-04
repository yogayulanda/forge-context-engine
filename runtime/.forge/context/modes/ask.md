---
id: mode.ask
title: "Mode: Ask"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-04
---

# Mode: Ask

## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/inferred.md`

## on_demand
- `knowledge/decisions/`, `knowledge/assumptions.md`, `knowledge/unknowns.md`
- Current code/docs/config only when the answer needs scoped verification

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
3000

## purpose
Answer developer questions using `.forge/context` first, with scoped code verification when needed.

## inputs
- Developer question.
- Relevant `.forge/context`.
- Scoped repository evidence when context is missing, stale, high-risk, or insufficient.

## behavior
- Load relevant context first and decide whether it is enough.
- Probe code/docs/config only when the question needs current evidence.
- Separate confirmed facts, inference, assumptions, and unknowns.
- Prefer current repository evidence when context or artifacts drift.
- Suggest the next mode only when useful.

## outputs
- Answer.
- Confirmed Facts.
- Inference.
- Assumptions.
- Unknowns / Ambiguity.
- Evidence.
- Verification Needed.
- Suggested Next Mode.

## status values
- `answered`
- `needs_more_evidence`
- `context_stale`
- `blocked_by_ambiguity`

## boundaries
- Do not create a plan, ECP, lifecycle artifact, or code change.
- Do not redesign, run broad audits, or broad-load `.forge/context`.
- Do not claim implementation details without evidence.

## next mode transitions
- Use `plan` when the answer turns into change intent.
- Use `verify-context` when stale context affects the answer.
- Use `review` only when the user asks to inspect an executed result.
