# ADR 001: Policy check must precede execution — never inline or post-hoc

**Date:** 2026-04-11  
**Status:** Accepted  
**Author:** Ashutosh Rana

---

## Context

When an AI agent invokes a tool or executes an action in a regulated environment,
there are three possible enforcement points:

1. **Pre-execution** — check the policy before the action runs
2. **Inline** — check the policy inside the action implementation
3. **Post-execution** — check the result after the action completes and roll back if unauthorized

The choice of enforcement point determines whether unauthorized access is prevented
or merely detected after the fact. In regulated environments, detection after
unauthorized access has already occurred is not compliance — it is a disclosure event
that must itself be reported.

This ADR records the decision to enforce policy **only at the pre-execution point**.

---

## Decision

`GovernedActionGuard.guard()` evaluates `ActionPolicy.permits()` and all
escalation rules **before** calling `execute_fn`. If the policy denies the action,
`execute_fn` is never called.

The audit record is emitted unconditionally — whether the action is permitted,
denied, or escalated — at the pre-execution point, before any data is accessed.

---

## Rationale

### Why not inline enforcement?

Inline enforcement — checking access control inside the tool implementation — creates
three failure modes:

1. **Inconsistency across callers.** Any caller that bypasses the guard and calls
   the tool directly will not get compliance enforcement. The guard exists precisely
   to be the single enforcement point regardless of how the tool is invoked.

2. **Mixed responsibilities.** A tool that retrieves transcript data should not
   also contain FERPA logic. Regulations change; tool business logic changes
   independently. Separating them reduces the surface area of compliance risk.

3. **Untestable compliance.** If FERPA enforcement is inside the tool, you cannot
   test enforcement independently of the tool's behavior. Pre-execution enforcement
   can be tested in isolation with a mock `execute_fn`.

### Why not post-execution / result filtering?

Post-execution checking means the action has already run. In the context of data
access, the unauthorized data has already been:

- Retrieved from the data store (the access event has occurred)
- Possibly logged in the data store's access audit trail
- Processed through any downstream code between execution and the post-check

For FERPA (34 CFR § 99.32), HIPAA (45 CFR § 164.312(b)), and GLBA (16 CFR § 314.4(e)),
the obligation is to prevent unauthorized access, not to detect and report it after
the fact. Post-execution filtering satisfies neither the spirit nor the letter
of these requirements.

This is the same reasoning behind the pre-filter requirement in
`enterprise-rag-patterns`: unauthorized documents must not enter the retrieval
pipeline at all, not be removed from the result set after scoring and ranking.

### Why emit the audit record even on denial?

The audit record of a denied or escalated action is compliance evidence of the
enforcement working correctly. If a USCIS officer, auditor, or institution's
privacy officer asks "what happened when an agent attempted to export records?",
the answer must be in the audit log — not only successful accesses.

A log that only records permitted actions provides no evidence that the enforcement
mechanism ever activated.

---

## Consequences

**Positive:**
- Unauthorized data is never accessed — no exposure window between action execution
  and post-check filtering
- Policy and tool implementations are independently testable
- A single audit record per evaluation event covers all outcomes

**Negative:**
- Tools wrapped by `GovernedActionGuard` cannot perform their own fallback logic
  on denial; they must rely on the guard's error return or `raise_on_deny` mechanism
- Execution context available inside the tool is not available at policy evaluation
  time; callers must pass relevant context via the `context` dict

**Mitigations:**
- The `context` parameter to `guard()` allows callers to pass evaluation-relevant
  metadata (session ID, request type, etc.) without requiring the tool to expose it
- `raise_on_deny=True` is available for callers that need exception-based control flow

---

## Alternatives considered

| Alternative | Rejected because |
|-------------|-----------------|
| Inline enforcement in each tool | Inconsistent coverage; mixed responsibilities; untestable isolation |
| Post-execution result filter | Data access has already occurred; does not satisfy minimum-disclosure obligations |
| Decorator on tool methods | Same timing as pre-execution but harder to test; couples compliance to language-level decoration rather than explicit policy objects |
