# Forge Adapter and Command Foundation

| Field | Value |
|---|---|
| Document | Forge Adapter and Command Foundation |
| Version | 1.2 |
| Date | 2026-05-26 |
| Status | `decision` |
| Scope | Shared skills, adapter architecture, command semantics, and tool compatibility boundaries |
| Dependency | `specs/mode-invocation.md`, `specs/runtime-migration.md`, `specs/framework-lifecycle.md`, `runtime/.forge/context/00-meta/conventions.md` |

---

## 0. Purpose

This document defines the foundation for Forge shared skills, adapters, and commands.

Shared skills, adapters, and commands make Forge usable from Claude, Codex, Cursor, and future AI tooling while preserving Forge's repository-native cognition model.

This document defines:
- Adapter architecture and ownership boundaries.
- Thin adapter philosophy.
- Shared skill philosophy.
- Canonical command semantics.
- Repository-native integration rules.
- Tool compatibility strategy.
- Shared adapter conventions.
- Explicit non-goals.
- Validation expectations for future adapter work.

This document does NOT:
- Build an orchestration system.
- Add agent runtime behavior.
- Add plugin marketplace behavior.
- Add execution engines, workflow DAGs, schedulers, or triggers.
- Add autonomous chaining.
- Add memory, RAG, vector search, or knowledge graph systems.
- Move repository cognition out of `.forge/context`.

---

## 1. Architecture

Canonical runtime adapter layout:

```text
runtime/
+-- skills/
+-- adapters/
+-- CLAUDE.md
+-- AGENTS.md
+-- .forge/
```

### 1.1 Source of Truth

Forge core source of truth remains:

```text
.forge/context
```

Adapters may point to Forge context, mode files, and runtime conventions. They must not become authoritative context stores.

Ownership:

| Layer | Owns | Does Not Own |
|---|---|---|
| Forge core | Cognition, modes, governance, lifecycle semantics, artifact semantics, repository evidence boundaries | Tool-specific invocation UI |
| Shared skill layer | Reusable invocation prompts, mode selection, loading reminders, output focus | Repository intelligence, lifecycle semantics, governance semantics, runtime state |
| Adapter layer | Tool entrypoints, loading hints, command wording, compatibility notes | Repository intelligence, lifecycle semantics, governance semantics, runtime flags |
| Execution surface | User/tool-specific invocation mechanism | Forge decisions, source-of-truth claims, orchestration state |

### 1.2 Runtime File Roles

- `runtime/CLAUDE.md` is the Claude-compatible root adapter.
- `runtime/AGENTS.md` is the Codex/agent-compatible root adapter.
- `runtime/skills/<skill>/SKILL.md` contains shared, tool-neutral Forge skill entrypoints.
- `runtime/adapters/<tool>/` contains tool-specific invocation notes only.
- `runtime/adapters/shared/` contains portable adapter and command conventions.
- `runtime/.forge/` contains Forge runtime context, modes, configuration, and repository-native cognition structure.

### 1.3 Loading Behavior

Adapter loading must follow the Forge invocation protocol:

1. Read `.forge/forge.config.yaml`.
2. Read `.forge/context/00-meta/context-manifest.md`.
3. Follow `.forge/context/00-meta/conventions.md`.
4. Treat `00-meta/*` and `01-core/*` as always-loaded core.
5. Read the requested mode file from `.forge/context/modes/<mode>.md`.
6. Load only the mode delta needed for the task.
7. Preserve evidence, inference, proposed-default, assumption, and unknown boundaries.

Adapters may phrase this sequence for a tool, but may not redefine it.

### 1.4 Skill And Command Ownership

Skills are shared operational entrypoints. Commands are tool-specific wrappers around skills.

Skills may:
- Select one Forge mode.
- State scoped loading intent.
- State invocation focus.
- State output expectations.
- State anti-drift constraints.

Skills must not:
- Define new lifecycle semantics.
- Duplicate mode behavior.
- Store repository intelligence.
- Create orchestration state.
- Chain other skills autonomously.
- Persist memory or hidden state.

Commands are owned by the adapter layer only as invocation text.

Commands may:
- Point to a shared skill.
- Map tool syntax to a skill name.
- Provide minimal tool-specific invocation wording.

