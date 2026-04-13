"""
21_japan_ai_governance.py — Four-layer AI governance framework for AI systems
subject to Japanese law, covering the overlapping national and sector-level
obligations that apply to AI-driven data processing in Japan.

Demonstrates a multi-layer governance orchestrator where four Japanese
regulatory frameworks each impose independent requirements on AI systems
deployed in Japan:

    Layer 1  — APPI (Act on the Protection of Personal Information, 2022
               amendments):
               Japan's Act on the Protection of Personal Information (APPI,
               Act No. 57 of 2003, substantially amended effective April 1,
               2022) is the primary data protection statute administered by
               the Personal Information Protection Commission (PPC). The 2022
               amendments significantly strengthened obligations relevant to
               AI systems:
               Article 2(3) — Special Care-Required Personal Information
                   (sensitive personal information): racial origin, creed,
                   social status, medical history, criminal record, having
                   suffered a crime, and disability status are designated
                   special-care categories requiring opt-in consent before
                   collection or use;
               Article 17 — Purpose Specification: personal information must
                   be acquired only to the extent necessary for the specified
                   purpose; the purpose must be communicated to the individual
                   before or at the time of acquisition;
               Article 19 — Data Minimization Principle: personal information
                   must not be handled beyond the scope necessary to achieve
                   the specified purpose; AI systems processing non-necessary
                   data for medium- and high-risk use cases must be flagged;
               Article 20-2 — Sensitive Personal Information: opt-in consent
                   required for any collection or use of special-care-required
                   personal information; no consent exception applies for
                   automated AI processing of health, criminal, or disability
                   data;
               Article 27 — Third-Party Provision: personal information must
                   not be provided to a third party (including another AI
                   processing pipeline) without the individual's consent or a
                   recognised lawful basis (opt-out, entrustment, shared use,
                   legal requirement);
               Article 28 — Cross-Border Transfer: transferring personal
                   information to a recipient in a foreign country requires
                   either an adequacy finding by the PPC (EU/UK received
                   adequacy in 2019; others require contractual safeguards) or
                   the individual's informed consent.

    Layer 2  — METI AI Governance Guidelines v1.1 (2022):
               Japan's Ministry of Economy, Trade and Industry (METI)
               published AI Governance Guidelines Version 1.1 in July 2022,
               establishing a risk-based, principle-centred governance
               framework for businesses that develop and deploy AI in Japan.
               The guidelines articulate seven core principles:
               Principle 2 (Human Involvement) — AI systems used in high-
                   impact automated decisions that affect individuals must
                   retain a meaningful human oversight pathway; fully
                   automated high-risk decisions without human oversight are
                   non-compliant;
               Principle 3 (Fairness / Non-Discrimination) — AI systems that
                   could produce discriminatory outcomes must be tested for
                   bias; medium- and high-risk AI systems must document
                   fairness testing and remediation;
               Principle 5 (Transparency / Explainability) — individuals
                   subject to automated AI decisions must be able to obtain
                   a meaningful explanation of how the decision was reached;
                   black-box models used in automated decisions require
                   compensating explainability mechanisms;
               Principle 6 (Accountability) — organisations deploying high-
                   risk AI must define a clear accountability chain assigning
                   responsibility for AI outcomes; accountability frameworks
                   must be documented and maintained;
               Principle 7 (Safety) — high-risk AI systems must complete a
                   formal safety assessment before deployment; safety
                   assessments must document identified risks and mitigations.

    Layer 3  — MHLW AI Guidelines for Medical Institutions:
               Japan's Ministry of Health, Labour and Welfare (MHLW)
               published AI Guidelines for Medical Institutions to govern
               clinical decision support AI and diagnostic AI systems
               deployed in Japanese healthcare settings. Key obligations
               include:
               Physician Oversight — clinical AI systems providing diagnostic
                   support or treatment recommendations must have a licensed
                   physician in the decision loop; fully autonomous clinical
                   AI decisions without physician review are prohibited;
               Audit Trail — medical AI systems that access patient data must
                   maintain a complete audit trail of AI interactions to
                   support clinical governance and post-market surveillance;
               Explainability — clinical AI must be able to provide an
                   explanation of each AI-generated recommendation to the
                   attending medical staff, supporting informed clinical
                   judgment and patient safety.

    Layer 4  — Cabinet Office Social Principles of Human-Centric AI (2019):
               Japan's Cabinet Office published the Social Principles of
               Human-Centric AI in March 2019, establishing the foundational
               ethical framework for AI governance across both public and
               private sectors. The principles are especially consequential
               for public sector AI systems:
               Principle 3 (Human Involvement) — AI systems deployed by
                   government agencies or ministerial bodies that make or
                   materially influence decisions affecting citizens must
                   maintain a meaningful human oversight pathway; citizens
                   must retain the ability to request human review;
               Principle 5 (Security / Safety / Transparency) — public sector
                   AI systems must maintain audit trails to support
                   transparency, accountability, and post-incident review by
                   the supervising ministry;
               Principle 7 (Fairness / Non-Discrimination) — public sector AI
                   that affects citizens' rights, benefits, or opportunities
                   must be tested for fairness and bias to prevent
                   discriminatory outcomes in public administration.

No external dependencies required.

Run:
    python examples/21_japan_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class JapanAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under Japan's METI AI Governance
    Guidelines v1.1 (2022).

    HIGH   — Significant potential to affect individual rights, safety, or
             welfare; human oversight required; fairness testing, safety
             assessment, and accountability framework mandatory.
    MEDIUM — Meaningful but bounded risk; fairness testing required; data
             minimisation enforced; lighter oversight obligations.
    LOW    — Limited potential for harm; minimal oversight requirements;
             some checks do not apply.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class JapanAIDecision(str, Enum):
    """Final governance decision for a Japan AI system evaluation."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    REDACTED = "REDACTED"


