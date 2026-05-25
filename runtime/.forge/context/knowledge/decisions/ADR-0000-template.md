---
id: knowledge.decision.adr-0000-template
title: ADR-0000 Template
type: knowledge
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-20
---

# ADR-0000: Template

> Template file. **Do not edit as a real decision.** Copy to `ADR-NNNN-title.md` when creating a new ADR.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | ADR format definition |
| AI writable | May **propose** new ADR as draft `status: proposed`; promotion to `accepted` requires human |
| Human confirmation | Required for all ADRs. `accepted` ADRs are immutable. |
| Append-only | Superseded ADRs marked `superseded`, never deleted |

## Front-Matter Schema

```yaml
---
id: knowledge.decision.adr-NNNN
title: ADR-NNNN — <title>
type: knowledge
status: proposed | accepted | superseded | deprecated
source: human
evidence:
  - { type: code|doc|adr|human|external, ref: <path|url> }
owner: <team>
updated: YYYY-MM-DD
---
```

## Body Structure

```markdown
# ADR-NNNN: <title>

- **Status:** proposed|accepted|superseded|deprecated
- **Date:** YYYY-MM-DD
- **Decision makers:** <name/team>

## Context
What is faced & why a decision is needed.

## Decision
The choice made — assertive statement.

## Alternatives
Options considered & reasons for rejection.

## Consequences
Positive, negative, and trade-off implications.

## Evidence
Concrete references: code, docs, other ADRs, external sources.
```
