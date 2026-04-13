"""
19_australia_ai_governance.py — Four-layer AI governance framework for AI systems
subject to Australian law, covering the overlapping federal and agency-level
obligations that apply to AI-driven data processing in Australia.

Demonstrates a multi-layer governance orchestrator where four Australian
regulatory frameworks each impose independent requirements on AI systems
deployed in Australia:

    Layer 1  — Australian AI Ethics Framework (DIIS, 8 principles):
               The Department of Industry, Innovation and Science (DIIS, formerly
               DISER) published Australia's AI Ethics Framework in 2019,
               establishing eight voluntary-but-expected principles for
               responsible AI development and deployment. Organisations deploying
               AI systems — particularly in government-adjacent and high-risk
               contexts — are expected to demonstrate alignment with all eight
               principles:
               (1) Human and Societal Wellbeing — AI systems must benefit
                   individuals, society, and the environment, with adverse
                   impacts assessed before deployment;
               (2) Human-Centred Values — AI must respect human rights, dignity,
                   and individual freedoms; design must place people at the centre;
               (3) Fairness — AI must not create or reinforce unfair bias or
                   discriminatory outcomes; ongoing bias monitoring required;
               (4) Privacy Protection and Security — personal data must be
                   protected throughout the AI lifecycle with appropriate
                   security safeguards;
               (5) Reliability and Safety — AI systems must perform reliably,
                   safely, and in accordance with their intended purpose;
                   validation against intended use cases is required;
               (6) Transparency and Explainability — stakeholders must be able
                   to understand when and how AI is being used, and the basis
                   of AI-driven decisions;
               (7) Contestability — affected individuals and groups must have
                   meaningful recourse to contest AI decisions;
               (8) Accountability — a responsible person or team must be
                   identifiable and accountable for AI outcomes.
               Exempt systems are flagged for annual classification review.
               High- and medium-risk systems must satisfy all seven checkable
               principles; compliant systems receive conditions for Principle 8
               (Fairness) ongoing monitoring and incident reporting.

    Layer 2  — Privacy Act 1988 — Australian Privacy Principles (APPs):
               The Privacy Act 1988 (Cth) and its thirteen Australian Privacy
               Principles (APPs) constitute Australia's primary federal privacy
               law, applicable to government agencies and private-sector
               organisations with annual turnover above AU$3 million. Four APPs
               are specifically material for AI systems:
               APP 1 — Open and transparent management of personal information:
                   Organisations must have a clearly expressed, up-to-date
                   privacy policy that is freely available (APP 1.3–1.4). For
                   AI systems this requires disclosure of what personal
                   information is collected, how it is used in AI processing,
                   and how individuals can seek access or correction;
               APP 3 — Collection of solicited personal information:
                   Personal information collected by AI systems must be
                   reasonably necessary for one or more of the entity's
                   functions, and individuals must be notified of the collection
                   and its purpose at or before the time of collection (APP 5);
               APP 6 — Use or disclosure of personal information:
                   Personal information must only be used or disclosed for the
                   primary purpose for which it was collected; secondary uses
                   require consent or must fall within a specific APP 6
                   exception; AI systems must not repurpose personal data
                   outside the original collection purpose without authorisation;
               APP 11 — Security of personal information:
                   Entities must take reasonable steps to protect personal
                   information from misuse, interference, loss, and unauthorised
                   access, modification, or disclosure; for AI systems this
                   includes data pipeline security, model access controls, and
                   output security. Compliant systems receive conditions
                   covering APP 12 (access rights), APP 13 (correction rights),
                   and the Notifiable Data Breach (NDB) scheme obligations.

    Layer 3  — Digital Transformation Agency (DTA) Automated Decision-Making
               (ADM) Framework:
               The Digital Transformation Agency published the Australian
               Government's framework for automated decision-making in 2020,
               updated in line with the Australian Public Service (APS) AI
               Strategy. The framework applies to Commonwealth government
               agencies and establishes three mandatory obligations for AI
               systems that make or materially influence decisions affecting
               individuals:
               (a) Right to human review — individuals affected by automated
                   government decisions must be informed of and able to request
                   a human review of that decision; this right cannot be
                   waived by policy or system design;
               (b) Explanation obligation — agencies must provide an explanation
                   of how an automated decision was made, on request from an
                   affected individual; explanations must be in plain language
                   and must identify the principal factors used;
               (c) Record-keeping — automated decisions must be documented in
                   a way that is compatible with the Freedom of Information
                   Act 1982 (FOI Act) retrieval obligations; agencies must be
                   able to produce decision records under an FOI request.
               Non-government systems receive a non-applicability note with
               direction to sector-specific guidance. Government systems failing
               any check are denied.

    Layer 4  — Australian Human Rights Commission (AHRC) AI Human Rights
               Guidelines:
               The Australian Human Rights Commission published its Human
               Rights and Technology Final Report in 2021 and subsequent
               AI guidelines, identifying obligations derived from Australia's
               international human rights commitments and domestic
               anti-discrimination legislation. Two checks are mandatory:
               (a) Non-discrimination and equality assessment — AI systems must
                   be assessed for potential discriminatory impact on protected
                   attributes under the Australian Human Rights Commission Act
                   1986, Racial Discrimination Act 1975, Sex Discrimination Act
                   1984, Age Discrimination Act 2004, and Disability
                   Discrimination Act 1992; the assessment must document
                   identified risks and the mitigations applied;
               (b) Accessible design verification — for medium- and high-risk
                   AI systems, the system's interfaces and outputs must be
                   verified for accessibility to people with disability under
                   the Disability Discrimination Act 1992; verification must
                   reference applicable accessibility standards (WCAG 2.1 AA
                   at minimum for digital interfaces). Compliant systems receive
                   conditions covering intersectional discrimination monitoring,
                   ongoing harm remediation, and consultation with affected
                   communities including First Nations peoples.

No external dependencies required.

Run:
    python examples/19_australia_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class AustralianAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under the Australian AI Ethics Framework.

    HIGH_RISK    — System has significant potential to affect individual rights,
                   safety, or welfare; all eight DIIS principles and full
                   inter-agency obligations apply.
    MEDIUM_RISK  — Meaningful but bounded risk; principles and key obligations
                   apply; accessibility verification required.
    LOW_RISK     — Limited potential for harm; core principles apply but
                   lighter conditions; some checks adjusted accordingly.
    EXEMPT       — Falls outside current framework scope; monitor for
                   regulatory clarification; voluntary adoption of all
                   eight principles recommended.
    """

    HIGH_RISK = "high_risk"
    MEDIUM_RISK = "medium_risk"
    LOW_RISK = "low_risk"
    EXEMPT = "exempt"


