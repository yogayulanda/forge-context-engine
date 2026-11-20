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

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/frontend.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. Put team-specific rules (libraries, error shapes, naming, test commands) in the copy, not here.

## Load
- `.forge/context` layer `frontend` files.
- The nearest existing page or component that does something similar, as the pattern to copy.
- The API client module and types for any endpoint the change calls.

## As planner
- Name the route/page, the components touched, and the state they own.
- List every UI state: loading, empty, error, success, and permission-denied when relevant.
- List the API calls and the fields used; flag any backend contract dependency as cross-repo work.
- Acceptance criteria are observable in the browser (what the user sees or can do).

## As executor
- Reuse existing components and design tokens before creating new ones.
- Keep data fetching in the repo's existing client/hooks layer; components receive data and callbacks.
- Implement all listed UI states; never leave a spinner without an error branch.
- Keep forms validated on the client and still handle server validation errors.
- No hard-coded API URLs, feature flags, or secrets; use the repo's config mechanism.
- Add or update component tests for each UI state the change adds.

## As reviewer
- Every listed UI state renders and is reachable.
- No direct API calls from presentational components.
- Accessibility basics: labels on inputs, keyboard focus order, sufficient contrast.
- No sensitive data stored in local storage or exposed in URLs.
- Bundle impact: no large new dependency without a stated reason.
