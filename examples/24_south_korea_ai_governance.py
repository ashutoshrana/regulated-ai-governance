"""
24_south_korea_ai_governance.py — Four-layer AI governance framework for AI
systems subject to South Korean law, covering the overlapping national and
sector-level obligations that apply to AI-driven data processing in Korea.

Demonstrates a multi-layer governance orchestrator where four Korean
regulatory frameworks each impose independent requirements on AI systems
deployed in South Korea:

    Layer 1  — Korea AI Framework Act (enacted January 23, 2024):
               South Korea's Act on the Development of Artificial Intelligence
               and Establishment of Trust-Based AI Framework (AI Framework Act)
               was promulgated January 23, 2024. It classifies AI systems by
               impact level and establishes obligations for high-impact AI:

               Article 10 — Prohibited Practices: AI systems used for social
                   credit scoring, subliminal manipulation, and certain real-time
                   biometric surveillance in public spaces are prohibited;
               Article 6  — High-Impact AI Transparency: operators of high-impact
                   AI systems must disclose AI involvement to users and obtain
                   acknowledgment before automated processing; systems that fail
                   to disclose require human review before deployment;
               Article 7  — Government Impact Assessment: government agencies
                   deploying high-impact AI systems must conduct a mandatory AI
                   impact assessment.

    Layer 2  — PIPA 2020 (Personal Information Protection Act, amended):
               Korea's Personal Information Protection Act (Act No. 16930,
               amended 2020, with significant amendments effective September 2023)
               governs the collection, use, and processing of personal information.
               Key provisions affecting AI systems:

               Article 15 — Lawful Collection/Use: personal information may be
                   collected and used only with the data subject's consent or
                   another recognised lawful basis (legal obligation, vital
                   interest, public task, or legitimate interest);
               Article 23 — Sensitive Information: processing of sensitive
                   personal information (ideology, religion, trade union
                   membership, political opinion, health data, sexual orientation,
                   genetic information, biometric data, criminal records) requires
                   explicit separate consent;
               Article 28-2 — Automated Decision-Making: data subjects have the
                   right to contest and request human review of automated
                   decisions; controllers must notify data subjects and provide a
                   mechanism to contest;
               Article 28-3 — Profiling: profiling of individuals based on
                   personal information for automated decision purposes requires
                   consent or another recognised basis;
               Article 39-3 — Cross-Border Transfer: personal information may
                   only be transferred abroad to jurisdictions providing adequate
                   protection or where the controller has obtained binding
                   transfer agreements (Standard Contractual Clauses or equivalent).

    Layer 3  — Korea Sectoral AI Regulations:
               Sector-specific AI obligations issued by Korean financial,
               employment, and healthcare regulators:

               Credit Information Act Article 20 (FSC/FSS) — AI-based automated
                   credit decisions must include explainability provisions and
                   provide the data subject with the right to contest;
               Korea Employment Act — automated hiring decision systems used in
                   employment screening must include a mandatory human review
                   stage before final employment decisions are made;
               Korean Medical Devices Act / Korean Medical Act — AI-based
                   clinical decision support software (Software as a Medical
                   Device, SaMD) requires approval from the Ministry of Food and
                   Drug Safety (MFDS) before clinical deployment; approved SaMD
                   must operate under physician oversight.

    Layer 4  — Korea Data Governance & AI Auditing:
               PIPA data governance obligations and the AI Framework Act's
               documentation and auditing requirements for significant and
               high-impact AI systems:

               Korea AI Framework Act — significant and high-impact AI systems
                   must maintain documentation of AI use, audit records, and
                   impact assessments; undisclosed use of such systems requires
                   escalation for human review;
               PIPA Article 28-2 — individuals subject to automated decisions
                   must be informed of the decision, the basis for it, and
                   provided with a meaningful mechanism to contest or request
                   human review; failure to provide this mechanism is a
                   governance gap requiring remediation.

No external dependencies required.

Run:
    python examples/24_south_korea_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class KoreaAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under Korea's AI Framework Act (2024).

    HIGH_IMPACT  — AI systems with significant potential to affect individual
                   rights, safety, or welfare; includes AI used in hiring,
                   credit decisions, medical diagnosis, law enforcement, and
                   other high-stakes domains.
    SIGNIFICANT  — AI systems with meaningful but bounded risk; includes
                   automated processing systems affecting personal interests
                   in regulated sectors.
    LIMITED      — AI systems with limited potential for harm; additional
                   obligations beyond baseline PIPA requirements are minimal.
    MINIMAL      — AI systems presenting negligible risk; routine low-stakes
                   automation.
    """

    HIGH_IMPACT = "HIGH_IMPACT"
    SIGNIFICANT = "SIGNIFICANT"
    LIMITED = "LIMITED"
    MINIMAL = "MINIMAL"