class AustralianAIDecision(str, Enum):
    """Final governance decision for an Australian AI system evaluation."""

    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    DENIED = "denied"


class AustralianSector(str, Enum):
    """
    Deployment sector for the AI system.

    GOVERNMENT          — Commonwealth or state government agency; DTA ADM
                          Framework obligations apply in Layer 3.
    PRIVATE_SECTOR      — General private-sector organisation; DTA ADM
                          Framework does not apply.
    HEALTH              — Healthcare or medical AI deployment; heightened
                          privacy and safety obligations apply.
    FINANCIAL_SERVICES  — ASIC/APRA-regulated financial services entity;
                          additional sector guidance applies.
    EDUCATION           — Educational institution; student data obligations
                          apply under Privacy Act.
    """

    GOVERNMENT = "government"
    PRIVATE_SECTOR = "private_sector"
    HEALTH = "health"
    FINANCIAL_SERVICES = "financial_services"
    EDUCATION = "education"


# ---------------------------------------------------------------------------
# Frozen context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AustraliaAIContext:
    """
    Governance review context for an Australian AI system.

    Attributes
    ----------
    system_id : str
        Unique identifier for the AI system under review.
    system_name : str
        Human-readable name of the AI system.
    risk_level : AustralianAIRiskLevel
        Risk classification under the Australian AI Ethics Framework (DIIS).
    deploying_sector : AustralianSector
        The sector in which the AI system is deployed. A value of
        ``AustralianSector.GOVERNMENT`` triggers DTA ADM Framework checks
        in Layer 3.

    — Australian AI Ethics Framework (DIIS 8 principles) —

    human_societal_wellbeing_assessed : bool
        True if an impact assessment for human and societal wellbeing has been
        completed before deployment (DIIS Principle 1).
    human_centred_design_applied : bool
        True if human-centred design processes have been applied, ensuring
        the AI system respects human rights, dignity, and individual freedom
        (DIIS Principle 2).
    privacy_protection_in_place : bool
        True if privacy protection and security measures are in place to
        safeguard personal data throughout the AI lifecycle (DIIS Principle 3).
    reliability_safety_validated : bool
        True if reliability and safety validation has been completed for the
        AI system's intended purpose and use cases (DIIS Principle 4).
    transparency_explainability_provided : bool
        True if transparency and explainability mechanisms are in place,
        enabling stakeholders to understand AI decisions and their basis
        (DIIS Principle 5).
    contestability_mechanism_available : bool
        True if a contestability mechanism exists allowing affected parties
        to challenge or appeal AI-driven decisions (DIIS Principle 6).
    accountability_governance_exists : bool
        True if an accountability governance structure exists identifying
        responsible individuals or teams for AI outcomes (DIIS Principle 7).

    — Privacy Act 1988 APPs —

    app1_privacy_policy_published : bool
        True if a current, clearly expressed privacy policy covering the AI
        system's personal information handling is freely available to the
        public (APP 1).
    app3_collection_consent_valid : bool
        True if personal information collected by the AI system is reasonably
        necessary and individuals have been notified of the collection and its
        purpose at or before the time of collection (APP 3 / APP 5).
    app6_use_disclosure_limited : bool
        True if personal information is used and disclosed only for the
        primary purpose of collection; secondary uses are authorised by
        consent or an applicable APP 6 exception (APP 6).
    app11_security_safeguards : bool
        True if reasonable security safeguards protect personal information
        from misuse, interference, loss, and unauthorised access, modification,
        or disclosure throughout the AI data pipeline (APP 11).

    — DTA ADM Framework (Government sector only) —

    human_review_right_provided : bool
        True if individuals affected by automated government decisions are
        informed of and able to exercise a right to request human review of
        those decisions (DTA ADM Framework).
    explanation_obligation_met : bool
        True if the agency provides, on request, a plain-language explanation
        of how an automated decision affecting an individual was made,
        identifying the principal factors used (DTA ADM Framework).
    adm_record_keeping_current : bool
        True if automated decision records are maintained in a format
        compatible with Freedom of Information Act 1982 retrieval obligations
        (DTA ADM Framework / FOI Act 1982).

    — AHRC AI Human Rights Guidelines —

    non_discrimination_assessment_done : bool
        True if a non-discrimination and equality impact assessment has been
        completed, addressing protected attributes under the Australian Human
        Rights Commission Act 1986, Racial Discrimination Act 1975, Sex
        Discrimination Act 1984, Age Discrimination Act 2004, and Disability
        Discrimination Act 1992 (AHRC AI Guidelines).
    accessible_design_verified : bool
        True if the AI system's interfaces and outputs have been verified for
        accessibility to people with disability, referencing applicable
        standards (WCAG 2.1 AA minimum for digital interfaces) under the
        Disability Discrimination Act 1992 (AHRC AI Guidelines).
    """

    # System identity
    system_id: str
    system_name: str
    risk_level: AustralianAIRiskLevel
    deploying_sector: AustralianSector

    # Australian AI Ethics Framework (DIIS 8 principles)
    human_societal_wellbeing_assessed: bool      # Principle 1: Human and societal wellbeing
    human_centred_design_applied: bool           # Principle 2: Human-centred values
    privacy_protection_in_place: bool            # Principle 3: Privacy protection and security
    reliability_safety_validated: bool           # Principle 4: Reliability and safety
    transparency_explainability_provided: bool   # Principle 5: Transparency and explainability
    contestability_mechanism_available: bool     # Principle 6: Contestability
    accountability_governance_exists: bool       # Principle 7: Accountability

    # Privacy Act 1988 APPs
    app1_privacy_policy_published: bool     # APP 1: Open and transparent management
    app3_collection_consent_valid: bool     # APP 3: Collection of solicited personal information
    app6_use_disclosure_limited: bool       # APP 6: Use or disclosure of personal information
    app11_security_safeguards: bool         # APP 11: Security of personal information

    # DTA ADM Framework (Government sector only — deploying_sector == GOVERNMENT)
    human_review_right_provided: bool       # Right to human review of automated decisions
    explanation_obligation_met: bool        # Explanation of automated decision provided on request
    adm_record_keeping_current: bool        # ADM decision records maintained (FOI Act compatible)

    # AHRC AI Human Rights
    non_discrimination_assessment_done: bool   # Non-discrimination and equality assessment
    accessible_design_verified: bool           # Disability Discrimination Act 1992 accessibility


