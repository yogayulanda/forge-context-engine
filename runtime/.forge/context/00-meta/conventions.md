---
id: meta.conventions
title: Conventions & AI Operational Contract
type: meta
status: confirmed
confidence: high
source: human
evidence:
  - { type: doc, ref: ../../../FORGE-CONTEXT-ARCHITECTURE.md }
  - { type: doc, ref: ../../../../specs/artifact-lifecycle.md }
owner: forge-context-engine
updated: 2026-06-05
---

# Context System Conventions

Rules for **managing the context system itself**. Not product engineering principles (→ `01-core/principles.md`).

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Normative. Load when task behavior, policy, or reporting rules need it. |
| AI writable | No |
| Human confirmation | Required for any change |
| Populated | Final in runtime; minor adaptation during target repo init |

---

## Scoped Convention Files

Load the relevant scoped file when a task specializes in that area. Do not load all scoped files for every task.

| File | Load when |
|---|---|
| `conventions-evidence.md` | Evidence requirements, source citation, context consistency, drift, implicit constraint extraction, table role classification |
| `conventions-validation.md` | Validation reporting, testing expectations, review evidence, prerequisite checks, missing validation behavior |
| `conventions-risk.md` | Risk classification, governance checks, approval-sensitive decisions, safety boundaries, secret handling |
| `conventions-language.md` | Language consistency, Indonesian/English usage, naming guidance, tone, reference stability |

---

## Naming & IDs

- Files: `kebab-case.md`
- ID format: `<zone>.<name>` (e.g. `system.payment-service`, `layer.backend`)
- ADR: `ADR-NNNN-title.md`, append-only

## Front-Matter Schema (Required on Every Context File)

```yaml
---
id: <zone>.<name>
title: <human-readable title>
type: meta|core|layer|system|knowledge|mode|generated
system_type: service|app|worker|library|infra-module|platform-component  # type=system only
status: confirmed|inferred|assumption|unknown|deprecated
confidence: high|medium|low
source: human|ai|hybrid
evidence:
  - { type: code|doc|adr|human|external, ref: <path|url> }
owner: <team-or-ref>
updated: YYYY-MM-DD
review_by: YYYY-MM-DD  # optional
---
```

## Status Vocabulary

| Status | Meaning | Authoritative |
|---|---|---|
| `confirmed` | Verified; safe as decision basis | Yes |
| `inferred` | AI-derived with evidence; non-authoritative | No |
| `assumption` | Temporary; not a final decision basis | No |
| `unknown` | Acknowledged gap; **guessing forbidden** | — |
| `deprecated` | No longer applies; not loaded | — |

## Core Loading Baseline

Start from `.forge/adapter.md`, then the requested mode or relevant compatibility/scenario guidance. Load only the relevant `00-meta/*` and `01-core/*` entries needed to execute that request safely. Modes **never** re-list core — delta only.

## Scoped Loading Semantics

Context loading is relevance-first, evidence-first, and bounded by task scope.

- Prefer direct repository evidence over broad context scans.
- Start with the requested mode contract and smallest relevant code surface before expanding into more context files.
- Do not load the entire `.forge/context` tree by default.
- Do not load every mode file by default.
- Do not load compatibility/scenario files unless the request or evidence makes them relevant.
- Load `include` entries only when relevant to the task; load `on_demand` entries only when they answer a concrete evidence need.
- Expand context only with a clear reason, such as contract ambiguity, ownership uncertainty, drift risk, cross-repo reference, incident blast-radius check, or governance risk.
- If a small plan can be grounded with one or two files plus the mode contract, stop there.
- If required evidence is outside the normal scoped budget, report `CONTEXT_BUDGET_LIMITED` and explain what evidence is missing or why expansion is needed.
- `token_budget` is a target operating range for concise work, not a blind hard cap. Exceeding normal scoped budget is allowed only when safe reasoning requires more evidence.
- Even under `CONTEXT_BUDGET_LIMITED`, broad-load-everything remains forbidden.

## Mode File Schema