class JapanSector(str, Enum):
    """
    Deployment sector for the AI system.

    HEALTHCARE          — Japanese healthcare institution; MHLW AI Guidelines
                          apply in Layer 3.
    FINANCIAL_SERVICES  — Financial institution; heightened accountability
                          obligations apply under METI guidelines.
    PUBLIC_SECTOR       — Government agency or ministerial body; Cabinet
                          Office Human-Centric AI Principles apply with
                          enhanced scrutiny in Layer 4.
    MANUFACTURING       — Industrial / manufacturing organisation; METI
                          operational safety considerations apply.
    GENERAL             — General private-sector organisation; baseline
                          APPI and METI guidelines apply.
    """

    HEALTHCARE = "HEALTHCARE"
    FINANCIAL_SERVICES = "FINANCIAL_SERVICES"
    PUBLIC_SECTOR = "PUBLIC_SECTOR"
    MANUFACTURING = "MANUFACTURING"
    GENERAL = "GENERAL"


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JapanAIContext:
    """
    Governance review context for a Japan AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    sector : JapanSector
        The sector in which the AI system is deployed. A value of
        ``JapanSector.HEALTHCARE`` triggers MHLW checks in Layer 3; a value
        of ``JapanSector.PUBLIC_SECTOR`` triggers enhanced Cabinet Office
        checks in Layer 4.
    ai_risk_level : JapanAIRiskLevel
        Risk level under METI AI Governance Guidelines v1.1.

    — APPI consent and personal information —

    is_automated_decision : bool
        True if the AI system makes a material decision about an individual
        with no human review in the decision loop (METI Principle 2).
    involves_personal_information : bool
        True if the AI system collects, uses, or discloses personal
        information (kojin joho) as defined by APPI Article 2(1).
    involves_sensitive_personal_info : bool
        True if the AI system processes special-care-required personal
        information (yo-hairyo kojin joho) as defined by APPI Article 2(3):
        racial origin, creed, social status, medical history, criminal
        record, having suffered a crime, or disability status.
    has_appi_consent : bool
        True if valid opt-in consent has been obtained from the individual
        for the specific processing purpose (required for sensitive PI under
        APPI Article 20-2; also satisfies the third-party provision basis
        under Article 27 and cross-border transfer under Article 28).
    has_third_party_provision_basis : bool
        True if a lawful basis for third-party provision of personal
        information exists under APPI Article 27 (consent, opt-out
        procedure, entrustment, shared use, legal requirement, etc.).
    is_cross_border_transfer : bool
        True if personal information is transferred to a recipient outside
        Japan, triggering APPI Article 28 cross-border transfer controls.
    transfer_to_adequate_country : bool
        True if the destination country has received a PPC adequacy finding
        (e.g. EU, UK) or equivalent contractual safeguards are in place
        (APPI Article 28 requirements).

    — Medical AI (MHLW guidelines) —

    is_medical_ai : bool
        True if the AI system provides clinical decision support, diagnostic
        recommendations, or other medical functions governed by MHLW AI
        Guidelines for Medical Institutions.
    has_physician_oversight : bool
        True if a licensed physician is in the decision loop for all
        clinical AI recommendations — mandatory under MHLW guidelines.

    — Public sector (Cabinet Office principles) —

    is_public_sector_ai : bool
        True if the AI system is deployed by a Japanese government agency,
        ministerial body, or local government authority.
    human_oversight_available : bool
        True if a human reviewer can review and override any AI decision
        (METI Principle 2; Cabinet Office Principle 3).
    explainability_available : bool
        True if the system can provide an explanation of any individual
        automated AI decision on request (METI Principle 5; MHLW guidelines).
    fairness_testing_done : bool
        True if bias and fairness testing has been conducted and documented
        (METI Principle 3; Cabinet Office Principle 7).
    accountability_chain_defined : bool
        True if a clear accountability assignment has been documented for
        AI outcomes (METI Principle 6).
    has_ai_safety_assessment : bool
        True if a formal safety / risk assessment has been completed before
        deployment (METI Principle 7).
    audit_trail_enabled : bool
        True if a comprehensive audit trail of AI decisions is maintained.
    data_minimization_applied : bool
        True if only personal information necessary for the specified purpose
        is collected and processed (APPI Article 19 + METI principle).
    """

    user_id: str
    sector: JapanSector
    ai_risk_level: JapanAIRiskLevel

    # APPI — personal information handling
    is_automated_decision: bool
    involves_personal_information: bool
    involves_sensitive_personal_info: bool
    has_appi_consent: bool
    has_third_party_provision_basis: bool
    is_cross_border_transfer: bool
    transfer_to_adequate_country: bool

    # MHLW — medical AI
    is_medical_ai: bool
    has_physician_oversight: bool

    # Cabinet Office / public sector
    is_public_sector_ai: bool
    human_oversight_available: bool

    # METI AI governance
    explainability_available: bool
    fairness_testing_done: bool
    accountability_chain_defined: bool
    has_ai_safety_assessment: bool

    # Operational controls
    audit_trail_enabled: bool
    data_minimization_applied: bool


