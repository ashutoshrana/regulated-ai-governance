"""
15_public_sector_ai_governance.py — Four-layer AI governance framework for
AI systems deployed by or on behalf of US federal agencies.

Demonstrates a multi-layer governance orchestrator where four overlapping
regulatory frameworks each impose independent obligations on AI/ML systems
used in federal agency operations:

    Layer 1  — OMB M-24-10 (Advancing Governance, Innovation, and Risk
               Management for Federal Agency Use of AI, March 28, 2024):
               Federal agencies must designate a Chief AI Officer (CAIO)
               and establish an AI Governance Board. AI use cases must be
               inventoried. Rights-impacting AI (affecting individual rights,
               benefits, or services) requires human review before adverse
               decisions and an appeal mechanism. Safety-impacting AI
               requires pre-deployment safety testing, monitoring, and
               incident reporting. Minimum-impact AI is exempt from
               most requirements.

    Layer 2  — Executive Order 14110 (Safe, Secure, and Trustworthy
               Development and Use of AI, October 30, 2023):
               Developers of dual-use foundation models must conduct
               adversarial testing (red-teaming) for CBRN threats and
               cybersecurity misuse before deployment. Safety evaluations
               are required for AI used in critical infrastructure or
               safety-critical functions. TEVV (Test, Evaluate, Verify,
               Validate) frameworks apply to high-risk applications.

    Layer 3  — NIST AI RMF (AI Risk Management Framework, AI 100-1, 2023):
               The four functions — GOVERN, MAP, MEASURE, MANAGE — each
               impose documentation and process requirements. GOVERN:
               organizational AI risk policies and accountability structures.
               MAP: context establishment, risk identification, AI system
               impact categorization. MEASURE: quantitative risk metrics,
               bias/fairness testing, performance benchmarks. MANAGE: risk
               response plans, remediation tracking, monitoring cadence.

    Layer 4  — Section 508 / ADA Accessibility (29 U.S.C. §794d;
               42 U.S.C. §12132):
               AI outputs used in public-facing federal services must comply
               with Section 508 of the Rehabilitation Act: accessible to
               individuals with disabilities. AI decisions affecting benefits
               or services must be explainable in plain language. Automated
               decisions must include a human review option for affected
               individuals (ties directly to OMB M-24-10 rights-impacting
               requirements).

No external dependencies required.

Run:
    python examples/15_public_sector_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, List, Optional


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class FederalAIUseCase(str, Enum):
    """Federal agency AI use cases under OMB M-24-10 classification."""

    BENEFITS_DETERMINATION = "BENEFITS_DETERMINATION"    # Rights-impacting
    ENFORCEMENT_ACTION = "ENFORCEMENT_ACTION"            # Rights-impacting
    CRIMINAL_JUSTICE_RISK = "CRIMINAL_JUSTICE_RISK"      # Rights-impacting
    IMMIGRATION_ADJUDICATION = "IMMIGRATION_ADJUDICATION"  # Rights-impacting
    CRITICAL_INFRASTRUCTURE = "CRITICAL_INFRASTRUCTURE"  # Safety-impacting
    MILITARY_OPERATIONS = "MILITARY_OPERATIONS"          # Safety-impacting
    SAFETY_CRITICAL_SYSTEMS = "SAFETY_CRITICAL_SYSTEMS"  # Safety-impacting
    CITIZEN_SERVICES_CHAT = "CITIZEN_SERVICES_CHAT"      # Low-risk public service
    INTERNAL_ANALYTICS = "INTERNAL_ANALYTICS"            # Minimum-impact
    DOCUMENT_CLASSIFICATION = "DOCUMENT_CLASSIFICATION"  # Minimum-impact


class AIImpactLevel(str, Enum):
    """
    OMB M-24-10 impact classification for federal AI use cases.

    RIGHTS_IMPACTING  — affects individual rights, benefits, or services
    SAFETY_IMPACTING  — affects critical infrastructure or safety functions
    LOW_IMPACT        — public-facing service, moderate risk
    MINIMUM_IMPACT    — internal, no direct impact on public
    """

    RIGHTS_IMPACTING = "RIGHTS_IMPACTING"
    SAFETY_IMPACTING = "SAFETY_IMPACTING"
    LOW_IMPACT = "LOW_IMPACT"
    MINIMUM_IMPACT = "MINIMUM_IMPACT"


class EO14110RiskTier(str, Enum):
    """
    EO 14110 risk tier for the AI model.

    DUAL_USE_FOUNDATION — foundation model capable of CBRN/cyber misuse
    SAFETY_CRITICAL     — used in critical infrastructure or safety functions
    HIGH_RISK           — high-stakes but not safety-critical
    STANDARD            — standard government AI, no dual-use risk
    """

    DUAL_USE_FOUNDATION = "DUAL_USE_FOUNDATION"
    SAFETY_CRITICAL = "SAFETY_CRITICAL"
    HIGH_RISK = "HIGH_RISK"
    STANDARD = "STANDARD"


class NISTRMFLevel(str, Enum):
    """
    NIST AI RMF implementation maturity level.

    FULL    — all four functions (GOVERN/MAP/MEASURE/MANAGE) documented
    PARTIAL — some functions documented; gaps noted
    MINIMAL — basic AI inventory only
    NONE    — no RMF implementation
    """

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    MINIMAL = "MINIMAL"
    NONE = "NONE"


class PublicSectorGovernanceDecision(str, Enum):
    """Final governance decision for the AI system."""

    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DENIED = "DENIED"


# ---------------------------------------------------------------------------
# Rights-impacting use cases (OMB M-24-10)
# ---------------------------------------------------------------------------

_RIGHTS_IMPACTING_USE_CASES: FrozenSet[FederalAIUseCase] = frozenset({
    FederalAIUseCase.BENEFITS_DETERMINATION,
    FederalAIUseCase.ENFORCEMENT_ACTION,
    FederalAIUseCase.CRIMINAL_JUSTICE_RISK,
    FederalAIUseCase.IMMIGRATION_ADJUDICATION,
})

_SAFETY_IMPACTING_USE_CASES: FrozenSet[FederalAIUseCase] = frozenset({
    FederalAIUseCase.CRITICAL_INFRASTRUCTURE,
    FederalAIUseCase.MILITARY_OPERATIONS,
    FederalAIUseCase.SAFETY_CRITICAL_SYSTEMS,
})

_MINIMUM_IMPACT_USE_CASES: FrozenSet[FederalAIUseCase] = frozenset({
    FederalAIUseCase.INTERNAL_ANALYTICS,
    FederalAIUseCase.DOCUMENT_CLASSIFICATION,
})


# ---------------------------------------------------------------------------
# Context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PublicSectorAIContext:
    """
    Governance review context for a federal AI system.

    Attributes
    ----------
    system_id : str
        Unique AI system identifier.
    system_name : str
        Human-readable system name.
    use_case : FederalAIUseCase
        Operational use case classification.
    impact_level : AIImpactLevel
        OMB M-24-10 impact classification.
    eo14110_risk_tier : EO14110RiskTier
        EO 14110 risk tier.
    nist_rmf_level : NISTRMFLevel
        NIST AI RMF implementation maturity.
    deploying_agency : str
        Name of the federal agency deploying the system.
    caio_designated : bool
        True if the agency has designated a Chief AI Officer.
    ai_inventory_maintained : bool
        True if the agency maintains an AI use case inventory.
    human_review_available : bool
        True if a human can review and override automated decisions
        (required for rights-impacting use cases).
    appeal_mechanism_exists : bool
        True if affected individuals have an appeal mechanism.
    pre_deployment_safety_testing_done : bool
        True if pre-deployment safety testing has been completed.
    incident_reporting_active : bool
        True if an AI incident reporting mechanism is operational.
    red_team_assessment_completed : bool
        True if adversarial red-teaming has been done (required for
        DUAL_USE_FOUNDATION models).
    tevv_framework_applied : bool
        True if TEVV (Test, Evaluate, Verify, Validate) has been applied.
    nist_govern_documented : bool
        True if NIST RMF GOVERN function is documented.
    nist_map_completed : bool
        True if NIST RMF MAP function is completed.
    nist_measure_quantified : bool
        True if NIST RMF MEASURE function has quantitative metrics.
    nist_manage_plan_exists : bool
        True if NIST RMF MANAGE function has a risk response plan.
    section_508_compliant : bool
        True if AI outputs are Section 508 accessible.
    plain_language_explanations : bool
        True if AI decisions are explainable in plain language to
        affected individuals.
    """

    system_id: str
    system_name: str
    use_case: FederalAIUseCase
    impact_level: AIImpactLevel
    eo14110_risk_tier: EO14110RiskTier
    nist_rmf_level: NISTRMFLevel
    deploying_agency: str
    caio_designated: bool
    ai_inventory_maintained: bool
    human_review_available: bool
    appeal_mechanism_exists: bool
    pre_deployment_safety_testing_done: bool
    incident_reporting_active: bool
    red_team_assessment_completed: bool
    tevv_framework_applied: bool
    nist_govern_documented: bool
    nist_map_completed: bool
    nist_measure_quantified: bool
    nist_manage_plan_exists: bool
    section_508_compliant: bool
    plain_language_explanations: bool


# ---------------------------------------------------------------------------
# Per-layer result
# ---------------------------------------------------------------------------


@dataclass
class PublicSectorGovernanceResult:
    """Result of a single governance layer evaluation."""

    layer: str
    decision: PublicSectorGovernanceDecision = PublicSectorGovernanceDecision.APPROVED
    findings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        return self.decision == PublicSectorGovernanceDecision.DENIED

    @property
    def has_conditions(self) -> bool:
        return self.decision == PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS


# ---------------------------------------------------------------------------
# Layer 1 — OMB M-24-10
# ---------------------------------------------------------------------------


class OMBM2410Filter:
    """
    Layer 1: OMB M-24-10 Federal AI Governance (March 2024).

    Baseline requirements for all non-minimum-impact AI:
    - Agency must have a CAIO designated
    - AI use case must be in the agency inventory

    Rights-impacting AI additional requirements:
    - Human review before adverse decisions
    - Appeal mechanism for affected individuals

    Safety-impacting AI additional requirements:
    - Pre-deployment safety testing
    - Incident reporting mechanism

    Minimum-impact AI: only inventory required; other requirements exempt.

    References
    ----------
    OMB M-24-10 — Advancing Governance, Innovation, and Risk Management
    for Agency Use of Artificial Intelligence (March 28, 2024)
    """

    def evaluate(self, context: PublicSectorAIContext) -> PublicSectorGovernanceResult:
        result = PublicSectorGovernanceResult(layer="OMB_M24_10")
        violations: list[str] = []
        conditions: list[str] = []

        # Minimum-impact: only inventory required
        if context.impact_level == AIImpactLevel.MINIMUM_IMPACT:
            if not context.ai_inventory_maintained:
                violations.append(
                    "OMB M-24-10: AI use case must be included in agency AI "
                    "inventory even for minimum-impact applications [§4(b)(i)]"
                )
        else:
            # All non-minimum-impact AI: CAIO + inventory
            if not context.caio_designated:
                violations.append(
                    "OMB M-24-10: Agency has not designated a Chief AI Officer "
                    "(CAIO) as required [§3(a)]"
                )
            if not context.ai_inventory_maintained:
                violations.append(
                    "OMB M-24-10: AI use case not included in agency AI "
                    "inventory [§4(b)(i)]"
                )

        # Rights-impacting: human review + appeal
        if context.use_case in _RIGHTS_IMPACTING_USE_CASES:
            if not context.human_review_available:
                violations.append(
                    "OMB M-24-10: Human review of automated decisions required "
                    "for rights-impacting AI before adverse action [§5(c)(i)]"
                )
            if not context.appeal_mechanism_exists:
                violations.append(
                    "OMB M-24-10: Appeal mechanism required for rights-impacting "
                    "AI decisions affecting individuals [§5(c)(ii)]"
                )

        # Safety-impacting: pre-deployment testing + incident reporting
        if context.use_case in _SAFETY_IMPACTING_USE_CASES:
            if not context.pre_deployment_safety_testing_done:
                violations.append(
                    "OMB M-24-10: Pre-deployment safety testing required for "
                    "safety-impacting AI [§5(d)(i)]"
                )
            if not context.incident_reporting_active:
                violations.append(
                    "OMB M-24-10: AI incident reporting mechanism required for "
                    "safety-impacting applications [§5(d)(ii)]"
                )

        # Conditions for rights/safety-impacting with full compliance
        if not violations:
            if context.use_case in _RIGHTS_IMPACTING_USE_CASES:
                conditions.append(
                    "OMB M-24-10: Rights-impacting AI — annual review of human "
                    "review logs and appeal rates required [§5(c)(iii)]"
                )
            elif context.use_case in _SAFETY_IMPACTING_USE_CASES:
                conditions.append(
                    "OMB M-24-10: Safety-impacting AI — continuous performance "
                    "monitoring and incident reporting required [§5(d)(iii)]"
                )

        if violations:
            result.decision = PublicSectorGovernanceDecision.DENIED
            result.findings = violations
        elif conditions:
            result.decision = PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
        else:
            result.decision = PublicSectorGovernanceDecision.APPROVED

        return result


# ---------------------------------------------------------------------------
# Layer 2 — EO 14110
# ---------------------------------------------------------------------------


class EO14110Filter:
    """
    Layer 2: Executive Order 14110 — Safe, Secure, and Trustworthy AI
    (October 30, 2023).

    Dual-use foundation models: adversarial red-teaming required before
    deployment to assess CBRN and cybersecurity misuse risk.

    Safety-critical applications: TEVV framework must be applied.

    High-risk systems: pre-deployment safety testing required.

    Standard systems: approved with documentation condition.

    References
    ----------
    Executive Order 14110 — 88 FR 75191 (October 30, 2023)
    NIST AI RMF Playbook — Section 4 (TEVV)
    """

    def evaluate(self, context: PublicSectorAIContext) -> PublicSectorGovernanceResult:
        result = PublicSectorGovernanceResult(layer="EO_14110")
        violations: list[str] = []
        conditions: list[str] = []

        if context.eo14110_risk_tier == EO14110RiskTier.DUAL_USE_FOUNDATION:
            if not context.red_team_assessment_completed:
                violations.append(
                    "EO 14110: Adversarial red-team assessment required for "
                    "dual-use foundation models before federal deployment "
                    "[EO 14110 §4.2(a)(i)]"
                )
            if not context.tevv_framework_applied:
                violations.append(
                    "EO 14110: TEVV (Test, Evaluate, Verify, Validate) "
                    "framework required for dual-use foundation models "
                    "[EO 14110 §4.2(a)(ii)]"
                )

        elif context.eo14110_risk_tier == EO14110RiskTier.SAFETY_CRITICAL:
            if not context.tevv_framework_applied:
                violations.append(
                    "EO 14110: TEVV framework required for safety-critical "
                    "federal AI applications [EO 14110 §4.2(b)]"
                )
            if not context.pre_deployment_safety_testing_done:
                violations.append(
                    "EO 14110: Pre-deployment safety testing required for "
                    "safety-critical AI [EO 14110 §4.2(b)(i)]"
                )

        elif context.eo14110_risk_tier == EO14110RiskTier.HIGH_RISK:
            if not context.pre_deployment_safety_testing_done:
                violations.append(
                    "EO 14110: Pre-deployment safety evaluation required for "
                    "high-risk federal AI [EO 14110 §4.2(c)]"
                )
            if not violations:
                conditions.append(
                    "EO 14110: HIGH_RISK system — quarterly performance review "
                    "and safety report required [EO 14110 §4.3]"
                )

        else:  # STANDARD
            conditions.append(
                "EO 14110: STANDARD risk tier — document AI safety practices "
                "per agency AI governance policy [EO 14110 §3]"
            )

        if violations:
            result.decision = PublicSectorGovernanceDecision.DENIED
            result.findings = violations
        elif conditions:
            result.decision = PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
        else:
            result.decision = PublicSectorGovernanceDecision.APPROVED

        return result


# ---------------------------------------------------------------------------
# Layer 3 — NIST AI RMF
# ---------------------------------------------------------------------------


class NISTAIRMFFilter:
    """
    Layer 3: NIST AI Risk Management Framework (AI 100-1, January 2023).

    FULL maturity: all four functions documented → conditions only.
    PARTIAL maturity: approved with conditions + gap remediation required.
    MINIMAL maturity: non-minimum-impact systems denied.
    NONE: denied for all non-minimum-impact systems.

    Minimum-impact systems: MINIMAL or higher accepted.

    References
    ----------
    NIST AI 100-1 — Artificial Intelligence Risk Management Framework (2023)
    NIST AI RMF Playbook — nist.gov/system/files/documents/2023/01/26/NIST.AI.100-1.pdf
    """

    def evaluate(self, context: PublicSectorAIContext) -> PublicSectorGovernanceResult:
        result = PublicSectorGovernanceResult(layer="NIST_AI_RMF")
        violations: list[str] = []
        conditions: list[str] = []

        if context.impact_level == AIImpactLevel.MINIMUM_IMPACT:
            if context.nist_rmf_level == NISTRMFLevel.NONE:
                violations.append(
                    "NIST AI RMF: Even minimum-impact AI requires basic AI "
                    "inventory and basic governance documentation [GOVERN function]"
                )
            else:
                conditions.append(
                    "NIST AI RMF: Minimum-impact AI — maintain AI inventory; "
                    "FULL RMF implementation not required [AI 100-1 §3.1]"
                )

        elif context.nist_rmf_level == NISTRMFLevel.NONE:
            violations.append(
                "NIST AI RMF: No RMF implementation — GOVERN, MAP, MEASURE, "
                "and MANAGE functions must be established [AI 100-1 §3]"
            )

        elif context.nist_rmf_level == NISTRMFLevel.MINIMAL:
            violations.append(
                "NIST AI RMF: MINIMAL implementation insufficient for "
                f"{context.impact_level.value} AI — full four-function "
                "implementation required [AI 100-1 §3.2]"
            )

        elif context.nist_rmf_level == NISTRMFLevel.PARTIAL:
            # Check which functions are missing
            missing = []
            if not context.nist_govern_documented:
                missing.append("GOVERN")
            if not context.nist_map_completed:
                missing.append("MAP")
            if not context.nist_measure_quantified:
                missing.append("MEASURE")
            if not context.nist_manage_plan_exists:
                missing.append("MANAGE")

            if missing:
                conditions.append(
                    f"NIST AI RMF: PARTIAL implementation — complete missing "
                    f"functions before next review: {', '.join(missing)} "
                    f"[AI 100-1 §3]"
                )
            else:
                # All four functions present but marked PARTIAL
                conditions.append(
                    "NIST AI RMF: RMF marked PARTIAL — update maturity to FULL "
                    "after confirming all four functions documented [AI 100-1 §3]"
                )

        else:  # FULL
            conditions.append(
                "NIST AI RMF: FULL implementation — maintain documentation "
                "currency; annual review of all four functions required "
                "[AI 100-1 §4]"
            )

        if violations:
            result.decision = PublicSectorGovernanceDecision.DENIED
            result.findings = violations
        elif conditions:
            result.decision = PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
        else:
            result.decision = PublicSectorGovernanceDecision.APPROVED

        return result


# ---------------------------------------------------------------------------
# Layer 4 — Section 508 / ADA Accessibility
# ---------------------------------------------------------------------------


class Section508Filter:
    """
    Layer 4: Section 508 of the Rehabilitation Act (29 U.S.C. §794d) and
    ADA Title II (42 U.S.C. §12132) accessibility requirements for federal
    AI systems.

    Public-facing AI outputs must comply with Section 508 accessibility
    standards. Rights-impacting and safety-impacting decisions must be
    explainable in plain language to affected individuals. This requirement
    ties directly to OMB M-24-10's human review obligation.

    Internal analytics and minimum-impact systems are exempt from
    plain-language explanation requirements if they have no public-facing
    output or direct individual impact.

    References
    ----------
    29 U.S.C. §794d — Section 508 of the Rehabilitation Act
    42 U.S.C. §12132 — ADA Title II
    Access Board WCAG 2.1 AA Standard (36 CFR Part 1194)
    """

    _PLAIN_LANGUAGE_REQUIRED: FrozenSet[FederalAIUseCase] = frozenset(
        _RIGHTS_IMPACTING_USE_CASES | _SAFETY_IMPACTING_USE_CASES | {
            FederalAIUseCase.CITIZEN_SERVICES_CHAT
        }
    )

    def evaluate(self, context: PublicSectorAIContext) -> PublicSectorGovernanceResult:
        result = PublicSectorGovernanceResult(layer="SECTION_508_ADA")
        violations: list[str] = []
        conditions: list[str] = []

        # Minimum-impact internal systems — reduced requirements
        if context.impact_level == AIImpactLevel.MINIMUM_IMPACT:
            conditions.append(
                "Section 508: Minimum-impact internal AI — ensure employee "
                "accessibility if outputs are consumed via agency interfaces "
                "[29 U.S.C. §794d]"
            )
            result.decision = PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
            return result

        # Section 508 accessibility for public-facing outputs
        if not context.section_508_compliant:
            violations.append(
                "Section 508: AI outputs used in federal services must comply "
                "with Section 508 accessibility standards (WCAG 2.1 AA) "
                "[29 U.S.C. §794d; 36 CFR §1194]"
            )

        # Plain-language explanations for rights/safety-impacting + citizen services
        if context.use_case in self._PLAIN_LANGUAGE_REQUIRED:
            if not context.plain_language_explanations:
                violations.append(
                    "Section 508 / ADA: AI decisions affecting individuals must "
                    "be explainable in plain language accessible to people with "
                    "disabilities; generic technical output is insufficient "
                    "[ADA Title II 42 U.S.C. §12132]"
                )

        if not violations:
            if context.section_508_compliant:
                conditions.append(
                    "Section 508: Maintain WCAG 2.1 AA compliance as AI outputs "
                    "evolve; accessibility testing required after each major "
                    "update [36 CFR §1194]"
                )

        if violations:
            result.decision = PublicSectorGovernanceDecision.DENIED
            result.findings = violations
        elif conditions:
            result.decision = PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
        else:
            result.decision = PublicSectorGovernanceDecision.APPROVED

        return result


# ---------------------------------------------------------------------------
# Four-layer orchestrator
# ---------------------------------------------------------------------------


@dataclass
class PublicSectorGovernanceReport:
    """Aggregated governance report from all four layers."""

    system_id: str
    system_name: str
    use_case: str
    final_decision: PublicSectorGovernanceDecision
    layer_results: List[PublicSectorGovernanceResult] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "system_id": self.system_id,
            "system_name": self.system_name,
            "use_case": self.use_case,
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


class PublicSectorGovernanceOrchestrator:
    """
    Four-layer public sector AI governance orchestrator.

    Evaluation order:
        OMB M-24-10  →  EO 14110  →  NIST AI RMF  →  Section 508 / ADA

    Decision aggregation:
    - Any DENIED layer → final decision is DENIED
    - No DENIED + any APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS
    - All APPROVED → APPROVED

    All layers evaluated regardless of earlier failures.
    """

    def __init__(self) -> None:
        self._omb = OMBM2410Filter()
        self._eo = EO14110Filter()
        self._nist = NISTAIRMFFilter()
        self._section508 = Section508Filter()

    def evaluate(self, context: PublicSectorAIContext) -> PublicSectorGovernanceReport:
        layer_results = [
            self._omb.evaluate(context),
            self._eo.evaluate(context),
            self._nist.evaluate(context),
            self._section508.evaluate(context),
        ]

        if any(lr.is_denied for lr in layer_results):
            final = PublicSectorGovernanceDecision.DENIED
        elif any(lr.has_conditions for lr in layer_results):
            final = PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        else:
            final = PublicSectorGovernanceDecision.APPROVED

        return PublicSectorGovernanceReport(
            system_id=context.system_id,
            system_name=context.system_name,
            use_case=context.use_case.value,
            final_decision=final,
            layer_results=layer_results,
        )


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_benefits_ctx():
    return PublicSectorAIContext(
        system_id="GOV-001",
        system_name="Benefits Eligibility Screening System",
        use_case=FederalAIUseCase.BENEFITS_DETERMINATION,
        impact_level=AIImpactLevel.RIGHTS_IMPACTING,
        eo14110_risk_tier=EO14110RiskTier.HIGH_RISK,
        nist_rmf_level=NISTRMFLevel.FULL,
        deploying_agency="SSA",
        caio_designated=True,
        ai_inventory_maintained=True,
        human_review_available=True,
        appeal_mechanism_exists=True,
        pre_deployment_safety_testing_done=True,
        incident_reporting_active=True,
        red_team_assessment_completed=False,
        tevv_framework_applied=True,
        nist_govern_documented=True,
        nist_map_completed=True,
        nist_measure_quantified=True,
        nist_manage_plan_exists=True,
        section_508_compliant=True,
        plain_language_explanations=True,
    )


def scenario_a_compliant_rights_impacting() -> None:
    """Fully compliant rights-impacting AI — APPROVED_WITH_CONDITIONS."""
    print("\n--- Scenario A: Compliant Rights-Impacting AI (Benefits) ---")
    orch = PublicSectorGovernanceOrchestrator()
    ctx = _compliant_benefits_ctx()
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")


def scenario_b_no_human_review() -> None:
    """Rights-impacting AI without human review — DENIED."""
    print("\n--- Scenario B: No Human Review for Rights-Impacting AI — DENIED ---")
    orch = PublicSectorGovernanceOrchestrator()
    ctx = _compliant_benefits_ctx()
    ctx2 = PublicSectorAIContext(
        **{**vars(ctx), "human_review_available": False, "appeal_mechanism_exists": False}
    )
    report = orch.evaluate(ctx2)
    print(f"  Decision: {report.final_decision.value}")
    omb = next(lr for lr in report.layer_results if lr.layer == "OMB_M24_10")
    for f in omb.findings:
        print(f"  OMB: {f[:80]}...")


def scenario_c_dual_use_no_red_team() -> None:
    """Dual-use foundation model without red-teaming — DENIED."""
    print("\n--- Scenario C: Dual-Use Foundation Model — No Red Team — DENIED ---")
    orch = PublicSectorGovernanceOrchestrator()
    ctx = PublicSectorAIContext(
        system_id="GOV-003",
        system_name="Agency LLM Foundation Model",
        use_case=FederalAIUseCase.CITIZEN_SERVICES_CHAT,
        impact_level=AIImpactLevel.LOW_IMPACT,
        eo14110_risk_tier=EO14110RiskTier.DUAL_USE_FOUNDATION,
        nist_rmf_level=NISTRMFLevel.FULL,
        deploying_agency="GSA",
        caio_designated=True,
        ai_inventory_maintained=True,
        human_review_available=True,
        appeal_mechanism_exists=True,
        pre_deployment_safety_testing_done=True,
        incident_reporting_active=True,
        red_team_assessment_completed=False,    # Missing
        tevv_framework_applied=False,            # Missing
        nist_govern_documented=True,
        nist_map_completed=True,
        nist_measure_quantified=True,
        nist_manage_plan_exists=True,
        section_508_compliant=True,
        plain_language_explanations=True,
    )
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    eo = next(lr for lr in report.layer_results if lr.layer == "EO_14110")
    for f in eo.findings:
        print(f"  EO 14110: {f[:80]}...")


def scenario_d_minimum_impact_internal() -> None:
    """Internal analytics — minimum requirements apply — APPROVED."""
    print("\n--- Scenario D: Internal Analytics (Minimum-Impact) — APPROVED ---")
    orch = PublicSectorGovernanceOrchestrator()
    ctx = PublicSectorAIContext(
        system_id="GOV-004",
        system_name="Budget Forecast Analytics Model",
        use_case=FederalAIUseCase.INTERNAL_ANALYTICS,
        impact_level=AIImpactLevel.MINIMUM_IMPACT,
        eo14110_risk_tier=EO14110RiskTier.STANDARD,
        nist_rmf_level=NISTRMFLevel.MINIMAL,
        deploying_agency="OMB",
        caio_designated=True,
        ai_inventory_maintained=True,
        human_review_available=False,
        appeal_mechanism_exists=False,
        pre_deployment_safety_testing_done=False,
        incident_reporting_active=False,
        red_team_assessment_completed=False,
        tevv_framework_applied=False,
        nist_govern_documented=True,
        nist_map_completed=False,
        nist_measure_quantified=False,
        nist_manage_plan_exists=False,
        section_508_compliant=True,
        plain_language_explanations=False,
    )
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")


if __name__ == "__main__":
    scenario_a_compliant_rights_impacting()
    scenario_b_no_human_review()
    scenario_c_dual_use_no_red_team()
    scenario_d_minimum_impact_internal()
    print("\nAll scenarios complete.")
