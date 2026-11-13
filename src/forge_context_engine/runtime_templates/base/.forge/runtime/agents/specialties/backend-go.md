---
id: specialty.backend-go
title: "Specialty: Backend Go"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [executor, reviewer]
applies_when: the backend change touches Go code (`go.mod` present, `*.go` files in scope); use together with `backend`
---

# Specialty: Backend Go

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/backend-go.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. The repo's existing Go style wins over every rule here.

## Load
- `go.mod`, the lint config (`.golangci.yml` or similar) when present, and the nearest existing Go file of the same kind.

## As executor
- Files: lower-case `snake_case.go`, tests in `<name>_test.go` beside the code, one main type or concern per file; follow the package's existing file split.
- Naming: MixedCaps, no underscores (except `TestX_Case`). Unexported by default; export only what another package calls. Functions start with a verb. Initialisms stay upper case (`userID`, `HTTPClient`). No `util`/`common` packages, no stutter (`transfer.Service`), no `Get` prefix on getters, 1-2 letter receivers, `-er` interfaces without `I` prefix.
- Functions: `ctx context.Context` first and never stored in a struct; `error` last and checked at once; happy path left-aligned, no `else` after `return`; more than 4 parameters become a request or options struct; no naked bool arguments; accept small interfaces defined by the consumer, return concrete types; constructors `NewX` take dependencies explicitly; no mutable globals or `init()`; `os.Exit`/`log.Fatal` only in `main`; no `panic` in business code.
- Errors: wrap as `fmt.Errorf("get account %s: %w", id, err)` without "failed to"; compare with `errors.Is`/`errors.As`, never by message text; error strings lower case without punctuation.
- Types and data: enums start at 1 so the zero value means unknown; explicit `json` tags on marshaled structs; decide `[]` versus `null` from the contract, because a nil slice marshals to `null`; comma-ok on type assertions; copy slices and maps received or returned at a boundary; keep variable scope small (`if err := f(); err != nil`) and watch `:=` shadowing `err`.
- Concurrency: every goroutine has an exit path through `ctx` or a closed channel; whoever starts it waits for it (`errgroup`, `sync.WaitGroup`); `defer` cleanup right after the error check.
- Tests: table-driven; helpers call `t.Helper()`; no `t.Fatal` inside goroutines.
- Tools: run `gofmt`/`goimports`, `go vet`, the repo linter, and `go test` with `-race` when the repo already uses it for the changed packages.

## As reviewer
- Let the linter judge formatting and import order; review what it cannot see.
- MAJOR: float for money; zero-value enum that means a real state; missing `json` tag or `null`/`[]` change on a response; goroutine without an exit path; error matched by message text; unchecked type assertion; shadowed `err` that hides a failure.
- MINOR: naming, stutter, `Get` prefixes, parameter count, nesting, missing `t.Helper()`.
