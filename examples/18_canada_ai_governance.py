"""
18_canada_ai_governance.py — Four-layer AI governance framework for AI systems
subject to Canadian law, covering the overlapping federal and provincial
obligations that apply to AI-driven data processing in Canada.

Demonstrates a multi-layer governance orchestrator where four Canadian
regulatory frameworks each impose independent requirements on AI systems
deployed in Canada:

    Layer 1  — Bill C-27 AIDA (Artificial Intelligence and Data Act):
               Bill C-27's Part 3, the Artificial Intelligence and Data Act
               (AIDA), establishes Canada's first federal AI-specific statute.
               Although not yet in force (as of 2024, awaiting passage and
               regulations), it introduces mandatory obligations for "high-impact"
               AI systems, including completed impact assessments (AIDA s.6),
               transparency notices to affected persons (AIDA s.9), mitigation
               measures (AIDA s.10), incident monitoring (AIDA s.11), and
               compliance with any applicable ministerial orders (AIDA s.35).
               Systems are classified by risk level; high-impact systems face
               the fullest set of obligations. Low-impact systems must maintain
               documentation for potential reclassification as regulations are
               finalised. Exempt systems are flagged for ongoing monitoring as
               regulatory scope is clarified.

    Layer 2  — CPPA (Consumer Privacy Protection Act):
               Part 1 of Bill C-27 replaces PIPEDA with the Consumer Privacy
               Protection Act (CPPA), Canada's modernised federal private-sector
               privacy law. Key obligations for AI systems include: meaningful,
               informed consent before processing personal information (CPPA
               s.15); specification of purpose before or at time of collection
               (CPPA s.12); proportionality and data minimization — collection,
               use, and disclosure limited to what is necessary for identified
               purposes (CPPA s.13); and contractual protections for cross-border
               transfers to jurisdictions that may not offer equivalent privacy
               protection (CPPA s.24). Individuals retain rights of access,
               correction, consent withdrawal (CPPA s.62), and data portability
               in structured, machine-readable format (CPPA s.63). Organisations
               must maintain a Privacy Management Programme that includes
               AI-specific policies.

    Layer 3  — OPC AI Guidelines 2023 (Office of the Privacy Commissioner):
               The Office of the Privacy Commissioner of Canada published
               AI guidelines in 2023 that establish privacy principles for
               organisations deploying AI systems processing personal information.
               The guidelines build on PIPEDA/CPPA obligations and identify five
               core requirements: (1) meaningful consent, (2) data minimization
               — limit personal information used in AI to what is necessary,
               (3) meaningful human oversight for automated decisions affecting
               individuals, (4) accuracy — AI systems must maintain data accuracy
               and minimise harm from inaccurate outputs, and (5) accountability
               — designated individual(s) responsible for CPPA/AI compliance
               with written policies. Annual privacy audits are recommended.
               All assessments must be documented and retained for OPC inspection.

    Layer 4  — Québec Law 25 (Act Respecting the Protection of Personal
               Information in the Private Sector, as amended by Act 25):
               Québec's Law 25, in force in full as of September 2023, is the
               most stringent provincial privacy law in Canada. Three obligations
               are specific to AI and automated decision-making:
               (a) Privacy Impact Assessment (PIA) mandatory before deployment
                   of any automated decision-making technology (Law 25 s.63.3);
               (b) Public disclosure of automated decisions — any organisation
                   making automated decisions about individuals must publish
                   the purpose, factors used, and the individual's right to
                   request human review (Law 25 s.12);
               (c) Designation of a Chief Privacy Officer (CPO) with the
                   authority and resources to enforce Law 25 obligations
                   (Law 25 s.3.1).
               Law 25 only applies when the AI system is deployed in the
               province of Québec. Data breaches must be reported to Québec's
               Commission d'accès à l'information within 30 days. PIAs must
               be updated whenever technology changes materially.

No external dependencies required.

Run:
    python examples/18_canada_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class CanadianAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under Bill C-27 AIDA.

    HIGH_IMPACT   — Meets the AIDA definition of a high-impact AI system;
                    full impact assessment and transparency obligations apply.
    MEDIUM_IMPACT — Significant potential consequences; documentation of
                    potential reclassification required.
    LOW_IMPACT    — Limited potential for harm; lighter obligations apply
                    but documentation must support reclassification reviews.
    EXEMPT        — Falls outside current AIDA scope; monitor for regulatory
                    clarification as Bill C-27 regulations are finalised.
    """

    HIGH_IMPACT = "high_impact"
    MEDIUM_IMPACT = "medium_impact"
    LOW_IMPACT = "low_impact"
    EXEMPT = "exempt"


