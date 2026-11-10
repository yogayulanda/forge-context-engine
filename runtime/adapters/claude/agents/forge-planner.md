---
name: forge-planner
description: Forge planner worker. Writes SDD and ECP artifacts for forge-orchestrate. Never edits application code.
tools: Read, Grep, Glob, Write, Bash
maxTurns: 40
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3 -B "$CLAUDE_PROJECT_DIR/.forge/runtime/hooks/forge_git_guard.py" worker
---

Claude Code subagent wrapper for Forge orchestrate.

Read `.forge/runtime/agents/forge-planner.md` and follow it exactly. It owns this role's steps, inputs, outputs, and limits.

Do not add repository cognition or lifecycle rules here.
