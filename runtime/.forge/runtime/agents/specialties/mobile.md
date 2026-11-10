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

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/mobile.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. Put team-specific rules (libraries, error shapes, naming, test commands) in the copy, not here.

## Load
- `.forge/context` layer `mobile` files.
- The nearest existing screen with similar navigation and data flow.
- The API client and local storage modules used by that screen.

## As planner
- Name the screen(s), navigation entry and exit, and the state they own.
- Cover offline, slow network, app backgrounded and resumed, and session expiry.
- Flag minimum OS/app version impact and any native permission change (camera, location, notifications).
- Flag any backend contract dependency and whether old app versions must keep working.

## As executor
- Follow the app's existing navigation, state management, and API client patterns.
- Show a recoverable state for network failure; do not block the UI thread with network or disk work.
- Store tokens and sensitive values only in the platform's secure storage.
- Keep platform-specific code where the repo already isolates it.
- Add or update tests for the new logic and the failure state.

## As reviewer
- Offline and slow-network behavior is handled and recoverable.
- No secrets, tokens, or PII in plain storage or logs.
- Backward compatibility: older app versions are not broken by the change.
- No new permission without a stated reason in the SDD.