# ---------------------------------------------------------------------------
# Per-layer result
# ---------------------------------------------------------------------------


@dataclass
class AustraliaAIGovernanceResult:
    """Result of a single Australian AI governance layer evaluation."""

    layer: str
    decision: AustralianAIDecision = AustralianAIDecision.APPROVED
    findings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        """True if this layer produced a DENIED decision."""
        return self.decision == AustralianAIDecision.DENIED

    @property
    def has_conditions(self) -> bool:
        """True if this layer produced an APPROVED_WITH_CONDITIONS decision."""
        return self.decision == AustralianAIDecision.APPROVED_WITH_CONDITIONS


# ---------------------------------------------------------------------------
# Layer 1 — Australian AI Ethics Framework (DIIS)
# ---------------------------------------------------------------------------


class AustralianAIEthicsFilter:
    """
    Layer 1: Australian AI Ethics Framework — Department of Industry,
    Innovation and Science (DIIS), 8 Principles (2019, updated 2023).

    The DIIS AI Ethics Framework establishes eight principles for responsible
    AI development and deployment in Australia. Although the framework is
    voluntary at federal level, government agencies and regulated-sector
    organisations are expected to demonstrate compliance. Principles 1–7 are
    evaluated as mandatory checks for non-exempt systems; Principle 8
    (Fairness) is enforced as an ongoing monitoring condition because bias
    assessment is continuous rather than a one-time gate. Exempt systems are
    flagged for annual classification review with a recommendation to adopt all
    eight principles voluntarily. Low-risk systems omit the privacy check
    (Principle 3) since they do not typically process personal information at
    scale.

    References
    ----------
    DIIS — Australia's Artificial Intelligence Ethics Framework (2019)
    DIIS — Principles for Responsible AI (2022 update)
    DIIS — Voluntary AI Safety Standard (2023)
    Australian Government AI in Government Policy (2023)
    """

    def evaluate(self, context: AustraliaAIContext) -> AustraliaAIGovernanceResult:  # noqa: C901
        result = AustraliaAIGovernanceResult(layer="AUSTRALIAN_AI_ETHICS_FRAMEWORK")

        # Exempt systems: outside current scope; flag for annual review
        if context.risk_level == AustralianAIRiskLevel.EXEMPT:
            result.decision = AustralianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "Australian AI Ethics Framework: System classified as exempt — "
                "review classification annually; voluntary adoption of all 8 "
                "principles recommended"
            )
            return result

        # Non-exempt systems: evaluate Principles 1–7
        violations: List[str] = []

        if not context.human_societal_wellbeing_assessed:
            violations.append(
                f"AI Ethics Principle 1 (Human and Societal Wellbeing): Impact "
                f"assessment for human and societal wellbeing not completed — "
                f"required for {context.risk_level.value} systems"
            )

        if not context.human_centred_design_applied:
            violations.append(
                "AI Ethics Principle 2 (Human-Centred Values): Human-centred "
                "design process not applied — AI must respect human rights, "
                "dignity, and freedom"
            )

        if not context.privacy_protection_in_place and context.risk_level != AustralianAIRiskLevel.LOW_RISK:
            violations.append(
                "AI Ethics Principle 3 (Privacy Protection): Privacy protection "
                "measures not in place — security safeguards required"
            )

        if not context.reliability_safety_validated:
            violations.append(
                "AI Ethics Principle 4 (Reliability and Safety): System "
                "reliability and safety validation not completed — testing "
                "against intended use required"
            )

        if not context.transparency_explainability_provided:
            violations.append(
                "AI Ethics Principle 5 (Transparency and Explainability): "
                "Transparency and explainability mechanisms not provided — "
                "stakeholders must understand AI decisions"
            )

        if not context.contestability_mechanism_available:
            violations.append(
                "AI Ethics Principle 6 (Contestability): No contestability "
                "mechanism — affected parties must have recourse to challenge "
                "AI decisions"
            )

        if not context.accountability_governance_exists:
            violations.append(
                "AI Ethics Principle 7 (Accountability): No accountability "
                "governance — responsible individual or team must be identifiable"
            )

        if violations:
            result.decision = AustralianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = AustralianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "AI Ethics: Annual review against all 8 DIIS principles recommended",
                "AI Ethics Principle 8 (Fairness): Ongoing monitoring for bias "
                "and discriminatory outcomes required",
                "AI Ethics: Incident reporting process should be established for "
                "AI failures",
            ])

        return result


