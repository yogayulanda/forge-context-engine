# AI Readiness Roadmap Example

Use Forge ai-readiness mode on this repo and save the remediation roadmap.
Keep the roadmap practical, grouped by time horizon, and optimized for AI-readiness gain per effort.

Expected compact output shape:

```md
# AI Readiness Remediation Roadmap

## Immediate

### 1. Resolve contract ownership ambiguity
- Priority: P0
- Outcome: AI can stop guessing which repository owns the shared boundary
- Target Area: `.forge/context/systems/<service>/system.md`
- Why It Improves AI Readiness: removes a high-impact ambiguity that blocks trustworthy architecture and interface guidance
- Suggested Action: confirm owner authority and add a reviewable context patch with evidence
- Dependencies: human answer to `AR-Q1`
- Effort: 30-60 minutes after confirmation

### 2. Strengthen repo-map entrypoints
- Priority: P1
- Outcome: AI can navigate the request flow and integration surfaces faster
- Target Area: `.forge/context/repo-map/overview.md`
- Why It Improves AI Readiness: reduces token waste during repository discovery
- Suggested Action: add entrypoints, key flows, and boundary paths supported by current repo evidence
- Dependencies: none
- Effort: 1-2 hours

## Near Term

### 3. Expand system-level context for service boundaries
- Priority: P1
- Outcome: AI has stronger guidance for multi-file service changes
- Target Area: `.forge/context/systems/<service>/system.md`
- Why It Improves AI Readiness: makes ownership, dependencies, and responsibilities explicit
- Suggested Action: add interface summary, dependency notes, and non-goals for the service boundary
- Dependencies: ownership confirmation
- Effort: 2-4 hours

### 4. Document critical validation expectations
- Priority: P2
- Outcome: AI can recommend safer validation for risky edits
- Target Area: `.forge/context/01-core/constraints.md` or `knowledge/decisions/`
- Why It Improves AI Readiness: improves validation honesty and edit safety
- Suggested Action: record required validation commands and manual checks for high-risk paths
- Dependencies: current validation entrypoints must be verified
- Effort: 1-3 hours

## Medium Term

### 5. Add durable context for public interfaces and contract surfaces
- Priority: P2
- Outcome: AI can reason about external boundaries with less ambiguity
- Target Area: `systems/`, `repo-map/`, and `knowledge/decisions/`
- Why It Improves AI Readiness: reduces repeated rediscovery across sessions and tools
- Suggested Action: capture only stable, evidence-backed interface summaries and ownership decisions
- Dependencies: validated service ownership and boundary evidence
- Effort: 0.5-1 day
```
