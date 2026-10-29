# ADR-0001: Opt-in autopilot control plane

- **Status:** proposed
- **Date:** 2026-10-29
- **Decision makers:** Yoga (maintainer)

## Context

Running Forge end to end today needs a human orchestrator: someone writes the prompt for each mode, carries artifacts between tools, and approves Gate 1 (plan) and Gate 2 (ECP). The go-core internal release (2026-10) used exactly this pattern by hand: Claude wrote batch prompts and reviewed reports, GitHub Copilot executed approved batch ECPs.

The maintainer wants to hand a spec to any AI tool (Claude, Codex, Copilot, Hermes) and get back one reviewable pull/merge request per spec, or one per batch for large specs. Role agents (dev, reviewer) may be a different service from the orchestrating tool. The human reviews and decides the merge.

Forge specs and `CLAUDE.md` currently list orchestration, runtime executors, and autonomous chaining as explicit non-goals, and `1.1.0rc1` is in feature freeze.

## Options considered

| Option | Summary | Why not chosen |
|---|---|---|
| A. Python runner in Forge | Forge drives every stage itself | Orchestrator fixed to Forge; no LLM judgment between stages |
| B. Orchestrator in paos-runtime | Personal VPS service with Telegram approvals | Not portable to work repos; bank code processed off-site |
| C. GitHub-native | Issues + Claude Code Action | Locked to one vendor and one host |
| D. LLM lead + subagents | One Claude Code session spawns subagents | Gates are only instructions; Claude Code only; no resume |
| **E. Forge control plane** | Any LLM orchestrates; Forge CLI owns state, gates, agent dispatch, PR | Chosen |

## Decision

Add an opt-in **autopilot control plane** to Forge as a `forge run` command group, specified in `specs/autopilot.md`.

- The orchestrator is any LLM tool. It reads the spec, decides, writes prompts, and calls `forge run` commands.
- Forge owns everything that must not depend on LLM compliance: run state, deterministic gates, worktree and branch handling, dispatch of role agents through configured command templates, validation commands, pull/merge request creation, and the run report.
- Existing modes (`plan`, `implementation`, `execute`, `review`) remain the content of each stage. Their files, statuses, and boundaries do not change.
- Autopilot replaces the human Gate 1 and Gate 2 approvals with deterministic policy gates **only inside an autopilot run**. The human gate moves to the pull/merge request. Merge is never automated.

## Scope of the exception

This ADR narrows, not removes, the existing non-goals:

- Allowed: the `forge run` command group, its run state under `.forge/runs/`, the `forge-autopilot` skill, and thin adapter wrappers for it.
- Still not allowed anywhere in Forge: schedulers, triggers, daemons, CI/CD or deploy behavior, auto-merge, persistent AI memory, vector stores, plugin marketplaces.
- Core modes, shared skills other than `forge-autopilot`, and adapters stay free of orchestration logic.

## Consequences

- Forge maintains a small runtime surface (subprocess dispatch, timeouts, git, `gh`/`glab`). Agent CLI flags live in user config templates, not Forge code, to limit breakage from third-party CLI changes.
- The release containing this is a minor version (`1.2.0`), not an RC patch.
- `CLAUDE.md` and specs that list orchestration as a non-goal reference this ADR for the scoped exception.
- Safety relies on deterministic gates computed from the diff and config, not on agent-declared risk alone.