Every `modes/*.md` file MUST expose exactly these Markdown sections after the title, in this order:

| Section | Meaning |
|---|---|
| `## include` | Context components normally loaded for this mode. |
| `## on_demand` | Context components loaded only when relevant. |
| `## exclude` | Context components never loaded by default. |
| `## token_budget` | Numeric target scoped context budget for this mode. |
| `## notes` | Concise mode-specific execution and reporting guidance. |

`token_budget` MUST contain only a decimal integer such as `4000`, `8000`, or `12000`; labels such as `medium` or `medium-high` are invalid. Treat the number as an operating range for scoped loading, not a blind cap.

Mode files are machine-resolvable context loading deltas and the authority for mode-specific execution behavior. They MUST NOT re-list `00-meta/*` or `01-core/*` unless explicitly needed, contain domain knowledge, or duplicate `conventions.md`.

## Mode Invocation

- Modes are loading deltas on top of always-loaded core.
- Read `.forge/forge.config.yaml` before mode execution and apply `run.interaction`.
- Mode files are authoritative for mode-specific execution behavior.
- Visible core modes are limited to `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context`.
- `init` owns confirmed repo context/config creation; `ask` owns evidence-aware understanding; `plan` owns Quick Plan or SDD; `implementation` owns ECP generation; `execute` owns approved ECP application; `review` owns executed-result review; `verify-context` owns context health/freshness only.
- Keep mode responsibilities distinct: ask does not plan or mutate; plan does not emit executable patches; implementation does not modify code; execute does not redesign; review does not modify code by default; verify-context does not validate plan/ECP/code/MR readiness.
- Test placement is convention-sensitive; validation is handled inside execute/review or as a workflow activity, not as a core lifecycle mode.
- Start from `.forge/adapter.md`, then load only the requested mode contract; bring in `conventions.md` and scoped convention files only when the task needs their rules.
- Load only context required by the task; do not broad-load `.forge/context` by default.
- Preserve evidence, inference, and unknown boundaries.
- In normal interactive output, keep loading details quiet. A short `Scoped context loaded` line is enough when helpful.
- Always surface blockers, missing evidence, unresolved ambiguity, validation limits, risks, and rollback according to the selected mode.
- When context is insufficient, use `CONTEXT_BUDGET_LIMITED` with missing evidence, affected conclusion/action, targeted expansion needed, and safe fallback if one exists.
- Runtime-managed cognition lives under `.forge/context`; repository-owned cognition remains in application code, repository docs, ADRs, and human confirmations.

## Adapter Boundary

Tool adapters such as `CLAUDE.md`, `AGENTS.md`, and `adapters/<tool>/` are invocation bridges only. They may point to Forge config, conventions, manifest, modes, commands, and specs, but they must not duplicate repository cognition, lifecycle semantics, validation/drift semantics, artifact semantics, governance rules, runtime flags, or secret-handling policy.

## Runtime Validation Semantics

See `conventions-validation.md` for full validation status vocabulary, prerequisite checks, and section structure.

Summary: Validation reporting must never imply success without evidence. Execute performs scoped validation for changed work; review checks validation evidence and gaps. Deeper test strategy is a validation activity rather than a core lifecycle mode.

## Artifact Lifecycle Semantics

See `specs/artifact-lifecycle.md` for the full artifact specification.

Summary: Lifecycle artifacts are optional, human-readable continuity helpers under `.forge/generated/` when persisted. Default behavior is chat output first; save Markdown artifacts only when requested, approved for continuity, or clearly useful for multi-session/multi-agent continuation. Generated artifacts do not replace repository code, docs, ADRs, or human confirmations. Context promotion goes through reviewed `.forge/context-patches/`, not direct writes into `.forge/context`. Artifact links are trace references only — not dependency graphs, workflow state, DAGs, orchestration, execution triggers, or agent memory.

## Context Quality Contract

`.forge/context` is the curated source of truth for durable repository cognition.