class CanadianAIDecision(str, Enum):
    """Final governance decision for a Canadian AI system evaluation."""

    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    DENIED = "denied"


# ---------------------------------------------------------------------------
# Frozen context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanadaAIContext:
    """
    Governance review context for a Canadian AI system.

    Attributes
    ----------
    system_id : str
        Unique identifier for the AI system under review.
    system_name : str
        Human-readable name of the AI system.
    risk_level : CanadianAIRiskLevel
        Risk classification under Bill C-27 AIDA.
    deploying_province : str
        Canadian province or territory code where the system is deployed
        (e.g. ``"QC"``, ``"ON"``, ``"BC"``, ``"AB"``). A value of ``"QC"``
        triggers Québec Law 25 obligations in Layer 4.

    — AIDA (Bill C-27) fields —

    is_high_impact_system : bool
        True if the system meets the AIDA definition of a high-impact AI
        system (to be defined in regulations; indicators include decisions
        affecting employment, credit, health, or liberty of individuals).
    impact_assessment_completed : bool
        True if the mandatory impact assessment has been completed before
        deployment (AIDA s.6).
    transparency_notice_provided : bool
        True if a transparency notice has been provided to persons affected
        by the high-impact AI system's outputs (AIDA s.9).
    ministerial_order_compliant : bool
        True if the system is compliant with any applicable ministerial
        orders issued under AIDA (AIDA s.35).

    — CPPA fields —

    meaningful_consent_obtained : bool
        True if meaningful, informed consent has been obtained before
        processing personal information (CPPA s.15).
    purpose_limitation_documented : bool
        True if the purpose of personal information collection has been
        specified before or at the time of collection (CPPA s.12).
    data_minimization_applied : bool
        True if collection, use, and disclosure of personal information is
        limited to what is necessary for the identified purposes (CPPA s.13).
    cross_border_transfer_safeguards : bool
        True if contractual protections ensuring CPPA-equivalent privacy are
        in place for any transfers of personal information to foreign
        jurisdictions (CPPA s.24).

    — OPC AI Guidelines fields —

    human_oversight_available : bool
        True if meaningful human oversight is available for automated
        decisions affecting individuals (OPC Guideline 3).
    accuracy_measures_in_place : bool
        True if measures to maintain data accuracy and minimise harm from
        inaccurate AI outputs are in place (OPC Guideline 4).
    accountability_framework_exists : bool
        True if designated individual(s) are responsible for CPPA/AI
        compliance and written policies are in place (OPC Guideline 5).

    — Québec Law 25 fields (enforced only when deploying_province == "QC") —

    privacy_impact_assessment_done : bool
        True if a Privacy Impact Assessment (PIA) has been completed before
        deployment of automated decision-making technology in Québec
        (Law 25 s.63.3).
    algorithmic_transparency_published : bool
        True if the purpose, factors, and the individual's right to request
        human review of any automated decision have been publicly disclosed
        (Law 25 s.12).
    data_governance_officer_designated : bool
        True if a Chief Privacy Officer (CPO) has been designated with
        authority and resources to enforce Law 25 (Law 25 s.3.1).
    """

    # System identity
    system_id: str
    system_name: str
    risk_level: CanadianAIRiskLevel
    deploying_province: str  # "QC", "ON", "BC", "AB", etc.; "QC" triggers Law 25

    # AIDA (Bill C-27) fields
    is_high_impact_system: bool
    impact_assessment_completed: bool
    transparency_notice_provided: bool
    ministerial_order_compliant: bool

    # CPPA fields
    meaningful_consent_obtained: bool
    purpose_limitation_documented: bool
    data_minimization_applied: bool
    cross_border_transfer_safeguards: bool

    # OPC AI Guidelines fields
    human_oversight_available: bool
    accuracy_measures_in_place: bool
    accountability_framework_exists: bool

    # Québec Law 25 fields (only enforced when deploying_province == "QC")
    privacy_impact_assessment_done: bool
    algorithmic_transparency_published: bool
    data_governance_officer_designated: bool


