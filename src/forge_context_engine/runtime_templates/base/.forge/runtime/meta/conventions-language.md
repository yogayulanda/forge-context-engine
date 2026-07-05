---
id: meta.conventions-language
title: Language, Naming & Reference Conventions
type: meta
status: confirmed
confidence: high
source: human
evidence:
  - { type: doc, ref: ../../../FORGE-CONTEXT-ARCHITECTURE.md }
owner: forge-context-engine
updated: 2026-06-03
---

# Language, Naming & Reference Conventions

Load this file when the task involves language consistency, Indonesian/English usage, naming guidance, tone, or reference stability.

`ui.language` controls human-facing narration, progress updates, and explanations. Forge Plans, ECPs, Execute Reports, Review Reports, task cards, specs, validation commands, commit messages, and generated Markdown artifact contents remain English by default unless the user explicitly requests another language.

---

## Engineering Style Convention

AI-generated repository changes should feel like pragmatic, idiomatic engineering in that repository, not framework exposition.

- Follow existing repository conventions by default: inspect nearby code, package layout, naming, tests, and error handling before creating a new pattern.
- Prefer idiomatic Go, explicit behavior, readable control flow, operational clarity, and maintainable local simplicity.
- Avoid academic architecture language, unnecessary ceremony, speculative extensibility, cleverness, and framework-style indirection.
- Do not blindly copy unsafe technical debt. Minimal safe corrections are allowed for unsafe error handling, obviously brittle behavior, or unnecessary complexity.
- Style evolution must be bounded to the task: no architecture rewrite, paradigm migration, competing coding style, or mass refactor during unrelated execution.
- Prefer explicit flow, focused functions, composition, and direct dependencies over unnecessary interfaces, generic-heavy abstraction, or abstraction created only for future possibility.
- Tests follow existing repository test style and placement. Add new test structure only when the repo lacks a convention or the task requires broader validation.

### Naming Guidance

Names must use natural engineering English and represent operational or business intent.

| Prefer | Avoid |
|---|---|
| `CreateTransactionHistory` | `ExecuteTransactionalPersistenceOperation` |
| `PublishEvent` | `BuildKafkaEventPayloadTransformer` |
| `HandleMessage` | `HandleIncomingTransactionHistoryProcessing` |
| `StartConsumer` | `InitializeConsumerRuntimeExecutionFacade` |
| `FindByReferenceID` | `ResolveReferenceIdentityLookupOperation` |

Function, type, method, and file names should feel familiar to normal engineers: clear, short enough to read, specific enough to operate, and free of "smart" or academic wording.

---

## Language Consistency Rule

Each repo's `.forge/context/` uses **one dominant natural language** for narrative content. Selected during init based on (in order):

1. Existing repo documentation language (README, ADRs, /docs)
2. Engineering team convention
3. Pre-existing context (legacy `.ai/` etc.)
4. Dominant commit/documentation language

The chosen language must be applied consistently across:

active `.forge/context/*.md` profile files · `systems/<unit>/system.md` · `layers/<x>/<x>.md` · `.forge/runtime/meta/glossary.md` · layer `README.md`

### What MUST NEVER Be Translated

Technical identifiers stay verbatim regardless of dominant language:

- Source code symbols (function/class/variable names)
- Database table & column names
- Field names, enum values, status codes
- Protocol names (gRPC, HTTP, AMQP, etc.)
- API paths, RPC method names, route patterns
- Migration filenames
- Event/topic names, queue names
- External system names, dependency names
- Configuration keys (env vars, config paths)
- Commands and shell snippets
- File paths
- Status enums and machine-readable mode/status values

Examples:

| Rule | Example |
|---|---|
| Keep verbatim | `ExternalRefID` stays `ExternalRefID` |
| Keep verbatim | `transaction_error_definitions` stays as-is |
| Keep verbatim | `direction: INBOUND/OUTBOUND` enum values unchanged |
| Keep verbatim | `CreateTransactionHistory` RPC name unchanged |

### Mixed Language Allowed Only For

- Preserving repo-native or business-native terminology when no equivalent exists
- External protocol or product naming
- Source-code identifiers embedded in prose

Whole sentences in a second language inside an otherwise single-language file are NOT acceptable.

### Human Narration vs Project Output

- Human-facing chat narration follows `ui.language`.
- Copyable/project output remains English by default.
- A user may explicitly request project artifacts in another language, but that changes only the requested artifact output, not commands or identifier-shaped text.

Example with `ui.language: id`:

- Narration: `Saya akan memakai Forge plan mode. Boundary-nya read-only.`
- Artifact heading: `Forge Plan`

### Anti-Patterns

- Translating only headings while leaving body in another language.
- Half-translating a file then leaving residue paragraphs untranslated.
- Translating identifier-shaped terms to "explain" them in prose.
- Forcing translation of repo-native business jargon that has no equivalent.

---

## Reference Stability Rule

When one context file refers to content in another, prefer **stable references** over fragile prose pointers — especially for translated/translatable headings.

| Prefer (stable) | Avoid (fragile) |
|---|---|
| `core.product` (id ref) | "the product file" |
| `.forge/context/01-service-overview.md` (file ref) | the file currently named "Product" |
| `core.product → producers list` (semantic ref) | `"Sumber Data"` section / `"Data Sources"` section |
| `system.payment-service` (id ref) | "payment service docs" |
| Slug anchor `#producers` if used consistently | Verbatim heading text in any language |

### Why

Heading text changes when language switches or when content is refactored. Identifier (`id`) and file-path references survive both.

### Practical Guidance

- Reference by `id` first, then file path, then anchor — heading text last.
- If anchor must be used, define it via consistent slug (e.g. `#producers`, `#data-flow`) that does not depend on translated heading.
- Avoid quoting translated headings inline; cite the file/id and let the reader navigate.