@dataclass(frozen=True)
class JapanAIDocument:
    """
    Document metadata submitted to the Japan AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    contains_personal_information : bool
        True if the document contains personal information of individuals
        as defined by APPI Article 2(1).
    contains_sensitive_personal_info : bool
        True if the document contains special-care-required personal
        information under APPI Article 2(3) (medical, criminal, disability,
        racial, social status, creed).
    data_classification : str
        Sensitivity classification: "PUBLIC", "INTERNAL", or "CONFIDENTIAL".
    is_medical_data : bool
        True if the document contains clinical or patient health records.
    is_government_data : bool
        True if the document contains official government or ministerial data.
    requires_human_decision : bool
        True if the document or its originating use case explicitly requires
        a human decision before any AI-driven action is taken.
    """

    document_id: str
    contains_personal_information: bool
    contains_sensitive_personal_info: bool
    data_classification: str
    is_medical_data: bool
    is_government_data: bool
    requires_human_decision: bool


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class JapanAIFilterResult:
    """Result of a single Japan AI governance filter evaluation."""

    filter_name: str
    decision: JapanAIDecision = JapanAIDecision.APPROVED
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = False

    @property
    def is_denied(self) -> bool:
        """True if this filter produced a DENIED decision."""
        return self.decision == JapanAIDecision.DENIED


# ---------------------------------------------------------------------------
# Layer 1 — APPI Data Protection
# ---------------------------------------------------------------------------