# ---------------------------------------------------------------------------
# Per-layer result
# ---------------------------------------------------------------------------


@dataclass
class CanadaAIGovernanceResult:
    """Result of a single Canadian AI governance layer evaluation."""

    layer: str
    decision: CanadianAIDecision = CanadianAIDecision.APPROVED
    findings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        """True if this layer produced a DENIED decision."""
        return self.decision == CanadianAIDecision.DENIED

    @property
    def has_conditions(self) -> bool:
        """True if this layer produced an APPROVED_WITH_CONDITIONS decision."""
        return self.decision == CanadianAIDecision.APPROVED_WITH_CONDITIONS


# ---------------------------------------------------------------------------
# Layer 1 — Bill C-27 AIDA Compliance
# ---------------------------------------------------------------------------


class AIDAComplianceFilter:
    """
    Layer 1: Bill C-27 AIDA — Artificial Intelligence and Data Act.

    AIDA (Part 3 of Bill C-27) is Canada's first federal AI-specific statute.
    It establishes obligations for "high-impact" AI systems: completed impact
    assessments (s.6), transparency notices to affected persons (s.9),
    mitigation measures (s.10), incident monitoring (s.11), and compliance
    with ministerial orders (s.35). Systems that are exempt or low-impact
    receive conditions for monitoring and documentation. High-impact systems
    that fail any check are denied.

    References
    ----------
    Bill C-27, Part 3 — Artificial Intelligence and Data Act (AIDA)
    AIDA s.6  — Impact assessment for high-impact AI systems
    AIDA s.9  — Transparency obligation to affected persons
    AIDA s.10 — Mitigation measures
    AIDA s.11 — Incident monitoring and reporting
    AIDA s.35 — Ministerial orders
    Innovation, Science and Economic Development Canada — AIDA guidance (2023)
    """

    def evaluate(self, context: CanadaAIContext) -> CanadaAIGovernanceResult:  # noqa: C901
        result = CanadaAIGovernanceResult(layer="AIDA_COMPLIANCE")

        # Exempt systems: outside current AIDA scope
        if context.risk_level == CanadianAIRiskLevel.EXEMPT:
            result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "System exempt from AIDA — monitor for classification updates "
                "as Bill C-27 regulations are finalised; document rationale for "
                "exempt classification and review when AIDA regulations come into force"
            )
            return result

        # Low-impact, non-high-impact systems: lighter obligations
        if (
            context.risk_level == CanadianAIRiskLevel.LOW_IMPACT
            and not context.is_high_impact_system
        ):
            result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "AIDA: Low-impact system — maintain documentation for potential "
                "reclassification; review classification when Bill C-27 AIDA "
                "regulations are finalised and when system scope or use cases change"
            )
            return result

        # High-impact systems: full AIDA checks apply
        if context.is_high_impact_system:
            violations: List[str] = []

            if not context.impact_assessment_completed:
                violations.append(
                    "AIDA s.6: High-impact AI system must complete an impact "
                    "assessment addressing foreseeable risks before deployment — "
                    "no impact assessment has been completed"
                )

            if not context.transparency_notice_provided:
                violations.append(
                    "AIDA s.9: High-impact AI system must provide a transparency "
                    "notice informing affected persons that an AI system is being "
                    "used and the nature of its outputs — no transparency notice found"
                )

            if not context.ministerial_order_compliant:
                violations.append(
                    "AIDA s.35: Non-compliance with applicable ministerial order — "
                    "deployment of a high-impact AI system that violates a "
                    "ministerial order is prohibited"
                )

            if violations:
                result.decision = CanadianAIDecision.DENIED
                result.findings = violations
            else:
                result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
                result.conditions.extend([
                    "AIDA: High-impact system — maintain impact assessment records "
                    "and make available to ISED on request; update when system "
                    "functionality, training data, or deployment population changes",
                    "AIDA s.10: Mitigation measures must be kept current and "
                    "proportionate to the risks identified in the impact assessment",
                    "AIDA s.11: Incident monitoring and reporting required — "
                    "establish a process to detect, assess, and report incidents "
                    "involving the high-impact AI system",
                ])

            return result

        # Medium-impact, not flagged as high-impact: documentation condition
        result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
        result.conditions.append(
            "AIDA: Medium-impact classification — review whether the system "
            "meets the high-impact definition under Bill C-27 AIDA regulations "
            "when finalised; maintain documentation to support classification "
            "rationale"
        )
        return result


