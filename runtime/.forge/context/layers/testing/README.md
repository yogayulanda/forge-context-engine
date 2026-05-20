---
id: layer.testing
title: "Layer: Testing"
type: layer
status: unknown
confidence: high
source: human
owner: unresolved
updated: 2026-05-20
---

# Layer: Testing

Entrypoint for the testing layer. Horizontal context for testing strategy and conventions.

## Files in This Folder

- `README.md` *(this file)* — entrypoint & navigation only
- `testing.md` — actual layer content *(created during init)*
- Sub-files added when content exceeds size budget *(≤ ~150 lines)*

## Activation

Activated if the target repo contains test files or test runner configuration.

If absent: delete this folder and remove `testing` from `forge.config.yaml` → `layers_enabled`.

## Content Policy

This README is navigation only. **No engineering knowledge here.** All testing conventions live in `testing.md` and its sub-files.
