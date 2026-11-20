---
name: forge-executor
description: Forge executor worker. Applies one orchestrator-accepted ECP and runs its validation. Never commits or pushes.
tools: Read, Grep, Glob, Edit, Write, Bash
maxTurns: 80
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3 -B "$CLAUDE_PROJECT_DIR/.forge/runtime/hooks/forge_git_guard.py" worker
---

Claude Code subagent wrapper for Forge orchestrate.

Read `.forge/runtime/agents/forge-executor.md` and follow it exactly. It owns this role's steps, inputs, outputs, and limits.

Do not add repository cognition or lifecycle rules here.
