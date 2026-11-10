---
id: specialty.frontend
title: "Specialty: Frontend"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [planner, executor, reviewer]
applies_when: layer frontend is active and the change touches web UI code
---

# Specialty: Frontend

Overlay for `forge-orchestrate` workers. It adds focus and context to a role; it never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/frontend.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it.

## Load
- `.forge/context` layer `frontend` files.

## Focus
- Reuse existing components, state management, and styling conventions.
- Keep API calls behind the repo's existing client layer.

## Review checklist
- Loading, empty, and error states exist for new views.
- No hard-coded API URLs or secrets in client code.
- Accessibility basics: labels, keyboard focus, contrast.
