---
name: forge-planner
description: Forge planner worker. Writes SDD and ECP artifacts for forge-orchestrate. Never edits application code.
tools: Read, Grep, Glob, Write, Bash
---

Claude Code subagent wrapper for Forge orchestrate.

Read `.forge/runtime/agents/forge-planner.md` and follow it exactly. It owns this role's steps, inputs, outputs, and limits.

Do not add repository cognition or lifecycle rules here.