class KoreaAIDecision(str, Enum):
    """Final governance decision for a Korea AI system evaluation."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class KoreaSector(str, Enum):
    """
    Deployment sector for the AI system.

    FINANCIAL   — Financial institution regulated by FSC/FSS; Credit
                  Information Act and FSC AI guidelines apply.
    HEALTHCARE  — Healthcare provider or digital health platform; MFDS SaMD
                  guidance and Korean Medical Act apply.
    PUBLIC      — Government agency or public administration body; Korea AI
                  Framework Act Article 7 impact assessment required for
                  high-impact AI.
    EMPLOYMENT  — Employment or HR platform; Korea Employment Act automated
                  hiring rules apply.
    EDUCATION   — Educational institution or EdTech platform.
    GENERAL     — General private-sector organisation; baseline PIPA and
                  AI Framework Act obligations apply.
    """

    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    PUBLIC = "public"
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    GENERAL = "general"


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KoreaAIContext:
    """
    Governance review context for a South Korea AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    sector : KoreaSector
        Deployment sector; controls which sectoral filter rules apply in
        Layer 3.
    ai_risk_level : KoreaAIRiskLevel
        Risk classification under Korea's AI Framework Act (2024).
    is_automated_decision : bool
        True if the AI system makes or significantly influences decisions
        about individuals without meaningful human involvement (PIPA Art. 28-2).
    involves_personal_info : bool
        True if the AI system collects, uses, or processes personal
        information as defined by PIPA §2(1).
    contains_sensitive_info : bool
        True if the AI system processes sensitive personal information
        (ideology, health, biometrics, criminal records) under PIPA Art. 23.
    has_pipa_consent : bool
        True if valid PIPA consent or another lawful basis has been obtained
        for processing personal information (PIPA Art. 15).
    has_sensitive_info_consent : bool
        True if explicit separate consent for sensitive personal information
        has been obtained (PIPA Art. 23).
    processing_purpose : str
        The stated purpose for processing personal information.  Recognised
        lawful bases that do not require consent: "legal_obligation",
        "vital_interest", "public_task".
    is_high_impact_ai : bool
        True if the AI system is classified as high-impact AI under the
        Korea AI Framework Act (2024).
    ai_transparency_disclosed : bool
        True if the AI system's involvement has been disclosed to users
        and acknowledgment obtained before automated processing, as
        required by Korea AI Framework Act Article 6 for high-impact AI.
    involves_prohibited_practice : bool
        True if the AI system is used for a prohibited practice under Korea
        AI Framework Act Article 10: social scoring, subliminal manipulation,
        or indiscriminate real-time biometric surveillance.
    is_automated_credit_decision : bool
        True if the AI system makes automated credit decisions (credit
        scoring, lending eligibility) in the financial sector.
    has_credit_explainability : bool
        True if the automated credit decision system provides explainability
        and a right to contest under Credit Information Act Article 20.
    is_automated_hiring_decision : bool
        True if the AI system makes or substantially contributes to hiring
        decisions without a human review stage.
    has_hiring_human_review : bool
        True if a mandatory human review stage is included before final
        employment decisions are made.
    is_medical_ai : bool
        True if the AI system provides clinical decision support,
        diagnostic recommendations, or other SaMD functionality under
        Korea's Medical Devices Act.
    has_mfds_approval : bool
        True if the medical AI / SaMD has received Ministry of Food and
        Drug Safety (MFDS) approval before clinical deployment.
    has_physician_oversight : bool
        True if AI-assisted medical decisions operate under physician
        oversight as required by the Korean Medical Act.
    cross_border_transfer : bool
        True if personal information is transferred to a recipient outside
        South Korea, triggering PIPA Article 39-3 controls.
    requester_jurisdiction : str
        ISO alpha-2 country code of the transfer destination.  Used to
        check against the adequacy list maintained by the PIPC.
    has_pipa_transfer_mechanism : bool
        True if a binding transfer mechanism (SCC or equivalent) is in
        place for cross-border transfers to non-adequate jurisdictions
        (PIPA Art. 39-3).
    profiling_involved : bool
        True if the AI system profiles individuals based on personal
        information for automated decision purposes (PIPA Art. 28-3).
    has_profiling_consent : bool
        True if consent or another recognised basis for profiling has been
        obtained (PIPA Art. 28-3).
    right_to_contest_provided : bool
        True if the data subject has been informed of the automated
        decision and provided with a mechanism to contest or request
        human review (PIPA Art. 28-2).
    is_generative_ai : bool
        True if the AI system is a generative AI model capable of
        producing synthetic content.
    has_ai_output_label : bool
        True if AI-generated outputs are clearly labelled as AI-generated.
    """

    user_id: str
    sector: KoreaSector
    ai_risk_level: KoreaAIRiskLevel
    is_automated_decision: bool
    involves_personal_info: bool
    contains_sensitive_info: bool
    has_pipa_consent: bool
    has_sensitive_info_consent: bool
    processing_purpose: str
    is_high_impact_ai: bool
    ai_transparency_disclosed: bool
    involves_prohibited_practice: bool
    is_automated_credit_decision: bool
    has_credit_explainability: bool
    is_automated_hiring_decision: bool
    has_hiring_human_review: bool
    is_medical_ai: bool
    has_mfds_approval: bool
    has_physician_oversight: bool
    cross_border_transfer: bool
    requester_jurisdiction: str
    has_pipa_transfer_mechanism: bool
    profiling_involved: bool
    has_profiling_consent: bool
    right_to_contest_provided: bool
    is_generative_ai: bool
    has_ai_output_label: bool


@dataclass(frozen=True)
class KoreaAIDocument:
    """
    Document metadata submitted to the Korea AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    content_type : str
        Type of document: e.g. "REPORT", "AI_OUTPUT", "USER_DATA", "CONTRACT".
    contains_personal_info : bool
        True if the document contains personal information of individuals as
        defined by PIPA §2(1).
    risk_level : str
        Risk classification: "HIGH_IMPACT", "SIGNIFICANT", "LIMITED", "MINIMAL".
    requires_human_review : bool
        True if the document has been flagged as requiring human review
        by a prior evaluation stage.
    processing_timestamp : str
        ISO-8601 timestamp of when the document was submitted for processing.
    jurisdiction : str
        ISO alpha-2 country code where the document processing takes place.
    """

    document_id: str
    content_type: str
    contains_personal_info: bool
    risk_level: str
    requires_human_review: bool
    processing_timestamp: str
    jurisdiction: str


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single Korea AI governance filter evaluation."""

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
# Layer 1 — Korea AI Framework Act (January 23, 2024)
# ---------------------------------------------------------------------------


