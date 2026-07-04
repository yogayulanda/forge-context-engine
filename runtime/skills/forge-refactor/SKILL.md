# forge-refactor

## Purpose
Scenario compatibility skill for behavior-preserving cleanup.

## Load
Read `.forge/forge.config.yaml` first. Apply `run.interaction` and related final run config fields. Load `.forge/runtime/meta/conventions.md`, use `.forge/runtime/meta/context-manifest.md` only as a routing index, then read `.forge/runtime/modes/refactor.md` as scenario guidance.

## Invocation
Use only when the user asks for bounded refactor work or an older prompt invokes `forge-refactor`.

## Focus
Route refactor work through `plan`, `implementation`, `execute`, and `review`; preserve behavior; classify risk; require plan/ECP approval for high-risk work.

## Output
Return scenario guidance, risk classification, evidence needed for behavior preservation, and recommended next core mode.

## Do NOT
Do not present refactor as a core lifecycle mode, hide behavior changes, perform architecture rewrites, or apply unapproved cleanup.