# ---------------------------------------------------------------------------
# Layer 2 — Privacy Act 1988 Australian Privacy Principles (APPs)
# ---------------------------------------------------------------------------


class PrivacyActAPPsFilter:
    """
    Layer 2: Privacy Act 1988 (Cth) — Australian Privacy Principles (APPs).

    The Privacy Act 1988 and its thirteen Australian Privacy Principles govern
    how personal information is collected, used, disclosed, and protected by
    Australian government agencies and private-sector organisations with annual
    turnover above AU$3 million (with lower thresholds for health service
    providers). Four APPs are evaluated as mandatory gates for AI systems:
    APP 1 (open and transparent management), APP 3 (collection consent and
    notification), APP 6 (purpose limitation for use and disclosure), and
    APP 11 (security safeguards). All four must be satisfied; failure on any
    one is an independent violation. Compliant systems receive conditions
    covering APP 12 (access), APP 13 (correction), and the Notifiable Data
    Breach scheme.

    References
    ----------
    Privacy Act 1988 (Cth)
    APP 1  — Open and transparent management of personal information
    APP 3  — Collection of solicited personal information
    APP 5  — Notification of the collection of personal information
    APP 6  — Use or disclosure of personal information
    APP 11 — Security of personal information
    APP 12 — Access to personal information
    APP 13 — Correction of personal information
    OAIC — Privacy and AI guidance (2023)
    Privacy Amendment (Notifiable Data Breaches) Act 2017 (NDB scheme)
    """

    def evaluate(self, context: AustraliaAIContext) -> AustraliaAIGovernanceResult:
        result = AustraliaAIGovernanceResult(layer="PRIVACY_ACT_1988_APPs")
        violations: List[str] = []

        if not context.app1_privacy_policy_published:
            violations.append(
                "APP 1: Privacy policy must be published and freely available — "
                "open and transparent management of personal information required"
            )

        if not context.app3_collection_consent_valid:
            violations.append(
                "APP 3: Collection of personal information must be reasonably "
                "necessary and consent valid — notification of collection required"
            )

        if not context.app6_use_disclosure_limited:
            violations.append(
                "APP 6: Personal information must only be used or disclosed for "
                "the primary purpose of collection — secondary use requires "
                "consent or exception"
            )

        if not context.app11_security_safeguards:
            violations.append(
                "APP 11: Reasonable security safeguards required to protect "
                "personal information from misuse, interference, loss, and "
                "unauthorised access"
            )

        if violations:
            result.decision = AustralianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = AustralianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "APP 12: Individuals have right to access their personal "
                "information — must be provided within 30 days",
                "APP 13: Correction right — individuals may request correction "
                "of inaccurate personal information",
                "Privacy Act: Notifiable Data Breach (NDB) scheme — breaches "
                "likely to cause serious harm must be notified to OAIC and "
                "affected individuals",
            ])

        return result


