"""
25_middle_east_ai_governance.py — Four-layer AI governance framework for AI
systems subject to Middle East law, covering the overlapping national and
sector-level obligations that apply to AI-driven data processing in the
Gulf Cooperation Council (GCC) region.

Demonstrates a multi-layer governance orchestrator where four regulatory
frameworks each impose independent requirements on AI systems deployed
across GCC jurisdictions:

    Layer 1  — UAE PDPL + UAE AI Ethics Principles 2019:
               UAE Federal Decree-Law No. 45/2021 on the Protection of
               Personal Data (UAE PDPL) came into force November 2021.
               Supplemented by the UAE National AI Strategy 2031 and the
               UAE AI Ethics Principles (2019) adopted by the UAE Cabinet:

               Article 7  — Lawful Basis: personal data may be processed
                   only with consent or another recognised lawful basis
                   (legal obligation, vital interest, public task, contract);
               Article 10 — Special Categories: explicit consent required
                   before processing biometric or other sensitive data;
               Article 16 — Data Protection Officer: controllers engaged in
                   high-risk processing must appoint a DPO;
               UAE AI Ethics Principle 3 — Transparency: AI systems must be
                   transparent about their nature and decision-making logic.

    Layer 2  — Saudi PDPL 2021 + NDMO + SAMA/SFDA:
               Saudi Arabia's Personal Data Protection Law (PDPL), promulgated
               by Royal Decree M/19 (September 2021, effective September 2022),
               establishes the national data protection framework.  Supplemented
               by NDMO data governance requirements and sector-specific
               approvals from SAMA (financial AI) and SFDA (medical AI):

               Article 4  — Consent: explicit consent required for personal
                   data collection and processing unless a recognised lawful
                   basis applies;
               NDMO Data Governance Framework — data must be classified
                   (Public/Sensitive/Confidential) before AI processing;
               SAMA Open Banking Framework — financial AI systems require
                   SAMA approval before deployment;
               Saudi SFDA AI/ML-based SaMD Guidance — medical AI systems
                   require SFDA approval.

    Layer 3  — Qatar PDPA Law No. 13/2016 + Qatar National AI Strategy:
               Qatar's Personal Data Privacy Protection Law (Law No. 13 of
               2016) and the Qatar National AI Strategy 2030 govern AI
               deployments in Qatar:

               Article 8  — Consent: processing of personal data requires
                   the data subject's consent unless a recognised basis applies;
               Article 9  — Profiling: profiling of individuals requires
                   explicit consent;
               Article 12 — Cross-Border Transfer: transfers outside Qatar
                   require MOTC authorisation or consent;
               Qatar National AI Strategy 2030 — automated decisions must
                   be explainable to affected individuals.

    Layer 4  — GCC Cross-Border Data Transfer Framework:
               Cross-border data flows within the GCC are governed by a
               combination of national PDPL/PDPA provisions and the GCC
               framework that treats member states (AE, SA, QA, BH, KW, OM)
               as adequate jurisdictions for mutual data transfers.  Transfers
               outside the GCC require jurisdiction-specific authorisation
               or consent.

No external dependencies required.

Run:
    python examples/25_middle_east_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class MiddleEastJurisdiction(str, Enum):
    """
    GCC member-state jurisdiction where the AI system is deployed.

    UAE          — United Arab Emirates (UAE PDPL Federal Decree-Law 45/2021)
    SAUDI_ARABIA — Kingdom of Saudi Arabia (Saudi PDPL Royal Decree M/19)
    QATAR        — State of Qatar (Qatar PDPA Law No. 13/2016)
    BAHRAIN      — Kingdom of Bahrain
    KUWAIT       — State of Kuwait
    OMAN         — Sultanate of Oman
    """

    UAE = "UAE"
    SAUDI_ARABIA = "SAUDI_ARABIA"
    QATAR = "QATAR"
    BAHRAIN = "BAHRAIN"
    KUWAIT = "KUWAIT"
    OMAN = "OMAN"


class MiddleEastSector(str, Enum):
    """
    Deployment sector for the AI system.

    GENERAL     — General private-sector organisation; baseline obligations apply.
    FINANCIAL   — Financial institution regulated by CBUAE (UAE) or SAMA (Saudi).
    HEALTHCARE  — Healthcare provider; UAE DOH or Saudi SFDA approval may apply.
    GOVERNMENT  — Government agency or public administration body.
    EDUCATION   — Educational institution or EdTech platform.
    ENERGY      — Energy, utilities, or critical infrastructure operator.
    RETAIL      — Retail, e-commerce, or consumer-facing platform.
    """

    GENERAL = "general"
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    EDUCATION = "education"
    ENERGY = "energy"
    RETAIL = "retail"


class MiddleEastAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under GCC regulatory frameworks.

    HIGH         — AI systems with significant potential to affect individual
                   rights, safety, or welfare; requires DPO and heightened
                   compliance obligations.
    MEDIUM       — AI systems with meaningful but bounded risk.
    LOW          — AI systems with limited potential for harm.
    UNCLASSIFIED — Risk level has not yet been assessed.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCLASSIFIED = "UNCLASSIFIED"


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MiddleEastAIContext:
    """
    Governance review context for a Middle East (GCC) AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    jurisdiction : MiddleEastJurisdiction
        Primary jurisdiction where the AI system is deployed.
    sector : MiddleEastSector
        Deployment sector; controls which sectoral filter rules apply.
    ai_risk_level : MiddleEastAIRiskLevel
        Risk classification under the applicable GCC regulatory framework.
    is_automated_decision : bool
        True if the AI system makes or significantly influences decisions
        about individuals without meaningful human involvement.
    involves_personal_data : bool
        True if the AI system collects, uses, or processes personal data.
    has_data_subject_consent : bool
        True if valid consent has been obtained from the data subject.
    processing_purpose : str
        Stated purpose for processing personal data.  Recognised lawful
        bases that may not require consent: "legal_obligation",
        "vital_interest", "public_task", "contract".
    is_uae_pdpl_subject : bool
        True if UAE Federal Decree-Law No. 45/2021 (PDPL) applies to
        this AI system's processing activities.
    has_uae_consent : bool
        True if valid UAE PDPL consent or another lawful basis has been
        obtained for UAE-jurisdictional processing.
    uae_dpo_appointed : bool
        True if a Data Protection Officer has been appointed as required
        by UAE PDPL Article 16 for high-risk processing activities.
    is_saudi_pdpl_subject : bool
        True if the Saudi Personal Data Protection Law (Royal Decree M/19,
        effective 2022) applies to this AI system's processing activities.
    has_saudi_consent : bool
        True if valid Saudi PDPL consent or another lawful basis has been
        obtained for Saudi-jurisdictional processing.
    saudi_data_classified : bool
        True if personal data has been classified (Public/Sensitive/
        Confidential) per the NDMO Data Governance Framework before AI
        processing.
    is_qatar_pdpa_subject : bool
        True if Qatar Personal Data Privacy Protection Law (Law No. 13/2016)
        applies to this AI system's processing activities.
    has_qatar_consent : bool
        True if valid Qatar PDPA consent or another lawful basis has been
        obtained for Qatar-jurisdictional processing.
    is_cross_border_transfer : bool
        True if personal data is transferred to a recipient in another
        jurisdiction, triggering GCC cross-border data transfer controls.
    transfer_destination_jurisdiction : str
        ISO alpha-2 country code of the data transfer destination.  Used
        to determine whether the destination is an adequate GCC jurisdiction
        or requires additional authorisation.
    is_high_impact_ai : bool
        True if the AI system is classified as high-impact AI with the
        potential for significant effects on individuals or society.
    ai_transparency_disclosed : bool
        True if the AI system's nature and decision-making logic have been
        disclosed to affected individuals as required by UAE AI Ethics
        Principles 2019 Principle 3.
    involves_biometric_data : bool
        True if the AI system processes biometric data (fingerprints, facial
        recognition, iris scans, voice prints, or similar).
    has_biometric_consent : bool
        True if explicit consent for biometric data processing has been
        obtained (UAE PDPL Article 10).
    is_financial_ai : bool
        True if the AI system is used in a financial services context
        (lending, credit scoring, insurance, payments, wealth management).
    has_cbuae_approval : bool
        True if the Central Bank of the UAE (CBUAE) has approved the
        financial AI system for deployment in the UAE.
    has_sama_approval : bool
        True if the Saudi Arabia Monetary Authority (SAMA) has approved
        the financial AI system for deployment in Saudi Arabia.
    is_medical_ai : bool
        True if the AI system provides clinical decision support, diagnostic
        recommendations, or other Software as a Medical Device (SaMD)
        functionality.
    has_doh_approval : bool
        True if the UAE Department of Health (DOH) has approved the medical
        AI system for deployment in the UAE.
    has_sfda_approval : bool
        True if the Saudi Food and Drug Authority (SFDA) has approved the
        medical AI system for deployment in Saudi Arabia.
    profiling_involved : bool
        True if the AI system profiles individuals based on personal data
        for automated decision purposes (Qatar PDPA Article 9).
    right_to_explanation_provided : bool
        True if affected individuals have been provided with an explanation
        of automated decisions as required by the Qatar National AI
        Strategy 2030.
    """

    user_id: str
    jurisdiction: MiddleEastJurisdiction
    sector: MiddleEastSector
    ai_risk_level: MiddleEastAIRiskLevel
    is_automated_decision: bool
    involves_personal_data: bool
    has_data_subject_consent: bool
    processing_purpose: str
    is_uae_pdpl_subject: bool
    has_uae_consent: bool
    uae_dpo_appointed: bool
    is_saudi_pdpl_subject: bool
    has_saudi_consent: bool
    saudi_data_classified: bool
    is_qatar_pdpa_subject: bool
    has_qatar_consent: bool
    is_cross_border_transfer: bool
    transfer_destination_jurisdiction: str
    is_high_impact_ai: bool
    ai_transparency_disclosed: bool
    involves_biometric_data: bool
    has_biometric_consent: bool
    is_financial_ai: bool
    has_cbuae_approval: bool
    has_sama_approval: bool
    is_medical_ai: bool
    has_doh_approval: bool
    has_sfda_approval: bool
    profiling_involved: bool
    right_to_explanation_provided: bool


@dataclass(frozen=True)
class MiddleEastAIDocument:
    """
    Document metadata submitted to the Middle East AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    content_type : str
        Type of document: e.g. "REPORT", "AI_OUTPUT", "USER_DATA", "CONTRACT".
    contains_personal_data : bool
        True if the document contains personal data of individuals.
    risk_level : str
        Risk classification: "HIGH", "MEDIUM", "LOW", "UNCLASSIFIED".
    requires_human_review : bool
        True if the document has been flagged as requiring human review
        by a prior evaluation stage.
    processing_timestamp : str
        ISO-8601 timestamp of when the document was submitted for processing.
    jurisdiction : str
        Jurisdiction identifier where the document processing takes place.
    """

    document_id: str
    content_type: str
    contains_personal_data: bool
    risk_level: str
    requires_human_review: bool
    processing_timestamp: str
    jurisdiction: str


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single Middle East AI governance filter evaluation."""

    filter_name: str
    decision: str = "APPROVED"
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = True

    @property
    def is_denied(self) -> bool:
        """True only if this filter produced a DENIED decision."""
        return self.decision == "DENIED"


