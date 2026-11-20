---
id: specialty.testing
title: "Specialty: Testing"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [tester, reviewer]
applies_when: always for the tester; for the reviewer when a test report exists
---

# Specialty: Testing

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/testing.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. Fill in the `Team settings` below in your copy.

## Team settings
- Unit test command: `<from the repo, for example make test>`
- Integration/e2e command: `<for example make test-e2e, or none>`
- Full suite command: `<for example make test-all>`
- Environment needed for e2e: `<for example docker compose up -d db, or none>`
- Test paths (the tester may only write here): `*_test.go`, `test/`, `tests/`, `e2e/`, `testdata/`
- Fixtures and test data rules: `<for example use testdata/ builders, never production data>`

When a value is still a `<placeholder>`, find it in the Makefile, package scripts, or CI config and cite where you found it. If it is not there, report it as missing.

## Load
- `.forge/context` layer `testing` files.
- The existing integration/e2e tests closest to the changed entry point, as the pattern to copy.

## As tester
- Use the commands and test paths above; never invent a command.
- If the e2e environment cannot start, write the tests anyway, mark e2e `blocked_by_environment`, and still run unit and integration tests.
- Prefer real dependencies the repo already uses in tests (test database, containers); fake only external providers the repo already fakes.
- Cover every acceptance criterion with at least one test and every high-risk area with at least one negative test.

## As reviewer
- Every acceptance criterion maps to at least one passing test in the test report.
- Negative scenarios exist for each high-risk area in the SDD.
- No existing test was weakened, skipped, or deleted.
- The full suite ran; a skipped full suite is a finding.