# ---------------------------------------------------------------------------
# Layer 3 — DTA Automated Decision-Making (ADM) Framework
# ---------------------------------------------------------------------------


class DTAADMFilter:
    """
    Layer 3: Digital Transformation Agency (DTA) Automated Decision-Making
    (ADM) Framework — Australian Government (2020, updated per APS AI Strategy
    2023).

    The DTA ADM Framework applies to Commonwealth government agencies deploying
    AI systems that make or materially influence decisions affecting individuals.
    It establishes three mandatory obligations: right to human review, obligation
    to explain automated decisions on request, and FOI-compatible record-keeping.
    Non-government systems receive a non-applicability note with direction to
    sector-specific guidance. Government systems that fail any check are denied;
    fully compliant government systems receive ongoing operational conditions.

    References
    ----------
    DTA — Automated Decision-Making Better Practice Guide (2020)
    Australian Government — APS Artificial Intelligence Strategy (2023)
    DTA — Digital Service Standard — Automated Decision-Making guidance
    Freedom of Information Act 1982 (Cth) — record-keeping obligations
    OAIC — Privacy considerations for automated decision systems (2022)
    """

    def evaluate(self, context: AustraliaAIContext) -> AustraliaAIGovernanceResult:
        result = AustraliaAIGovernanceResult(layer="DTA_ADM_FRAMEWORK")

        # Non-government systems: DTA ADM Framework does not apply
        if context.deploying_sector != AustralianSector.GOVERNMENT:
            result.decision = AustralianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.append(
                "DTA ADM Framework applies to Commonwealth government agencies "
                "only — private sector should refer to Australian AI Ethics "
                "Framework and relevant sector-specific guidance"
            )
            return result

        # Government sector: full ADM Framework checks apply
        violations: List[str] = []

        if not context.human_review_right_provided:
            violations.append(
                "DTA ADM Framework: Right to request human review of automated "
                "decisions is mandatory for government agency AI systems "
                "affecting individuals"
            )

        if not context.explanation_obligation_met:
            violations.append(
                "DTA ADM Framework: Obligation to explain automated decisions "
                "on request — individuals must be able to understand how "
                "decisions affecting them were made"
            )

        if not context.adm_record_keeping_current:
            violations.append(
                "DTA ADM Framework: Decision record-keeping required — automated "
                "decisions must be documented and retrievable under the Freedom "
                "of Information Act 1982"
            )

        if violations:
            result.decision = AustralianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = AustralianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "DTA ADM: Human review requests must be processed within "
                "standard administrative decision-review timeframes",
                "DTA ADM: Consult the OAIC before deploying AI systems that "
                "handle sensitive personal information",
                "DTA ADM: Annual review of automated decision systems "
                "recommended per APS AI Strategy",
            ])

        return result