Good curated context is:
- Stable beyond the current task or chat session
- Repository-specific
- Evidence-backed
- Compact and non-redundant
- Useful for future AI or human work in this repository
- Durable enough to survive one-off execution details
- Clear about `confirmed` vs `inferred` vs `assumption` vs `unknown`
- Scoped to repository/project knowledge rather than temporary execution traces

Do not put these in `.forge/context`:
- Raw terminal logs
- Full execution reports
- One-off Quick Plans
- Temporary ECPs
- Long review reports
- Speculative ideas without evidence
- Duplicate notes already captured in better context or source documents
- Stale details without current evidence
- Generic AI advice not specific to this repository
- Scratchpad or implementation working notes

Path boundary:
- `.forge/context` holds curated durable context only.
- `.forge/generated/...` holds working artifacts when requested or approved.
- `.forge/context-patches/...` holds proposed durable context updates pending review.
- A generated artifact is not automatically context.
- A context patch is a proposal, not automatically accepted context.

Context Quality Checklist:
- Is this stable beyond the current task?
- Is it repository-specific?
- Is there current evidence?
- Will future work benefit from it?
- Is it compact enough?
- Does it belong in `.forge/context` rather than `.forge/generated/...`?
- Is it replacing or duplicating existing context?
- Does it require review before promotion?

Context maintenance cadence:
- `Context Impact Check` is a small per-task review check.
- `Context Quality Audit` is a larger milestone/release/manual check for stale, noisy, missing, or low-quality context.
- Do not turn every task into a full context quality audit.

`review` should use a structured `Context Impact` section to determine whether a durable context update is needed. When an update is needed, propose a reviewable `.forge/context-patches/...` patch instead of mutating `.forge/context` directly. `verify-context` may validate curated context health and reviewable patch quality, but it must not accept patches automatically.

When artifact persistence is mentioned in mode output or docs, keep it concise. Prefer wording such as:
- `Artifact Persistence: Not saved by default.`
- `Save to .forge/generated/... only when requested or approved.`

## Intelligence & Governance Semantics

See `conventions-risk.md` for full governance, drift, cross-repo awareness, and secret safety rules.

Summary: HIGH-risk decisions require human approval. Raw secrets and raw PII must never be logged, persisted, or quoted. Governance output is operational risk signals, not checklists.

## Runtime Interaction Behavior

Forge uses `run.interaction` as the controlling interaction setting.

| Value | Behavior |
|---|---|
| `manual` | Default interactive behavior. Ask concise clarification questions for blocking decisions; continue after human confirmation. |
| `auto` | Automation-safe behavior. Do not ask conversational questions; emit structured required decisions and blocking statuses. |

Important decisions are governed by policy, not by an active decision-authority config knob. Domain rule, data mutation, architecture boundary, external contract, security boundary, and migration changes require human confirmation.

## Language Output Policy

- Human-facing narration, progress updates, and explanations follow `ui.language`.
- Copyable/project artifacts remain English by default unless the user explicitly requests another language.
- English-by-default project artifacts include Plans, ECPs, Execute Reports, Review Reports, task cards, specs, validation commands, commit messages, and generated Markdown artifact contents.
- Do not translate commands, file paths, config keys, status enums, or code identifiers.

## Unknown Decision Semantics

| Classification | Meaning | Runtime behavior |
|---|---|---|
| `blocking` | Cannot safely continue without an authoritative decision | Interactive: ask the minimum decision question. Automation: emit the selected mode's allowed blocking/readiness status. |
| `proposed-default` | Low-risk, conventional, reversible, non-authoritative operational choice | AI may continue, but must label the value `proposed`, `not confirmed`. |
| `informational` | Useful uncertainty that does not affect safe continuation | Record only; do not interrupt workflow. |

Proposed defaults never become confirmed facts without human confirmation.

## AI Operational Contract (Normative)

