"""
17_uk_ai_governance.py — Four-layer AI governance framework for AI systems
subject to UK law following the UK's post-Brexit regulatory approach.

Demonstrates a multi-layer governance orchestrator where four overlapping
UK regulatory obligations each impose independent requirements on AI systems
deployed in the United Kingdom:

    Layer 1  — UK GDPR Automated Decision-Making
               (UK GDPR Article 22, DPA 2018 Schedule 1):
               UK GDPR Article 22 gives individuals the right not to be
               subject to solely automated decisions that have legal or
               similarly significant effects. Solely automated decisions
               with legal effect require: a documented lawful basis,
               human review availability, and an opt-out mechanism.
               Where special category (sensitive) personal data is processed,
               explicit consent must also be obtained. Systems that are not
               solely automated, or that do not produce legally significant
               effects, proceed with a best-practice condition.

    Layer 2  — ICO AI Auditing Framework (2022):
               The Information Commissioner's Office AI Auditing Framework
               applies to any organisation using AI that processes personal
               data. It requires completed bias testing (Article 5(1)(f) UK
               GDPR — integrity and confidentiality), an explainability
               mechanism (Articles 13/14 UK GDPR — meaningful information
               about the logic involved), and validated accuracy before
               deployment. All three checks are mandatory; failure on any
               one triggers DENIED. Compliant systems receive an annual
               re-audit condition.

    Layer 3  — UK Equality Act 2010:
               The Equality Act 2010 prohibits indirect discrimination
               (s.19) against individuals sharing protected characteristics
               (age, disability, gender reassignment, marriage and civil
               partnership, pregnancy and maternity, race, religion or
               belief, sex, and sexual orientation). AI systems must
               complete a disparate-impact assessment and support reasonable
               adjustments for disability (s.20/21). Public sector bodies
               deploying AI are also subject to the Public Sector Equality
               Duty (PSED, s.149), which requires a documented equality
               impact assessment to be completed and published.

    Layer 4  — DSIT AI Safety Principles (UK AI White Paper 2023):
               The Department for Science, Innovation and Technology
               published five cross-sector AI principles in the 2023 UK
               AI White Paper (Cm 9458), intended to guide all AI systems
               regardless of sector:
                   Safety     — foreseeable harm testing required
                   Security   — adversarial (red-team) testing required
                   Fairness   — implicit in Layers 1–3; reinforced here
                   Accountability — a responsible officer must be designated
                   Transparency — stakeholders must be informed of AI use
                   Contestability — a mechanism to challenge AI decisions
                                    must be provided
               All five checks are mandatory. Compliant systems receive
               conditions aligned to the regulator-led implementation
               guidance expected under the forthcoming AI regulation.

No external dependencies required.

Run:
    python examples/17_uk_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class UKAIDecision(str, Enum):
    """Final governance decision for a UK AI system evaluation."""

    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DENIED = "DENIED"


class UKAIRiskTier(str, Enum):
    """
    Voluntary risk categorisation from the DSIT AI White Paper (2023).

    HIGH_RISK   — Significant potential for harm to individuals or society;
                  all safety, security and accountability checks are critical.
    MEDIUM_RISK — Moderate potential for harm; full compliance still required.
    LOW_RISK    — Limited harm potential; compliance checks apply with lighter
                  ongoing monitoring obligations.
    """

    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_RISK = "LOW_RISK"


# ---------------------------------------------------------------------------
# Frozen context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UKAIContext:
    """
    Governance review context for a UK AI system.

    Attributes
    ----------
    system_id : str
        Unique identifier for the AI system under review.
    system_name : str
        Human-readable name of the AI system.
    risk_tier : UKAIRiskTier
        Voluntary risk categorisation per the DSIT AI White Paper (2023).
    deploying_sector : str
        Sector in which the system is deployed, e.g. ``"financial_services"``,
        ``"healthcare"``, ``"public_sector"``, ``"retail"``.

    — UK GDPR Automated Decision-Making (Article 22, DPA 2018 Sch. 1) —

    is_solely_automated : bool
        True if decisions are made without any meaningful human involvement.
    decision_has_legal_effect : bool
        True if the decision has a legal or similarly significant effect on the
        data subject (e.g. credit refusal, employment rejection).
    processes_sensitive_categories : bool
        True if the system processes Article 9 special category data
        (health, racial/ethnic origin, biometric data, etc.).
    lawful_basis_documented : bool
        True if a documented lawful basis for solely automated decision-making
        exists (e.g. contract, explicit consent, or statutory authorisation).
    explicit_consent_obtained : bool
        True if explicit consent has been obtained for processing special
        category data in the automated decision-making context.
    human_review_available : bool
        True if data subjects can request human review of automated decisions.
    opt_out_mechanism_provided : bool
        True if an accessible opt-out mechanism is available to data subjects.

    — ICO AI Auditing Framework (2022) —

    bias_testing_completed : bool
        True if bias testing has been completed across protected characteristics
        in the training and output data (UK GDPR Article 5(1)(f)).
    explainability_mechanism_in_place : bool
        True if the system provides meaningful information about the logic of
        automated processing to data subjects (UK GDPR Articles 13/14).
    accuracy_validated : bool
        True if model accuracy has been formally validated and documented
        per the ICO AI Auditing Framework.

    — Equality Act 2010 —

    disparate_impact_assessment_done : bool
        True if a disparate impact assessment across protected characteristics
        has been completed (Equality Act 2010 s.19).
    reasonable_adjustments_supported : bool
        True if the system supports reasonable adjustments for disability
        (Equality Act 2010 s.20/21).
    public_sector_equality_duty : bool
        True if the deploying organisation is a public authority subject to
        the Public Sector Equality Duty (Equality Act 2010 s.149).
    equality_impact_documented : bool
        True if an equality impact assessment has been completed and documented
        (required for public authorities under s.149 PSED).

    — DSIT AI Safety Principles (UK AI White Paper 2023) —

    safety_testing_completed : bool
        True if foreseeable harm testing (safety principle) has been completed.
    adversarial_testing_done : bool
        True if adversarial/red-team testing (security principle) has been done.
    responsible_officer_designated : bool
        True if a named responsible officer (accountability principle) has been
        designated for this AI system.
    stakeholder_disclosure_made : bool
        True if affected stakeholders have been informed about AI use
        (transparency principle).
    contestability_mechanism_provided : bool
        True if a mechanism allowing individuals to challenge AI decisions
        (contestability principle) has been implemented.
    """

    system_id: str
    system_name: str
    risk_tier: UKAIRiskTier
    deploying_sector: str
    # UK GDPR ADM
    is_solely_automated: bool
    decision_has_legal_effect: bool
    processes_sensitive_categories: bool
    lawful_basis_documented: bool
    explicit_consent_obtained: bool
    human_review_available: bool
    opt_out_mechanism_provided: bool
    # ICO AI Auditing Framework
    bias_testing_completed: bool
    explainability_mechanism_in_place: bool
    accuracy_validated: bool
    # Equality Act 2010
    disparate_impact_assessment_done: bool
    reasonable_adjustments_supported: bool
    public_sector_equality_duty: bool
    equality_impact_documented: bool
    # DSIT Safety Principles
    safety_testing_completed: bool
    adversarial_testing_done: bool
    responsible_officer_designated: bool
    stakeholder_disclosure_made: bool
    contestability_mechanism_provided: bool


# ---------------------------------------------------------------------------
# Per-layer result
# ---------------------------------------------------------------------------


@dataclass
class UKAIGovernanceResult:
    """Result of a single UK AI governance layer evaluation."""

    layer: str
    decision: UKAIDecision = UKAIDecision.APPROVED
    findings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        """True if this layer produced a DENIED decision."""
        return self.decision == UKAIDecision.DENIED

    @property
    def has_conditions(self) -> bool:
        """True if this layer produced an APPROVED_WITH_CONDITIONS decision."""
        return self.decision == UKAIDecision.APPROVED_WITH_CONDITIONS


# ---------------------------------------------------------------------------
# Layer 1 — UK GDPR Automated Decision-Making
# ---------------------------------------------------------------------------


class UKGDPRAutomatedDecisionFilter:
    """
    Layer 1: UK GDPR Article 22 — Automated Decision-Making (ADM).

    Where an AI system makes solely automated decisions with legal or similarly
    significant effects, UK GDPR Article 22 requires: a documented lawful basis,
    availability of human review, and an accessible opt-out mechanism.  Where
    special category (sensitive) personal data is processed, DPA 2018 Schedule 1
    additionally requires explicit consent.

    Systems that are not solely automated, or whose decisions lack legal
    significance, receive an APPROVED_WITH_CONDITIONS with a best-practice note.

    References
    ----------
    UK GDPR — Article 22 (right not to be subject to solely automated decisions)
    UK GDPR — Recital 71 (safeguards for automated decision-making)
    DPA 2018 — Schedule 1 (conditions for processing special category data)
    ICO Guide to UK GDPR — Automated Decision-Making and Profiling
    """

    def evaluate(self, context: UKAIContext) -> UKAIGovernanceResult:  # noqa: C901
        result = UKAIGovernanceResult(layer="UK_GDPR_AUTOMATED_DECISION")

        if not (context.is_solely_automated and context.decision_has_legal_effect):
            # Article 22 obligations do not apply; issue best-practice note
            result.decision = UKAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "UK GDPR Article 22 (best practice): System is not solely "
                "automated or does not produce legally significant effects — "
                "Article 22 safeguards do not apply, but document the human "
                "involvement or non-significant nature to evidence compliance; "
                "review if system scope changes"
            )
            return result

        # Solely automated decision with legal/significant effect: full checks apply
        violations: List[str] = []

        if not context.lawful_basis_documented:
            violations.append(
                "UK GDPR Article 22(2): Solely automated decision with legal "
                "effect requires a documented lawful basis (contract, explicit "
                "consent, or authorised by UK law) — no lawful basis found"
            )

        if not context.human_review_available:
            violations.append(
                "UK GDPR Article 22(3): Data subjects must be able to obtain "
                "human intervention and to contest solely automated decisions — "
                "no human review mechanism is available"
            )

        if not context.opt_out_mechanism_provided:
            violations.append(
                "UK GDPR Article 22(3): Data subjects must be able to express "
                "their point of view and contest the decision — no opt-out or "
                "contestation mechanism has been provided"
            )

        if context.processes_sensitive_categories and not context.explicit_consent_obtained:
            violations.append(
                "UK GDPR Article 22(4) / DPA 2018 Schedule 1: Solely automated "
                "decisions involving special category personal data require "
                "explicit consent or another Schedule 1 DPA 2018 condition — "
                "explicit consent has not been obtained"
            )

        if violations:
            result.decision = UKAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = UKAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "UK GDPR Article 22: Solely automated ADM safeguards in place — "
                "maintain records of lawful basis, human review requests, and "
                "opt-out exercise; review annually and after each model update"
            )

        return result


# ---------------------------------------------------------------------------
# Layer 2 — ICO AI Auditing Framework
# ---------------------------------------------------------------------------


class ICOAIAuditingFilter:
    """
    Layer 2: ICO AI Auditing Framework (2022).

    The Information Commissioner's Office AI Auditing Framework requires
    organisations processing personal data via AI to complete three mandatory
    checks: bias testing, explainability, and accuracy validation.  Each
    missing check is an independent violation; all three must pass before
    deployment.  Compliant systems receive an annual re-audit condition.

    References
    ----------
    ICO — AI Auditing Framework (2022)
    UK GDPR — Article 5(1)(d) (accuracy principle)
    UK GDPR — Article 5(1)(f) (integrity and confidentiality)
    UK GDPR — Articles 13/14 (right to meaningful information about logic)
    ICO — Guidance on Explaining Decisions Made with AI (2022)
    """

    def evaluate(self, context: UKAIContext) -> UKAIGovernanceResult:
        result = UKAIGovernanceResult(layer="ICO_AI_AUDITING")
        violations: List[str] = []

        if not context.bias_testing_completed:
            violations.append(
                "Article 5(1)(f) UK GDPR: bias testing is required to ensure "
                "integrity and confidentiality of processing — bias testing has "
                "not been completed across protected characteristics in training "
                "and output data (ICO AI Auditing Framework, Bias section)"
            )

        if not context.explainability_mechanism_in_place:
            violations.append(
                "Article 13/14 UK GDPR: meaningful information about the logic "
                "involved in automated processing must be provided to data subjects "
                "— no explainability mechanism is in place "
                "(ICO AI Auditing Framework, Explainability section)"
            )

        if not context.accuracy_validated:
            violations.append(
                "ICO AI Auditing: accuracy must be validated and documented before "
                "deployment — Article 5(1)(d) UK GDPR accuracy principle requires "
                "that personal data processed by AI is kept accurate and up to date; "
                "no formal accuracy validation has been completed"
            )

        if violations:
            result.decision = UKAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = UKAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "ICO AI Auditing Framework: bias testing, explainability, and "
                "accuracy validation all complete — conduct annual re-audit and "
                "re-run bias testing whenever training data, model architecture, "
                "or deployment population changes materially"
            )

        return result


# ---------------------------------------------------------------------------
# Layer 3 — UK Equality Act 2010
# ---------------------------------------------------------------------------


class UKEqualityActFilter:
    """
    Layer 3: Equality Act 2010 — Indirect Discrimination and Reasonable
    Adjustments.

    Section 19 prohibits indirect discrimination: applying a provision,
    criterion, or practice (PCP) that puts persons sharing a protected
    characteristic at a particular disadvantage without objective justification.
    AI systems must complete a disparate impact assessment before deployment.

    Section 20/21 imposes a duty to make reasonable adjustments for disabled
    persons.  AI systems that cannot support reasonable adjustments may cause
    direct discrimination by exclusion.

    Section 149 (PSED) requires public authorities to have due regard to
    equality objectives; a documented equality impact assessment is required
    before deploying AI in a public sector context.

    References
    ----------
    Equality Act 2010 — s.19 (indirect discrimination)
    Equality Act 2010 — s.20/21 (duty to make reasonable adjustments)
    Equality Act 2010 — s.149 (Public Sector Equality Duty)
    Equality and Human Rights Commission — Guidance on the PSED
    """

    def evaluate(self, context: UKAIContext) -> UKAIGovernanceResult:
        result = UKAIGovernanceResult(layer="UK_EQUALITY_ACT")
        violations: List[str] = []

        if not context.disparate_impact_assessment_done:
            violations.append(
                "Equality Act 2010 s.19: AI system must not have unjustifiable "
                "disparate impact on persons sharing protected characteristics "
                "(age, disability, race, sex, religion, sexual orientation, etc.) — "
                "a disparate impact assessment has not been completed"
            )

        if not context.reasonable_adjustments_supported:
            violations.append(
                "Equality Act 2010 s.20/21: AI system must support reasonable "
                "adjustments for disability — the system does not currently "
                "accommodate reasonable adjustments (e.g. alternative interaction "
                "modes, additional processing time, assisted decision pathways)"
            )

        if context.public_sector_equality_duty and not context.equality_impact_documented:
            violations.append(
                "Equality Act 2010 s.149: Public sector bodies must have due "
                "regard to the need to advance equality of opportunity and foster "
                "good relations — a documented equality impact assessment (EIA) "
                "is required before deploying AI in a public sector context and "
                "has not been completed"
            )

        if violations:
            result.decision = UKAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = UKAIDecision.APPROVED_WITH_CONDITIONS
            conditions = [
                "Equality Act 2010 s.19: Disparate impact assessment complete — "
                "re-run assessment after each model update, training data change, "
                "or material expansion of deployment population"
            ]
            if context.public_sector_equality_duty:
                conditions.append(
                    "Equality Act 2010 s.149 PSED: Equality impact assessment "
                    "documented — publish findings in accordance with public sector "
                    "transparency obligations and review annually"
                )
            result.decision = UKAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions

        return result


# ---------------------------------------------------------------------------
# Layer 4 — DSIT AI Safety Principles
# ---------------------------------------------------------------------------


class DSITAISafetyPrinciplesFilter:
    """
    Layer 4: DSIT AI Safety Principles (UK AI White Paper 2023, Cm 9458).

    The Department for Science, Innovation and Technology defined five
    cross-sector principles applicable to all AI systems in the UK.
    Regulators are expected to implement these within their existing
    frameworks; they are currently non-statutory but carry significant
    policy weight and are expected to underpin forthcoming AI legislation.

    Principles checked:
        Safety         — foreseeable harm testing (physical, psychological,
                         financial, societal)
        Security       — adversarial/red-team testing to identify exploitable
                         vulnerabilities
        Accountability — a named responsible officer must be designated
        Transparency   — stakeholders must be informed that AI is being used
                         and how it affects them
        Contestability — individuals must have a mechanism to challenge
                         AI-driven decisions affecting them

    References
    ----------
    DSIT — A pro-innovation approach to AI regulation (2023, Cm 9458)
    DSIT — AI Safety Institute framework and guidance (2024)
    UK GDPR — Article 5(1)(f) (security principle, reinforces Safety/Security)
    """

    def evaluate(self, context: UKAIContext) -> UKAIGovernanceResult:
        result = UKAIGovernanceResult(layer="DSIT_AI_SAFETY_PRINCIPLES")
        violations: List[str] = []

        if not context.safety_testing_completed:
            violations.append(
                "DSIT AI White Paper: Safety principle — foreseeable harm testing "
                "is required before deployment; the system must be assessed for "
                "physical, psychological, financial, and societal harms across "
                "plausible use and misuse scenarios — no safety testing found"
            )

        if not context.adversarial_testing_done:
            violations.append(
                "DSIT AI White Paper: Security principle — adversarial testing "
                "(red-teaming) is required to identify exploitable vulnerabilities "
                "including prompt injection, data poisoning, and model inversion — "
                "adversarial testing has not been completed"
            )

        if not context.responsible_officer_designated:
            violations.append(
                "DSIT AI White Paper: Accountability principle — a named "
                "responsible officer must be designated with clear accountability "
                "for the AI system's compliance, performance, and incident "
                "response — no responsible officer has been designated"
            )

        if not context.stakeholder_disclosure_made:
            violations.append(
                "DSIT AI White Paper: Transparency principle — stakeholders "
                "affected by or interacting with the AI system must be informed "
                "about its use, capabilities, and limitations — stakeholder "
                "disclosure has not been made"
            )

        if not context.contestability_mechanism_provided:
            violations.append(
                "DSIT AI White Paper: Contestability principle — a mechanism "
                "allowing individuals to challenge AI-driven decisions that "
                "affect them must be provided — no contestability mechanism "
                "has been implemented"
            )

        if violations:
            result.decision = UKAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = UKAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "DSIT AI White Paper: All five cross-sector principles satisfied "
                "(Safety, Security, Accountability, Transparency, Contestability) — "
                "document evidence of each principle in the AI system register; "
                "re-assess Safety and Security testing after significant model "
                "updates; review Accountability assignment annually"
            )

        return result


# ---------------------------------------------------------------------------
# Four-layer orchestrator
# ---------------------------------------------------------------------------


@dataclass
class UKAIGovernanceReport:
    """Aggregated UK AI governance report across all four layers."""

    system_id: str
    system_name: str
    risk_tier: str
    final_decision: UKAIDecision
    layer_results: List[UKAIGovernanceResult] = field(default_factory=list)

    def summary(self) -> dict:
        """Return a serialisable summary of the full governance report."""
        return {
            "system_id": self.system_id,
            "system_name": self.system_name,
            "risk_tier": self.risk_tier,
            "final_decision": self.final_decision.value,
            "layers": [
                {
                    "layer": lr.layer,
                    "decision": lr.decision.value,
                    "findings": lr.findings,
                    "conditions": lr.conditions,
                }
                for lr in self.layer_results
            ],
        }


class UKAIGovernanceOrchestrator:
    """
    Four-layer UK AI governance orchestrator.

    Evaluation order:
        UK GDPR Automated Decision-Making  →  ICO AI Auditing  →
        UK Equality Act  →  DSIT AI Safety Principles

    Decision aggregation:
    - Any DENIED layer → final decision is DENIED
    - No DENIED + any APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS
    - All APPROVED → APPROVED

    All four layers are always evaluated regardless of earlier results.
    """

    def __init__(self) -> None:
        self._gdpr = UKGDPRAutomatedDecisionFilter()
        self._ico = ICOAIAuditingFilter()
        self._equality = UKEqualityActFilter()
        self._dsit = DSITAISafetyPrinciplesFilter()

    def evaluate(self, context: UKAIContext) -> UKAIGovernanceReport:
        """
        Evaluate all four UK governance layers and return an aggregated report.

        Parameters
        ----------
        context : UKAIContext
            The AI system context to evaluate.

        Returns
        -------
        UKAIGovernanceReport
            Full report containing per-layer results and a single final decision.
        """
        layer_results = [
            self._gdpr.evaluate(context),
            self._ico.evaluate(context),
            self._equality.evaluate(context),
            self._dsit.evaluate(context),
        ]

        if any(lr.is_denied for lr in layer_results):
            final = UKAIDecision.DENIED
        elif any(lr.has_conditions for lr in layer_results):
            final = UKAIDecision.APPROVED_WITH_CONDITIONS
        else:
            final = UKAIDecision.APPROVED

        return UKAIGovernanceReport(
            system_id=context.system_id,
            system_name=context.system_name,
            risk_tier=context.risk_tier.value,
            final_decision=final,
            layer_results=layer_results,
        )


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_public_sector_ctx() -> UKAIContext:
    """Base context: fully compliant HIGH_RISK public sector HR AI system."""
    return UKAIContext(
        system_id="UK-AI-001",
        system_name="Public Sector HR Screening System",
        risk_tier=UKAIRiskTier.HIGH_RISK,
        deploying_sector="public_sector",
        # UK GDPR ADM
        is_solely_automated=True,
        decision_has_legal_effect=True,
        processes_sensitive_categories=False,
        lawful_basis_documented=True,
        explicit_consent_obtained=False,
        human_review_available=True,
        opt_out_mechanism_provided=True,
        # ICO
        bias_testing_completed=True,
        explainability_mechanism_in_place=True,
        accuracy_validated=True,
        # Equality Act
        disparate_impact_assessment_done=True,
        reasonable_adjustments_supported=True,
        public_sector_equality_duty=True,
        equality_impact_documented=True,
        # DSIT
        safety_testing_completed=True,
        adversarial_testing_done=True,
        responsible_officer_designated=True,
        stakeholder_disclosure_made=True,
        contestability_mechanism_provided=True,
    )


def scenario_a_compliant_public_sector_hr() -> None:
    """
    Scenario A: Fully compliant HIGH_RISK public sector HR AI (automated
    shortlisting) — expected APPROVED_WITH_CONDITIONS (conditions from all
    layers since solely automated with legal effect).
    """
    print("\n--- Scenario A: Compliant PUBLIC SECTOR HR Screening AI (HIGH_RISK) ---")
    orch = UKAIGovernanceOrchestrator()
    ctx = _compliant_public_sector_ctx()
    report = orch.evaluate(ctx)
    print(f"  Final decision: {report.final_decision.value}")
    for lr in report.layer_results:
        status = "CONDITIONS" if lr.has_conditions else lr.decision.value
        print(f"  [{lr.layer}] {lr.decision.value}")
        for cond in lr.conditions:
            print(f"    Condition: {cond[:88]}...")


def scenario_b_loan_decision_no_human_review() -> None:
    """
    Scenario B: Solely automated loan decision system — no human review
    available and no opt-out — expected DENIED (UK GDPR ADM violations).
    """
    print("\n--- Scenario B: Automated Loan Decision — No Human Review --- DENIED ---")
    orch = UKAIGovernanceOrchestrator()
    base = _compliant_public_sector_ctx()
    ctx = UKAIContext(
        system_id="UK-AI-002",
        system_name="Automated Loan Decisioning Engine",
        risk_tier=UKAIRiskTier.HIGH_RISK,
        deploying_sector="financial_services",
        is_solely_automated=True,
        decision_has_legal_effect=True,
        processes_sensitive_categories=False,
        lawful_basis_documented=True,
        explicit_consent_obtained=False,
        human_review_available=False,          # VIOLATION
        opt_out_mechanism_provided=False,      # VIOLATION
        bias_testing_completed=base.bias_testing_completed,
        explainability_mechanism_in_place=base.explainability_mechanism_in_place,
        accuracy_validated=base.accuracy_validated,
        disparate_impact_assessment_done=base.disparate_impact_assessment_done,
        reasonable_adjustments_supported=base.reasonable_adjustments_supported,
        public_sector_equality_duty=False,
        equality_impact_documented=False,
        safety_testing_completed=base.safety_testing_completed,
        adversarial_testing_done=base.adversarial_testing_done,
        responsible_officer_designated=base.responsible_officer_designated,
        stakeholder_disclosure_made=base.stakeholder_disclosure_made,
        contestability_mechanism_provided=base.contestability_mechanism_provided,
    )
    report = orch.evaluate(ctx)
    print(f"  Final decision: {report.final_decision.value}")
    gdpr_layer = next(lr for lr in report.layer_results
                      if lr.layer == "UK_GDPR_AUTOMATED_DECISION")
    print(f"  [{gdpr_layer.layer}] {gdpr_layer.decision.value}")
    for finding in gdpr_layer.findings:
        print(f"    Finding: {finding[:88]}...")


def scenario_c_missing_bias_testing() -> None:
    """
    Scenario C: Healthcare AI system with bias testing and explainability both
    missing — expected DENIED (ICO AI Auditing violations).
    """
    print("\n--- Scenario C: Healthcare AI — Missing Bias Testing --- DENIED ---")
    orch = UKAIGovernanceOrchestrator()
    base = _compliant_public_sector_ctx()
    ctx = UKAIContext(
        system_id="UK-AI-003",
        system_name="Clinical Triage Risk Scoring System",
        risk_tier=UKAIRiskTier.HIGH_RISK,
        deploying_sector="healthcare",
        is_solely_automated=False,             # human-in-the-loop
        decision_has_legal_effect=False,
        processes_sensitive_categories=True,
        lawful_basis_documented=True,
        explicit_consent_obtained=True,
        human_review_available=True,
        opt_out_mechanism_provided=True,
        bias_testing_completed=False,          # VIOLATION
        explainability_mechanism_in_place=False,  # VIOLATION
        accuracy_validated=True,
        disparate_impact_assessment_done=base.disparate_impact_assessment_done,
        reasonable_adjustments_supported=base.reasonable_adjustments_supported,
        public_sector_equality_duty=True,
        equality_impact_documented=True,
        safety_testing_completed=base.safety_testing_completed,
        adversarial_testing_done=base.adversarial_testing_done,
        responsible_officer_designated=base.responsible_officer_designated,
        stakeholder_disclosure_made=base.stakeholder_disclosure_made,
        contestability_mechanism_provided=base.contestability_mechanism_provided,
    )
    report = orch.evaluate(ctx)
    print(f"  Final decision: {report.final_decision.value}")
    ico_layer = next(lr for lr in report.layer_results if lr.layer == "ICO_AI_AUDITING")
    print(f"  [{ico_layer.layer}] {ico_layer.decision.value}")
    for finding in ico_layer.findings:
        print(f"    Finding: {finding[:88]}...")


def scenario_d_low_risk_non_automated() -> None:
    """
    Scenario D: LOW_RISK retail recommendation engine — not solely automated,
    no legal effects, private sector deployer.  Expected APPROVED_WITH_CONDITIONS
    (best-practice conditions from all layers).
    """
    print("\n--- Scenario D: LOW_RISK Retail Recommendation Engine ---")
    orch = UKAIGovernanceOrchestrator()
    ctx = UKAIContext(
        system_id="UK-AI-004",
        system_name="Product Recommendation Engine",
        risk_tier=UKAIRiskTier.LOW_RISK,
        deploying_sector="retail",
        is_solely_automated=False,
        decision_has_legal_effect=False,
        processes_sensitive_categories=False,
        lawful_basis_documented=True,
        explicit_consent_obtained=False,
        human_review_available=True,
        opt_out_mechanism_provided=True,
        bias_testing_completed=True,
        explainability_mechanism_in_place=True,
        accuracy_validated=True,
        disparate_impact_assessment_done=True,
        reasonable_adjustments_supported=True,
        public_sector_equality_duty=False,
        equality_impact_documented=False,
        safety_testing_completed=True,
        adversarial_testing_done=True,
        responsible_officer_designated=True,
        stakeholder_disclosure_made=True,
        contestability_mechanism_provided=True,
    )
    report = orch.evaluate(ctx)
    print(f"  Final decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")


if __name__ == "__main__":
    scenario_a_compliant_public_sector_hr()
    scenario_b_loan_decision_no_human_review()
    scenario_c_missing_bias_testing()
    scenario_d_low_risk_non_automated()