# ---------------------------------------------------------------------------
# Layer 4 — AHRC AI Human Rights Guidelines
# ---------------------------------------------------------------------------


class AHRCAIGuidelinesFilter:
    """
    Layer 4: Australian Human Rights Commission (AHRC) AI Human Rights
    Guidelines — Human Rights and Technology Final Report (2021) and
    subsequent AI guidelines.

    The AHRC guidelines translate Australia's international human rights
    commitments and domestic anti-discrimination legislation into AI governance
    obligations. Two checks are mandatory: a non-discrimination and equality
    impact assessment covering all relevant Acts, and — for medium- and
    high-risk systems — verification that AI interfaces are accessible to
    people with disability. Compliant systems receive conditions covering
    intersectional discrimination monitoring, ongoing harm remediation, and
    consultation with affected communities including First Nations peoples.

    References
    ----------
    AHRC — Human Rights and Technology Final Report (2021)
    AHRC — Using Artificial Intelligence to Make Decisions: Addressing the
            Problem of Algorithmic Bias (2020)
    Australian Human Rights Commission Act 1986 (Cth)
    Racial Discrimination Act 1975 (Cth)
    Sex Discrimination Act 1984 (Cth)
    Age Discrimination Act 2004 (Cth)
    Disability Discrimination Act 1992 (Cth)
    WCAG 2.1 Level AA — Web Content Accessibility Guidelines
    """

    def evaluate(self, context: AustraliaAIContext) -> AustraliaAIGovernanceResult:
        result = AustraliaAIGovernanceResult(layer="AHRC_AI_HUMAN_RIGHTS")
        violations: List[str] = []

        if not context.non_discrimination_assessment_done:
            violations.append(
                "AHRC AI Guidelines: Non-discrimination and equality assessment "
                "required — AI must not have discriminatory impact on protected "
                "attributes under Australian Human Rights Commission Act 1986, "
                "Racial Discrimination Act 1975, Sex Discrimination Act 1984, "
                "Disability Discrimination Act 1992"
            )

        if (
            not context.accessible_design_verified
            and context.risk_level in {
                AustralianAIRiskLevel.HIGH_RISK,
                AustralianAIRiskLevel.MEDIUM_RISK,
            }
        ):
            violations.append(
                "AHRC AI Guidelines / Disability Discrimination Act 1992: "
                "Accessibility verification required for medium and high-risk "
                "AI systems — AI interfaces must be accessible to people with "
                "disability"
            )

        if violations:
            result.decision = AustralianAIDecision.DENIED
            result.findings = violations
        else:
            result.decision = AustralianAIDecision.APPROVED_WITH_CONDITIONS
            result.conditions.extend([
                "AHRC: Impact assessment should consider intersectional "
                "discrimination (multiple protected attributes)",
                "AHRC: Ongoing monitoring for discriminatory outcomes required "
                "— document and remediate any identified harms",
                "AHRC: Consult with affected communities, particularly First "
                "Nations peoples, before deploying AI systems that affect them",
            ])

        return result


# ---------------------------------------------------------------------------
# Four-layer orchestrator
# ---------------------------------------------------------------------------


