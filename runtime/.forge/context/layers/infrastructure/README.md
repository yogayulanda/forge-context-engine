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

**Conditional activation.** Activate ONLY if the target repo demonstrably owns deployment or environment provisioning.

### Sufficient evidence (activate)

- Terraform / OpenTofu modules
- Helm charts
- Kubernetes manifests
- CI/CD **deployment** logic (not just test/build steps)
- Deployment scripts (e.g. ansible, custom shell deploy)
- Environment provisioning code

### Not sufficient on its own (do NOT activate)

These belong to `backend` / `systems/<unit>` unless deployment ownership is also evidenced:

- DB migrations
- Build tooling (Makefile, npm scripts for build/test)
- Environment variables / `.env.example`
- Local-development Dockerfile (no orchestration)
- Local config files

If only these exist → infrastructure layer is **not** activated. Delete the folder and remove from `forge.config.yaml` → `layers_enabled`.

If evidence is **partial** (e.g. partial K8s manifest, deployment script that calls into another repo):
- Activate with `confidence: medium` or `low`.
- Add unknown entries describing the ownership boundary.
- Do NOT assume infrastructure ownership.

## Content Policy

This README is navigation only. **No engineering knowledge here.** All infrastructure conventions live in `infrastructure.md` and its sub-files.
