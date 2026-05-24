# Shared Runtime Validation Case

| Field | Value |
|---|---|
| Pattern | Shared runtime topology |
| Lifecycle state | `benchmarked` |
| Coverage category | Topology semantics, edge classification, hallucination resistance |
| Scope | Repository-neutral cognition benchmark |

---

## 1. Pattern Name

`shared-runtime`

Forge must distinguish shared runtime adoption from service-to-service runtime topology.

---

## 2. Lifecycle State

`benchmarked`

This case represents a validated cognition pattern added to `validation-cases/` for future regression detection.

It does not imply the pattern is `stable` across broad repository diversity.

---

## 3. Generic Topology Shape

```text
deployable-service --imports/uses-runtime--> shared-runtime
```

The shared runtime may also be classified as a `platform-component` when evidence shows it provides reusable platform behavior.

The deployable service may also be classified as a `consumer` when evidence shows it adopts the shared runtime.

---

## 4. Expected Repository Roles

| Role | Meaning |
|---|---|
| `deployable-service` | Independently runnable or deployable application/service unit |
| `shared-runtime` | Reusable runtime foundation imported or embedded by deployable units |
| `platform-component` | Shared component that provides platform-level behavior or conventions |
| `consumer` | Unit that adopts or depends on the shared runtime |

Role classification must be evidence-backed.

One unit may hold more than one role when the evidence supports it.

---

## 5. Expected Edge Classification

Expected edge:

```text
deployable-service --imports/uses-runtime--> shared-runtime
```

Not expected:

```text
deployable-service --runtime-calls--> shared-runtime
```

`imports/uses-runtime` means the service depends on shared runtime code, configuration, conventions, or initialization behavior.

`runtime-calls` means network, RPC, queue, event, job, database, or other runtime interaction between independently executing systems.

Package imports alone classify an adoption edge, not a service-to-service runtime edge.

---

## 6. Incorrect Interpretations Forge Must Reject

Forge must reject the following interpretations unless direct evidence exists:

- `shared-runtime == deployable-service`
- `utility-library == shared-runtime`
- `imports/uses-runtime == runtime-calls`
- Package imports imply service-to-service topology.
- A single consumer plus one shared runtime proves full platform maturity.
- Shared runtime adoption proves runtime ecosystem boundaries.
- Platform component status proves deployability.
- Runtime initialization code proves an external runtime call.

---

## 7. Evidence Shape Required

Required evidence for `deployable-service`:

- Entrypoint, build target, deployment artifact, service configuration, or equivalent runnable-unit signal.

Required evidence for `shared-runtime`:

- Imported module/package/library used for runtime foundation behavior.
- Runtime initialization, middleware, bootstrap, framework, shared config, or equivalent adoption signal.
- Absence of independent deployable-service evidence, unless dual-role evidence is explicit.

Required evidence for `imports/uses-runtime`:

- Import statement, module dependency, package reference, build dependency, or runtime bootstrap usage.
- Evidence that the dependency is used by the deployable service.

Required evidence for `runtime-calls`:

- Network call, RPC client/server edge, queue/event exchange, scheduled job interaction, service discovery reference, database-mediated runtime workflow, or equivalent execution-time interaction.

If runtime-call evidence is absent, Forge must not infer `runtime-calls`.

---

## 8. Expected Forge Behavior

Forge should:

- Classify the deployable unit as `deployable-service`.
- Classify the adopting unit as `consumer`.
- Classify the shared foundation as `shared-runtime` when runtime foundation evidence exists.
- Classify the shared foundation as `platform-component` when platform behavior evidence exists.
- Create an `imports/uses-runtime` edge from the deployable service to the shared runtime.
- Avoid creating a `runtime-calls` edge from package imports alone.
- Treat one consuming service plus one shared runtime as pilot validation only.
- Keep unresolved maturity, version, ownership, and compatibility claims as unknown unless evidenced.

---

## 9. Hallucination Boundaries

Forge must not infer:

- Service-to-service calls from package imports.
- Deployability from shared runtime code.
- Shared runtime status from generic utility helpers.
- Full platform maturity from one consumer.
- Compatibility guarantees without version or contract evidence.
- Ownership, SLA, release policy, or governance from topology alone.
- Runtime ecosystem boundaries from shared runtime adoption.

Unknowns must remain explicit when evidence is insufficient.

---

## 10. Regression Signals

This case regresses if Forge:

- Labels a shared runtime as a deployable service without deployability evidence.
- Labels a utility library as shared runtime without runtime foundation evidence.
- Converts `imports/uses-runtime` into `runtime-calls`.
- Infers service-to-service topology from package imports.
- Promotes pilot validation to platform maturity.
- Invents compatibility, version, ownership, or governance claims.
- Treats repository count or file count as topology maturity.

---

## 11. Coverage Category

Primary coverage:

- Topology diversity.
- Semantic coverage.
- Cognition correctness.
- Hallucination resistance.

This case covers the boundary between:

- Shared runtime adoption.
- Runtime service topology.
- Platform component classification.
- Platform maturity.

---

## 12. Promotion Criteria Toward Stable

This pattern may move toward `stable` only after:

- Multiple repositories or topology variants validate the same edge classification.
- Shared runtime adoption remains distinct from runtime-call topology.
- Utility libraries remain distinct from shared runtimes.
- Deployable-service classification remains evidence-backed.
- Pilot adoption remains distinct from platform maturity.
- Hallucination boundaries remain consistent across diverse code layouts.
- Regression expectations remain valid across all benchmarked variants.

One consuming service plus one shared runtime is sufficient for pilot validation.

It is not sufficient for full platform maturity.
