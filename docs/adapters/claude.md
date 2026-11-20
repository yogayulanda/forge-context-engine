# Claude Adapter

Claude enters Forge through `CLAUDE.md`, shared skills, and optional slash command wrappers.

## How Invocation Works

Common requests:

```text
/forge-plan
/forge-review
/forge-ai-readiness
Use Forge ask mode to explain this service flow.
Use Forge verify-context mode to check context freshness.
```

The expected path is:

```text
Claude request -> CLAUDE.md or command wrapper -> shared skill -> .forge/context mode -> scoped repository evidence
```

## What The Adapter Does

`CLAUDE.md` tells Claude to:

- read `.forge/forge.config.yaml`
- apply `run.interaction` and related final run config fields
- read conventions and the routing manifest
- read the requested mode file
- load only task-relevant context
- keep output concise and mode-aligned

Slash command wrappers under `adapters/claude/commands/` are invocation helpers only.

## Expected Usage Style

Use natural, bounded prompts:

```text
Use Forge plan mode for this retry improvement.
Preserve the public event schema and list validation needed.
```

```text
Use Forge review mode on this branch.
Focus on correctness, validation honesty, security, context impact, and the exact diff reviewed.
```

```text
Use Forge ai-readiness mode on this repo.
Produce an AI readiness report, grouped findings, and a remediation roadmap.
```

## Boundaries

The Claude adapter must not:

- store repository cognition
- duplicate lifecycle semantics
- broad-load `.forge/context`
- imply autonomous execution
- introduce orchestration, schedulers, or persistent memory

Current code, docs, ADRs, and human confirmations win over adapter text.

## forge-orchestrate git guard

Forge installs `.forge/runtime/hooks/forge_git_guard.py` (Python standard library only). Worker subagents in `.claude/agents/` already register it with the `worker` role. To guard the orchestrator session as well, add this once to the target repository's `.claude/settings.json` (merge with existing content):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -B \"$CLAUDE_PROJECT_DIR/.forge/runtime/hooks/forge_git_guard.py\" orchestrator"
          }
        ]
      }
    ]
  }
}
```

The orchestrator role blocks pushes to `main`, `master`, or the remote default branch, force pushes, tag pushes, branch deletes, `git tag`, `git merge`, and MR/PR merge commands. Forge does not write `.claude/settings.json` itself, so existing settings are never overwritten.

## Keep sensitive files out of the model

`Output redaction` in `.forge/adapter.md` controls what the AI writes. It cannot stop a file's content from reaching the model once the AI reads it. To stop the read itself, add deny rules to the target repository's `.claude/settings.json` (merge with existing content, and adjust the paths to your repository):

```json
{
  "permissions": {
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(secrets/**)",
      "Read(config/prod/**)"
    ]
  }
}
```

Behavior per the Claude Code permissions documentation (verify against the current docs, since it changes between versions):

- Bare file names match at any depth, so `Read(.env)` blocks every `.env` under the project. A single-directory pattern such as `secrets/**` in a deny rule matches that directory at any depth.
- Read deny rules apply to the built-in file tools, to file commands Claude Code recognizes in Bash (`cat`, `head`, `tail`, `sed`), and to redirection targets. They apply right away, without the workspace trust step.
- They do not block a command that reads files without naming them (for example `grep -r pattern .`) or a script that opens files itself. For OS-level blocking, enable the Claude Code sandbox.

Other tools have their own controls. GitHub Copilot Business and Enterprise use content exclusion configured by an organization admin. Whether your provider uses your data for training depends on your plan and organization settings; confirm with your security team.