1. AI does not self-promote status — **propose only**.
2. AI does not present `inferred`/`assumption` as fact.
3. On encountering `unknown`, AI classifies it as `blocking`, `proposed-default`, or `informational`; guessing confirmed facts is forbidden.
4. New inferences go to `knowledge/inferred.md` or `generated/`, never to `source: human` files.
5. Without `evidence`, max status is `assumption`.
6. AI does not fabricate architecture, APIs, services, databases, integrations, ownership, or business rules.
7. Treat legacy AI artifacts (`.ai/`, `.claude/`, `AGENTS.md`, etc.) as **reference**, not source-of-truth. Repo code wins on conflict.
8. Tag every `unknowns.md` entry with classification: `blocking` / `proposed-default` / `informational`.
9. Use `owner: unresolved` (not `TBD`) when owner is undetermined; create one root unknown `U-OWN`.
10. **Evidence Consistency** — before finalizing context, cross-check critical claims against repo evidence. If repo shows N items, context must say N — not approximate. See `conventions-evidence.md`.
11. **Drift Detection** — when repo evidence changes after context was written, mark affected entries as stale, refresh from current code, log unresolved ambiguity in `unknowns.md`. See `conventions-evidence.md`.
12. **No Phantom ADRs** — never list `ADR-NNNN` in `architecture.md` unless the file actually exists. Planned ADRs go to `assumptions.md` or `unknowns.md`.
13. **Implicit Constraint Extraction** — during init, scan code for implicit constraints. See `conventions-evidence.md` for extraction table and routing.
14. **Internal Table Hygiene** — markdown table cells follow the same conventions as front-matter. Owner cells use `unresolved`, never `TBD`. Status/classification cells use the canonical vocabulary.
15. **Secret Safety** — raw secrets are never displayed, copied, summarized, or stored. See `conventions-risk.md`.
16. **Automation Safety** — automation-safe behavior never asks conversational questions, never auto-approves HIGH-risk decisions, and never treats decision traces as orchestration state.
17. **Scoped Intelligence Safety** — `CONTEXT_BUDGET_LIMITED`, drift statuses, cross-repo awareness, incident/refactor intelligence, and governance signals are semantic reporting tools only; they do not add RAG, vector search, knowledge graphs, agents, orchestration, schedulers, CI/CD, deploy behavior, runtime executors, or autonomous loops.

## Confidence Calibration

Default confidence for `source: ai` + `status: inferred` is `medium`.

Use `confidence: high` only when the claim is directly and deterministically verifiable from repository evidence. Never use `high` merely because the reasoning feels plausible.

| Claim type | Confidence |
|---|---|
| Direct code evidence, e.g. module name declared in `go.mod` | `high` allowed |
| Inferred architecture intent from docs/code pattern | `medium` |
| Ownership inferred from absence of `CODEOWNERS` | `unknown`, not `high` |
| Deployment ownership not found in repo | `unknown` or `medium`, not `high` |

## Status Promotion

```
assumption ──(evidence)──► inferred ──(human confirmation)──► confirmed
```

Promotion to `confirmed` requires entry in `knowledge/confirmations.md`.

## Lifecycle & Staleness

| Zone | Lifecycle |
|---|---|
| `temp/*` | Single session → deleted (gitignored, never authoritative) |
| `generated/*` | Until regenerated → overwritten. Commit only if stable & useful. Never source-of-truth. |
| `inferred`/`assumption`/`unknown` | Until resolved |
| `core`/`layer`/`system` | Maintained → `deprecated` |
| ADR | Permanent → `superseded`, never deleted |

- `updated` exceeding `governance.staleness_days` → triggers re-review.
- Code change at `evidence` path demotes `confirmed` → `inferred`.

## Anti-Duplication

- One fact, one home.
- Shared context referenced via `id`, **never copied**.
- `systems/*` does not copy `01-core/` or `layers/*` standards.
- `modes/*` does not list `00-meta/*` or `01-core/*`.
- Domain/scope facts live in `01-core/product.md`. `systems/<name>/system.md` references — does not re-list — them.
- When the same list appears in two files, the file closer to the canonical home keeps it; the other becomes a reference by `id`.

## Ownership Rule

| Situation | Action |
|---|---|
| Owner known at init | Set on every file as the canonical team/individual reference |
| Owner unknown at init | Use `owner: unresolved` and create **one** unknown entry (`U-OWN`) in `knowledge/unknowns.md` |
| Multiple ownership | Use a short ref token (e.g. `team.payments`) and define it once in `glossary.md` |