@dataclass
class AustraliaAIGovernanceReport:
    """Aggregated Australian AI governance report across all four layers."""

    context: AustraliaAIContext
    layer_results: List[AustraliaAIGovernanceResult]
    final_decision: AustralianAIDecision

    def summary(self) -> dict:
        """Return a serialisable summary of the full governance report."""
        return {
            "system_id": self.context.system_id,
            "system_name": self.context.system_name,
            "risk_level": self.context.risk_level.value,
            "deploying_sector": self.context.deploying_sector.value,
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


class AustraliaAIGovernanceOrchestrator:
    """
    Four-layer Australian AI governance orchestrator.

    Evaluation order:
        AustralianAIEthicsFilter  →  PrivacyActAPPsFilter  →
        DTAADMFilter  →  AHRCAIGuidelinesFilter

    Decision aggregation:
    - Any DENIED layer → final decision is DENIED
    - No DENIED + any APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS
    - All APPROVED → APPROVED

    All four layers are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    """

    def __init__(self) -> None:
        self._filters = [
            AustralianAIEthicsFilter(),
            PrivacyActAPPsFilter(),
            DTAADMFilter(),
            AHRCAIGuidelinesFilter(),
        ]

    def evaluate(self, context: AustraliaAIContext) -> AustraliaAIGovernanceReport:
        """
        Evaluate all four Australian governance layers and return an aggregated
        report.

        Parameters
        ----------
        context : AustraliaAIContext
            The AI system context to evaluate.

        Returns
        -------
        AustraliaAIGovernanceReport
            Full report containing per-layer results and a single final decision.
        """
        results = [f.evaluate(context) for f in self._filters]

        if any(r.is_denied for r in results):
            final = AustralianAIDecision.DENIED
        elif any(r.has_conditions for r in results):
            final = AustralianAIDecision.APPROVED_WITH_CONDITIONS
        else:
            final = AustralianAIDecision.APPROVED

        return AustraliaAIGovernanceReport(
            context=context,
            layer_results=results,
            final_decision=final,
        )


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _fully_compliant_government_high_risk_base() -> AustraliaAIContext:
    """
    Base context: fully compliant HIGH_RISK government AI system.
    Used as the baseline from which failing scenarios are derived.
    """
    return AustraliaAIContext(
        system_id="AU-AI-001",
        system_name="Commonwealth Government Benefits Eligibility Assessment System",
        risk_level=AustralianAIRiskLevel.HIGH_RISK,
        deploying_sector=AustralianSector.GOVERNMENT,
        # DIIS AI Ethics Framework — Principles 1–7
        human_societal_wellbeing_assessed=True,
        human_centred_design_applied=True,
        privacy_protection_in_place=True,
        reliability_safety_validated=True,
        transparency_explainability_provided=True,
        contestability_mechanism_available=True,
        accountability_governance_exists=True,
        # Privacy Act 1988 APPs
        app1_privacy_policy_published=True,
        app3_collection_consent_valid=True,
        app6_use_disclosure_limited=True,
        app11_security_safeguards=True,
        # DTA ADM Framework
        human_review_right_provided=True,
        explanation_obligation_met=True,
        adm_record_keeping_current=True,
        # AHRC AI Human Rights
        non_discrimination_assessment_done=True,
        accessible_design_verified=True,
    )


def scenario_1_compliant_government_high_risk() -> None:
    """
    Scenario 1: Fully compliant HIGH_RISK government AI system.

    All DIIS, Privacy Act, DTA ADM, and AHRC checks pass.
    Expected: APPROVED_WITH_CONDITIONS (all four layers produce conditions;
    no denials).
    """
    print(
        "\n--- Scenario 1: Compliant HIGH_RISK Government Benefits AI "
        "--- APPROVED_WITH_CONDITIONS ---"
    )
    orch = AustraliaAIGovernanceOrchestrator()
    ctx = _fully_compliant_government_high_risk_base()
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


def scenario_2_private_sector_compliant() -> None:
    """
    Scenario 2: Fully compliant MEDIUM_RISK private-sector AI system.

    DTA ADM Framework Layer 3 returns APPROVED_WITH_CONDITIONS with a
    non-applicability note (not a denial) since deploying_sector is
    PRIVATE_SECTOR. All other layers pass.
    Expected: APPROVED_WITH_CONDITIONS.
    """
    print(
        "\n--- Scenario 2: Compliant MEDIUM_RISK Private-Sector AI "
        "--- APPROVED_WITH_CONDITIONS ---"
    )
    orch = AustraliaAIGovernanceOrchestrator()
    base = _fully_compliant_government_high_risk_base()
    ctx = AustraliaAIContext(
        system_id="AU-AI-002",
        system_name="Financial Services Customer Credit Risk Scoring Engine",
        risk_level=AustralianAIRiskLevel.MEDIUM_RISK,
        deploying_sector=AustralianSector.FINANCIAL_SERVICES,
        # DIIS AI Ethics Framework — all pass
        human_societal_wellbeing_assessed=base.human_societal_wellbeing_assessed,
        human_centred_design_applied=base.human_centred_design_applied,
        privacy_protection_in_place=base.privacy_protection_in_place,
        reliability_safety_validated=base.reliability_safety_validated,
        transparency_explainability_provided=base.transparency_explainability_provided,
        contestability_mechanism_available=base.contestability_mechanism_available,
        accountability_governance_exists=base.accountability_governance_exists,
        # Privacy Act 1988 APPs — all pass
        app1_privacy_policy_published=base.app1_privacy_policy_published,
        app3_collection_consent_valid=base.app3_collection_consent_valid,
        app6_use_disclosure_limited=base.app6_use_disclosure_limited,
        app11_security_safeguards=base.app11_security_safeguards,
        # DTA ADM — not applicable (private sector); fields irrelevant but provided
        human_review_right_provided=base.human_review_right_provided,
        explanation_obligation_met=base.explanation_obligation_met,
        adm_record_keeping_current=base.adm_record_keeping_current,
        # AHRC — all pass
        non_discrimination_assessment_done=base.non_discrimination_assessment_done,
        accessible_design_verified=base.accessible_design_verified,
    )
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


def scenario_3_government_missing_human_review() -> None:
    """
    Scenario 3: HIGH_RISK government system — all ethics and privacy checks pass
    but human_review_right_provided is False.

    DTA ADM Framework check fails.
    Expected: DENIED.
    """
    print(
        "\n--- Scenario 3: Government HIGH_RISK AI — Missing Human Review Right "
        "--- DENIED ---"
    )
    orch = AustraliaAIGovernanceOrchestrator()
    base = _fully_compliant_government_high_risk_base()
    ctx = AustraliaAIContext(
        system_id="AU-AI-003",
        system_name="Commonwealth Employment Services Automated Job Matching System",
        risk_level=AustralianAIRiskLevel.HIGH_RISK,
        deploying_sector=AustralianSector.GOVERNMENT,
        # DIIS AI Ethics Framework — all pass
        human_societal_wellbeing_assessed=base.human_societal_wellbeing_assessed,
        human_centred_design_applied=base.human_centred_design_applied,
        privacy_protection_in_place=base.privacy_protection_in_place,
        reliability_safety_validated=base.reliability_safety_validated,
        transparency_explainability_provided=base.transparency_explainability_provided,
        contestability_mechanism_available=base.contestability_mechanism_available,
        accountability_governance_exists=base.accountability_governance_exists,
        # Privacy Act 1988 APPs — all pass
        app1_privacy_policy_published=base.app1_privacy_policy_published,
        app3_collection_consent_valid=base.app3_collection_consent_valid,
        app6_use_disclosure_limited=base.app6_use_disclosure_limited,
        app11_security_safeguards=base.app11_security_safeguards,
        # DTA ADM — human review right missing
        human_review_right_provided=False,          # VIOLATION
        explanation_obligation_met=base.explanation_obligation_met,
        adm_record_keeping_current=base.adm_record_keeping_current,
        # AHRC — all pass
        non_discrimination_assessment_done=base.non_discrimination_assessment_done,
        accessible_design_verified=base.accessible_design_verified,
    )
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


def scenario_4_missing_non_discrimination_assessment() -> None:
    """
    Scenario 4: HIGH_RISK private-sector health AI system — all ethics,
    privacy, and DTA checks pass (DTA non-applicable for private sector)
    but non_discrimination_assessment_done is False.

    AHRC AI Guidelines check fails.
    Expected: DENIED.
    """
    print(
        "\n--- Scenario 4: Private-Sector Health AI — Missing Non-Discrimination "
        "Assessment --- DENIED ---"
    )
    orch = AustraliaAIGovernanceOrchestrator()
    base = _fully_compliant_government_high_risk_base()
    ctx = AustraliaAIContext(
        system_id="AU-AI-004",
        system_name="AI-Assisted Clinical Triage and Patient Prioritisation Engine",
        risk_level=AustralianAIRiskLevel.HIGH_RISK,
        deploying_sector=AustralianSector.HEALTH,
        # DIIS AI Ethics Framework — all pass
        human_societal_wellbeing_assessed=base.human_societal_wellbeing_assessed,
        human_centred_design_applied=base.human_centred_design_applied,
        privacy_protection_in_place=base.privacy_protection_in_place,
        reliability_safety_validated=base.reliability_safety_validated,
        transparency_explainability_provided=base.transparency_explainability_provided,
        contestability_mechanism_available=base.contestability_mechanism_available,
        accountability_governance_exists=base.accountability_governance_exists,
        # Privacy Act 1988 APPs — all pass
        app1_privacy_policy_published=base.app1_privacy_policy_published,
        app3_collection_consent_valid=base.app3_collection_consent_valid,
        app6_use_disclosure_limited=base.app6_use_disclosure_limited,
        app11_security_safeguards=base.app11_security_safeguards,
        # DTA ADM — not applicable (health/private sector); fields provided for completeness
        human_review_right_provided=base.human_review_right_provided,
        explanation_obligation_met=base.explanation_obligation_met,
        adm_record_keeping_current=base.adm_record_keeping_current,
        # AHRC — non-discrimination assessment missing
        non_discrimination_assessment_done=False,   # VIOLATION
        accessible_design_verified=base.accessible_design_verified,
    )
    report = orch.evaluate(ctx)
    import json
    print(json.dumps(report.summary(), indent=2))


if __name__ == "__main__":
    scenario_1_compliant_government_high_risk()
    scenario_2_private_sector_compliant()
    scenario_3_government_missing_human_review()
    scenario_4_missing_non_discrimination_assessment()