Commands must not:
- Define new lifecycle semantics.
- Duplicate mode behavior.
- Store repository intelligence.
- Create orchestration state.
- Chain other commands autonomously.
- Persist memory or hidden state.

### 1.5 Skill Structure

Shared skills live under:

```text
runtime/skills/<skill>/SKILL.md
```

Required skill sections:

| Section | Purpose |
|---|---|
| `Purpose` | Names the Forge workflow the skill invokes. |
| `Load` | Repeats scoped Forge loading without adding new semantics. |
| `Invocation` | Describes when a user or tool should invoke the skill. |
| `Focus` | States the mode-specific attention area at a high level. |
| `Output` | Points to the mode-owned result shape. |
| `Do NOT` | Prevents broad loading, cognition duplication, orchestration, memory, and runtime drift. |

Skills are not adapters. Adapters translate tool syntax into skill invocation.

Skills are not runtime. They store no state and run no execution loop.

Skills are not cognition sources. Repository intelligence still comes from `.forge/context`, repository code/docs/ADRs, and explicit human confirmation.

### 1.6 Root Adapter Content Boundary

Root adapters such as `runtime/CLAUDE.md` and `runtime/AGENTS.md` should contain only:
- Bootstrap entrypoint order.
- Tool-specific skill or command invocation mapping.
- Concise loading and output hints.
- Pointers to Forge core and specs.

Root adapters should reference, not restate:
- Runtime interaction semantics.
- Validation and drift semantics.
- Artifact lifecycle semantics.
- Secret handling rules.
- Governance and approval behavior.
- Mode-specific execution and reporting behavior.

If a root adapter needs a large rule list to be correct, that rule belongs in `.forge/context/00-meta/conventions.md`, a mode file, or a spec instead.

---

## 2. Thin Adapter Philosophy

Forge adapters are thin.

They are:
- Invocation bridges.
- Loading hints.
- Operational entrypoints.
- Tool compatibility surfaces.

They are not:
- Cognition sources.
- Runtime systems.
- Governance layers.
- Workflow engines.
- Memory layers.
- Repository knowledge stores.

### 2.1 Shared Skill Philosophy

Forge skills are reusable invocation layers.

They are:
- Tool-neutral Forge workflow entrypoints.
- Compact operational prompts.
- Shared loading reminders.
- Invocation-friction reducers.

They are not:
- Cognition sources.
- Adapters.
- Runtime systems.
- Workflow or orchestration units.
- Memory systems.
- Execution platforms.

Skills invoke Forge lifecycle behavior. They do not override `.forge/context`, mode files, conventions, or specs.

The stable bridge is:

```text
tool syntax -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

### 2.2 Core Rules

- Forge core owns cognition.
- `.forge/context` owns repository-native truth.
- Mode files own lifecycle loading deltas and operational semantics.
- Shared skills own reusable invocation wording.
- `runtime.non_interactive` remains the single interaction behavior switch.
- Adapters own only tool-specific invocation shape.
- Commands remain short and task-facing.
- A command that works in multiple repositories must change behavior only because `.forge/context` differs.

### 2.3 Anti-Drift Rules

Adapters and skills must not:
- Become orchestration systems.
- Contain repository intelligence.
- Become alternate runtime layers.
- Create parallel cognition systems.
- Duplicate governance, lifecycle, artifact, or runtime semantics.
- Copy large sections of `.forge/context/00-meta/conventions.md`.
- Add hidden approval, scheduling, retry, execution, or chaining behavior.
- Treat tool-specific files as higher authority than `.forge/context`.

When an adapter needs more detail, it must point back to Forge core files instead of restating them.

---

## 3. Skill And Command Semantics

Forge skills are concise operational prompts that invoke a mode and set output expectations. Commands are tool-specific wrappers that point to skills.

Canonical skill structure:

```text
# <skill-name>

## Purpose
<mode workflow intent>

## Load
<mode and scoped context to load>

## Invocation
<when to use this skill>

## Focus
<mode-specific focus>

## Output
<expected result shape>

