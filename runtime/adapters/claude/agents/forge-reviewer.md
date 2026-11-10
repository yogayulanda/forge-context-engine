---
name: forge-reviewer
description: Forge reviewer worker. Reviews the diff in a fresh context and returns a verdict. Never edits code.
tools: Read, Grep, Glob, Bash
---

Claude Code subagent wrapper for Forge orchestrate.

Read `.forge/runtime/agents/forge-reviewer.md` and follow it exactly. It owns this role's steps, inputs, outputs, and limits.

Do not add repository cognition or lifecycle rules here.
