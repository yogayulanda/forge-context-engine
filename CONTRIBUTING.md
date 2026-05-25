# Contributing To Forge Context Engine

Forge is a foundation for bounded engineering cognition: repo-first, evidence-driven, operational, and human-review-aware.

Contributions are welcome when they make real engineering work clearer, safer, and easier to review without expanding Forge into an autonomous automation platform.

## Contribution Philosophy

Prefer changes that:

- preserve repository code, docs, ADRs, and human confirmations as source of truth
- keep lifecycle modes distinct
- improve operational clarity
- reduce ambiguity found in real usage
- strengthen evidence, status, validation, or safety boundaries
- keep patches concise and reviewable

Avoid changes that:

- add orchestration semantics
- add agent loops or autonomous execution systems
- add DAG or workflow engines
- add hidden persistent memory systems
- encourage broad global context loading by default
- introduce theoretical framework expansion without real-world evidence
- redesign lifecycle semantics in a large, speculative PR

## How To Propose Changes

For small documentation or wording fixes, open a focused PR with:

- the problem being solved
- the file or mode affected
- the evidence or usage friction behind the change
- why the change preserves existing lifecycle boundaries

For semantic changes, start with an issue or design note first. Explain the observed real-world failure, affected mode or rule, and the minimal refinement needed.

## Reporting Cognition, UX, Or Runtime Issues

Good reports include:

- the requested Forge mode
- the expected output
- the actual confusing or unsafe output
- relevant repository/context evidence
- whether the issue affected planning, implementation, execution, testing, review, incident, or refactor work

Keep examples sanitized. Do not include production secrets, customer data, private URLs, or credentials.

## Patch Expectations

- Keep patches small.
- Prefer explicit wording over abstraction.
- Add or update validation rules when a recurring failure is found.
- Preserve `runtime.non_interactive` as the single controlling interaction flag.
- Keep `runtime.profile` as metadata only.
- Keep artifacts bounded, mode-owned, and non-authoritative.
- Do not add new lifecycle modes, statuses, artifact types, or workflows unless repeated real-world evidence justifies the change.

Forge should evolve from field evidence, not from theoretical completeness.