class APPIDataProtectionFilter:
    """
    Layer 1: APPI (Act on the Protection of Personal Information) — Japan,
    2022 amendments (effective April 1, 2022).

    The APPI is Japan's primary data protection statute administered by the
    Personal Information Protection Commission (PPC). The 2022 amendments
    substantially strengthened obligations relevant to AI systems. This
    filter evaluates the five principal APPI controls most material for AI:

    (a) Sensitive PI opt-in consent (Article 20-2) — special-care-required
        personal information (race, creed, social status, medical history,
        criminal record, disability) requires explicit opt-in consent before
        collection or use; no exception exists for AI processing;
    (b) Third-party provision basis (Article 27) — personal information must
        not be provided to a third party without consent or a recognised
        lawful basis (opt-out procedure, entrustment, shared use, legal
        requirement);
    (c) Cross-border transfer adequacy (Article 28) — transfer of personal
        information outside Japan requires a PPC adequacy finding for the
        destination country or contractual safeguards of equivalent
        protection;
    (d) Document-level sensitive PI mismatch — if a document contains
        sensitive PI but the processing context does not declare sensitive PI
        handling, the document must be redacted before AI processing;
    (e) Data minimisation (Article 19 + METI) — personal information must
        not be processed beyond the scope necessary for the specified purpose;
        non-minimised medium- and high-risk systems are flagged for review.

    References
    ----------
    Act on the Protection of Personal Information (Act No. 57 of 2003),
        as amended by Act No. 44 of 2020 (effective April 1, 2022)
    PPC — Guidelines on the Act on the Protection of Personal Information
        (General Rules) (2021, updated 2022)
    PPC — Guidance on Cross-Border Transfer (Article 28 / Third Schedule)
    """

    FILTER_NAME = "APPI_DATA_PROTECTION"

    def evaluate(
        self, context: JapanAIContext, document: JapanAIDocument
    ) -> JapanAIFilterResult:
        # Sensitive personal information without opt-in consent
        if context.involves_sensitive_personal_info and not context.has_appi_consent:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.DENIED,
                reason=(
                    "APPI Article 20-2: Opt-in consent required for sensitive "
                    "personal information (special care-required personal information)"
                ),
                regulation_citation=(
                    "Act on the Protection of Personal Information (2022 amendments), "
                    "Article 20-2 — Special Care-Required Personal Information: "
                    "racial origin, creed, social status, medical history, criminal "
                    "record, disability status"
                ),
                requires_logging=True,
            )

        # Personal information provided to third party without lawful basis
        if (
            context.involves_personal_information
            and not context.has_third_party_provision_basis
            and not context.has_appi_consent
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.DENIED,
                reason=(
                    "APPI Article 27: Third-party provision of personal information "
                    "requires consent or other lawful basis"
                ),
                regulation_citation=(
                    "Act on the Protection of Personal Information (2022 amendments), "
                    "Article 27 — Provision to Third Parties: consent, opt-out "
                    "procedure, entrustment, shared use, or legal requirement required"
                ),
                requires_logging=True,
            )

        # Cross-border transfer to a non-adequate country without safeguards
        if context.is_cross_border_transfer and not context.transfer_to_adequate_country:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.DENIED,
                reason=(
                    "APPI Article 28: Cross-border transfer requires adequacy "
                    "decision or equivalent protection measures"
                ),
                regulation_citation=(
                    "Act on the Protection of Personal Information (2022 amendments), "
                    "Article 28 — Provision to Third Parties in Foreign Countries: "
                    "PPC adequacy finding or equivalent contractual safeguards required"
                ),
                requires_logging=True,
            )

        # Document contains sensitive PI but context does not declare it
        if (
            document.contains_sensitive_personal_info
            and not context.involves_sensitive_personal_info
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REDACTED,
                reason=(
                    "APPI: Document contains sensitive personal information — "
                    "context must declare sensitive PI handling"
                ),
                regulation_citation=(
                    "Act on the Protection of Personal Information (2022 amendments), "
                    "Article 20-2 — Special Care-Required Personal Information: "
                    "document must be redacted until context declares sensitive PI "
                    "handling and consent basis"
                ),
                requires_logging=True,
            )

        # Data minimisation not applied for non-low-risk AI
        if (
            not context.data_minimization_applied
            and context.ai_risk_level != JapanAIRiskLevel.LOW
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "APPI Article 19 + METI Principle: Data minimization required "
                    "— collect only necessary personal information"
                ),
                regulation_citation=(
                    "Act on the Protection of Personal Information (2022 amendments), "
                    "Article 19 — Accuracy; METI AI Governance Guidelines v1.1 (2022) "
                    "— data minimisation principle for medium/high-risk AI"
                ),
                requires_logging=True,
            )

        return JapanAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=JapanAIDecision.APPROVED,
            reason=(
                "Compliant with APPI (Act on Protection of Personal Information) "
                "2022 amendments"
            ),
            regulation_citation=(
                "Act on the Protection of Personal Information (2022 amendments) "
                "— all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 2 — METI AI Governance Guidelines
# ---------------------------------------------------------------------------


class METIAIPrinciplesFilter:
    """
    Layer 2: METI AI Governance Guidelines v1.1 — Ministry of Economy, Trade
    and Industry (July 2022).

    METI published AI Governance Guidelines Version 1.1 in July 2022,
    providing a risk-based, principle-centred governance framework for
    businesses developing and deploying AI in Japan. The guidelines articulate
    seven core AI governance principles. This filter evaluates the five
    principal controls most material for AI deployment decisions:

    (a) Human oversight (Principle 2) — high-impact automated decisions must
        retain a meaningful human oversight pathway; fully automated high-risk
        decisions without human oversight are non-compliant;
    (b) Explainability (Principle 5) — individuals subject to automated AI
        decisions must be able to obtain a meaningful explanation of the
        decision; black-box automated decisions are flagged for human review;
    (c) Fairness testing (Principle 3) — medium- and high-risk AI systems
        must be tested for bias and discriminatory outcomes and results
        documented; untested systems are flagged;
    (d) Accountability (Principle 6) — high-risk AI deployments must define
        a clear accountability chain assigning responsibility for AI outcomes;
        undocumented accountability frameworks are flagged;
    (e) Safety assessment (Principle 7) — high-risk AI systems must complete
        a formal safety / risk assessment before deployment.

    References
    ----------
    METI — AI Governance Guidelines Version 1.0 (2021)
    METI — AI Governance Guidelines Version 1.1 (July 2022)
    METI — Governance Innovation: Redesigning Law and Architecture (2021)
    """

    FILTER_NAME = "METI_AI_GOVERNANCE_GUIDELINES"

    def evaluate(
        self, context: JapanAIContext, document: JapanAIDocument
    ) -> JapanAIFilterResult:
        # High-risk automated decision without human oversight
        if (
            context.is_automated_decision
            and context.ai_risk_level == JapanAIRiskLevel.HIGH
            and not context.human_oversight_available
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.DENIED,
                reason=(
                    "METI AI Governance Guidelines v1.1 Principle 2 (Human "
                    "Oversight): High-impact automated decisions require human "
                    "oversight"
                ),
                regulation_citation=(
                    "METI AI Governance Guidelines v1.1 (2022), Principle 2 — "
                    "Human Involvement: degree of human oversight must be "
                    "commensurate with the risk level of the AI decision"
                ),
                requires_logging=True,
            )

        # Automated decision without explainability
        if context.is_automated_decision and not context.explainability_available:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "METI AI Governance Guidelines Principle 5 (Transparency): "
                    "Explainability required for individual AI decisions"
                ),
                regulation_citation=(
                    "METI AI Governance Guidelines v1.1 (2022), Principle 5 — "
                    "Transparency / Explainability: individuals affected by automated "
                    "AI decisions must be able to obtain a meaningful explanation"
                ),
                requires_logging=True,
            )

        # Fairness testing not done for medium/high-risk AI
        if (
            not context.fairness_testing_done
            and context.ai_risk_level in {JapanAIRiskLevel.HIGH, JapanAIRiskLevel.MEDIUM}
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "METI AI Governance Guidelines Principle 3 (Fairness): "
                    "Bias/fairness testing required for medium/high-risk AI"
                ),
                regulation_citation=(
                    "METI AI Governance Guidelines v1.1 (2022), Principle 3 — "
                    "Fairness / Non-Discrimination: AI systems must be tested for "
                    "biased or discriminatory outcomes; results must be documented"
                ),
                requires_logging=True,
            )

        # Accountability chain not defined for high-risk AI
        if (
            not context.accountability_chain_defined
            and context.ai_risk_level == JapanAIRiskLevel.HIGH
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "METI AI Governance Guidelines Principle 6 (Accountability): "
                    "Clear accountability assignment required for high-risk AI"
                ),
                regulation_citation=(
                    "METI AI Governance Guidelines v1.1 (2022), Principle 6 — "
                    "Accountability: organisations must define and document a clear "
                    "accountability chain for AI outcomes before deployment"
                ),
                requires_logging=True,
            )

        # Safety assessment not done for high-risk AI
        if (
            not context.has_ai_safety_assessment
            and context.ai_risk_level == JapanAIRiskLevel.HIGH
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "METI AI Governance Guidelines Principle 7 (Safety): Safety "
                    "assessment required before deployment of high-risk AI"
                ),
                regulation_citation=(
                    "METI AI Governance Guidelines v1.1 (2022), Principle 7 — "
                    "Safety: formal safety / risk assessment must be completed "
                    "before deploying high-risk AI systems"
                ),
                requires_logging=True,
            )

        return JapanAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=JapanAIDecision.APPROVED,
            reason="Compliant with METI AI Governance Guidelines v1.1 (2022)",
            regulation_citation=(
                "METI AI Governance Guidelines v1.1 (2022) — all applicable "
                "principles satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 3 — MHLW Medical AI
# ---------------------------------------------------------------------------


class MHLWMedicalAIFilter:
    """
    Layer 3: MHLW AI Guidelines for Medical Institutions — Ministry of Health,
    Labour and Welfare (Japan).

    The MHLW published AI Guidelines for Medical Institutions to govern
    clinical decision support and diagnostic AI deployed in Japanese healthcare
    settings. Non-medical AI systems are outside the scope of this filter and
    receive an immediate approval with a note. For medical AI systems, three
    principal controls apply:

    (a) Physician oversight — clinical AI systems must have a licensed
        physician in the decision loop; fully autonomous clinical AI decisions
        without physician review are prohibited under the Medical Practitioners
        Act and MHLW guidelines;
    (b) Audit trail — medical AI systems accessing patient data must maintain
        a complete audit trail to support clinical governance, post-market
        surveillance, and incident investigation;
    (c) Explainability — clinical AI must be able to provide an explanation
        of each AI-generated recommendation to attending medical staff to
        support informed clinical judgment and patient safety.

    References
    ----------
    MHLW — AI Guidelines for Medical Institutions (2021)
    MHLW — Act on Securing Quality, Efficacy and Safety of Products Including
            Pharmaceuticals and Medical Devices (Pharmaceutical and Medical
            Device Act / PMD Act) — AI-related guidance
    MHLW — Ethical Guidelines for AI Research and Development in Medicine
    """

    FILTER_NAME = "MHLW_MEDICAL_AI"

    def evaluate(
        self, context: JapanAIContext, document: JapanAIDocument
    ) -> JapanAIFilterResult:
        # Not a medical AI system — MHLW guidelines not applicable
        if not context.is_medical_ai:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.APPROVED,
                reason=(
                    "MHLW Medical AI Guidelines not applicable — not a medical AI "
                    "system"
                ),
                regulation_citation=(
                    "MHLW AI Guidelines for Medical Institutions — scope limited to "
                    "clinical decision support and diagnostic AI systems"
                ),
            )

        # Medical AI without licensed physician oversight
        if context.is_medical_ai and not context.has_physician_oversight:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.DENIED,
                reason=(
                    "MHLW AI Guidelines for Medical Institutions: Licensed physician "
                    "oversight required for clinical AI decision support"
                ),
                regulation_citation=(
                    "MHLW AI Guidelines for Medical Institutions — Physician "
                    "Oversight Requirement: clinical AI must have a licensed "
                    "physician in the decision loop; autonomous clinical AI "
                    "decisions are prohibited"
                ),
                requires_logging=True,
            )

        # Medical AI accessing patient data without audit trail
        if (
            context.is_medical_ai
            and document.is_medical_data
            and not context.audit_trail_enabled
        ):
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "MHLW: Audit trail required for medical AI accessing patient data"
                ),
                regulation_citation=(
                    "MHLW AI Guidelines for Medical Institutions — Audit Trail: "
                    "medical AI systems must maintain a complete record of AI "
                    "interactions with patient data for clinical governance"
                ),
                requires_logging=True,
            )

        # Medical AI without explainability for medical staff
        if context.is_medical_ai and not context.explainability_available:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "MHLW AI Guidelines: Clinical AI must provide explanations "
                    "for medical staff"
                ),
                regulation_citation=(
                    "MHLW AI Guidelines for Medical Institutions — Explainability: "
                    "clinical AI must explain each AI-generated recommendation to "
                    "attending medical staff to support informed clinical judgment"
                ),
                requires_logging=True,
            )

        return JapanAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=JapanAIDecision.APPROVED,
            reason="Compliant with MHLW AI Guidelines for Medical Institutions",
            regulation_citation=(
                "MHLW AI Guidelines for Medical Institutions — all applicable "
                "controls satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cabinet Office Social Principles of Human-Centric AI
# ---------------------------------------------------------------------------


class CabinetOfficeAIStrategyFilter:
    """
    Layer 4: Cabinet Office Social Principles of Human-Centric AI (March 2019).

    Japan's Cabinet Office published the Social Principles of Human-Centric
    AI in March 2019 as the foundational ethical framework for AI governance
    across both public and private sectors. The principles are especially
    consequential for public sector AI systems. Non-public-sector low-risk
    systems receive an immediate approval with a note. For public sector AI
    systems and non-public-sector non-low-risk systems, three principal
    controls apply:

    (a) Human involvement (Principle 3) — public sector AI systems that
        make or materially influence decisions affecting citizens must
        maintain a meaningful human oversight pathway; citizens must be
        able to request human review of AI-influenced decisions;
    (b) Security / transparency (Principle 5) — public sector AI systems
        must maintain audit trails to support transparency, accountability,
        and post-incident review by the supervising ministry;
    (c) Fairness / non-discrimination (Principle 7) — public sector AI
        that affects citizens' rights, benefits, or opportunities must be
        tested for bias to prevent discriminatory outcomes in public
        administration.

    References
    ----------
    Cabinet Office, Government of Japan — Social Principles of Human-Centric
        AI (March 2019)
    Cabinet Office — Integrated Innovation Strategy 2023
    Cabinet Office — AI Strategy 2022 — Human-Centric AI goals
    """

    FILTER_NAME = "CABINET_OFFICE_AI_STRATEGY"

    def evaluate(
        self, context: JapanAIContext, document: JapanAIDocument
    ) -> JapanAIFilterResult:
        # Not public sector and low risk — minimal Cabinet Office obligations
        if not context.is_public_sector_ai and context.ai_risk_level == JapanAIRiskLevel.LOW:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.APPROVED,
                reason=(
                    "Cabinet Office Social Principles of Human-Centric AI (2019) "
                    "— not a public sector system, low risk"
                ),
                regulation_citation=(
                    "Cabinet Office Social Principles of Human-Centric AI (2019) "
                    "— enhanced public sector controls not applicable"
                ),
            )

        # Public sector AI without human oversight
        if context.is_public_sector_ai and not context.human_oversight_available:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.DENIED,
                reason=(
                    "Cabinet Office Human-Centric AI Principle 3: Public sector AI "
                    "requires human oversight for decisions affecting citizens"
                ),
                regulation_citation=(
                    "Cabinet Office Social Principles of Human-Centric AI (2019), "
                    "Principle 3 — Human Involvement: public sector AI systems must "
                    "maintain a human oversight pathway; citizens must retain the "
                    "ability to request human review"
                ),
                requires_logging=True,
            )

        # Public sector AI without audit trail
        if context.is_public_sector_ai and not context.audit_trail_enabled:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "Cabinet Office Human-Centric AI Principle 5 "
                    "(Security/Transparency): Audit trail required for public sector AI"
                ),
                regulation_citation=(
                    "Cabinet Office Social Principles of Human-Centric AI (2019), "
                    "Principle 5 — Security / Safety / Transparency: public sector "
                    "AI must maintain audit trails to support transparency and "
                    "post-incident review by the supervising ministry"
                ),
                requires_logging=True,
            )

        # Public sector AI without fairness testing
        if not context.fairness_testing_done and context.is_public_sector_ai:
            return JapanAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=JapanAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "Cabinet Office Human-Centric AI Principle 7 "
                    "(Fairness/Non-discrimination): Fairness testing required for "
                    "public sector AI affecting citizens"
                ),
                regulation_citation=(
                    "Cabinet Office Social Principles of Human-Centric AI (2019), "
                    "Principle 7 — Fairness / Non-Discrimination: public sector AI "
                    "affecting citizens' rights or benefits must be tested for bias "
                    "to prevent discriminatory outcomes in public administration"
                ),
                requires_logging=True,
            )

        return JapanAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=JapanAIDecision.APPROVED,
            reason=(
                "Compliant with Cabinet Office Social Principles of Human-Centric "
                "AI (2019)"
            ),
            regulation_citation=(
                "Cabinet Office Social Principles of Human-Centric AI (2019) "
                "— all applicable principles satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class JapanAIGovernanceOrchestrator:
    """
    Four-layer Japan AI governance orchestrator.

    Evaluation order:
        APPIDataProtectionFilter  →  METIAIPrinciplesFilter  →
        MHLWMedicalAIFilter       →  CabinetOfficeAIStrategyFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``JapanAIFilterResult`` objects
    and passed to ``JapanAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            APPIDataProtectionFilter(),
            METIAIPrinciplesFilter(),
            MHLWMedicalAIFilter(),
            CabinetOfficeAIStrategyFilter(),
        ]

    def evaluate(
        self, context: JapanAIContext, document: JapanAIDocument
    ) -> List[JapanAIFilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : JapanAIContext
            The AI system processing context to evaluate.
        document : JapanAIDocument
            The document being processed by the AI system.

        Returns
        -------
        list[JapanAIFilterResult]
            One result per filter, in evaluation order.
        """
        return [f.evaluate(context, document) for f in self._filters]


# ---------------------------------------------------------------------------
# Aggregated governance report
# ---------------------------------------------------------------------------


@dataclass
class JapanAIGovernanceReport:
    """
    Aggregated Japan AI governance report across all four filters.

    Decision aggregation:
    - Any DENIED result   → overall_decision is DENIED
    - No DENIED + any REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_REVIEW
    - All APPROVED        → APPROVED

    Attributes
    ----------
    context : JapanAIContext
        The AI system context that was evaluated.
    document : JapanAIDocument
        The document that was evaluated.
    filter_results : list[JapanAIFilterResult]
        Per-filter results in evaluation order.
    """

    context: JapanAIContext
    document: JapanAIDocument
    filter_results: List[JapanAIFilterResult]

    @property
    def overall_decision(self) -> JapanAIDecision:
        """
        Aggregate decision across all filters.

        Returns DENIED if any filter denied; REQUIRES_HUMAN_REVIEW if any
        filter requires human review (but none denied); APPROVED otherwise.
        """
        if any(r.is_denied for r in self.filter_results):
            return JapanAIDecision.DENIED
        if any(
            r.decision == JapanAIDecision.REQUIRES_HUMAN_REVIEW
            for r in self.filter_results
        ):
            return JapanAIDecision.REQUIRES_HUMAN_REVIEW
        return JapanAIDecision.APPROVED

    @property
    def is_compliant(self) -> bool:
        """
        True if no filter produced a DENIED decision.

        Note: REQUIRES_HUMAN_REVIEW is not a denial — the request can still
        proceed after human review; REDACTED indicates partial compliance
        pending document remediation.
        """
        return not any(r.is_denied for r in self.filter_results)

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary across all four filters.

        Returns a multi-line string listing each filter name, its decision,
        and either the approval reason or the denial/review reason.
        """
        lines: List[str] = [
            f"Japan AI Governance Report — user_id={self.context.user_id}",
            f"Sector: {self.context.sector.value}  |  "
            f"Risk Level: {self.context.ai_risk_level.value}  |  "
            f"Overall Decision: {self.overall_decision.value}",
            "",
        ]
        for result in self.filter_results:
            lines.append(f"  [{result.decision.value}]  {result.filter_name}")
            if result.reason:
                lines.append(f"    Reason: {result.reason}")
            if result.regulation_citation:
                lines.append(f"    Citation: {result.regulation_citation}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_low_risk_general_base() -> tuple[JapanAIContext, JapanAIDocument]:
    """
    Base context: fully compliant LOW risk GENERAL sector system.
    Used as the baseline from which failing scenarios are derived.
    """
    context = JapanAIContext(
        user_id="JP-AI-001",
        sector=JapanSector.GENERAL,
        ai_risk_level=JapanAIRiskLevel.LOW,
        # APPI
        is_automated_decision=False,
        involves_personal_information=False,
        involves_sensitive_personal_info=False,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        # MHLW
        is_medical_ai=False,
        has_physician_oversight=False,
        # Cabinet Office
        is_public_sector_ai=False,
        human_oversight_available=True,
        # METI
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        # Operational
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    document = JapanAIDocument(
        document_id="DOC-001",
        contains_personal_information=False,
        contains_sensitive_personal_info=False,
        data_classification="INTERNAL",
        is_medical_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    return context, document


def _compliant_medical_ai_base() -> tuple[JapanAIContext, JapanAIDocument]:
    """
    Base context: fully compliant HIGH risk HEALTHCARE medical AI system.
    All MHLW requirements satisfied.
    """
    context = JapanAIContext(
        user_id="JP-AI-002",
        sector=JapanSector.HEALTHCARE,
        ai_risk_level=JapanAIRiskLevel.HIGH,
        # APPI
        is_automated_decision=True,
        involves_personal_information=True,
        involves_sensitive_personal_info=True,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        # MHLW
        is_medical_ai=True,
        has_physician_oversight=True,
        # Cabinet Office
        is_public_sector_ai=False,
        human_oversight_available=True,
        # METI
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        # Operational
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    document = JapanAIDocument(
        document_id="DOC-002",
        contains_personal_information=True,
        contains_sensitive_personal_info=True,
        data_classification="CONFIDENTIAL",
        is_medical_data=True,
        is_government_data=False,
        requires_human_decision=False,
    )
    return context, document


def _run_scenario(
    label: str,
    context: JapanAIContext,
    document: JapanAIDocument,
) -> JapanAIGovernanceReport:
    orchestrator = JapanAIGovernanceOrchestrator()
    results = orchestrator.evaluate(context, document)
    report = JapanAIGovernanceReport(
        context=context, document=document, filter_results=results
    )
    print(f"\n{'=' * 70}")
    print(f"SCENARIO: {label}")
    print("=" * 70)
    print(report.compliance_summary)
    return report


def main() -> None:  # noqa: C901
    print("Japan AI Governance Framework — Scenario Demonstrations")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # Scenario 1: Compliant LOW risk GENERAL sector — should APPROVE all layers
    # -----------------------------------------------------------------------
    ctx1, doc1 = _compliant_low_risk_general_base()
    report1 = _run_scenario("Compliant low-risk general sector AI", ctx1, doc1)
    assert report1.overall_decision == JapanAIDecision.APPROVED, (
        f"Scenario 1 expected APPROVED, got {report1.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 2: Sensitive PI without consent → DENIED (APPI Layer 1)
    # -----------------------------------------------------------------------
    ctx2 = JapanAIContext(
        user_id="JP-AI-003",
        sector=JapanSector.HEALTHCARE,
        ai_risk_level=JapanAIRiskLevel.HIGH,
        is_automated_decision=True,
        involves_personal_information=True,
        involves_sensitive_personal_info=True,
        has_appi_consent=False,             # <-- triggers DENIED
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        is_medical_ai=True,
        has_physician_oversight=True,
        is_public_sector_ai=False,
        human_oversight_available=True,
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    doc2 = JapanAIDocument(
        document_id="DOC-003",
        contains_personal_information=True,
        contains_sensitive_personal_info=True,
        data_classification="CONFIDENTIAL",
        is_medical_data=True,
        is_government_data=False,
        requires_human_decision=False,
    )
    report2 = _run_scenario(
        "Sensitive PI without APPI consent → DENIED", ctx2, doc2
    )
    assert report2.overall_decision == JapanAIDecision.DENIED, (
        f"Scenario 2 expected DENIED, got {report2.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 3: Medical AI without physician oversight → DENIED (MHLW Layer 3)
    # -----------------------------------------------------------------------
    ctx3 = JapanAIContext(
        user_id="JP-AI-004",
        sector=JapanSector.HEALTHCARE,
        ai_risk_level=JapanAIRiskLevel.HIGH,
        is_automated_decision=True,
        involves_personal_information=True,
        involves_sensitive_personal_info=True,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        is_medical_ai=True,
        has_physician_oversight=False,      # <-- triggers DENIED
        is_public_sector_ai=False,
        human_oversight_available=True,
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    doc3 = JapanAIDocument(
        document_id="DOC-004",
        contains_personal_information=True,
        contains_sensitive_personal_info=True,
        data_classification="CONFIDENTIAL",
        is_medical_data=True,
        is_government_data=False,
        requires_human_decision=False,
    )
    report3 = _run_scenario(
        "Medical AI without physician oversight → DENIED", ctx3, doc3
    )
    assert report3.overall_decision == JapanAIDecision.DENIED, (
        f"Scenario 3 expected DENIED, got {report3.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 4: High-risk automated decision, no human oversight → DENIED (METI)
    # -----------------------------------------------------------------------
    ctx4 = JapanAIContext(
        user_id="JP-AI-005",
        sector=JapanSector.FINANCIAL_SERVICES,
        ai_risk_level=JapanAIRiskLevel.HIGH,
        is_automated_decision=True,
        involves_personal_information=True,
        involves_sensitive_personal_info=False,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        is_medical_ai=False,
        has_physician_oversight=False,
        is_public_sector_ai=False,
        human_oversight_available=False,    # <-- triggers DENIED
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    doc4 = JapanAIDocument(
        document_id="DOC-005",
        contains_personal_information=True,
        contains_sensitive_personal_info=False,
        data_classification="CONFIDENTIAL",
        is_medical_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    report4 = _run_scenario(
        "High-risk automated decision, no human oversight (METI) → DENIED", ctx4, doc4
    )
    assert report4.overall_decision == JapanAIDecision.DENIED, (
        f"Scenario 4 expected DENIED, got {report4.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 5: Public sector AI without human oversight → DENIED (Cabinet Office)
    # -----------------------------------------------------------------------
    ctx5 = JapanAIContext(
        user_id="JP-AI-006",
        sector=JapanSector.PUBLIC_SECTOR,
        ai_risk_level=JapanAIRiskLevel.MEDIUM,
        is_automated_decision=True,
        involves_personal_information=True,
        involves_sensitive_personal_info=False,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        is_medical_ai=False,
        has_physician_oversight=False,
        is_public_sector_ai=True,
        human_oversight_available=False,    # <-- triggers DENIED
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    doc5 = JapanAIDocument(
        document_id="DOC-006",
        contains_personal_information=True,
        contains_sensitive_personal_info=False,
        data_classification="INTERNAL",
        is_medical_data=False,
        is_government_data=True,
        requires_human_decision=False,
    )
    report5 = _run_scenario(
        "Public sector AI without human oversight (Cabinet Office) → DENIED", ctx5, doc5
    )
    assert report5.overall_decision == JapanAIDecision.DENIED, (
        f"Scenario 5 expected DENIED, got {report5.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 6: Compliant HIGH risk HEALTHCARE medical AI → APPROVED
    # -----------------------------------------------------------------------
    ctx6, doc6 = _compliant_medical_ai_base()
    report6 = _run_scenario("Compliant high-risk healthcare medical AI", ctx6, doc6)
    assert report6.overall_decision == JapanAIDecision.APPROVED, (
        f"Scenario 6 expected APPROVED, got {report6.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 7: Medium-risk AI without fairness testing → REQUIRES_HUMAN_REVIEW
    # -----------------------------------------------------------------------
    ctx7 = JapanAIContext(
        user_id="JP-AI-008",
        sector=JapanSector.GENERAL,
        ai_risk_level=JapanAIRiskLevel.MEDIUM,
        is_automated_decision=False,
        involves_personal_information=True,
        involves_sensitive_personal_info=False,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        is_medical_ai=False,
        has_physician_oversight=False,
        is_public_sector_ai=False,
        human_oversight_available=True,
        explainability_available=True,
        fairness_testing_done=False,        # <-- triggers REQUIRES_HUMAN_REVIEW
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    doc7 = JapanAIDocument(
        document_id="DOC-008",
        contains_personal_information=True,
        contains_sensitive_personal_info=False,
        data_classification="INTERNAL",
        is_medical_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    report7 = _run_scenario(
        "Medium-risk AI without fairness testing → REQUIRES_HUMAN_REVIEW", ctx7, doc7
    )
    assert report7.overall_decision == JapanAIDecision.REQUIRES_HUMAN_REVIEW, (
        f"Scenario 7 expected REQUIRES_HUMAN_REVIEW, got {report7.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 8: Cross-border transfer to non-adequate country → DENIED (APPI)
    # -----------------------------------------------------------------------
    ctx8 = JapanAIContext(
        user_id="JP-AI-009",
        sector=JapanSector.GENERAL,
        ai_risk_level=JapanAIRiskLevel.MEDIUM,
        is_automated_decision=False,
        involves_personal_information=True,
        involves_sensitive_personal_info=False,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=True,
        transfer_to_adequate_country=False,  # <-- triggers DENIED
        is_medical_ai=False,
        has_physician_oversight=False,
        is_public_sector_ai=False,
        human_oversight_available=True,
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    doc8 = JapanAIDocument(
        document_id="DOC-009",
        contains_personal_information=True,
        contains_sensitive_personal_info=False,
        data_classification="CONFIDENTIAL",
        is_medical_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    report8 = _run_scenario(
        "Cross-border transfer to non-adequate country → DENIED (APPI)", ctx8, doc8
    )
    assert report8.overall_decision == JapanAIDecision.DENIED, (
        f"Scenario 8 expected DENIED, got {report8.overall_decision}"
    )

    print(f"\n{'=' * 70}")
    print("All scenarios completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