## Do NOT
<forbidden behavior>
```

### 3.1 Required Skill Sections

| Section | Purpose |
|---|---|
| `Purpose` | Identifies the reusable Forge workflow. |
| `Load` | Identifies the Forge mode and any scoped context hints. |
| `Invocation` | Maps user intent to skill use. |
| `Focus` | Keeps attention on the mode-owned concern. |
| `Output` | Defines the expected response or artifact shape. |
| `Do NOT` | Prevents drift, broad loading, duplication, or orchestration behavior. |

### 3.2 Skill Rules

Skills must:
- Name exactly one primary Forge mode unless the user explicitly asks for a handoff.
- Load mode deltas through `.forge/context/modes/<mode>.md`.
- Keep repository intelligence in `.forge/context`.
- Use direct repository evidence when task scope requires validation.
- Preserve unknowns instead of guessing.
- State output expectations compactly.
- Stay portable across compatible tools.

Skills may reference lifecycle artifact types when the mode owns them.

Skills must not:
- Reimplement the mode file.
- Hard-code domain assumptions such as fintech, frontend, or infrastructure behavior.
- Run multi-step autonomous chains.
- Add hidden state, memory, or scheduling.
- Define approval policy outside Forge runtime semantics.

### 3.3 Command Rules

Commands must:
- Point to a shared skill.
- Stay tool-specific and short.
- Avoid reusable workflow logic.
- Avoid repository intelligence.

Commands may provide aliases for tool-specific invocation surfaces.

### 3.4 Skill And Command Naming

Canonical skill naming:

```text
forge-ask
forge-plan
forge-implement
forge-execute
forge-test
forge-review
forge-incident
forge-refactor
```

Tool syntax examples:
- Claude: `/forge-review`, `/forge-plan`
- Codex: `$forge-review`, `/skill forge-review`, future-compatible `/forge-review`
- Scoped variants: `forge:review:security`, `forge:testing:contract`

Scope suffixes must describe loading or output focus. They must not imply new modes.

---

## 4. Repository-Native Integration

The same skill or command must behave differently in different repositories because each repository has different `.forge/context` evidence.

Examples:

| Skill or command | Repository Type | Behavior Source |
|---|---|---|
| `forge:review` | Fintech service | Financial correctness, idempotency, retry/replay, PII/secrets, and ledger risk from local `.forge/context` and code evidence |
| `forge:review` | Frontend app | UI behavior, accessibility, state flow, build constraints, and product evidence from local `.forge/context` and code evidence |
| `forge:review` | Infrastructure module | Provisioning risk, blast radius, rollback, secrets, and environment boundaries from local `.forge/context` and code evidence |

The skill text is stable. Repository behavior is local.

Repository intelligence must come from:

```text
.forge/context
```

Repository intelligence must not come from:
- Adapter files.
- Skill files.
- Command files.
- Tool-specific rules.
- Global assistant memory.
- Inferred cross-repo assumptions.

If `.forge/context` lacks enough evidence, the skill, adapter, or command must preserve the gap as an unknown and request targeted evidence or report a blocked status according to runtime interaction behavior.

---

## 5. Tool Compatibility Strategy

Forge separates three concerns:

| Concern | Description |
|---|---|
| Forge core | Repository cognition, lifecycle modes, governance semantics, artifact lifecycle, runtime semantics |
| Shared skill layer | Reusable tool-neutral workflow entrypoints under `runtime/skills/` |
| Adapter layer | Tool-specific entry files, command text, loading hints, compatibility wrappers |
| Execution surface | Claude slash commands, Codex `AGENTS.md`, Cursor rules, future assistant invocation surfaces |

### 5.1 Claude

Claude compatibility uses:
- Root `CLAUDE.md` as the thin adapter.
- Optional Claude slash command files that point to shared skills.
- No duplicated Forge cognition in Claude-specific folders.

### 5.2 Codex

Codex compatibility uses:
- Root `AGENTS.md` as the thin adapter.
- Codex instructions that point to shared skills, `.forge/`, and mode files.
- No Codex-specific repository intelligence.
- Skills-first invocation through `$forge-review`, `/skill forge-review`, or natural prompts such as "Use Forge review skill", depending on Codex surface/version.
- No parallel Codex command-wrapper layer unless the Codex runtime explicitly requires it later.

### 5.3 Cursor

Cursor compatibility uses:
- Cursor rules that point to `.forge/`.
- Mode-aware command prompts that resolve to shared skills where supported.
- No Cursor-specific lifecycle or governance layer.

### 5.4 Future Tools

Future adapters must be added as thin folders under:

```text
runtime/adapters/<tool>/
```

A future adapter is acceptable only if it can be described as:
- An invocation bridge.
- A loading hint surface.
- A command portability wrapper.

If it needs state, scheduling, autonomous loops, execution graphs, or repository intelligence, it is outside this foundation.

---

## 6. Adapter Conventions

### 6.1 Naming

- Adapter folders use lowercase tool names: `claude`, `codex`, `cursor`.
- Shared conventions live in `adapters/shared`.
- Command files use lowercase kebab-case when materialized as files.
- Command names use `forge:<mode>` and optional suffixes.
- Mode names must match `.forge/context/modes/*.md`.

### 6.2 Folder Semantics

| Folder | Purpose |
|---|---|
| `skills/` | Shared Forge skill entrypoints and invocation semantics. |
| `adapters/claude/` | Claude invocation notes and optional slash-command mapping. |
| `adapters/codex/` | Codex invocation notes and `AGENTS.md` mapping. |
| `adapters/cursor/` | Cursor rules/invocation notes. |
| `adapters/shared/` | Portable command semantics and anti-duplication rules. |

Adapter folders are documentation and compatibility surfaces unless a future spec explicitly allows a generated adapter artifact. They are not runtime state.

### 6.3 Portability

Portable adapter content should:
- Reference canonical Forge files by path.
- Reference shared skills by path instead of copying reusable workflow text.
- Avoid tool-only vocabulary when a Forge term exists.
- Keep command sections stable.
- Keep output expectations mode-owned.
- Prefer small wrappers over copied policies.

### 6.4 Extension Boundary

Allowed future extensions:
- Additional lightweight shared skills for confirmed Forge modes.
- Additional thin adapters for new tools.
- Tool-specific command syntax wrappers.
- Validation cases proving adapter behavior remains thin.
- Small mapping tables from tool invocation syntax to Forge mode names.

Forbidden future extensions in this layer:
- Workflow DAGs.
- Agent loops.
- Execution schedulers.
- Retry engines.
- CI/CD pipelines.
- Deploy runtimes.
- Persistent memory stores.
- Repository intelligence caches.
- Plugin marketplaces.

---

## 7. Explicit Non-Goals

Forge adapters are not:
- Orchestration engines.
- AI operating systems.
- Workflow runtimes.
- Deploy runtimes.
- Memory systems.
- Autonomous-agent frameworks.
- CI/CD systems.
- Plugin marketplaces.
- Runtime executors.
- Knowledge graphs.
- RAG systems.
- Vector databases.

Forge remains a cognition and workflow layer. It structures how AI assistants load repository context, preserve evidence boundaries, and produce reviewable engineering outputs.

---

## 8. Validation Pass

Any skill, adapter, or command foundation change must validate:

- Architecture remains bounded to invocation and compatibility.
- Forge identity remains cognition-focused.
- Shared skills remain thin invocation layers.
- No orchestration behavior is introduced.
- No duplicated cognition is introduced.
- No alternate runtime/platform layer is introduced.
- `.forge/context` remains the source of truth.
- Mode files remain the source of lifecycle loading semantics.
- `runtime.non_interactive` remains the single interaction behavior switch.
- Repository-native behavior is preserved.
- Skill files contain no repository intelligence.
- Tool-specific files contain no repository intelligence.
- Root adapters remain thin: bootstrap, invocation mapping, concise hints, and references only.
- Heavy operational semantics remain in `.forge/context/00-meta/conventions.md`, mode files, and specs.

Validation outcome for this foundation:

| Check | Result |
|---|---|
| Bounded architecture | Pass |
| Cognition-focused identity | Pass |
| Orchestration creep | Not introduced |
| Duplicated cognition | Not introduced |
| Runtime/platform explosion | Not introduced |
| Repository-native behavior | Preserved |

---

## 9. Risks and Future Considerations

Risks:
- Tool-specific command systems may encourage duplicated policy text.
- Future adapters may drift into workflow automation.
- Teams may store repository intelligence in adapter files for convenience.
- Command aliases may create hidden lifecycle variants.

Controls:
- Keep adapter files short.
- Point back to `.forge/context` for cognition.
- Keep commands section-based and operational.
- Add validation cases before expanding adapter behavior.
- Reject adapter changes that require hidden state, scheduling, or autonomous chaining.

Future consideration:
- A later phase may define materialized command templates for specific tools. Those templates must remain wrappers around this foundation and the mode invocation protocol.
