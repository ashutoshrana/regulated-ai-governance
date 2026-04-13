# Implementation Note 01 — Multi-Framework AI Governance: Why Single-Layer Compliance Fails

**Repo:** `regulated-ai-governance`
**Relates to:** [`examples/03_multi_framework_orchestration.py`](../examples/03_multi_framework_orchestration.py), [`examples/05_healthcare_ai_governance.py`](../examples/05_healthcare_ai_governance.py)
**ADR cross-reference:** [ADR-001 (policy-before-execution)](adr/001-policy-before-execution.md), [ADR-004 (framework-agnostic-core)](adr/004-framework-agnostic-core.md)

---

## The failure mode: a single compliance layer that does not fail loudly

Most AI systems in regulated environments start with one compliance check: a HIPAA policy guard, a FERPA scope filter, or an IAM role check. The first deployment works fine. The second deployment adds a new regulation. Rather than adding an independent guard, teams extend the existing policy with extra conditions.

The result is a monolithic policy object with sixty allowed-actions, a dozen denied-actions, and escalation rules that interact in ways the original author did not anticipate. The policy passes CI because unit tests cover the cases that were written; they do not cover the cases that were not imagined.

This is how a healthcare RAG system ends up HIPAA-compliant but NIST AI RMF-unaware — and why a clinician override of an AI recommendation goes unlogged.

---

## Why the `GovernanceOrchestrator` uses deny-all aggregation

The core design decision in this library is that **if any configured framework denies an action, the overall decision is DENY.** There is no weighted vote. There is no "majority rules." Every framework has veto power.

This is not arbitrary conservatism. It reflects a legal reality: compliance obligations are conjunctive, not disjunctive. An AI action that violates GDPR is illegal even if it is fully compliant with HIPAA. HIPAA compliance does not confer GDPR compliance. NIST AI RMF conformance does not satisfy EU AI Act requirements. Each regulation is an independent obligation.

The deny-all model ensures that adding a new framework never silently reduces the protection of existing frameworks. It also makes policy failures loud: when an action is denied, the `ComprehensiveAuditReport.framework_results` list identifies precisely which framework(s) denied and why.

**Counterargument and response:** Some teams argue that deny-all is too restrictive for workflows where only one framework applies (e.g., a US-only system that will never be subject to GDPR). The correct response is not to weaken the aggregator — it is to configure only the frameworks that apply. Use `GovernanceOrchestrator(framework_guards=[...])` to include only the guards relevant to your deployment context. The orchestrator is a composition tool; its guarantee is only as narrow as the guards you register.

---

## Escalation routing: why different violations go to different humans

Not all denied actions are alike. A HIPAA minimum-necessary violation should route to a privacy officer. A NIST AI RMF human-oversight gap should route to a clinical reviewer. An EU AI Act high-risk AI classification concern should route to a legal team. Routing everything to a single on-call queue wastes attention and delays resolution.

The `EscalationRule` in each `ActionPolicy` carries an `escalation_target` — a string identifier for the team or role that should handle the escalation. The `ComprehensiveAuditReport` preserves per-framework escalation targets so that downstream SIEM and GRC systems can route alerts correctly.

Design principle: escalation targets are strings, not function references. This keeps the governance library independent of your alerting infrastructure. The sink function you pass to `GovernanceOrchestrator(audit_sink=...)` owns the routing logic.

---

## Skip vs. deny: jurisdictional applicability

A framework that does not apply to a deployment is different from a framework that applies and permits an action. The `FrameworkGuard` supports a `jurisdiction_applies` flag (or a callable that takes the actor context and returns a bool). When jurisdiction does not apply, the guard is **skipped** — it does not vote, and the `ComprehensiveAuditReport` records it as `skipped=True`.

This matters for two reasons:

1. **Correctness:** A system operating entirely in the US should not be denied because it fails an EU AI Act check that was never applicable.
2. **Auditability:** The audit trail shows that the framework was evaluated for applicability and explicitly skipped — not ignored. An auditor reading the log can see that the team made a deliberate jurisdictional determination, not an oversight.

The distinction between `skipped` and `permitted` is preserved in the `framework_results` list on every `ComprehensiveAuditReport`.

---

## What breaks when HIPAA exists but NIST AI RMF does not

A concrete failure scenario illustrates why this matters.

A clinical decision support system is deployed with a HIPAA policy guard. The HIPAA guard correctly restricts ePHI access to treating providers. The system is approved for production.

Six months later, the system adds an `recommend_treatment_plan` action. The HIPAA guard has no objection — recommending a treatment plan does not involve disclosing ePHI to an unauthorized party. The action is permitted.

But NIST AI RMF AI 600-1 (GenAI profile) identifies high-risk AI actions in clinical settings as requiring human oversight. Without a NIST guard, `recommend_treatment_plan` executes autonomously. A clinician does not review the recommendation before it appears in the patient record.

The system is HIPAA-compliant. It is not safe.

Multi-framework governance prevents this class of failure by making it structurally impossible to add a new high-stakes action category without explicitly evaluating it against every configured framework.

---

## Implementing a new framework: the three-step pattern

Adding a new regulation or standard to an existing `GovernanceOrchestrator` requires three steps:

1. **Define the policy.** Create an `ActionPolicy` with the allowed actions, denied actions, and escalation rules that reflect the regulation's requirements. For regulations with published factory functions (e.g., `make_dora_ict_management_policy()`), start there and override as needed.

2. **Wrap it in a guard.** Instantiate a `GovernedActionGuard` with the policy, the regulation label (used in audit records), and the actor ID. Set `block_on_escalation=True` for regulations where escalation means "do not proceed" (most safety-critical standards). Set `block_on_escalation=False` for regulations where escalation means "proceed but notify" (some audit-trail-only requirements).

3. **Register it.** Add a `FrameworkGuard(regulation="...", guard=...)` to the `framework_guards` list in your `GovernanceOrchestrator`. No other code changes are needed. The orchestrator's deny-all aggregation automatically includes the new framework in every subsequent evaluation.

See `examples/05_healthcare_ai_governance.py` for a complete three-framework example using HIPAA, NIST AI RMF, and EU AI Act.

---

## Audit-only (shadow) mode: rolling out a new framework safely

Adding a new framework to a production system carries risk: the new framework might deny actions that were previously allowed, breaking workflows that depend on those actions.

`GovernanceOrchestrator(audit_only=True)` evaluates all frameworks and emits a full `ComprehensiveAuditReport` per evaluation — but **does not block any action**. This enables:

- **Shadow-mode compliance assessment:** run the new framework in production for 30 days and collect audit data before enforcing it.
- **A/B compliance testing:** compare the deny rate of a proposed policy against a more permissive baseline before switching.
- **Incident post-mortem replay:** replay a production action log against a new framework to determine whether the framework would have prevented an incident.

Switch from shadow mode to enforcement by removing `audit_only=True`. The audit trail is identical in both modes, so the transition is zero-configuration.

See `examples/05_healthcare_ai_governance.py`, Scenario E for a runnable shadow-mode demonstration.
