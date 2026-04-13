"""
16_eu_ai_act_governance.py — Four-layer AI governance framework for
AI systems subject to the EU AI Act (Regulation (EU) 2024/1689).

Demonstrates a multi-layer governance orchestrator where four overlapping
EU AI Act compliance obligations each impose independent requirements on AI
systems deployed in the European Union:

    Layer 1  — Risk Classification and Prohibited Practices
               (Articles 5–7, Annexes I–III):
               AI systems are classified by risk level. Prohibited practices
               (Article 5) include real-time remote biometric identification
               in public spaces, social scoring, manipulation of vulnerable
               groups, and subliminal techniques. High-risk systems (Annex III)
               include biometrics, education, employment, essential services,
               law enforcement, migration, justice administration, and safety
               components of products. Systems must be classified before
               deployment; prohibited systems may not be deployed.

    Layer 2  — Conformity Assessment and CE Marking (Articles 9, 43–49):
               High-risk AI systems must undergo a conformity assessment
               (internal or third-party depending on Annex IV categorization)
               before market placement. A risk management system (Article 9)
               must be established, documenting residual risks and mitigation
               measures throughout the AI system lifecycle. The system must
               receive a CE marking before EU market placement.

    Layer 3  — Data Governance and Bias Examination (Article 10):
               Training, validation, and test datasets must meet quality
               criteria: relevance, representativeness, and completeness.
               For high-risk systems, bias examination must identify and
               address possible biases in data relevant to protected
               characteristics (Article 10(5)). Ongoing data monitoring
               is required post-deployment.

    Layer 4  — Transparency, Human Oversight, and Post-Market Monitoring
               (Articles 13–14, 26, 61–62):
               Deployers must implement human oversight measures designed
               into the system before deployment. Instructions for use must
               cover capabilities, limitations, and maintenance requirements.
               Deployers must maintain logs (Article 26) and report serious
               incidents to national competent authorities within 15 working
               days. Citizen-facing AI must provide plain-language explanations.

No external dependencies required.

Run:
    python examples/16_eu_ai_act_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, List, Optional


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class EUAIActRiskLevel(str, Enum):
    """
    EU AI Act risk classification (Articles 5–7).

    PROHIBITED       — Banned AI practices (Article 5); may not be deployed
    HIGH_RISK        — Annex III systems; full conformity assessment required
    LIMITED_TRANSPARENCY — Disclosure obligations only (chatbots, deepfakes)
    MINIMAL_RISK     — No specific obligations; voluntary Code of Practice
    """

    PROHIBITED = "PROHIBITED"
    HIGH_RISK = "HIGH_RISK"
    LIMITED_TRANSPARENCY = "LIMITED_TRANSPARENCY"
    MINIMAL_RISK = "MINIMAL_RISK"


class AnnexIIICategory(str, Enum):
    """
    EU AI Act Annex III high-risk AI system categories.

    These categories trigger the full high-risk compliance pathway.
    """

    BIOMETRIC_IDENTIFICATION = "BIOMETRIC_IDENTIFICATION"
    CRITICAL_INFRASTRUCTURE = "CRITICAL_INFRASTRUCTURE"
    EDUCATION_VOCATIONAL = "EDUCATION_VOCATIONAL"
    EMPLOYMENT_WORKERS = "EMPLOYMENT_WORKERS"
    ESSENTIAL_SERVICES = "ESSENTIAL_SERVICES"
    LAW_ENFORCEMENT = "LAW_ENFORCEMENT"
    MIGRATION_ASYLUM = "MIGRATION_ASYLUM"
    JUSTICE_DEMOCRACY = "JUSTICE_DEMOCRACY"


class EUConformityAssessmentRoute(str, Enum):
    """
    Conformity assessment procedure route (Articles 43–44).

    INTERNAL_CONTROL   — Article 43(2): provider self-assessment
    THIRD_PARTY_NOTIFIED — Article 43(1): notified body assessment required
    """

    INTERNAL_CONTROL = "INTERNAL_CONTROL"
    THIRD_PARTY_NOTIFIED = "THIRD_PARTY_NOTIFIED"
    NOT_REQUIRED = "NOT_REQUIRED"


class NISTRMFMappingLevel(str, Enum):
    """Alignment between EU AI Act Article 9 RMS and NIST AI RMF."""

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    MINIMAL = "MINIMAL"
    NONE = "NONE"


class EUGovernanceDecision(str, Enum):
    """Final governance decision."""

    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DENIED = "DENIED"


# ---------------------------------------------------------------------------
# Prohibited practice sets
# ---------------------------------------------------------------------------

_PROHIBITED_RISK_LEVELS: FrozenSet[EUAIActRiskLevel] = frozenset({
    EUAIActRiskLevel.PROHIBITED,
})

_LIMITED_TRANSPARENCY_OBLIGATION_TRIGGERS: FrozenSet[str] = frozenset({
    "chatbot",
    "deepfake_generation",
    "emotion_recognition",
    "synthetic_media",
})


# ---------------------------------------------------------------------------
# Context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EUAIActContext:
    """
    Governance review context for an AI system under the EU AI Act.

    Attributes
    ----------
    system_id : str
        Unique AI system identifier.
    system_name : str
        Human-readable name of the AI system.
    risk_level : EUAIActRiskLevel
        EU AI Act risk classification.
    annex_iii_category : Optional[AnnexIIICategory]
        Annex III category for high-risk systems; None for non-high-risk.
    conformity_assessment_route : EUConformityAssessmentRoute
        Which conformity assessment route applies.
    deploying_country : str
        EU member state where the system is deployed (ISO 3166-1 alpha-2).
    provider_name : str
        AI system provider (manufacturer/developer) name.

    — Article 5 / Prohibited Practices —
    is_prohibited_practice : bool
        True if any prohibited Article 5 practice is used (should never deploy).

    — Article 9 / Risk Management System —
    risk_management_system_established : bool
        True if a documented risk management system covering the full lifecycle
        has been established per Article 9.
    residual_risks_acceptable : bool
        True if residual risks after mitigation are judged acceptable
        (benefits outweigh residual risks per Article 9(4)).
    post_market_monitoring_plan : bool
        True if a post-market monitoring plan is in place per Article 72.

    — Article 10 / Data Governance —
    training_data_quality_documented : bool
        True if training dataset quality criteria are documented.
    bias_examination_completed : bool
        True if a bias examination for protected characteristics has been
        completed per Article 10(5) (required for HIGH_RISK only).
    data_monitoring_active : bool
        True if ongoing post-deployment data quality monitoring is active.

    — Conformity Assessment (Articles 43–49) —
    conformity_assessment_completed : bool
        True if the applicable conformity assessment procedure is complete.
    ce_marking_affixed : bool
        True if the CE marking has been affixed and the declaration of
        conformity filed with the relevant national authority.

    — Article 13 / Transparency —
    instructions_for_use_complete : bool
        True if the instructions for use cover capabilities, limitations,
        intended purpose, and maintenance per Article 13.
    disclosure_obligation_met : bool
        True if limited-transparency obligations (chatbot/deepfake disclosure)
        are met per Article 50.

    — Article 14 / Human Oversight —
    human_oversight_measures_designed : bool
        True if human oversight measures are built into the system before
        deployment, enabling operators to intervene per Article 14.
    override_capability_available : bool
        True if deployers can stop or override the AI system's output per
        Article 14(4)(d).

    — Article 26 / Deployer Obligations —
    deployer_logs_maintained : bool
        True if deployers maintain logs of system operation per Article 26(6).
    serious_incident_reporting_active : bool
        True if a process for reporting serious incidents to the national
        competent authority within 15 working days is operational per Article 73.
    """

    system_id: str
    system_name: str
    risk_level: EUAIActRiskLevel
    annex_iii_category: Optional[AnnexIIICategory]
    conformity_assessment_route: EUConformityAssessmentRoute
    deploying_country: str
    provider_name: str
    is_prohibited_practice: bool
    risk_management_system_established: bool
    residual_risks_acceptable: bool
    post_market_monitoring_plan: bool
    training_data_quality_documented: bool
    bias_examination_completed: bool
    data_monitoring_active: bool
    conformity_assessment_completed: bool
    ce_marking_affixed: bool
    instructions_for_use_complete: bool
    disclosure_obligation_met: bool
    human_oversight_measures_designed: bool
    override_capability_available: bool
    deployer_logs_maintained: bool
    serious_incident_reporting_active: bool


# ---------------------------------------------------------------------------
# Per-layer result
# ---------------------------------------------------------------------------


@dataclass
class EUGovernanceResult:
    """Result of a single EU AI Act governance layer evaluation."""

    layer: str
    decision: EUGovernanceDecision = EUGovernanceDecision.APPROVED
    findings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        return self.decision == EUGovernanceDecision.DENIED

    @property
    def has_conditions(self) -> bool:
        return self.decision == EUGovernanceDecision.APPROVED_WITH_CONDITIONS


# ---------------------------------------------------------------------------
# Layer 1 — Risk Classification
# ---------------------------------------------------------------------------


class EURiskClassificationFilter:
    """
    Layer 1: EU AI Act Risk Classification and Prohibited Practices.

    Prohibited practices (Article 5) are unconditional denials.
    High-risk systems (Annex III) proceed to conformity assessment.
    Limited-transparency systems must meet disclosure obligations.
    Minimal-risk systems are approved with a voluntary code condition.

    References
    ----------
    EU AI Act — Regulation (EU) 2024/1689 — Articles 5–7, Annex III
    Recital 60: Prohibitions on unacceptable risk AI
    Article 50: Transparency obligations for limited-transparency AI
    """

    def evaluate(self, context: EUAIActContext) -> EUGovernanceResult:
        result = EUGovernanceResult(layer="EU_RISK_CLASSIFICATION")

        # Prohibited practices — unconditional denial
        if context.is_prohibited_practice or context.risk_level == EUAIActRiskLevel.PROHIBITED:
            result.decision = EUGovernanceDecision.DENIED
            result.findings.append(
                "EU AI Act Article 5: This AI system engages in a prohibited "
                "practice (real-time biometric surveillance, social scoring, "
                "manipulation of vulnerable groups, or subliminal techniques) — "
                "deployment is unconditionally prohibited in the EU"
            )
            return result

        if context.risk_level == EUAIActRiskLevel.HIGH_RISK:
            if context.annex_iii_category is None:
                result.decision = EUGovernanceDecision.DENIED
                result.findings.append(
                    "EU AI Act Article 6: System classified as HIGH_RISK but "
                    "no Annex III category has been specified — risk classification "
                    "must identify the applicable Annex III category"
                )
            else:
                result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
                result.conditions.append(
                    f"EU AI Act Annex III §{context.annex_iii_category.value}: "
                    f"HIGH_RISK system — full conformity assessment pathway "
                    f"applies; CE marking required before EU market placement "
                    f"[Article 43]"
                )

        elif context.risk_level == EUAIActRiskLevel.LIMITED_TRANSPARENCY:
            if not context.disclosure_obligation_met:
                result.decision = EUGovernanceDecision.DENIED
                result.findings.append(
                    "EU AI Act Article 50: Limited-transparency AI system must "
                    "disclose to users that they are interacting with AI — "
                    "disclosure obligation not met"
                )
            else:
                result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
                result.conditions.append(
                    "EU AI Act Article 50: LIMITED_TRANSPARENCY — maintain "
                    "user disclosure at all points of interaction; update "
                    "disclosures when new interaction modes are introduced"
                )

        else:  # MINIMAL_RISK
            result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "EU AI Act Recital 97: MINIMAL_RISK system — voluntary "
                "adherence to EU AI Code of Practice is encouraged; "
                "no mandatory requirements apply"
            )

        return result


# ---------------------------------------------------------------------------
# Layer 2 — Conformity Assessment
# ---------------------------------------------------------------------------


class EUConformityAssessmentFilter:
    """
    Layer 2: EU AI Act Conformity Assessment and CE Marking (Articles 9, 43–49).

    For HIGH_RISK systems: a risk management system (Article 9) must be
    established with documented residual risks and a post-market monitoring
    plan. The applicable conformity assessment (internal control or third-party
    notified body) must be completed and CE marking affixed.

    Non-high-risk systems pass this layer unconditionally.

    References
    ----------
    EU AI Act — Articles 9, 43–49
    Article 9 — Risk Management System
    Article 43 — Conformity Assessment Procedures for HIGH_RISK AI
    Article 49 — CE Marking of Conformity
    """

    def evaluate(self, context: EUAIActContext) -> EUGovernanceResult:
        result = EUGovernanceResult(layer="EU_CONFORMITY_ASSESSMENT")

        if context.risk_level != EUAIActRiskLevel.HIGH_RISK:
            result.decision = EUGovernanceDecision.APPROVED
            return result

        violations = []
        conditions = []

        # Article 9 — Risk Management System
        if not context.risk_management_system_established:
            violations.append(
                "EU AI Act Article 9(1): A risk management system covering the "
                "full AI lifecycle must be established for HIGH_RISK systems — "
                "no risk management documentation found"
            )
        if not context.residual_risks_acceptable:
            violations.append(
                "EU AI Act Article 9(4): Residual risks after mitigation must be "
                "judged acceptable (benefits must outweigh residual risks) — "
                "residual risk assessment has not been completed or accepted"
            )
        if not context.post_market_monitoring_plan:
            violations.append(
                "EU AI Act Article 72: A post-market monitoring plan must be "
                "established before deployment of HIGH_RISK AI — no plan found"
            )

        # Conformity assessment
        if not context.conformity_assessment_completed:
            violations.append(
                f"EU AI Act Article 43: Conformity assessment "
                f"({context.conformity_assessment_route.value}) has not been "
                f"completed — HIGH_RISK AI may not be placed on the EU market "
                f"without a completed conformity assessment"
            )

        # CE marking
        if not context.ce_marking_affixed:
            violations.append(
                "EU AI Act Article 49: CE marking has not been affixed — "
                "HIGH_RISK AI systems must bear CE marking and a declaration "
                "of conformity before EU market placement"
            )

        if not violations:
            conditions.append(
                "EU AI Act Article 43: Conformity assessment complete — "
                "maintain documentation currency; re-assessment required for "
                "substantial modifications per Article 6(3)"
            )
            conditions.append(
                "EU AI Act Article 72: Post-market monitoring active — submit "
                "annual reports to the national competent authority"
            )

        if violations:
            result.decision = EUGovernanceDecision.DENIED
            result.findings = violations
        else:
            result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions

        return result


# ---------------------------------------------------------------------------
# Layer 3 — Data Governance
# ---------------------------------------------------------------------------


class EUDataGovernanceFilter:
    """
    Layer 3: EU AI Act Article 10 — Data and Data Governance.

    High-risk AI systems must document training data quality criteria and
    complete a bias examination for protected characteristics. Ongoing
    data quality monitoring is required post-deployment. Non-high-risk
    systems receive a best-practice condition.

    References
    ----------
    EU AI Act — Article 10
    Article 10(2): Training data quality criteria
    Article 10(5): Bias examination for protected characteristics
    """

    def evaluate(self, context: EUAIActContext) -> EUGovernanceResult:
        result = EUGovernanceResult(layer="EU_DATA_GOVERNANCE")

        if context.risk_level != EUAIActRiskLevel.HIGH_RISK:
            result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "EU AI Act Article 10 (best practice): Document training data "
                "quality criteria and consider bias examination even for "
                "non-high-risk systems — supports voluntary Code of Practice"
            )
            return result

        violations = []
        conditions = []

        if not context.training_data_quality_documented:
            violations.append(
                "EU AI Act Article 10(2): Training, validation, and test datasets "
                "must meet quality criteria (relevance, representativeness, "
                "completeness) — no data quality documentation found for this "
                "HIGH_RISK system"
            )

        if not context.bias_examination_completed:
            violations.append(
                "EU AI Act Article 10(5): HIGH_RISK AI systems must examine "
                "training data for possible biases affecting protected "
                "characteristics (sex, race, ethnic origin, disability, etc.) — "
                "bias examination has not been completed"
            )

        if not context.data_monitoring_active:
            violations.append(
                "EU AI Act Article 10 / Article 72: Post-deployment data quality "
                "monitoring must be active for HIGH_RISK AI systems to detect "
                "distribution shift and emerging biases"
            )

        if not violations:
            conditions.append(
                "EU AI Act Article 10(5): Bias examination complete — re-examine "
                "for new protected characteristic categories if training data "
                "is updated; document in the technical file [Article 11]"
            )

        if violations:
            result.decision = EUGovernanceDecision.DENIED
            result.findings = violations
        else:
            result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions

        return result


# ---------------------------------------------------------------------------
# Layer 4 — Transparency, Human Oversight, Post-Market Monitoring
# ---------------------------------------------------------------------------


class EUTransparencyHumanOversightFilter:
    """
    Layer 4: EU AI Act Transparency (Article 13), Human Oversight (Article 14),
    and Post-Market Monitoring (Articles 26, 61–62).

    HIGH_RISK systems must provide complete instructions for use, human
    oversight measures built into the system, and override capability for
    deployers. All systems subject to reporting obligations must have incident
    reporting active. Minimal-risk systems receive an informational condition.

    References
    ----------
    EU AI Act — Articles 13, 14, 26, 61–62, 73
    Article 13: Transparency and provision of information to deployers
    Article 14: Human oversight measures
    Article 26(6): Deployer obligation to maintain logs
    Article 73: Reporting obligations for providers and deployers
    """

    def evaluate(self, context: EUAIActContext) -> EUGovernanceResult:
        result = EUGovernanceResult(layer="EU_TRANSPARENCY_OVERSIGHT")

        if context.risk_level == EUAIActRiskLevel.MINIMAL_RISK:
            result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "EU AI Act Article 13 (best practice): Provide clear information "
                "about AI system capabilities and limitations even for minimal-risk "
                "systems; supports user trust and voluntary code compliance"
            )
            return result

        violations = []
        conditions = []

        # Article 13 — Transparency
        if not context.instructions_for_use_complete:
            violations.append(
                "EU AI Act Article 13(1): Instructions for use must describe "
                "capabilities, limitations, intended purpose, foreseeable misuse, "
                "and maintenance requirements — instructions are incomplete"
            )

        # Article 14 — Human oversight
        if context.risk_level == EUAIActRiskLevel.HIGH_RISK:
            if not context.human_oversight_measures_designed:
                violations.append(
                    "EU AI Act Article 14(1): Human oversight measures must be "
                    "designed into the HIGH_RISK AI system before deployment — "
                    "no human oversight measures have been implemented"
                )
            if not context.override_capability_available:
                violations.append(
                    "EU AI Act Article 14(4)(d): Deployers must be able to stop "
                    "or interrupt the HIGH_RISK AI system — no override or "
                    "stop capability is available"
                )

        # Articles 26(6) and 73 — Deployer logs and incident reporting (HIGH_RISK only)
        if context.risk_level == EUAIActRiskLevel.HIGH_RISK:
            if not context.deployer_logs_maintained:
                violations.append(
                    "EU AI Act Article 26(6): Deployers must maintain logs of "
                    "HIGH_RISK AI system operation where the system generates logs — "
                    "logs are not being maintained"
                )
            if not context.serious_incident_reporting_active:
                violations.append(
                    "EU AI Act Article 73: Providers and deployers of HIGH_RISK AI "
                    "must report serious incidents to the national competent authority "
                    "within 15 working days — no incident reporting mechanism is active"
                )

        if not violations:
            conditions.append(
                "EU AI Act Article 13: Instructions for use current — review "
                "annually and after each significant capability change"
            )
            if context.risk_level == EUAIActRiskLevel.HIGH_RISK:
                conditions.append(
                    "EU AI Act Article 14: Human oversight operational — review "
                    "effectiveness annually and after every significant AI output "
                    "error or incident [Article 26]"
                )
                conditions.append(
                    "EU AI Act Article 73: Incident reporting active — ensure "
                    "15-working-day reporting timeline is embedded in incident "
                    "response procedures"
                )

        if violations:
            result.decision = EUGovernanceDecision.DENIED
            result.findings = violations
        else:
            result.decision = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions

        return result


# ---------------------------------------------------------------------------
# Four-layer orchestrator
# ---------------------------------------------------------------------------


@dataclass
class EUAIActGovernanceReport:
    """Aggregated EU AI Act governance report from all four layers."""

    system_id: str
    system_name: str
    risk_level: str
    final_decision: EUGovernanceDecision
    layer_results: List[EUGovernanceResult] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "system_id": self.system_id,
            "system_name": self.system_name,
            "risk_level": self.risk_level,
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


class EUAIActGovernanceOrchestrator:
    """
    Four-layer EU AI Act governance orchestrator.

    Evaluation order:
        Risk Classification  →  Conformity Assessment  →
        Data Governance  →  Transparency / Human Oversight

    Decision aggregation:
    - Any DENIED layer → final decision is DENIED
    - No DENIED + any APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS
    - All APPROVED → APPROVED

    All layers evaluated regardless of earlier failures.
    """

    def __init__(self) -> None:
        self._risk = EURiskClassificationFilter()
        self._conformity = EUConformityAssessmentFilter()
        self._data = EUDataGovernanceFilter()
        self._transparency = EUTransparencyHumanOversightFilter()

    def evaluate(self, context: EUAIActContext) -> EUAIActGovernanceReport:
        layer_results = [
            self._risk.evaluate(context),
            self._conformity.evaluate(context),
            self._data.evaluate(context),
            self._transparency.evaluate(context),
        ]

        if any(lr.is_denied for lr in layer_results):
            final = EUGovernanceDecision.DENIED
        elif any(lr.has_conditions for lr in layer_results):
            final = EUGovernanceDecision.APPROVED_WITH_CONDITIONS
        else:
            final = EUGovernanceDecision.APPROVED

        return EUAIActGovernanceReport(
            system_id=context.system_id,
            system_name=context.system_name,
            risk_level=context.risk_level.value,
            final_decision=final,
            layer_results=layer_results,
        )


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_high_risk_ctx() -> EUAIActContext:
    return EUAIActContext(
        system_id="EU-AI-001",
        system_name="CV Screening System",
        risk_level=EUAIActRiskLevel.HIGH_RISK,
        annex_iii_category=AnnexIIICategory.EMPLOYMENT_WORKERS,
        conformity_assessment_route=EUConformityAssessmentRoute.INTERNAL_CONTROL,
        deploying_country="DE",
        provider_name="TechCorp GmbH",
        is_prohibited_practice=False,
        risk_management_system_established=True,
        residual_risks_acceptable=True,
        post_market_monitoring_plan=True,
        training_data_quality_documented=True,
        bias_examination_completed=True,
        data_monitoring_active=True,
        conformity_assessment_completed=True,
        ce_marking_affixed=True,
        instructions_for_use_complete=True,
        disclosure_obligation_met=True,
        human_oversight_measures_designed=True,
        override_capability_available=True,
        deployer_logs_maintained=True,
        serious_incident_reporting_active=True,
    )


def scenario_a_compliant_high_risk() -> None:
    """Fully compliant HIGH_RISK employment AI — APPROVED_WITH_CONDITIONS."""
    print("\n--- Scenario A: Compliant HIGH_RISK Employment Screening AI ---")
    orch = EUAIActGovernanceOrchestrator()
    ctx = _compliant_high_risk_ctx()
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")


def scenario_b_prohibited_practice() -> None:
    """Prohibited AI practice — unconditional DENIED."""
    print("\n--- Scenario B: Prohibited Practice — Real-Time Biometric Surveillance ---")
    orch = EUAIActGovernanceOrchestrator()
    ctx = EUAIActContext(
        **{**vars(_compliant_high_risk_ctx()),
           "system_id": "EU-AI-002",
           "risk_level": EUAIActRiskLevel.PROHIBITED,
           "is_prohibited_practice": True}
    )
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    risk_layer = next(lr for lr in report.layer_results if lr.layer == "EU_RISK_CLASSIFICATION")
    for finding in risk_layer.findings:
        print(f"  Finding: {finding[:90]}...")


def scenario_c_missing_conformity_assessment() -> None:
    """HIGH_RISK without completed conformity assessment — DENIED."""
    print("\n--- Scenario C: HIGH_RISK — No Conformity Assessment --- DENIED ---")
    orch = EUAIActGovernanceOrchestrator()
    ctx = EUAIActContext(
        **{**vars(_compliant_high_risk_ctx()),
           "conformity_assessment_completed": False,
           "ce_marking_affixed": False}
    )
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    ca_layer = next(lr for lr in report.layer_results if lr.layer == "EU_CONFORMITY_ASSESSMENT")
    for f in ca_layer.findings:
        print(f"  Finding: {f[:80]}...")


def scenario_d_limited_transparency_chatbot() -> None:
    """LIMITED_TRANSPARENCY chatbot with proper disclosure — APPROVED_WITH_CONDITIONS."""
    print("\n--- Scenario D: LIMITED_TRANSPARENCY Chatbot — Compliant ---")
    orch = EUAIActGovernanceOrchestrator()
    ctx = EUAIActContext(
        system_id="EU-AI-004",
        system_name="Customer Service Chatbot",
        risk_level=EUAIActRiskLevel.LIMITED_TRANSPARENCY,
        annex_iii_category=None,
        conformity_assessment_route=EUConformityAssessmentRoute.NOT_REQUIRED,
        deploying_country="FR",
        provider_name="ChatCo SAS",
        is_prohibited_practice=False,
        risk_management_system_established=False,
        residual_risks_acceptable=True,
        post_market_monitoring_plan=False,
        training_data_quality_documented=False,
        bias_examination_completed=False,
        data_monitoring_active=False,
        conformity_assessment_completed=False,
        ce_marking_affixed=False,
        instructions_for_use_complete=True,
        disclosure_obligation_met=True,
        human_oversight_measures_designed=True,
        override_capability_available=True,
        deployer_logs_maintained=True,
        serious_incident_reporting_active=False,
    )
    report = orch.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")


if __name__ == "__main__":
    scenario_a_compliant_high_risk()
    scenario_b_prohibited_practice()
    scenario_c_missing_conformity_assessment()
    scenario_d_limited_transparency_chatbot()
