---
id: layer.backend
title: "Layer: Backend"
type: layer
status: unknown
confidence: high
source: human
owner: unresolved
updated: 2026-05-20
---

# Layer: Backend

Entrypoint for the backend layer. Horizontal context for backend engineering discipline.

## Files in This Folder

- `README.md` *(this file)* — entrypoint & navigation only
- `backend.md` — actual layer content *(created during init; absent in fresh runtime)*
- Sub-files added when content exceeds size budget *(≤ ~150 lines)*

## Activation

Activated only if the target repo contains backend code (server, API, business logic).

If absent: delete this folder and remove `backend` from `forge.config.yaml` → `layers_enabled`.

## Content Policy

This README is navigation only. **No engineering knowledge here.** All backend conventions, patterns, and standards live in `backend.md` and its sub-files.
