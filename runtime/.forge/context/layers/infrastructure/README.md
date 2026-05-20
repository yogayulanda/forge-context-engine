---
id: layer.infrastructure
title: "Layer: Infrastructure"
type: layer
status: unknown
confidence: high
source: human
owner: unresolved
updated: 2026-05-20
---

# Layer: Infrastructure

Entrypoint for the infrastructure layer. Horizontal context for IaC, deployment, and runtime environment.

## Files in This Folder

- `README.md` *(this file)* — entrypoint & navigation only
- `infrastructure.md` — actual layer content *(created during init)*
- Sub-files added when content exceeds size budget *(≤ ~150 lines)*

## Activation

**Conditional activation.** Activate only if the target repo contains concrete infrastructure ownership evidence:

- Helm charts
- Terraform / OpenTofu modules
- Kubernetes manifests
- Dockerfile + orchestration configs (compose, etc.)
- CI/CD deployment logic (not just test runs)

Service repos often delegate deployment to a separate repo. If evidence is **weak/partial**:
- Activate with `confidence: medium` or `low`.
- Add ownership unknowns referencing the gap.
- Do NOT assume infra ownership.

If evidence is **absent**: delete this folder and remove `infrastructure` from `forge.config.yaml` → `layers_enabled`.

## Content Policy

This README is navigation only. **No engineering knowledge here.** All infrastructure conventions live in `infrastructure.md` and its sub-files.