# ---------------------------------------------------------------------------
# Layer 2 — CPPA Data Governance
# ---------------------------------------------------------------------------


class CPPADataGovernanceFilter:
    """
    Layer 2: CPPA — Consumer Privacy Protection Act (Bill C-27, Part 1).

    The CPPA replaces PIPEDA as Canada's primary federal private-sector privacy
    law. For AI systems processing personal information, four obligations are
    mandatory: meaningful consent (s.15), purpose limitation (s.12), data
    minimization (s.13), and cross-border transfer safeguards (s.24). All four
    must be satisfied; failure on any one is an independent violation. Compliant
    systems receive conditions covering individuals' rights of access, correction,
    and portability.

    References
    ----------
    CPPA s.12  — Specification of purpose
    CPPA s.13  — Limiting collection, use, and disclosure
    CPPA s.15  — Meaningful consent
    CPPA s.24  — Cross-border transfers
    CPPA s.62  — Right of access and correction
    CPPA s.63  — Data portability
    OPC — CPPA guidance and advisory opinions
    """

    def evaluate(self, context: CanadaAIContext) -> CanadaAIGovernanceResult:
        result = CanadaAIGovernanceResult(layer="CPPA_DATA_GOVERNANCE")
        violations: List[str] = []

        if not context.meaningful_consent_obtained:
            violations.append(
                "CPPA s.15: Meaningful, informed consent is required before "
                "collecting, using, or disclosing personal information — consent "
                "must be obtained in plain language and cover the specific "
                "purposes for which the AI system processes personal information"
            )

        if not context.purpose_limitation_documented:
            violations.append(
                "CPPA s.12: The purpose of personal information collection must "
                "be specified before or at the time of collection — no documented "
                "purpose specification has been provided for the AI system's use "
                "of personal information"
            )

        if not context.data_minimization_applied:
            violations.append(
                "CPPA s.13: Collection, use, and disclosure of personal information "
                "must be limited to what is necessary for the identified purposes — "
                "data minimization controls have not been applied to the AI system's "
                "personal information processing"
            )

        if not context.cross_border_transfer_safeguards:
            violations.append(
                "CPPA s.24: Transfers of personal information to foreign "
                "jurisdictions require contractual protections ensuring that "
                "the recipient provides privacy protection equivalent to CPPA — "
                "no cross-border transfer safeguards have been put in place"
            )

        if violations:
            result.decision = CanadianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "CPPA s.62: Individuals retain the right to access, correct, "
                "and withdraw consent for use of their personal information — "
                "ensure mechanisms are in place to honour these rights promptly",
                "CPPA s.63: Data portability right — provide personal information "
                "in a structured, machine-readable format on request; verify AI "
                "system outputs and source data are portable",
                "CPPA: Privacy Management Programme must include AI-specific "
                "policies covering consent management, purpose limitation, and "
                "data minimization for AI training and inference pipelines",
            ])

        return result