class KoreaAIFrameworkActFilter:
    """
    Layer 1: Korea Act on the Development of Artificial Intelligence and
    Establishment of Trust-Based AI Framework (AI Framework Act, enacted
    January 23, 2024).

    South Korea's AI Framework Act establishes a risk-based governance
    framework for AI systems deployed in Korea.  Two principal controls
    apply:

    (a) Prohibited practices (Article 10) — AI systems used for social
        credit scoring, subliminal manipulation of behaviour or decisions,
        and certain indiscriminate real-time biometric surveillance are
        absolutely prohibited regardless of consent or business justification;
    (b) High-impact AI transparency (Article 6) — operators of high-impact
        AI systems must clearly disclose AI involvement to users and obtain
        acknowledgment before the system makes or significantly contributes
        to automated decisions; systems that operate without this disclosure
        must be referred for human review;
    (c) Government impact assessment (Article 7) — government agencies
        deploying high-impact AI systems must conduct a mandatory AI impact
        assessment before deployment (enforced via Layer 3 sectoral filter
        for PUBLIC sector).

    References
    ----------
    Act on the Development of Artificial Intelligence and Establishment of
    Trust-Based AI Framework (Korea, January 23, 2024)
    Ministry of Science and ICT — AI Framework Act Implementation Guidelines
    """

    FILTER_NAME = "KOREA_AI_FRAMEWORK_ACT"

    def evaluate(
        self, context: KoreaAIContext, document: KoreaAIDocument
    ) -> FilterResult:
        # Article 10 — prohibited AI practices
        if context.involves_prohibited_practice:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Korea AI Framework Act Article 10: Prohibited AI practices — "
                    "social scoring systems, subliminal manipulation, and real-time "
                    "biometric surveillance are prohibited"
                ),
                regulation_citation=(
                    "Korea AI Framework Act (January 23, 2024), Article 10 — "
                    "Prohibited AI Practices: AI systems used for social credit "
                    "scoring, subliminal manipulation of human behaviour, and "
                    "indiscriminate real-time biometric surveillance in public "
                    "spaces are absolutely prohibited"
                ),
                requires_logging=True,
            )

        # Article 6 — high-impact AI without transparency disclosure
        if (
            context.ai_risk_level == KoreaAIRiskLevel.HIGH_IMPACT
            and not context.ai_transparency_disclosed
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Korea AI Framework Act Article 6: High-impact AI systems must "
                    "disclose AI involvement and obtain acknowledgment before "
                    "automated processing"
                ),
                regulation_citation=(
                    "Korea AI Framework Act (January 23, 2024), Article 6 — "
                    "Transparency Obligations for High-Impact AI: operators must "
                    "clearly disclose AI involvement and obtain acknowledgment "
                    "from users before the system makes or substantially influences "
                    "automated decisions"
                ),
                requires_logging=True,
            )

        # Article 6 — high-impact AI with disclosure: explicitly approved
        if context.ai_risk_level == KoreaAIRiskLevel.HIGH_IMPACT:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason=(
                    "Korea AI Framework Act Article 6: High-impact AI transparency "
                    "requirements satisfied — AI involvement disclosed and "
                    "acknowledgment obtained"
                ),
                regulation_citation=(
                    "Korea AI Framework Act (January 23, 2024), Article 6 — "
                    "Transparency obligations satisfied"
                ),
                requires_logging=False,
            )

        # Not high-impact — baseline AI Framework Act obligations satisfied
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Korea AI Framework Act — not high-impact AI classification; "
                "baseline obligations satisfied"
            ),
            regulation_citation=(
                "Korea AI Framework Act (January 23, 2024) — not high-impact AI "
                "classification; Articles 10 and 6 not triggered"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — PIPA 2020 (Personal Information Protection Act)
# ---------------------------------------------------------------------------


class KoreaPIPAFilter:
    """
    Layer 2: Korea Personal Information Protection Act (PIPA, Act No. 16930),
    as amended in 2020 and with significant amendments effective September 2023.

    PIPA governs the collection, use, disclosure, and processing of personal
    information in Korea.  Five principal controls apply to AI systems:

    (a) Lawful collection and use (Article 15) — personal information may be
        collected and used only with the data subject's consent or another
        recognised lawful basis: legal obligation, vital interest, or public
        task; processing without a valid basis is prohibited;
    (b) Sensitive information (Article 23) — explicit separate consent is
        required before processing sensitive personal information (ideology,
        religion, trade union membership, political opinion, health data,
        sexual orientation, genetic information, biometric data, criminal
        records);
    (c) Automated decision-making (Article 28-2) — data subjects have the
        right to contest and request human review of automated decisions;
        controllers must notify data subjects and provide a meaningful
        mechanism to contest;
    (d) Profiling (Article 28-3) — profiling of individuals based on
        personal information for automated decision purposes requires
        consent or another recognised basis;
    (e) Cross-border transfer (Article 39-3) — personal information may
        only be transferred to jurisdictions providing adequate protection
        or where a binding transfer mechanism (SCC or equivalent) is in
        place.

    References
    ----------
    Personal Information Protection Act (Korea, Act No. 16930, amended 2020)
    PIPA Amendment (effective September 15, 2023) — AI and automated
        decision-making provisions (Articles 28-2 and 28-3)
    Personal Information Protection Commission (PIPC) — Adequacy List
    """

    FILTER_NAME = "KOREA_PIPA"

    # Jurisdictions the PIPC has determined provide adequate protection
    # (indicative — production deployments must track official PIPC guidance)
    _ADEQUATE_JURISDICTIONS: frozenset = frozenset(
        {"KR", "EU", "UK", "CH", "JP", "NZ", "CA"}
    )

    # Processing purposes treated as lawful bases that do not require consent
    _LAWFUL_NON_CONSENT_PURPOSES: frozenset = frozenset(
        {"legal_obligation", "vital_interest", "public_task"}
    )

    def evaluate(
        self, context: KoreaAIContext, document: KoreaAIDocument
    ) -> FilterResult:
        # No personal information involved — PIPA does not apply
        if not context.involves_personal_info:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason="PIPA: No personal information involved — PIPA obligations not triggered",
                regulation_citation=(
                    "Personal Information Protection Act (Korea, Act No. 16930) — "
                    "no personal information processing; PIPA Article 15 not triggered"
                ),
                requires_logging=False,
            )

        # Article 15 — no consent and no recognised lawful basis
        if (
            not context.has_pipa_consent
            and context.processing_purpose not in self._LAWFUL_NON_CONSENT_PURPOSES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "PIPA Article 15: Consent or lawful basis required for personal "
                    "information processing — neither consent nor a recognised "
                    "lawful basis (legal_obligation, vital_interest, public_task) "
                    "has been established"
                ),
                regulation_citation=(
                    "Personal Information Protection Act (Korea), Article 15 — "
                    "Collection and Use of Personal Information: personal information "
                    "may only be processed with data subject consent or under a "
                    "recognised lawful basis"
                ),
                requires_logging=True,
            )

        # Article 23 — sensitive information without explicit consent
        if context.contains_sensitive_info and not context.has_sensitive_info_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "PIPA Article 23: Explicit consent required for sensitive personal "
                    "information (ideology, health data, biometrics, criminal records)"
                ),
                regulation_citation=(
                    "Personal Information Protection Act (Korea), Article 23 — "
                    "Processing of Sensitive Information: ideology, religion, trade "
                    "union membership, political opinions, health data, sexual "
                    "orientation, genetic information, biometric data, and criminal "
                    "records require explicit separate consent"
                ),
                requires_logging=True,
            )

        # Article 28-2 — automated decision without right to contest
        if context.is_automated_decision and not context.right_to_contest_provided:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "PIPA Article 28-2: Automated decision-making must provide right "
                    "to contest and request human review — mechanism not provided"
                ),
                regulation_citation=(
                    "Personal Information Protection Act (Korea), Article 28-2 — "
                    "Right to Refuse or Request Explanation for Automated Decisions: "
                    "data subjects must be notified and provided with a meaningful "
                    "mechanism to contest automated decisions and request human review"
                ),
                requires_logging=True,
            )

        # Article 28-3 — profiling without consent
        if context.profiling_involved and not context.has_profiling_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "PIPA Article 28-3: Profiling based on personal information "
                    "requires consent — consent not obtained"
                ),
                regulation_citation=(
                    "Personal Information Protection Act (Korea), Article 28-3 — "
                    "Automated Profiling: profiling of individuals based on personal "
                    "information for automated decision purposes requires consent "
                    "or another recognised legal basis"
                ),
                requires_logging=True,
            )

        # Article 39-3 — cross-border transfer controls
        if context.cross_border_transfer:
            if (
                context.requester_jurisdiction not in self._ADEQUATE_JURISDICTIONS
                and not context.has_pipa_transfer_mechanism
            ):
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="DENIED",
                    reason=(
                        f"PIPA Article 39-3: Cross-border transfer without adequate "
                        f"safeguards or binding agreement — destination "
                        f"{context.requester_jurisdiction!r} is not on the adequacy "
                        f"list and no transfer mechanism (SCC or equivalent) is in place"
                    ),
                    regulation_citation=(
                        "Personal Information Protection Act (Korea), Article 39-3 — "
                        "Cross-Border Transfer of Personal Information: transfer to "
                        "non-adequate jurisdictions requires binding standard contractual "
                        "clauses or equivalent protective measures approved by the PIPC"
                    ),
                    requires_logging=True,
                )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with PIPA — all applicable obligations satisfied "
                "(Articles 15, 23, 28-2, 28-3, 39-3)"
            ),
            regulation_citation=(
                "Personal Information Protection Act (Korea, Act No. 16930), "
                "Article 15 — all applicable PIPA obligations satisfied"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Korea Sectoral AI Regulations
# ---------------------------------------------------------------------------


class KoreaSectoralAIFilter:
    """
    Layer 3: Korea Sectoral AI Regulations — financial, employment, healthcare,
    and public sector.

    Korean financial, employment, healthcare, and government regulators have
    issued sector-specific AI governance requirements.  Non-applicable sectors
    receive immediate approval.  Five principal sectoral controls apply:

    (a) Credit Information Act Article 20 (Financial Sector) — AI-based
        automated credit decisions must include explainability provisions and
        give the data subject the right to contest the decision; absence of
        explainability triggers a mandatory human review escalation;
    (b) Korea Employment Act (Employment Sector) — automated hiring decision
        systems used in employment screening must include a mandatory human
        review stage before any final employment decision; fully automated
        hiring without human review is non-compliant;
    (c) Korean Medical Devices Act — SaMD approval (Healthcare Sector) —
        AI-based clinical decision support software meeting the Software as a
        Medical Device (SaMD) definition requires MFDS approval before
        clinical deployment; unapproved medical AI constitutes a violation
        of the Medical Devices Act;
    (d) Korean Medical Act — physician oversight (Healthcare Sector) —
        even where MFDS SaMD approval has been obtained, AI-assisted medical
        decisions must operate under physician oversight;
    (e) Korea AI Framework Act Article 7 (Public Sector) — government agencies
        deploying high-impact AI systems must conduct a mandatory AI impact
        assessment before deployment.

    References
    ----------
    Credit Information Use and Protection Act (Korea), Article 20
    Korea Employment Act (근로기준법) — AI hiring provisions
    Korean Medical Devices Act (의료기기법) — SaMD (Software as a Medical Device)
    Korean Medical Act (의료법) — physician oversight requirements
    Korea AI Framework Act (January 23, 2024), Article 7
    """

    FILTER_NAME = "KOREA_SECTORAL_AI"

    def evaluate(
        self, context: KoreaAIContext, document: KoreaAIDocument
    ) -> FilterResult:
        # Financial sector — automated credit decision without explainability
        if (
            context.sector == KoreaSector.FINANCIAL
            and context.is_automated_credit_decision
            and not context.has_credit_explainability
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Credit Information Use and Protection Act Article 20: Automated "
                    "credit decisions require explainability and right to contest — "
                    "explainability not provided"
                ),
                regulation_citation=(
                    "Credit Information Use and Protection Act (Korea), Article 20 — "
                    "Automated credit scoring and lending eligibility decisions must "
                    "provide explainability provisions and give the data subject the "
                    "right to contest the automated decision"
                ),
                requires_logging=True,
            )

        # Employment sector — automated hiring without human review
        if (
            context.sector == KoreaSector.EMPLOYMENT
            and context.is_automated_hiring_decision
            and not context.has_hiring_human_review
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Korea Employment Act: Automated hiring decisions require human "
                    "review stage — no human review stage included"
                ),
                regulation_citation=(
                    "Korea Employment Act — AI Automated Hiring Provisions: automated "
                    "hiring decision systems used in employment screening must include "
                    "a mandatory human review stage before final employment decisions"
                ),
                requires_logging=True,
            )

        # Healthcare sector — medical AI without MFDS SaMD approval
        if (
            context.sector == KoreaSector.HEALTHCARE
            and context.is_medical_ai
            and not context.has_mfds_approval
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Korean Medical Devices Act: AI-based clinical decision support "
                    "requires MFDS SaMD approval — approval not obtained"
                ),
                regulation_citation=(
                    "Korean Medical Devices Act (의료기기법) — Software as a Medical "
                    "Device (SaMD): AI-based clinical decision support software "
                    "requires Ministry of Food and Drug Safety (MFDS) SaMD approval "
                    "before deployment in clinical settings"
                ),
                requires_logging=True,
            )

        # Healthcare sector — MFDS-approved medical AI without physician oversight
        if (
            context.sector == KoreaSector.HEALTHCARE
            and context.is_medical_ai
            and context.has_mfds_approval
            and not context.has_physician_oversight
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Korean Medical Act: AI-assisted medical decisions require "
                    "physician oversight — physician oversight not established"
                ),
                regulation_citation=(
                    "Korean Medical Act (의료법) — AI-Assisted Medical Decisions: "
                    "even where MFDS SaMD approval is obtained, AI-assisted medical "
                    "decisions must operate under physician oversight and cannot be "
                    "fully autonomous"
                ),
                requires_logging=True,
            )

        # Public sector — government high-impact AI requires impact assessment
        if (
            context.sector == KoreaSector.PUBLIC
            and context.ai_risk_level == KoreaAIRiskLevel.HIGH_IMPACT
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Korea AI Framework Act Article 7: Government high-impact AI "
                    "systems require mandatory impact assessment before deployment"
                ),
                regulation_citation=(
                    "Korea AI Framework Act (January 23, 2024), Article 7 — "
                    "Government AI Impact Assessment: government agencies deploying "
                    "high-impact AI systems must conduct a mandatory AI impact "
                    "assessment before deployment"
                ),
                requires_logging=True,
            )

        # No sectoral requirements triggered
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "No sectoral AI governance requirements triggered — all applicable "
                "sectoral obligations satisfied"
            ),
            regulation_citation=(
                "Credit Information Use and Protection Act Article 20; "
                "Korea Employment Act; Korean Medical Devices Act; "
                "Korean Medical Act; Korea AI Framework Act Article 7 — "
                "no applicable sectoral obligations triggered"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Korea Data Governance & AI Auditing
# ---------------------------------------------------------------------------


class KoreaDataGovernanceFilter:
    """
    Layer 4: Korea Data Governance and AI Auditing — PIPA data governance
    obligations and AI Framework Act documentation requirements.

    Two principal governance controls apply to significant and high-impact
    AI systems:

    (a) AI Framework Act documentation (Significant + High-Impact AI) —
        significant and high-impact AI systems must maintain documentation of
        AI use, system purpose, and audit records; undisclosed or
        undocumented use of such systems requires escalation for human review
        before deployment;
    (b) PIPA Article 28-2 — right to contest automated decisions — individuals
        subject to automated decisions that process personal information must
        be informed of the decision and provided with a meaningful mechanism
        to contest the decision or request human review; absence of this
        mechanism is a governance gap requiring remediation.

    References
    ----------
    Korea AI Framework Act (January 23, 2024) — documentation and auditing
    Personal Information Protection Act (Korea), Article 28-2
    Personal Information Protection Commission (PIPC) — Automated Decision
        Guidance (2023)
    """

    FILTER_NAME = "KOREA_DATA_GOVERNANCE"

    _REQUIRES_DOCUMENTATION: frozenset = frozenset(
        {KoreaAIRiskLevel.HIGH_IMPACT, KoreaAIRiskLevel.SIGNIFICANT}
    )

    def evaluate(
        self, context: KoreaAIContext, document: KoreaAIDocument
    ) -> FilterResult:
        # AI Framework Act — significant/high-impact AI without transparency disclosure
        if (
            context.ai_risk_level in self._REQUIRES_DOCUMENTATION
            and not context.ai_transparency_disclosed
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Korea AI Framework Act: Significant and high-impact AI systems "
                    "require documentation of AI use and audit records — "
                    "AI transparency not disclosed"
                ),
                regulation_citation=(
                    "Korea AI Framework Act (January 23, 2024) — Documentation and "
                    "Auditing: significant and high-impact AI systems must maintain "
                    "documentation of AI use, system purpose, audit records, and "
                    "impact assessments; undisclosed use requires human review"
                ),
                requires_logging=True,
            )

        # PIPA Article 28-2 — personal info + automated decision without contest mechanism
        if context.involves_personal_info and context.is_automated_decision:
            if not context.right_to_contest_provided:
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="REQUIRES_HUMAN_REVIEW",
                    reason=(
                        "PIPA Article 28-2: Individuals must be informed of and able "
                        "to contest automated decisions — right to contest not provided"
                    ),
                    regulation_citation=(
                        "Personal Information Protection Act (Korea), Article 28-2 — "
                        "Right to Refuse or Request Explanation for Automated "
                        "Decisions: individuals subject to automated decisions must "
                        "be informed and provided a meaningful mechanism to contest "
                        "or request human review"
                    ),
                    requires_logging=True,
                )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Korea data governance requirements — AI Framework Act "
                "documentation and PIPA data governance obligations satisfied"
            ),
            regulation_citation=(
                "Korea AI Framework Act (January 23, 2024) — documentation and "
                "auditing obligations satisfied; PIPA data governance requirements "
                "satisfied"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class KoreaAIGovernanceOrchestrator:
    """
    Four-layer South Korea AI governance orchestrator.

    Evaluation order:
        KoreaAIFrameworkActFilter  →  KoreaPIPAFilter  →
        KoreaSectoralAIFilter      →  KoreaDataGovernanceFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``FilterResult`` objects and passed
    to ``KoreaAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            KoreaAIFrameworkActFilter(),
            KoreaPIPAFilter(),
            KoreaSectoralAIFilter(),
            KoreaDataGovernanceFilter(),
        ]

    def evaluate(
        self, context: KoreaAIContext, document: KoreaAIDocument
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : KoreaAIContext
            The AI system processing context to evaluate.
        document : KoreaAIDocument
            The document being processed by the AI system.

        Returns
        -------
        list[FilterResult]
            One result per filter, in evaluation order.
        """
        return [f.evaluate(context, document) for f in self._filters]


# ---------------------------------------------------------------------------
# Aggregated governance report
# ---------------------------------------------------------------------------


@dataclass
class KoreaAIGovernanceReport:
    """
    Aggregated South Korea AI governance report across all four filters.

    Decision aggregation:
    - Any DENIED result                     → overall_decision is "DENIED"
    - No DENIED + any REQUIRES_HUMAN_REVIEW → "REQUIRES_HUMAN_REVIEW"
    - All APPROVED                          → "APPROVED"

    Attributes
    ----------
    context : KoreaAIContext
        The AI system context that was evaluated.
    document : KoreaAIDocument
        The document that was evaluated.
    filter_results : list[FilterResult]
        Per-filter results in evaluation order.
    """

    context: KoreaAIContext
    document: KoreaAIDocument
    filter_results: List[FilterResult]

    @property
    def overall_decision(self) -> str:
        """
        Aggregate decision across all filters.

        Returns "DENIED" if any filter denied; "REQUIRES_HUMAN_REVIEW" if any
        filter requires human review (but none denied); "APPROVED" otherwise.
        """
        if any(r.is_denied for r in self.filter_results):
            return "DENIED"
        if any(r.decision == "REQUIRES_HUMAN_REVIEW" for r in self.filter_results):
            return "REQUIRES_HUMAN_REVIEW"
        return "APPROVED"

    @property
    def is_compliant(self) -> bool:
        """
        True only if overall_decision is "APPROVED".

        Note: REQUIRES_HUMAN_REVIEW is not a denial but is not fully
        compliant without human review completion.
        """
        return self.overall_decision == "APPROVED"

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary across all four filters.

        Returns a multi-line string listing each filter name, its decision,
        and either the approval reason or the denial/review reason.
        """
        lines: List[str] = [
            f"Korea AI Governance Report — user_id={self.context.user_id}",
            (
                f"Sector: {self.context.sector.value}  |  "
                f"Risk Level: {self.context.ai_risk_level.value}  |  "
                f"Overall Decision: {self.overall_decision}"
            ),
            "",
        ]
        for result in self.filter_results:
            lines.append(f"  [{result.decision}]  {result.filter_name}")
            if result.reason:
                lines.append(f"    Reason: {result.reason}")
            if result.regulation_citation:
                lines.append(f"    Citation: {result.regulation_citation}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_minimal_general_base() -> tuple[KoreaAIContext, KoreaAIDocument]:
    """
    Base context: fully compliant MINIMAL-risk GENERAL sector system.
    Used as the baseline from which failing scenarios are derived.
    """
    context = KoreaAIContext(
        user_id="KR-AI-001",
        sector=KoreaSector.GENERAL,
        ai_risk_level=KoreaAIRiskLevel.MINIMAL,
        is_automated_decision=False,
        involves_personal_info=False,
        contains_sensitive_info=False,
        has_pipa_consent=True,
        has_sensitive_info_consent=True,
        processing_purpose="service_delivery",
        is_high_impact_ai=False,
        ai_transparency_disclosed=True,
        involves_prohibited_practice=False,
        is_automated_credit_decision=False,
        has_credit_explainability=True,
        is_automated_hiring_decision=False,
        has_hiring_human_review=True,
        is_medical_ai=False,
        has_mfds_approval=False,
        has_physician_oversight=False,
        cross_border_transfer=False,
        requester_jurisdiction="KR",
        has_pipa_transfer_mechanism=True,
        profiling_involved=False,
        has_profiling_consent=True,
        right_to_contest_provided=True,
        is_generative_ai=False,
        has_ai_output_label=True,
    )
    document = KoreaAIDocument(
        document_id="DOC-KR-001",
        content_type="REPORT",
        contains_personal_info=False,
        risk_level="MINIMAL",
        requires_human_review=False,
        processing_timestamp="2024-06-01T09:00:00+09:00",
        jurisdiction="KR",
    )
    return context, document


def _demonstrate_scenario(
    title: str,
    context: KoreaAIContext,
    document: KoreaAIDocument,
    orchestrator: KoreaAIGovernanceOrchestrator,
) -> None:
    results = orchestrator.evaluate(context, document)
    report = KoreaAIGovernanceReport(
        context=context,
        document=document,
        filter_results=results,
    )
    print(f"\n{'=' * 70}")
    print(f"Scenario: {title}")
    print("=" * 70)
    print(report.compliance_summary)


if __name__ == "__main__":
    orchestrator = KoreaAIGovernanceOrchestrator()
    base_ctx, base_doc = _compliant_minimal_general_base()

    # Scenario 1 — fully compliant baseline
    _demonstrate_scenario(
        "Fully Compliant MINIMAL-Risk GENERAL AI System",
        base_ctx,
        base_doc,
        orchestrator,
    )

    # Scenario 2 — prohibited practice (social scoring)
    ctx2 = KoreaAIContext(
        **{**base_ctx.__dict__, "involves_prohibited_practice": True}
    )
    _demonstrate_scenario(
        "Prohibited AI Practice — Social Scoring (Art. 10 Denial)",
        ctx2,
        base_doc,
        orchestrator,
    )

    # Scenario 3 — high-impact AI without transparency disclosure
    ctx3 = KoreaAIContext(
        **{
            **base_ctx.__dict__,
            "ai_risk_level": KoreaAIRiskLevel.HIGH_IMPACT,
            "ai_transparency_disclosed": False,
        }
    )
    _demonstrate_scenario(
        "High-Impact AI Without Transparency Disclosure (Art. 6 Review)",
        ctx3,
        base_doc,
        orchestrator,
    )

    # Scenario 4 — personal info without PIPA consent
    ctx4 = KoreaAIContext(
        **{
            **base_ctx.__dict__,
            "involves_personal_info": True,
            "has_pipa_consent": False,
            "processing_purpose": "marketing",
        }
    )
    _demonstrate_scenario(
        "Personal Information Without PIPA Consent (Art. 15 Denial)",
        ctx4,
        base_doc,
        orchestrator,
    )

    # Scenario 5 — healthcare medical AI without MFDS approval
    ctx5 = KoreaAIContext(
        **{
            **base_ctx.__dict__,
            "sector": KoreaSector.HEALTHCARE,
            "is_medical_ai": True,
            "has_mfds_approval": False,
        }
    )
    _demonstrate_scenario(
        "Healthcare Medical AI Without MFDS Approval (SaMD Denial)",
        ctx5,
        base_doc,
        orchestrator,
    )

    # Scenario 6 — financial automated credit decision without explainability
    ctx6 = KoreaAIContext(
        **{
            **base_ctx.__dict__,
            "sector": KoreaSector.FINANCIAL,
            "is_automated_credit_decision": True,
            "has_credit_explainability": False,
        }
    )
    _demonstrate_scenario(
        "Financial Credit AI Without Explainability (Credit Act Art. 20)",
        ctx6,
        base_doc,
        orchestrator,
    )

    # Scenario 7 — cross-border transfer to non-adequate jurisdiction without SCC
    ctx7 = KoreaAIContext(
        **{
            **base_ctx.__dict__,
            "involves_personal_info": True,
            "has_pipa_consent": True,
            "cross_border_transfer": True,
            "requester_jurisdiction": "BR",
            "has_pipa_transfer_mechanism": False,
        }
    )
    _demonstrate_scenario(
        "Cross-Border Transfer Without Adequate Safeguards (PIPA Art. 39-3)",
        ctx7,
        base_doc,
        orchestrator,
    )