# ---------------------------------------------------------------------------
# Layer 1 — UAE PDPL (Federal Decree-Law No. 45/2021) + UAE AI Ethics 2019
# ---------------------------------------------------------------------------


class UAEAIFilter:
    """
    Layer 1: UAE Federal Decree-Law No. 45/2021 on the Protection of Personal
    Data (UAE PDPL) and UAE AI Ethics Principles (2019).

    The UAE PDPL came into force in November 2021 and establishes a
    comprehensive personal data protection framework for the UAE.  It is
    supplemented by the UAE National AI Strategy 2031 and the UAE AI Ethics
    Principles adopted by the UAE Cabinet in 2019.  Four principal controls
    apply to AI systems:

    (a) Lawful basis (Article 7) — personal data may be processed only with
        the data subject's consent or another recognised lawful basis: legal
        obligation, vital interest, public task, or contract; processing
        without a valid basis is prohibited;
    (b) Special categories (Article 10) — explicit consent is required
        before processing biometric data or other special category data;
    (c) AI transparency (UAE AI Ethics Principles 2019, Principle 3) —
        AI systems that have significant impact on individuals must be
        transparent about their nature and decision-making logic; high-impact
        AI without transparency disclosure requires human review;
    (d) Data Protection Officer (Article 16) — controllers engaged in
        high-risk processing (including high-risk AI) must appoint a DPO.

    References
    ----------
    UAE Federal Decree-Law No. 45/2021 on the Protection of Personal Data
    UAE AI Ethics Principles (2019), UAE Cabinet Resolution
    UAE National AI Strategy 2031
    """

    FILTER_NAME = "UAE_AI_FILTER"

    _LAWFUL_BASES = frozenset(
        {"legal_obligation", "vital_interest", "public_task", "contract"}
    )

    def evaluate(
        self, context: MiddleEastAIContext, document: MiddleEastAIDocument
    ) -> FilterResult:
        # Not subject to UAE jurisdiction — pass through
        if (
            not context.is_uae_pdpl_subject
            or context.jurisdiction != MiddleEastJurisdiction.UAE
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason="UAE PDPL: Not subject to UAE jurisdiction",
                regulation_citation=(
                    "UAE Federal Decree-Law No. 45/2021 (UAE PDPL) — "
                    "jurisdiction not applicable to this processing activity"
                ),
                requires_logging=False,
            )

        # Article 7 — lawful basis for personal data processing
        if (
            context.involves_personal_data
            and not context.has_uae_consent
            and context.processing_purpose not in self._LAWFUL_BASES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "UAE PDPL Article 7: Consent or lawful basis required for "
                    "personal data processing"
                ),
                regulation_citation=(
                    "UAE Federal Decree-Law No. 45/2021 (UAE PDPL), Article 7 — "
                    "Lawful Basis for Processing: personal data may be processed "
                    "only with consent or a recognised lawful basis (legal "
                    "obligation, vital interest, public task, or contract)"
                ),
                requires_logging=True,
            )

        # Article 10 — biometric data requires explicit consent
        if context.involves_biometric_data and not context.has_biometric_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "UAE PDPL Article 10: Explicit consent required for biometric "
                    "data processing"
                ),
                regulation_citation=(
                    "UAE Federal Decree-Law No. 45/2021 (UAE PDPL), Article 10 — "
                    "Special Categories of Personal Data: processing of biometric "
                    "data requires explicit consent from the data subject"
                ),
                requires_logging=True,
            )

        # UAE AI Ethics Principles 2019, Principle 3 — transparency for high-impact AI
        if context.is_high_impact_ai and not context.ai_transparency_disclosed:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "UAE AI Ethics Principles (2019) Principle 3: AI systems must "
                    "be transparent about their nature and decision-making"
                ),
                regulation_citation=(
                    "UAE AI Ethics Principles (2019), Principle 3 — Transparency: "
                    "AI systems with significant impact on individuals must disclose "
                    "their nature and the basis for their decisions; high-impact AI "
                    "without transparency disclosure requires human review before "
                    "automated processing"
                ),
                requires_logging=True,
            )

        # Article 16 — DPO required for high-risk AI processing
        if (
            context.ai_risk_level == MiddleEastAIRiskLevel.HIGH
            and not context.uae_dpo_appointed
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "UAE PDPL Article 16: Data Protection Officer required for "
                    "high-risk AI processing"
                ),
                regulation_citation=(
                    "UAE Federal Decree-Law No. 45/2021 (UAE PDPL), Article 16 — "
                    "Data Protection Officer: controllers conducting high-risk "
                    "processing activities, including high-risk AI systems, must "
                    "appoint a Data Protection Officer before processing commences"
                ),
                requires_logging=True,
            )

        # All UAE PDPL and AI Ethics requirements satisfied
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "UAE PDPL and AI Ethics requirements satisfied — lawful basis "
                "confirmed, biometric consent obtained where applicable, and "
                "AI transparency obligations met"
            ),
            regulation_citation=(
                "UAE Federal Decree-Law No. 45/2021 (UAE PDPL) — all applicable "
                "obligations satisfied"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Saudi PDPL 2021 + NDMO + SAMA / SFDA
# ---------------------------------------------------------------------------


class SaudiAIFilter:
    """
    Layer 2: Saudi Arabia Personal Data Protection Law (PDPL, Royal Decree M/19,
    2021) supplemented by NDMO Data Governance Framework, SAMA Open Banking
    Framework, and Saudi SFDA AI/ML-based SaMD Guidance.

    The Saudi PDPL was promulgated by Royal Decree M/19 on September 16, 2021,
    and became effective September 14, 2022.  The National Data Management
    Office (NDMO) issued a supporting Data Governance Framework that requires
    data classification before AI processing.  Four principal controls apply:

    (a) Consent (Article 4) — explicit consent is required for personal data
        collection and processing unless the processing is for legal obligation,
        vital interest, or a public task;
    (b) Data classification (NDMO) — personal data must be classified as
        Public, Sensitive, or Confidential by the controller before it may
        be processed by AI systems;
    (c) SAMA financial AI approval — financial AI systems operating in Saudi
        Arabia require SAMA approval under the SAMA Open Banking Framework
        and AI Governance Principles before deployment;
    (d) SFDA medical AI approval — AI-based Software as a Medical Device
        (SaMD) requires SFDA approval under the Saudi SFDA AI/ML-based
        SaMD Guidance before clinical deployment.

    References
    ----------
    Saudi Arabia Personal Data Protection Law (Royal Decree M/19, 2021)
    NDMO Data Governance Framework (Saudi Arabia, 2020)
    SAMA Open Banking Framework and AI Governance Principles
    Saudi SFDA AI/ML-based Software as a Medical Device (SaMD) Guidance
    """

    FILTER_NAME = "SAUDI_AI_FILTER"

    _LAWFUL_BASES = frozenset({"legal_obligation", "vital_interest", "public_task"})

    def evaluate(
        self, context: MiddleEastAIContext, document: MiddleEastAIDocument
    ) -> FilterResult:
        # Not subject to Saudi jurisdiction — pass through
        if (
            not context.is_saudi_pdpl_subject
            or context.jurisdiction != MiddleEastJurisdiction.SAUDI_ARABIA
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason="Saudi PDPL: Not subject to Saudi Arabia jurisdiction",
                regulation_citation=(
                    "Saudi Arabia Personal Data Protection Law (Royal Decree M/19) — "
                    "jurisdiction not applicable to this processing activity"
                ),
                requires_logging=False,
            )

        # Article 4 — consent or lawful basis required for personal data
        if (
            context.involves_personal_data
            and not context.has_saudi_consent
            and context.processing_purpose not in self._LAWFUL_BASES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Saudi PDPL Article 4: Explicit consent required for personal "
                    "data collection and processing"
                ),
                regulation_citation=(
                    "Saudi Arabia Personal Data Protection Law (Royal Decree M/19), "
                    "Article 4 — Conditions for Data Processing: explicit consent "
                    "is required for the collection and processing of personal data "
                    "unless a recognised lawful basis (legal obligation, vital "
                    "interest, public task) applies"
                ),
                requires_logging=True,
            )

        # NDMO — data classification required before AI processing
        if not context.saudi_data_classified and context.involves_personal_data:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "NDMO Data Governance Framework: Personal data must be classified "
                    "(Public/Sensitive/Confidential) before AI processing"
                ),
                regulation_citation=(
                    "NDMO Data Governance Framework (Saudi Arabia) — Data "
                    "Classification: personal data must be classified as Public, "
                    "Sensitive, or Confidential by the data controller before the "
                    "data may be used in AI processing; unclassified personal data "
                    "cannot be processed by AI systems without prior classification"
                ),
                requires_logging=True,
            )

        # SAMA — financial AI requires SAMA approval
        if context.is_financial_ai and not context.has_sama_approval:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "SAMA Open Banking Framework + AI Governance: Financial AI "
                    "systems require SAMA approval before deployment"
                ),
                regulation_citation=(
                    "SAMA Open Banking Framework and AI Governance Principles "
                    "(Saudi Arabia Monetary Authority) — Financial AI System "
                    "Approval: AI systems used in financial services, including "
                    "lending, credit scoring, insurance underwriting, and payment "
                    "processing, require SAMA approval before deployment in Saudi "
                    "Arabia"
                ),
                requires_logging=True,
            )

        # SFDA — medical AI requires SFDA approval
        if context.is_medical_ai and not context.has_sfda_approval:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason="Saudi SFDA AI/ML-based SaMD Guidance: Medical AI requires SFDA approval",
                regulation_citation=(
                    "Saudi SFDA AI/ML-based Software as a Medical Device (SaMD) "
                    "Guidance — Regulatory Approval: AI-based clinical decision "
                    "support and diagnostic software constitutes a medical device "
                    "under Saudi law and requires SFDA approval before clinical "
                    "deployment in Saudi Arabia"
                ),
                requires_logging=True,
            )

        # All Saudi PDPL and sectoral requirements satisfied
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Saudi PDPL and sectoral requirements satisfied — consent confirmed, "
                "data classified, and applicable sectoral approvals obtained"
            ),
            regulation_citation=(
                "Saudi Arabia Personal Data Protection Law (Royal Decree M/19) — "
                "all applicable obligations satisfied"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Qatar PDPA Law No. 13/2016 + Qatar National AI Strategy 2030
# ---------------------------------------------------------------------------


class QatarAIFilter:
    """
    Layer 3: Qatar Personal Data Privacy Protection Law (Law No. 13 of 2016)
    and Qatar National AI Strategy 2030.

    Qatar's PDPA (Law No. 13/2016) establishes data protection obligations
    for organisations processing personal data in Qatar.  The Qatar National
    AI Strategy 2030, announced by the Ministry of Communications and
    Information Technology (MCIT), establishes principles for trustworthy
    AI deployment.  Four principal controls apply:

    (a) Consent (Article 8) — processing of personal data requires the
        data subject's consent unless processing is for a recognised basis;
    (b) Automated decisions (Qatar National AI Strategy 2030) — automated
        decisions that affect individuals must be explainable; systems that
        cannot provide explanations require human review;
    (c) Profiling (Article 9) — profiling of individuals based on personal
        data requires explicit data subject consent;
    (d) Cross-border transfer (Article 12) — transfers of personal data
        outside Qatar require authorisation from the Ministry of Transport
        and Communications (MOTC) or consent.

    References
    ----------
    Qatar Personal Data Privacy Protection Law (Law No. 13 of 2016)
    Qatar National AI Strategy 2030, MCIT
    Qatar MOTC Data Protection Guidelines
    """

    FILTER_NAME = "QATAR_AI_FILTER"

    def evaluate(
        self, context: MiddleEastAIContext, document: MiddleEastAIDocument
    ) -> FilterResult:
        # Not subject to Qatar jurisdiction — pass through
        if (
            not context.is_qatar_pdpa_subject
            or context.jurisdiction != MiddleEastJurisdiction.QATAR
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason="Qatar PDPA: Not subject to Qatar jurisdiction",
                regulation_citation=(
                    "Qatar Personal Data Privacy Protection Law (Law No. 13/2016) — "
                    "jurisdiction not applicable to this processing activity"
                ),
                requires_logging=False,
            )

        # Article 8 — consent required for personal data processing
        if context.involves_personal_data and not context.has_qatar_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Qatar PDPA Law No. 13/2016 Article 8: Consent required for "
                    "personal data processing"
                ),
                regulation_citation=(
                    "Qatar Personal Data Privacy Protection Law (Law No. 13/2016), "
                    "Article 8 — Conditions for Lawful Processing: processing of "
                    "personal data requires the explicit consent of the data subject "
                    "or another recognised lawful basis"
                ),
                requires_logging=True,
            )

        # Qatar National AI Strategy 2030 — automated decisions must be explainable
        if context.is_automated_decision and not context.right_to_explanation_provided:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Qatar National AI Strategy 2030: Automated decisions must be "
                    "explainable to affected individuals"
                ),
                regulation_citation=(
                    "Qatar National AI Strategy 2030 (MCIT) — Explainability "
                    "Principle: AI systems that make or significantly contribute to "
                    "automated decisions affecting individuals must provide a "
                    "meaningful explanation of the decision basis; systems without "
                    "explainability require human review"
                ),
                requires_logging=True,
            )

        # Article 9 — profiling requires explicit data subject consent
        if context.profiling_involved and not context.has_data_subject_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Qatar PDPA Article 9: Profiling requires explicit data "
                    "subject consent"
                ),
                regulation_citation=(
                    "Qatar Personal Data Privacy Protection Law (Law No. 13/2016), "
                    "Article 9 — Profiling: the profiling of individuals based on "
                    "personal data for purposes of automated decision-making requires "
                    "the explicit consent of the data subject"
                ),
                requires_logging=True,
            )

        # All Qatar PDPA and AI Strategy requirements satisfied
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Qatar PDPA and AI Strategy requirements satisfied — consent "
                "confirmed, automated decision explainability provided, and "
                "profiling consent obtained where applicable"
            ),
            regulation_citation=(
                "Qatar Personal Data Privacy Protection Law (Law No. 13/2016) — "
                "all applicable obligations satisfied"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — GCC Cross-Border Data Transfer Framework
# ---------------------------------------------------------------------------


class GCCCrossBorderFilter:
    """
    Layer 4: GCC Cross-Border Data Transfer Framework.

    Cross-border data flows within the GCC are governed by a combination of
    national PDPL/PDPA provisions and the GCC framework that treats member
    states as adequate jurisdictions for mutual data transfers.  Each GCC
    member state's national law also contains specific provisions for transfers
    outside the GCC:

    UAE PDPL Article 26 — transfers of personal data outside the GCC require
        consent or an adequacy decision; transfers within the GCC are
        permitted under the GCC cross-border data sharing framework;
    Saudi PDPL Article 29 — cross-border transfers outside Saudi Arabia
        require approval from the Saudi Data and Artificial Intelligence
        Authority (SDAIA); transfers to GCC member states are treated as
        adequate;
    Qatar PDPA Article 12 — cross-border transfers of personal data outside
        Qatar require authorisation from MOTC or the data subject's consent;
        transfers within the GCC are permitted.

    GCC adequate member states: AE (UAE), SA (Saudi Arabia), QA (Qatar),
        BH (Bahrain), KW (Kuwait), OM (Oman).

    References
    ----------
    UAE Federal Decree-Law No. 45/2021 (PDPL), Article 26
    Saudi Arabia Personal Data Protection Law (Royal Decree M/19), Article 29
    Qatar Personal Data Privacy Protection Law (Law No. 13/2016), Article 12
    GCC Data Protection and Cross-Border Transfer Framework
    """

    FILTER_NAME = "GCC_CROSS_BORDER_FILTER"

    # ISO alpha-2 codes for GCC member states — treated as adequate among themselves
    _GCC_ADEQUATE = frozenset({"AE", "SA", "QA", "BH", "KW", "OM"})

    def evaluate(
        self, context: MiddleEastAIContext, document: MiddleEastAIDocument
    ) -> FilterResult:
        # No cross-border transfer — this filter does not apply
        if not context.is_cross_border_transfer:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason="No cross-border data transfer involved",
                regulation_citation=(
                    "GCC Cross-Border Data Transfer Framework — no cross-border "
                    "transfer; filter not applicable"
                ),
                requires_logging=False,
            )

        dest = context.transfer_destination_jurisdiction

        # GCC-to-GCC transfer — all member states are adequate
        if dest in self._GCC_ADEQUATE:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason=(
                    f"GCC cross-border transfer to {dest} — GCC member state "
                    "is an adequate jurisdiction"
                ),
                regulation_citation=(
                    "GCC cross-border data sharing framework — adequate jurisdiction: "
                    "transfers between GCC member states (AE, SA, QA, BH, KW, OM) "
                    "are permitted under the mutual adequacy framework"
                ),
                requires_logging=False,
            )

        # UAE — transfer to non-GCC jurisdiction requires consent or adequacy
        if (
            context.jurisdiction == MiddleEastJurisdiction.UAE
            and dest not in self._GCC_ADEQUATE
            and not context.has_uae_consent
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "UAE PDPL Article 26: Cross-border transfer outside GCC requires "
                    "consent or adequacy decision"
                ),
                regulation_citation=(
                    "UAE Federal Decree-Law No. 45/2021 (UAE PDPL), Article 26 — "
                    "Cross-Border Data Transfer: transfers of personal data to "
                    "jurisdictions outside the GCC require either the data subject's "
                    "consent or an adequacy decision; no consent or adequacy "
                    "decision is in place for the destination jurisdiction"
                ),
                requires_logging=True,
            )

        # Saudi Arabia — transfer to non-GCC jurisdiction requires SDAIA approval
        if (
            context.jurisdiction == MiddleEastJurisdiction.SAUDI_ARABIA
            and dest not in self._GCC_ADEQUATE
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Saudi PDPL Article 29: Cross-border transfer outside KSA "
                    "requires SDAIA approval"
                ),
                regulation_citation=(
                    "Saudi Arabia Personal Data Protection Law (Royal Decree M/19), "
                    "Article 29 — Cross-Border Data Transfer: transfers of personal "
                    "data outside Saudi Arabia require approval from the Saudi Data "
                    "and Artificial Intelligence Authority (SDAIA); transfers to GCC "
                    "member states are treated as adequate and do not require "
                    "additional approval"
                ),
                requires_logging=True,
            )

        # Qatar — transfer to non-GCC jurisdiction requires MOTC authorisation or consent
        if (
            context.jurisdiction == MiddleEastJurisdiction.QATAR
            and dest not in self._GCC_ADEQUATE
            and not context.has_qatar_consent
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Qatar PDPA Article 12: Cross-border transfer requires MOTC "
                    "authorization or consent"
                ),
                regulation_citation=(
                    "Qatar Personal Data Privacy Protection Law (Law No. 13/2016), "
                    "Article 12 — Cross-Border Transfer: transfers of personal data "
                    "outside Qatar require authorisation from the Ministry of "
                    "Transport and Communications (MOTC) or the data subject's "
                    "explicit consent; no authorisation or consent is in place "
                    "for the destination jurisdiction"
                ),
                requires_logging=True,
            )

        # All GCC cross-border transfer requirements satisfied
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "GCC cross-border data transfer requirements satisfied — applicable "
                "consent, adequacy, or authorisation requirements met"
            ),
            regulation_citation=(
                "GCC data transfer requirements satisfied — applicable national PDPL "
                "cross-border transfer provisions met"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------


@dataclass
class MiddleEastAIGovernanceReport:
    """
    Aggregated governance report produced by the MiddleEastAIGovernanceOrchestrator.

    Attributes
    ----------
    context : MiddleEastAIContext
        The governance context that was evaluated.
    document : MiddleEastAIDocument
        The document that was evaluated.
    filter_results : list[FilterResult]
        Ordered list of FilterResult objects from each filter layer.
    """

    context: MiddleEastAIContext
    document: MiddleEastAIDocument
    filter_results: List[FilterResult]

    @property
    def overall_decision(self) -> str:
        """
        Aggregate decision across all filter results.

        Returns "DENIED" if any filter produced a DENIED decision.
        Returns "REQUIRES_HUMAN_REVIEW" if no filter was DENIED but at
        least one filter requires human review.
        Returns "APPROVED" only if all filters approved.
        """
        if any(r.decision == "DENIED" for r in self.filter_results):
            return "DENIED"
        if any(r.decision == "REQUIRES_HUMAN_REVIEW" for r in self.filter_results):
            return "REQUIRES_HUMAN_REVIEW"
        return "APPROVED"

    @property
    def is_compliant(self) -> bool:
        """True only if overall_decision is 'APPROVED'."""
        return self.overall_decision == "APPROVED"

    @property
    def compliance_summary(self) -> str:
        """Human-readable summary of the governance evaluation."""
        decision = self.overall_decision
        jurisdiction = self.context.jurisdiction.value
        sector = self.context.sector.value
        user_id = self.context.user_id
        n_filters = len(self.filter_results)
        n_approved = sum(1 for r in self.filter_results if r.decision == "APPROVED")
        n_denied = sum(1 for r in self.filter_results if r.decision == "DENIED")
        n_review = sum(
            1 for r in self.filter_results if r.decision == "REQUIRES_HUMAN_REVIEW"
        )

        lines = [
            f"Middle East AI Governance Report — User: {user_id}",
            f"Jurisdiction: {jurisdiction} | Sector: {sector} | "
            f"Risk Level: {self.context.ai_risk_level.value}",
            f"Overall Decision: {decision}",
            f"Filter Results: {n_filters} evaluated, {n_approved} approved, "
            f"{n_denied} denied, {n_review} require human review",
        ]

        if n_denied > 0:
            lines.append(
                "Action Required: One or more filters denied this request. "
                "Resolve compliance violations before resubmitting."
            )
        elif n_review > 0:
            lines.append(
                "Action Required: This request requires human review before "
                "automated processing may proceed."
            )
        else:
            lines.append(
                "All applicable GCC regulatory requirements satisfied. "
                "Processing may proceed."
            )

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class MiddleEastAIGovernanceOrchestrator:
    """
    Four-layer Middle East (GCC) AI governance orchestrator.

    Applies all four filter layers sequentially and collects all results
    regardless of whether an earlier layer produced a DENIED or
    REQUIRES_HUMAN_REVIEW outcome.  This ensures complete compliance
    visibility across all applicable regulatory frameworks.

    Layers
    ------
    1. UAEAIFilter        — UAE PDPL + UAE AI Ethics Principles 2019
    2. SaudiAIFilter      — Saudi PDPL + NDMO + SAMA/SFDA
    3. QatarAIFilter      — Qatar PDPA + Qatar National AI Strategy 2030
    4. GCCCrossBorderFilter — GCC cross-border data transfer framework
    """

    def __init__(self) -> None:
        self._filters = [
            UAEAIFilter(),
            SaudiAIFilter(),
            QatarAIFilter(),
            GCCCrossBorderFilter(),
        ]

    def evaluate(
        self, context: MiddleEastAIContext, document: MiddleEastAIDocument
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return their results.

        Parameters
        ----------
        context : MiddleEastAIContext
            The AI processing context to evaluate.
        document : MiddleEastAIDocument
            The document submitted for governance review.

        Returns
        -------
        list[FilterResult]
            Ordered list of FilterResult objects, one per filter layer.
            All four filters always run regardless of earlier outcomes.
        """
        return [f.evaluate(context, document) for f in self._filters]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # ------------------------------------------------------------------
    # Scenario 1: Compliant UAE general-purpose AI with low risk
    # ------------------------------------------------------------------
    uae_compliant_ctx = MiddleEastAIContext(
        user_id="u-uae-001",
        jurisdiction=MiddleEastJurisdiction.UAE,
        sector=MiddleEastSector.GENERAL,
        ai_risk_level=MiddleEastAIRiskLevel.LOW,
        is_automated_decision=False,
        involves_personal_data=True,
        has_data_subject_consent=True,
        processing_purpose="service_delivery",
        is_uae_pdpl_subject=True,
        has_uae_consent=True,
        uae_dpo_appointed=True,
        is_saudi_pdpl_subject=False,
        has_saudi_consent=False,
        saudi_data_classified=False,
        is_qatar_pdpa_subject=False,
        has_qatar_consent=False,
        is_cross_border_transfer=False,
        transfer_destination_jurisdiction="",
        is_high_impact_ai=False,
        ai_transparency_disclosed=True,
        involves_biometric_data=False,
        has_biometric_consent=False,
        is_financial_ai=False,
        has_cbuae_approval=False,
        has_sama_approval=False,
        is_medical_ai=False,
        has_doh_approval=False,
        has_sfda_approval=False,
        profiling_involved=False,
        right_to_explanation_provided=True,
    )
    uae_doc = MiddleEastAIDocument(
        document_id="doc-uae-001",
        content_type="REPORT",
        contains_personal_data=True,
        risk_level="LOW",
        requires_human_review=False,
        processing_timestamp="2025-06-01T10:00:00+04:00",
        jurisdiction="UAE",
    )
    orchestrator = MiddleEastAIGovernanceOrchestrator()
    results = orchestrator.evaluate(uae_compliant_ctx, uae_doc)
    report = MiddleEastAIGovernanceReport(
        context=uae_compliant_ctx, document=uae_doc, filter_results=results
    )
    print("=" * 70)
    print("SCENARIO 1: Compliant UAE General AI")
    print("=" * 70)
    print(report.compliance_summary)
    for r in results:
        print(f"  [{r.filter_name}] {r.decision} — {r.reason[:60]}...")
    print()

    # ------------------------------------------------------------------
    # Scenario 2: Saudi financial AI without SAMA approval
    # ------------------------------------------------------------------
    saudi_financial_ctx = MiddleEastAIContext(
        user_id="u-sa-002",
        jurisdiction=MiddleEastJurisdiction.SAUDI_ARABIA,
        sector=MiddleEastSector.FINANCIAL,
        ai_risk_level=MiddleEastAIRiskLevel.HIGH,
        is_automated_decision=True,
        involves_personal_data=True,
        has_data_subject_consent=True,
        processing_purpose="contract",
        is_uae_pdpl_subject=False,
        has_uae_consent=False,
        uae_dpo_appointed=False,
        is_saudi_pdpl_subject=True,
        has_saudi_consent=True,
        saudi_data_classified=True,
        is_qatar_pdpa_subject=False,
        has_qatar_consent=False,
        is_cross_border_transfer=False,
        transfer_destination_jurisdiction="",
        is_high_impact_ai=True,
        ai_transparency_disclosed=True,
        involves_biometric_data=False,
        has_biometric_consent=False,
        is_financial_ai=True,
        has_cbuae_approval=False,
        has_sama_approval=False,   # ← MISSING SAMA APPROVAL
        is_medical_ai=False,
        has_doh_approval=False,
        has_sfda_approval=False,
        profiling_involved=False,
        right_to_explanation_provided=True,
    )
    results2 = orchestrator.evaluate(saudi_financial_ctx, uae_doc)
    report2 = MiddleEastAIGovernanceReport(
        context=saudi_financial_ctx, document=uae_doc, filter_results=results2
    )
    print("=" * 70)
    print("SCENARIO 2: Saudi Financial AI — Missing SAMA Approval")
    print("=" * 70)
    print(report2.compliance_summary)
    for r in results2:
        print(f"  [{r.filter_name}] {r.decision} — {r.reason[:60]}...")
    print()

    # ------------------------------------------------------------------
    # Scenario 3: UAE cross-border transfer to non-GCC without consent
    # ------------------------------------------------------------------
    cross_border_ctx = MiddleEastAIContext(
        user_id="u-uae-003",
        jurisdiction=MiddleEastJurisdiction.UAE,
        sector=MiddleEastSector.RETAIL,
        ai_risk_level=MiddleEastAIRiskLevel.MEDIUM,
        is_automated_decision=False,
        involves_personal_data=True,
        has_data_subject_consent=False,   # ← NO CONSENT for cross-border
        processing_purpose="contract",
        is_uae_pdpl_subject=True,
        has_uae_consent=True,
        uae_dpo_appointed=True,
        is_saudi_pdpl_subject=False,
        has_saudi_consent=False,
        saudi_data_classified=False,
        is_qatar_pdpa_subject=False,
        has_qatar_consent=False,
        is_cross_border_transfer=True,
        transfer_destination_jurisdiction="US",   # ← Non-GCC
        is_high_impact_ai=False,
        ai_transparency_disclosed=True,
        involves_biometric_data=False,
        has_biometric_consent=False,
        is_financial_ai=False,
        has_cbuae_approval=False,
        has_sama_approval=False,
        is_medical_ai=False,
        has_doh_approval=False,
        has_sfda_approval=False,
        profiling_involved=False,
        right_to_explanation_provided=True,
    )
    results3 = orchestrator.evaluate(cross_border_ctx, uae_doc)
    report3 = MiddleEastAIGovernanceReport(
        context=cross_border_ctx, document=uae_doc, filter_results=results3
    )
    print("=" * 70)
    print("SCENARIO 3: UAE Cross-Border Transfer to US — No Consent")
    print("=" * 70)
    print(report3.compliance_summary)
    for r in results3:
        print(f"  [{r.filter_name}] {r.decision} — {r.reason[:60]}...")