# ---------------------------------------------------------------------------
# Layer 3 — OPC AI Guidelines 2023
# ---------------------------------------------------------------------------


class OPCGuidelinesFilter:
    """
    Layer 3: OPC AI Guidelines 2023 — Office of the Privacy Commissioner of
    Canada.

    The OPC published AI-specific guidelines in 2023 identifying five core
    privacy requirements for AI systems processing personal information. The
    guidelines build on CPPA obligations and apply the OPC's interpretation of
    existing privacy law to AI contexts. Three checks are mandatory violations:
    absence of meaningful consent, absence of human oversight, and absence of
    an accountability framework. Compliant systems receive conditions covering
    annual audits and documentation retention.

    References
    ----------
    OPC — Principles for responsible, trustworthy and privacy-protective AI (2023)
    OPC Guideline 1 — Meaningful consent
    OPC Guideline 2 — Data minimization for AI
    OPC Guideline 3 — Human oversight of automated decisions
    OPC Guideline 4 — Accuracy and reliability of AI outputs
    OPC Guideline 5 — Accountability and governance
    """

    def evaluate(self, context: CanadaAIContext) -> CanadaAIGovernanceResult:
        result = CanadaAIGovernanceResult(layer="OPC_AI_GUIDELINES")
        violations: List[str] = []

        if not context.meaningful_consent_obtained:
            violations.append(
                "OPC Guideline 1: Meaningful consent is foundational — consent "
                "must be clear, specific to the AI system's purposes, and obtained "
                "before personal information is used in AI processing; this "
                "obligation applies independently of CPPA s.15 consent requirements"
            )

        if not context.human_oversight_available:
            violations.append(
                "OPC Guideline 3: Meaningful human oversight is required for "
                "automated decisions affecting individuals — a mechanism for "
                "human review of AI-driven decisions must be available and "
                "accessible to affected individuals upon request"
            )

        if not context.accuracy_measures_in_place:
            violations.append(
                "OPC Guideline 4: Accuracy obligation — AI systems processing "
                "personal information must maintain data accuracy and implement "
                "measures to minimise harm arising from inaccurate or outdated "
                "personal information used in AI training or inference"
            )

        if not context.accountability_framework_exists:
            violations.append(
                "OPC Guideline 5: Accountability — one or more designated "
                "individual(s) must be responsible for CPPA and AI governance "
                "compliance; written policies covering AI-specific privacy "
                "risks, incident response, and audit procedures are required"
            )

        if violations:
            result.decision = CanadianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "OPC: Annual privacy audit recommended for AI systems processing "
                "personal information — include review of consent currency, "
                "data flows, model drift, and access rights fulfilment",
                "OPC Guideline 2: Limit personal information used to train or "
                "operate the AI system to what is strictly necessary; audit "
                "training datasets for excessive or irrelevant personal data",
                "OPC: Document all AI-related privacy assessments, consent "
                "records, and accountability assignments; retain records for "
                "OPC inspection and litigation purposes",
            ])

        return result


# ---------------------------------------------------------------------------
# Layer 4 — Québec Law 25
# ---------------------------------------------------------------------------


