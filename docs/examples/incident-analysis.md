# Incident Analysis

Use this example when a symptom or regression needs evidence-based diagnosis.

## Incident Request

```text
Use Forge ask mode for the incident scenario: repeated 500 responses from the checkout endpoint after the last deploy.
Use repository evidence and available logs.
Separate symptoms, likely causes, possible causes, mitigations, rollback, and next checks.
```

Expected output:

- symptom summary
- impact scope
- direct evidence
- likely cause only when supported
- possible causes when evidence is incomplete
- immediate mitigation options
- rollback possibility
- missing evidence

## Follow-Up Plan

```text
Use Forge plan mode for a bounded remediation of the confirmed checkout failure.
Do not redesign checkout flow or payment contracts.
```

Expected output:

- remediation scope
- risks
- validation path
- rollback
- explicit non-goals

## Execute Only After Approval

```text
Use Forge execute mode for the approved remediation ECP.
Stop if the observed symptom no longer matches the proposed fix.
```

Expected output:

- bounded changes
- validation performed
- remaining incident risk
- reviewer focus

Do not use an incident scenario to invent a root cause, redesign architecture, or apply unapproved fixes.
