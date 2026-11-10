---
id: specialty.mobile
title: "Specialty: Mobile"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [planner, executor, reviewer]
applies_when: layer mobile is active and the change touches iOS, Android, or cross-platform app code
---

# Specialty: Mobile

Overlay for `forge-orchestrate` workers. It adds focus and context to a role; it never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/mobile.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it.

## Load
- `.forge/context` layer `mobile` files.

## Focus
- Follow the app's navigation, state, and API client conventions.
- Consider offline, slow network, and app resume behavior.

## Review checklist
- No secrets or tokens stored in plain storage.
- Network failures show a recoverable state.
- Platform-specific code is isolated where the repo already isolates it.