class QuebecLaw25Filter:
    """
    Layer 4: Québec Law 25 (Act Respecting the Protection of Personal
    Information in the Private Sector, as amended by Act 25, in force
    September 2023).

    Law 25 is the most stringent provincial privacy law in Canada and applies
    to any organisation doing business in Québec. Three obligations are
    specific to AI and automated decision-making: a mandatory Privacy Impact
    Assessment before deployment (s.63.3), public disclosure of automated
    decision logic and individual rights (s.12), and designation of a Chief
    Privacy Officer (s.3.1). When deploying_province is not "QC" this layer
    approves with a monitoring note. All three checks must pass for Québec
    deployments.

    References
    ----------
    Loi 25 — Loi modernisant des dispositions législatives en matière de
              protection des renseignements personnels (Act 25, 2021)
    Law 25 s.3.1  — Designation of a person responsible for personal information
    Law 25 s.12   — Transparency requirements for automated decisions
    Law 25 s.63.3 — Privacy Impact Assessment before automated decision deployment
    Commission d'accès à l'information — Law 25 guidance (2023)
    """

    def evaluate(self, context: CanadaAIContext) -> CanadaAIGovernanceResult:
        result = CanadaAIGovernanceResult(layer="QUEBEC_LAW_25")

        if context.deploying_province != "QC":
            result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "Québec Law 25 does not apply — system is not deployed in "
                "Québec. Monitor provincial privacy law developments across "
                "other Canadian provinces; British Columbia (PIPA) and Alberta "
                "(PIPA) impose similar obligations that may require attention"
            )
            return result

        # Québec deployment: full Law 25 checks apply
        violations: List[str] = []

        if not context.privacy_impact_assessment_done:
            violations.append(
                "Québec Law 25 s.63.3: A Privacy Impact Assessment (PIA) is "
                "mandatory before deploying any automated decision-making "
                "technology in Québec — no PIA has been completed; deployment "
                "must be halted until the PIA is conducted and documented"
            )

        if not context.algorithmic_transparency_published:
            violations.append(
                "Québec Law 25 s.12: Any organisation making automated decisions "
                "about individuals in Québec must publicly disclose the purpose "
                "of the system, the factors used in the decision, and the "
                "individual's right to request human review — no algorithmic "
                "transparency disclosure has been published"
            )

        if not context.data_governance_officer_designated:
            violations.append(
                "Québec Law 25 s.3.1: A person responsible for the protection of "
                "personal information (Chief Privacy Officer) must be designated "
                "for any organisation doing business in Québec — no CPO has been "
                "designated with the authority and resources to enforce Law 25"
            )

        if violations:
            result.decision = CanadianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = CanadianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "Québec Law 25: PIA must be updated whenever the technology, "
                "data sources, or intended uses of the automated decision-making "
                "system change materially; document each update",
                "Québec Law 25 s.12: Automated decision notices must be provided "
                "to affected individuals upon request, describing the factors "
                "used and the individual's right to request human review",
                "Québec Law 25: Data breaches involving personal information of "
                "Québec residents must be reported to the Commission d'accès à "
                "l'information within 30 days of discovery",
            ])

        return result


# ---------------------------------------------------------------------------
# Four-layer orchestrator
# ---------------------------------------------------------------------------


@dataclass
class CanadaAIGovernanceReport:
    """Aggregated Canadian AI governance report across all four layers."""

    context: CanadaAIContext
    layer_results: List[CanadaAIGovernanceResult]
    final_decision: CanadianAIDecision

    def summary(self) -> dict:
        """Return a serialisable summary of the full governance report."""
        return {
            "system_id": self.context.system_id,
            "system_name": self.context.system_name,
            "risk_level": self.context.risk_level.value,
            "deploying_province": self.context.deploying_province,
            "final_decision": self.final_decision.value,
            "layers": [
                {
                    "layer": r.layer,
                    "decision": r.decision.value,
                    "findings": r.findings,
                    "conditions": r.conditions,
                }
                for r in self.layer_results
            ],
        }


