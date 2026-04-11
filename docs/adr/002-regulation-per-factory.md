# ADR 002: One policy factory per regulation and role — not a universal policy object

**Date:** 2026-04-11  
**Status:** Accepted  
**Author:** Ashutosh Rana

---

## Context

Regulated access control involves two dimensions:

1. **Regulation**: FERPA, HIPAA, GLBA, GDPR — each with distinct statutory definitions
   of what constitutes protected data, what access is authorized, and what must be logged.

2. **Role**: Within each regulation, the authorized scope differs by actor role.
   Under HIPAA, a treating provider may access clinical notes that a billing staff
   member may not. Under FERPA, an academic advisor may access any advisee's records
   while a student may only access their own.

The design question was: should the library provide one generic `ActionPolicy`
constructor that callers configure from scratch, or should it provide pre-built
factories for each regulation–role combination?

---

## Decision

The library exposes:

1. **Low-level primitives** (`ActionPolicy`, `EscalationRule`) — for callers who
   need full control and are building domain-specific policies not covered by the
   provided factories.

2. **Regulation-specific factory functions** in `regulated_ai_governance.regulations.*`
   — for the most common role combinations within each regulation. Each factory
   returns a fully configured `ActionPolicy` with the correct allow/deny sets and
   escalation rules for that regulation and role.

The factories follow the naming pattern `make_{regulation}_{role}_policy()`, e.g.:
- `make_ferpa_student_policy()`
- `make_hipaa_treating_provider_policy()`
- `make_glba_loan_officer_policy()`

---

## Rationale

### Why not a single universal policy object?

A universal policy object with all regulations and all roles in one configuration
creates several problems:

1. **Misconfiguration is silent.** If a caller building a FERPA student agent
   accidentally leaves HIPAA PHI actions in the allowed set, the policy is wrong
   but no error is raised. The factory pattern makes it structurally impossible to
   misconfigure a FERPA policy with HIPAA-specific actions.

2. **Regulations are not additive.** FERPA and HIPAA are not subsets of each other.
   A record can be both a FERPA education record and a HIPAA health record (e.g.,
   a student's mental health records at a university). The applicable rule depends
   on the type of institution and how the record is maintained. A combined policy
   object would obscure this distinction and make compliance analysis harder, not
   easier.

3. **Role-specific defaults are non-obvious.** The difference between a treating
   provider's HIPAA access rights and a billing staff member's access rights is
   defined in 45 CFR § 164.506. A caller building a billing agent from a generic
   policy object must know and correctly implement this distinction. A factory
   function encodes it correctly by default.

### Why keep the low-level primitives?

Two reasons:

1. **Extensibility.** The provided factories cover the most common cases. A caller
   building an agent for a GDPR data subject request, an IRB-approved genomics
   research pipeline, or a state privacy regulation not covered by the library needs
   the primitives to construct a correct policy without forking the library.

2. **Testability.** The factories are implemented in terms of the primitives and
   tested against them. Callers who extend the library with new policies can test
   their configurations using the same test patterns as the built-in factories.

### Why include escalation rules in the factories?

The most common compliance failure mode in enterprise AI is not unauthorized data
access — it is unauthorized data *export* or *sharing*. An agent that reads a
student's transcript is within FERPA scope; an agent that emails that transcript
to an external address is a reportable FERPA violation.

The factories include escalation rules for export and external-share action patterns
by default because these are the highest-risk actions that regulations require
institutions to track and control. Callers who do not need escalation can override
`escalation_rules=[]` when constructing the policy, but the default is conservative.

### Factory function signature design

Each factory function accepts keyword arguments for the escalation target and any
role-specific overrides, with safe defaults for all parameters. This allows a caller
to use the factory with zero configuration for the default case:

```python
policy = make_ferpa_student_policy()  # zero configuration, safe defaults
```

and customize only what differs from the default:

```python
policy = make_ferpa_student_policy(
    allowed_record_categories={"academic_record"},  # narrower than default
    escalate_exports_to="my_compliance_queue",      # custom routing
)
```

---

## Consequences

**Positive:**
- The correct policy for a given regulation and role is one function call
- Misconfiguration of regulation-specific logic is structurally prevented by the factory
- Factories are independently testable against their statutory definitions
- The low-level primitives remain available for non-covered cases

**Negative:**
- Each new regulation requires new factory functions; the library is not self-extending
- Factory functions embed regulatory interpretations that may differ from an institution's
  legal counsel's reading of the same regulation

**Mitigations:**
- The factory docstrings cite the specific regulatory section they implement, allowing
  callers to compare the implementation against the text of the regulation
- The low-level `ActionPolicy` constructor remains the authoritative extension point
  for institutions whose legal interpretation differs from the factory defaults

---

## Alternatives considered

| Alternative | Rejected because |
|-------------|-----------------|
| Single universal `CompliancePolicy(regulation=..., role=...)` object | Implicit cross-regulation mixing; silent misconfiguration; obscures role-specific statutory differences |
| Class hierarchy per regulation (`FERPAPolicy(StudentRole)`) | Over-engineered; inheritance creates implicit coupling between regulations that are independent statutes |
| Configuration file (YAML/JSON policy definitions) | Adds a serialization layer with no benefit for a code-first library; compliance logic should be auditable as code |