`owner: TBD` is deprecated. Use `unresolved` (single root unknown) or a real ref.

## Layer Activation Rule

A layer is **activated** only when concrete evidence exists in the target repo.

| Layer | Evidence Required | Not Sufficient on Its Own |
|---|---|---|
| `backend` | Application code (server, API, business logic) | — |
| `frontend` | UI/web client code | — |
| `mobile` | iOS/Android/cross-platform code | — |
| `infrastructure` | Terraform/Helm/K8s manifests, CI/CD deployment logic, deployment scripts, environment provisioning | DB migrations, build tooling, env vars, local Dockerfile, local config |
| `testing` | Test files or test runner configuration | — |

DB migrations, Makefile build targets, `.env.example`, local Dockerfiles do **not** justify activating the infrastructure layer. Activate `infrastructure` only when the repo demonstrably owns deployment or environment provisioning.

Activation outcomes:
- **Strong evidence** → activate, `confidence: high`.
- **Weak/partial evidence** → activate with `confidence: medium/low` + add unknown entries.
- **Evidence absent** → remove the layer folder; remove from `forge.config.yaml` → `layers_enabled`.

## README vs Layer Content Policy

| File | Role | Content |
|---|---|---|
| `layers/<x>/README.md` | Entrypoint & TOC | Purpose statement, navigation links, growth path. Stays lightweight. |
| `layers/<x>/<x>.md` (and sub-files) | Engineering knowledge | Conventions, patterns, tech stack, layer-specific rules. Real layer content. |

README must NOT duplicate `<x>.md` content. If `<x>.md` exists, README becomes a one-paragraph pointer + table of files.

## Legacy AI Artifact Handling

When initializing on a repo that already has AI/context artifacts (`.ai/`, `.claude/`, `.cursor/`, `AGENTS.md`, ad-hoc docs):

- Treat legacy artifacts as **reference**, not source of truth.
- Repository code always wins on conflict.
- Conflicts go to `knowledge/unknowns.md`.
- Useful legacy content is re-expressed in correct zones with proper `status` + `evidence`.
- Never copy legacy content verbatim into `01-core/`/`layers/`/`systems/` without re-validating against code.

## Unknown Classification

| Classification | Meaning | Trigger |
|---|---|---|
| `blocking` | Work cannot safely continue without resolution | Authoritative contract, ownership/SLA/compliance, destructive migration, security, production topology, retry/DLQ, event schema authority |
| `proposed-default` | Work may continue using a labeled safe default | Low-risk reversible operational choice |
| `informational` | Work may continue without a default | Optional optimization, future topology possibility, non-critical ambiguity |

AI sorts unknowns by classification during plan mode. Blocking unknowns must be surfaced before implementation or release.

## Glossary Signal Rule

If every entry in `glossary.md` carries the same `status`/`source`, do **not** repeat the value on each row. Use a single header note:

```
> All entries below: `status: inferred`, `source: ai`, unless overridden in the row.
```

## Phantom ADR Rule

`architecture.md` and any other context file MUST NOT cite `ADR-NNNN` references unless the ADR file actually exists at `knowledge/decisions/ADR-NNNN-*.md`.

| Intent | Where it goes |
|---|---|
| ADR exists | Cite as `evidence: { type: adr, ref: ... }` |
| ADR planned but not written | Entry in `assumptions.md` or `unknowns.md` (priority `important`) |
| Roadmap idea | `unknowns.md` (priority `informational`) — never cited as evidence |

## Engineering Style & Naming

See `conventions-language.md` for full engineering style conventions, naming guidance, language consistency rules, and reference stability rules.

## Validation Semantics

See `conventions-validation.md` for validation layer distinctions, source-of-truth order, and constraint extraction.

## Evidence & Constraint Conventions

See `conventions-evidence.md` for evidence consistency targets, drift detection, implicit constraint extraction, and runtime vs seed semantics.