class CanadaAIGovernanceOrchestrator:
    """
    Four-layer Canadian AI governance orchestrator.

    Evaluation order:
        AIDA Compliance  →  CPPA Data Governance  →
        OPC AI Guidelines  →  Québec Law 25

    Decision aggregation:
    - Any DENIED layer → final decision is DENIED
    - No DENIED + any APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS
    - All APPROVED → APPROVED

    All four layers are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    """

    def __init__(self) -> None:
        self._filters = [
            AIDAComplianceFilter(),
            CPPADataGovernanceFilter(),
            OPCGuidelinesFilter(),
            QuebecLaw25Filter(),
        ]

    def evaluate(self, context: CanadaAIContext) -> CanadaAIGovernanceReport:
        """
        Evaluate all four Canadian governance layers and return an aggregated
        report.

        Parameters
        ----------
        context : CanadaAIContext
            The AI system context to evaluate.

        Returns
        -------
        CanadaAIGovernanceReport
            Full report containing per-layer results and a single final decision.
        """
        results = [f.evaluate(context) for f in self._filters]

        if any(r.is_denied for r in results):
            final = CanadianAIDecision.DENIED
        elif any(r.has_conditions for r in results):
            final = CanadianAIDecision.APPROVED_WITH_CONDITIONS
        else:
            final = CanadianAIDecision.APPROVED

        return CanadaAIGovernanceReport(
            context=context,
            layer_results=results,
            final_decision=final,
        )


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _fully_compliant_quebec_base() -> CanadaAIContext:
    """
    Base context: fully compliant HIGH_IMPACT AI system deployed in Québec.
    Used as the baseline from which failing scenarios are derived.
    """
    return CanadaAIContext(
        system_id="CA-AI-001",
        system_name="Québec Financial Services Credit-Risk Scoring System",
        risk_level=CanadianAIRiskLevel.HIGH_IMPACT,
        deploying_province="QC",
        # AIDA
        is_high_impact_system=True,
        impact_assessment_completed=True,
        transparency_notice_provided=True,
        ministerial_order_compliant=True,
        # CPPA
        meaningful_consent_obtained=True,
        purpose_limitation_documented=True,
        data_minimization_applied=True,
        cross_border_transfer_safeguards=True,
        # OPC Guidelines
        human_oversight_available=True,
        accuracy_measures_in_place=True,
        accountability_framework_exists=True,
        # Québec Law 25
        privacy_impact_assessment_done=True,
        algorithmic_transparency_published=True,
        data_governance_officer_designated=True,
    )


def scenario_1_compliant_quebec_high_impact() -> None:
    """
    Scenario 1: Fully compliant HIGH_IMPACT AI system deployed in Québec.

    All AIDA, CPPA, OPC, and Québec Law 25 checks pass.
    Expected: APPROVED_WITH_CONDITIONS (conditions from all four layers
    since high-impact + Québec deployment).
    """
    print("\n--- Scenario 1: Compliant HIGH_IMPACT Québec Credit-Risk AI ---")
    orch = CanadaAIGovernanceOrchestrator()
    ctx = _fully_compliant_quebec_base()
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


def scenario_2_non_quebec_missing_consent() -> None:
    """
    Scenario 2: Non-Québec (Ontario) MEDIUM_IMPACT system missing consent.

    Consent is absent → DENIED at both CPPA and OPC layers.
    Expected: DENIED.
    """
    print("\n--- Scenario 2: Ontario Medium-Impact AI — Missing Consent --- DENIED ---")
    orch = CanadaAIGovernanceOrchestrator()
    base = _fully_compliant_quebec_base()
    ctx = CanadaAIContext(
        system_id="CA-AI-002",
        system_name="Ontario HR Candidate Screening System",
        risk_level=CanadianAIRiskLevel.MEDIUM_IMPACT,
        deploying_province="ON",
        # AIDA — medium-impact, not flagged as high-impact
        is_high_impact_system=False,
        impact_assessment_completed=base.impact_assessment_completed,
        transparency_notice_provided=base.transparency_notice_provided,
        ministerial_order_compliant=base.ministerial_order_compliant,
        # CPPA — consent missing
        meaningful_consent_obtained=False,      # VIOLATION
        purpose_limitation_documented=base.purpose_limitation_documented,
        data_minimization_applied=base.data_minimization_applied,
        cross_border_transfer_safeguards=base.cross_border_transfer_safeguards,
        # OPC — consent also independently required
        human_oversight_available=base.human_oversight_available,
        accuracy_measures_in_place=base.accuracy_measures_in_place,
        accountability_framework_exists=base.accountability_framework_exists,
        # Québec Law 25 — not applicable (ON)
        privacy_impact_assessment_done=base.privacy_impact_assessment_done,
        algorithmic_transparency_published=base.algorithmic_transparency_published,
        data_governance_officer_designated=base.data_governance_officer_designated,
    )
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


def scenario_3_quebec_missing_pia() -> None:
    """
    Scenario 3: Québec HIGH_IMPACT system — all federal checks pass but
    Privacy Impact Assessment not completed.

    Expected: DENIED at Québec Law 25 layer.
    """
    print("\n--- Scenario 3: Québec High-Impact AI — Missing PIA --- DENIED ---")
    orch = CanadaAIGovernanceOrchestrator()
    base = _fully_compliant_quebec_base()
    ctx = CanadaAIContext(
        system_id="CA-AI-003",
        system_name="Québec Healthcare Triage Recommendation Engine",
        risk_level=CanadianAIRiskLevel.HIGH_IMPACT,
        deploying_province="QC",
        # AIDA — all pass
        is_high_impact_system=True,
        impact_assessment_completed=base.impact_assessment_completed,
        transparency_notice_provided=base.transparency_notice_provided,
        ministerial_order_compliant=base.ministerial_order_compliant,
        # CPPA — all pass
        meaningful_consent_obtained=base.meaningful_consent_obtained,
        purpose_limitation_documented=base.purpose_limitation_documented,
        data_minimization_applied=base.data_minimization_applied,
        cross_border_transfer_safeguards=base.cross_border_transfer_safeguards,
        # OPC — all pass
        human_oversight_available=base.human_oversight_available,
        accuracy_measures_in_place=base.accuracy_measures_in_place,
        accountability_framework_exists=base.accountability_framework_exists,
        # Québec Law 25 — PIA missing
        privacy_impact_assessment_done=False,   # VIOLATION
        algorithmic_transparency_published=base.algorithmic_transparency_published,
        data_governance_officer_designated=base.data_governance_officer_designated,
    )
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


def scenario_4_exempt_system() -> None:
    """
    Scenario 4: EXEMPT LOW_IMPACT internal analytics system deployed in BC.

    AIDA exemption applies; CPPA, OPC, and Law 25 (non-Québec) still checked.
    Expected: APPROVED_WITH_CONDITIONS across all layers (no denials).
    """
    print("\n--- Scenario 4: Exempt BC Internal Analytics System ---")
    orch = CanadaAIGovernanceOrchestrator()
    ctx = CanadaAIContext(
        system_id="CA-AI-004",
        system_name="BC Internal Operations Analytics Dashboard",
        risk_level=CanadianAIRiskLevel.EXEMPT,
        deploying_province="BC",
        # AIDA — exempt classification
        is_high_impact_system=False,
        impact_assessment_completed=False,
        transparency_notice_provided=False,
        ministerial_order_compliant=True,
        # CPPA — all pass
        meaningful_consent_obtained=True,
        purpose_limitation_documented=True,
        data_minimization_applied=True,
        cross_border_transfer_safeguards=True,
        # OPC — all pass
        human_oversight_available=True,
        accuracy_measures_in_place=True,
        accountability_framework_exists=True,
        # Québec Law 25 — not applicable (BC)
        privacy_impact_assessment_done=False,
        algorithmic_transparency_published=False,
        data_governance_officer_designated=False,
    )
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


if __name__ == "__main__":
    scenario_1_compliant_quebec_high_impact()
    scenario_2_non_quebec_missing_consent()
    scenario_3_quebec_missing_pia()
    scenario_4_exempt_system()
