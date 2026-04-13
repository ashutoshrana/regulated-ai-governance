"""
23_india_ai_governance.py — Four-layer AI governance framework for AI systems
subject to Indian law, covering the overlapping national and sector-level
obligations that apply to AI-driven data processing in India.

Demonstrates a multi-layer governance orchestrator where four Indian
regulatory frameworks each impose independent requirements on AI systems
deployed in India:

    Layer 1  — DPDP Act (Digital Personal Data Protection Act, 2023):
               India's Digital Personal Data Protection Act 2023 (DPDP Act,
               No. 22 of 2023) is the first comprehensive data protection
               statute in India, receiving Presidential assent on August 11,
               2023. The Act establishes obligations for Data Fiduciaries
               (entities processing personal data) and rights for Data
               Principals (individuals whose data is processed):

               §4 — Lawful Processing: personal data may be processed only
                   for a lawful purpose after providing notice to the data
                   principal, based on consent OR for "legitimate uses"
                   (e.g., voluntarily shared data, safety/emergency, state
                   functions). AI systems processing personal data must
                   operate under a recognised legal basis;
               §6 — Consent: where consent is the legal basis, it must be
                   free, specific, informed, unconditional, and unambiguous;
                   bundled or coerced consent is invalid;
               §9 — Children's Data: processing personal data of children
                   (age < 18) requires verifiable parental consent; tracking,
                   behavioural monitoring, or targeted advertising directed at
                   children is absolutely prohibited;
               §12 — Right of Access: data principal has the right to obtain
                   information about the processing of their personal data;
                   access requests must be fulfilled;
               §16 — Cross-Border Transfer: the Central Government may
                   restrict transfer of personal data to certain countries
                   or territories by notification; transfer to restricted
                   jurisdictions is prohibited.

    Layer 2  — MEITY AI Advisory (Ministry of Electronics & IT, 2024):
               India's Ministry of Electronics and Information Technology
               (MEITY) issued AI advisory notices beginning March 2024,
               imposing obligations on significant AI platforms operating
               in India. Key provisions:

               Notice 1 (Labelling) — Platforms deploying AI/ML that can
                   generate deepfakes or synthetic media must clearly label
                   all AI-generated content; unlabelled synthetic media
                   constitutes a compliance breach under the IT Rules 2021;
               Notice 2 (Elections) — AI systems must not generate content
                   that undermines the electoral process, violates applicable
                   Indian laws, or spreads misinformation; election-related AI
                   must implement specific content safeguards;
               Notice 3 (Generative AI Testing) — Generative AI deployed in
                   India must undergo testing for bias and hallucination before
                   deployment; medium- and high-risk generative AI without
                   documented testing must be referred for human review.

    Layer 3  — IT Act 2000 + IT Rules 2021 (Information Technology Act):
               India's Information Technology Act 2000 and the associated
               Information Technology (Reasonable Security Practices and
               Procedures and Sensitive Personal Data or Information) Rules
               2011, as updated by the IT (Intermediary Guidelines and
               Digital Media Ethics Code) Rules 2021:

               §43A (IT Act) — Security Practices: body corporates handling
                   sensitive personal data or information (SPDI) must
                   implement and maintain reasonable security practices and
                   procedures commensurate with the sensitivity of the data;
               Rule 5 (IT Rules 2011) — Written Consent: before collecting
                   sensitive personal data, the body corporate must obtain
                   written consent (electronic consent acceptable) from the
                   provider of the information;
               Rule 6 (IT Rules 2011) — Disclosure to Third Parties: SPDI
                   must not be disclosed to a third party without the provider's
                   prior written consent, except where required by law.

    Layer 4  — India Sectoral AI Requirements:
               Sector-specific AI obligations issued by Indian financial,
               insurance, and health regulators:

               RBI AI Guidance (2024) — Reserve Bank of India guidance
                   requires that AI/ML models used in banking and credit
                   decisions (including credit scoring, fraud detection, and
                   lending) must have a model risk management framework
                   covering validation, monitoring, and governance;
               IRDAI Guidelines — Insurance Regulatory and Development
                   Authority of India requires human oversight for AI-driven
                   underwriting decisions; fully automated underwriting without
                   human review availability is non-compliant;
               MoHFW / CDSCO Guidance — AI clinical decision support software
                   that meets the definition of Software as a Medical Device
                   (SaMD) requires approval from the Central Drugs Standard
                   Control Organisation (CDSCO) before deployment in clinical
                   settings; AI clinical tools operating without CDSCO SaMD
                   approval are non-compliant.

No external dependencies required.

Run:
    python examples/23_india_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class IndiaAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under India's emerging AI governance
    framework and the MEITY AI Advisory (2024).

    HIGH   — Significant potential to affect individual rights, safety, or
             welfare; impacts high-stakes decisions in credit, healthcare,
             elections, or public administration.
    MEDIUM — Meaningful but bounded risk; includes generative AI with moderate
             impact potential and automated decision systems in regulated sectors.
    LOW    — Limited potential for harm; minimal additional oversight
             requirements beyond baseline DPDP obligations.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IndiaAIDecision(str, Enum):
    """Final governance decision for an India AI system evaluation."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    REDACTED = "REDACTED"


class IndiaSector(str, Enum):
    """
    Deployment sector for the AI system.

    BANKING      — Banking or credit institution regulated by the Reserve Bank
                   of India (RBI); AI Guidance 2024 applies.
    INSURANCE    — Insurance entity regulated by the Insurance Regulatory and
                   Development Authority of India (IRDAI).
    HEALTHCARE   — Healthcare provider, hospital, or digital health platform;
                   CDSCO SaMD guidance applies for clinical AI.
    EDUCATION    — Educational institution or EdTech platform.
    GOVERNMENT   — Government agency or public administration body.
    TELECOM      — Telecom operator or communications service provider.
    GENERAL      — General private-sector organisation; baseline DPDP and
                   MEITY/IT Act obligations apply.
    """

    BANKING = "banking"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    GOVERNMENT = "government"
    TELECOM = "telecom"
    GENERAL = "general"


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndiaAIContext:
    """
    Governance review context for an India AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    sector : IndiaSector
        Deployment sector; controls which sectoral filter rules apply in
        Layer 4.
    ai_risk_level : IndiaAIRiskLevel
        Risk classification under India's AI governance framework and the
        MEITY AI Advisory (2024).

    — DPDP Act 2023 fields —

    involves_personal_data : bool
        True if the AI system collects, uses, or processes personal data as
        defined by the DPDP Act 2023 §2(t): any data about an identifiable
        individual.
    dpdp_legal_basis : str
        The legal basis for processing personal data under DPDP Act §4.
        Valid values: "consent", "legitimate_uses", "state_function", "none".
    has_dpdp_consent : bool
        True if valid consent under DPDP Act §6 has been obtained: free,
        specific, informed, unconditional, and unambiguous. Required when
        dpdp_legal_basis == "consent".
    involves_childrens_data : bool
        True if the AI system processes personal data of children (age < 18)
        within the meaning of DPDP Act §9.
    has_parental_consent : bool
        True if verifiable parental consent has been obtained for processing
        children's personal data (required by DPDP Act §9).
    is_data_principal_access_request : bool
        True if the request is a data principal exercising the right of access
        to their personal data under DPDP Act §12.
    involves_cross_border_transfer : bool
        True if personal data is transferred to a recipient outside India,
        triggering DPDP Act §16 cross-border transfer controls.
    destination_country : str
        ISO alpha-2 country code of the destination for cross-border transfer.
        Used to check against the Central Government restricted country list
        under DPDP Act §16.

    — MEITY AI Advisory 2024 fields —

    can_generate_synthetic_media : bool
        True if the AI system can produce deepfakes, synthetic media, or other
        AI-generated audio/video/image content (MEITY Notice 1).
    has_ai_generated_label : bool
        True if all AI-generated content is clearly labelled as AI-generated
        as required by MEITY Advisory Notice 1.
    is_election_related_ai : bool
        True if the AI system relates to electoral processes, voter targeting,
        political content generation, or election-period deployment
        (MEITY Notice 2).
    has_election_content_safeguards : bool
        True if the system implements content safeguards to prevent generation
        of election-subverting or misinformation content (MEITY Notice 2).
    is_generative_ai : bool
        True if the AI system is a generative AI model (MEITY Notice 3).
    has_bias_hallucination_testing : bool
        True if the generative AI has undergone documented bias and
        hallucination testing before deployment (MEITY Notice 3).

    — IT Act / IT Rules fields —

    is_body_corporate : bool
        True if the deploying entity is a body corporate as defined under the
        IT Act 2000 §43A.
    handles_sensitive_personal_data : bool
        True if the system handles Sensitive Personal Data or Information
        (SPDI) as defined in IT Rules 2011 Rule 3: passwords, financial
        information, health data, biometrics, sexuality, etc.
    has_reasonable_security_practices : bool
        True if the body corporate has implemented reasonable security
        practices commensurate with SPDI sensitivity (IT Act §43A).
    involves_sensitive_personal_data : bool
        True if the AI system collects SPDI (IT Rules 2011 Rule 3).
    has_written_consent : bool
        True if written (including electronic) consent has been obtained from
        the provider of SPDI before collection (IT Rules 2011 Rule 5(1)).
    involves_third_party_disclosure : bool
        True if SPDI is disclosed or shared with any third party.
    has_disclosure_consent : bool
        True if prior written consent for third-party SPDI disclosure has been
        obtained (IT Rules 2011 Rule 6).

    — Sectoral fields —

    is_credit_ai : bool
        True if the AI system is used for credit scoring, lending, or credit
        risk management in the banking sector.
    has_model_risk_management : bool
        True if a model risk management framework (validation, monitoring,
        governance) is in place for the AI model (RBI AI Guidance 2024).
    is_automated_underwriting : bool
        True if the AI system performs automated insurance underwriting
        decisions with no human review pathway.
    human_review_available : bool
        True if a human underwriter or reviewer can review and override
        AI-driven underwriting decisions (IRDAI Guidelines).
    is_clinical_decision_support : bool
        True if the AI system provides clinical decision support, diagnostic
        recommendations, or other software functionality that meets the
        CDSCO definition of Software as a Medical Device (SaMD).
    has_cdsco_approval : bool
        True if the clinical AI system has received CDSCO SaMD approval
        before deployment in clinical settings.
    """

    user_id: str
    sector: IndiaSector
    ai_risk_level: IndiaAIRiskLevel

    # DPDP Act 2023
    involves_personal_data: bool
    dpdp_legal_basis: str  # "consent", "legitimate_uses", "state_function", "none"
    has_dpdp_consent: bool
    involves_childrens_data: bool
    has_parental_consent: bool
    is_data_principal_access_request: bool
    involves_cross_border_transfer: bool
    destination_country: str  # ISO alpha-2

    # MEITY AI Advisory 2024
    can_generate_synthetic_media: bool
    has_ai_generated_label: bool
    is_election_related_ai: bool
    has_election_content_safeguards: bool
    is_generative_ai: bool
    has_bias_hallucination_testing: bool

    # IT Act 2000 / IT Rules 2021
    is_body_corporate: bool
    handles_sensitive_personal_data: bool
    has_reasonable_security_practices: bool
    involves_sensitive_personal_data: bool
    has_written_consent: bool
    involves_third_party_disclosure: bool
    has_disclosure_consent: bool

    # Sectoral
    is_credit_ai: bool
    has_model_risk_management: bool
    is_automated_underwriting: bool
    human_review_available: bool
    is_clinical_decision_support: bool
    has_cdsco_approval: bool


@dataclass(frozen=True)
class IndiaAIDocument:
    """
    Document metadata submitted to the India AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    document_type : str
        Type of document: e.g. "REPORT", "AI_OUTPUT", "USER_DATA", "CONTRACT".
    contains_personal_data : bool
        True if the document contains personal data of individuals as defined
        by the DPDP Act 2023.
    contains_sensitive_data : bool
        True if the document contains Sensitive Personal Data or Information
        (SPDI) as defined by IT Rules 2011 Rule 3.
    is_ai_output : bool
        True if the document is output generated by an AI system (triggers
        MEITY labelling obligations if synthetic media is involved).
    classification : str
        Sensitivity classification: "PERSONAL_DATA", "SENSITIVE_DATA",
        "PUBLIC", or "AI_OUTPUT".
    data_subject_count : int
        Number of data subjects whose personal data is contained in the
        document (used for proportionality assessment).
    """

    document_id: str
    document_type: str
    contains_personal_data: bool
    contains_sensitive_data: bool
    is_ai_output: bool
    classification: str  # "PERSONAL_DATA", "SENSITIVE_DATA", "PUBLIC", "AI_OUTPUT"
    data_subject_count: int


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single India AI governance filter evaluation."""

    filter_name: str
    decision: IndiaAIDecision = IndiaAIDecision.APPROVED
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = False

    @property
    def is_denied(self) -> bool:
        """True if this filter produced a DENIED decision."""
        return self.decision == IndiaAIDecision.DENIED


# ---------------------------------------------------------------------------
# Layer 1 — DPDP Act 2023
# ---------------------------------------------------------------------------


class DPDPDataProtectionFilter:
    """
    Layer 1: Digital Personal Data Protection Act 2023 (DPDP Act,
    No. 22 of 2023), India.

    The DPDP Act is India's first comprehensive data protection statute,
    receiving Presidential assent on August 11, 2023. It establishes
    obligations on Data Fiduciaries (entities determining the purpose and
    means of processing personal data) and rights for Data Principals
    (individuals whose data is processed). This filter evaluates the five
    principal DPDP controls most material for AI systems:

    (a) Lawful processing basis (§4) — personal data may only be processed
        for a lawful purpose after providing notice to the data principal,
        based on consent, legitimate uses (state functions, voluntarily
        shared data, emergencies), or other Central Government–notified
        purposes; no other basis is valid;
    (b) Valid consent (§6) — where consent is the processing basis, it must
        be free, specific, informed, unconditional, and unambiguous; bundled
        or coerced consent is invalid;
    (c) Children's data (§9) — processing personal data of individuals below
        age 18 requires verifiable parental consent; tracking, behavioural
        monitoring, and targeted advertising directed at children are
        absolutely prohibited;
    (d) Data principal right of access (§12) — data principals may request
        information about the processing of their personal data; access
        requests must be fulfilled promptly;
    (e) Cross-border transfer restrictions (§16) — the Central Government
        may by notification restrict transfer of personal data to specified
        countries; transfers to restricted jurisdictions are prohibited.

    References
    ----------
    Digital Personal Data Protection Act 2023 (No. 22 of 2023)
    Ministry of Electronics and Information Technology — DPDP Rules (draft)
    """

    FILTER_NAME = "DPDP_DATA_PROTECTION"

    # Countries restricted by Central Government notification under §16
    # (illustrative set — production deployments must track official gazette)
    _RESTRICTED_COUNTRIES: frozenset = frozenset({"CN", "RU", "PK"})

    def evaluate(
        self, context: IndiaAIContext, document: IndiaAIDocument
    ) -> FilterResult:
        # §12 — data principal access request: immediately approve
        if context.is_data_principal_access_request:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.APPROVED,
                reason=(
                    "DPDP Act 2023 §12 — data principal right of access: "
                    "request must be fulfilled"
                ),
                regulation_citation=(
                    "Digital Personal Data Protection Act 2023, §12 — "
                    "Right of Data Principal to obtain information about "
                    "processing of personal data"
                ),
            )

        # §4 — personal data without a valid legal basis
        if context.involves_personal_data and context.dpdp_legal_basis not in {
            "consent",
            "legitimate_uses",
            "state_function",
        }:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "DPDP Act 2023 §4 — lawful purpose with notice required "
                    "for personal data processing; no valid legal basis provided"
                ),
                regulation_citation=(
                    "Digital Personal Data Protection Act 2023, §4 — "
                    "Grounds for Processing Personal Data: must be a lawful "
                    "purpose with notice to data principal OR based on consent, "
                    "legitimate uses, or state function"
                ),
                requires_logging=True,
            )

        # §6 — consent basis without valid consent
        if (
            context.involves_personal_data
            and context.dpdp_legal_basis == "consent"
            and not context.has_dpdp_consent
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "DPDP Act 2023 §6 — valid consent required (free, specific, "
                    "informed, unconditional, unambiguous) but not obtained"
                ),
                regulation_citation=(
                    "Digital Personal Data Protection Act 2023, §6 — "
                    "Consent: must be free, specific, informed, unconditional, "
                    "and unambiguous; bundled or coerced consent is invalid"
                ),
                requires_logging=True,
            )

        # §9 — children's personal data without parental consent
        if context.involves_childrens_data and not context.has_parental_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "DPDP Act 2023 §9 — parental consent required for processing "
                    "children's personal data (age < 18)"
                ),
                regulation_citation=(
                    "Digital Personal Data Protection Act 2023, §9 — "
                    "Processing of Personal Data of Children: verifiable parental "
                    "consent required; tracking and behavioural monitoring "
                    "of children prohibited"
                ),
                requires_logging=True,
            )

        # §16 — cross-border transfer to restricted country
        if (
            context.involves_cross_border_transfer
            and context.destination_country in self._RESTRICTED_COUNTRIES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    f"DPDP Act 2023 §16 — cross-border transfer to restricted "
                    f"jurisdiction ({context.destination_country}) is prohibited"
                ),
                regulation_citation=(
                    "Digital Personal Data Protection Act 2023, §16 — "
                    "Transfer of Personal Data Outside India: Central Government "
                    "may restrict transfer to specified countries by notification"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=IndiaAIDecision.APPROVED,
            reason=(
                "Compliant with Digital Personal Data Protection Act 2023 — "
                "all applicable obligations satisfied"
            ),
            regulation_citation=(
                "Digital Personal Data Protection Act 2023 (No. 22 of 2023) "
                "— §4, §6, §9, §12, §16 obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 2 — MEITY AI Advisory 2024
# ---------------------------------------------------------------------------


class MEITYAIAdvisoryFilter:
    """
    Layer 2: Ministry of Electronics and IT (MEITY) AI Advisory 2024.

    MEITY issued advisory notices beginning March 2024 (with subsequent
    updates) imposing obligations on significant AI platforms deployed in
    India. The advisory was issued under the Ministry's authority and the
    IT Act 2000 / IT Rules 2021 framework. Three key requirements apply:

    (a) AI-generated content labelling (Notice 1) — platforms deploying AI
        that can generate deepfakes or synthetic media must clearly label
        all AI-generated outputs; unlabelled synthetic media breaches the
        IT Rules 2021 and the advisory;
    (b) Election content safeguards (Notice 2) — AI systems must not
        generate content that undermines the electoral process, violates
        applicable Indian law, or spreads misinformation; election-related
        AI must implement specific technical and procedural safeguards;
    (c) Generative AI testing (Notice 3) — generative AI deployed in India
        must be tested for bias and hallucination before deployment; medium-
        and high-risk generative AI without documented testing results must
        be referred for human review before deployment.

    References
    ----------
    MEITY AI Advisory Notice, March 1, 2024 (F. No. 3(1)/2024-CERT-In)
    MEITY AI Advisory Update, March 15, 2024
    IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021
    """

    FILTER_NAME = "MEITY_AI_ADVISORY"

    def evaluate(
        self, context: IndiaAIContext, document: IndiaAIDocument
    ) -> FilterResult:
        # Notice 1 — synthetic media without AI-generated label
        if context.can_generate_synthetic_media and not context.has_ai_generated_label:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "MEITY AI Advisory March 2024 — AI-generated content must be "
                    "labelled; platform generating synthetic media without label "
                    "requires human review"
                ),
                regulation_citation=(
                    "MEITY AI Advisory Notice (March 2024) — Notice 1: "
                    "Platforms deploying AI that can generate deepfakes or "
                    "synthetic media must clearly label all AI-generated outputs"
                ),
                requires_logging=True,
            )

        # Notice 2 — election-related AI without safeguards
        if context.is_election_related_ai and not context.has_election_content_safeguards:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "MEITY AI Advisory — election-related AI requires content "
                    "safeguards to prevent electoral process subversion and "
                    "misinformation"
                ),
                regulation_citation=(
                    "MEITY AI Advisory Notice (March 2024) — Notice 2: "
                    "AI systems must not generate content undermining the electoral "
                    "process or spreading misinformation; content safeguards required "
                    "for election-related AI"
                ),
                requires_logging=True,
            )

        # Notice 3 — generative AI without bias/hallucination testing
        if (
            context.is_generative_ai
            and context.ai_risk_level in {IndiaAIRiskLevel.HIGH, IndiaAIRiskLevel.MEDIUM}
            and not context.has_bias_hallucination_testing
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "MEITY AI Advisory — generative AI requires bias/hallucination "
                    "testing before deployment; medium/high-risk system without "
                    "documented testing requires human review"
                ),
                regulation_citation=(
                    "MEITY AI Advisory Notice (March 2024) — Notice 3: "
                    "Generative AI deployed in India must undergo testing for bias "
                    "and hallucination before deployment"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=IndiaAIDecision.APPROVED,
            reason=(
                "Compliant with MEITY AI Advisory (March 2024) — all applicable "
                "notices satisfied"
            ),
            regulation_citation=(
                "MEITY AI Advisory Notice (March 2024) — Notices 1, 2, 3: "
                "all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 3 — IT Act 2000 + IT Rules 2021
# ---------------------------------------------------------------------------


class IndiaITActFilter:
    """
    Layer 3: Information Technology Act 2000 + IT (Reasonable Security
    Practices and Procedures and Sensitive Personal Data or Information)
    Rules 2011 (IT Rules 2011).

    The Information Technology Act 2000 (as amended by the Information
    Technology (Amendment) Act 2008) and the IT Rules 2011 together govern
    the handling of Sensitive Personal Data or Information (SPDI) by body
    corporates operating in India. Three principal controls apply to AI
    systems:

    (a) Reasonable security practices (IT Act §43A) — body corporates
        handling SPDI must implement and maintain reasonable security
        practices commensurate with the sensitivity of the data; failure
        to maintain reasonable practices triggers liability for wrongful
        loss or gain caused by negligence;
    (b) Written consent before collection (IT Rules 2011 Rule 5(1)) —
        before collecting SPDI, the body corporate must obtain written
        consent (electronic consent acceptable) from the provider of the
        information; the consent must specifically authorise the collection
        and use of the SPDI for the stated purpose;
    (c) Consent before third-party disclosure (IT Rules 2011 Rule 6) —
        SPDI must not be disclosed to any third party without the prior
        written consent of the provider, except as required by law or for
        lawful purposes previously consented to.

    SPDI under IT Rules 2011 Rule 3 includes: passwords, financial
    information (bank accounts, credit/debit card details), physical,
    physiological and mental health conditions, sexual orientation,
    medical records, biometric information, and any other information
    received in confidence.

    References
    ----------
    Information Technology Act, 2000 (Act No. 21 of 2000), §43A
    IT (Reasonable Security Practices and Procedures and Sensitive
        Personal Data or Information) Rules, 2011
    """

    FILTER_NAME = "INDIA_IT_ACT"

    def evaluate(
        self, context: IndiaAIContext, document: IndiaAIDocument
    ) -> FilterResult:
        # §43A — body corporate handling SPDI without reasonable security practices
        if (
            context.is_body_corporate
            and context.handles_sensitive_personal_data
            and not context.has_reasonable_security_practices
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "IT Act 2000 §43A — reasonable security practices required "
                    "for body corporates handling sensitive personal data; "
                    "security practices not implemented"
                ),
                regulation_citation=(
                    "Information Technology Act 2000, §43A — Compensation for "
                    "failure to protect data: body corporates must implement "
                    "reasonable security practices for sensitive personal data"
                ),
                requires_logging=True,
            )

        # Rule 5(1) — collecting SPDI without written consent
        if context.involves_sensitive_personal_data and not context.has_written_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "IT Rules 2021 Rule 5(1) — written consent required before "
                    "collecting sensitive personal data; consent not obtained"
                ),
                regulation_citation=(
                    "IT (Reasonable Security Practices) Rules 2011, Rule 5(1) — "
                    "Collection of Information: written (including electronic) "
                    "consent from the provider required before collecting SPDI"
                ),
                requires_logging=True,
            )

        # Rule 6 — disclosing SPDI to third parties without consent
        if (
            context.involves_third_party_disclosure
            and context.involves_sensitive_personal_data
            and not context.has_disclosure_consent
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "IT Rules 2021 Rule 6 — prior consent required for "
                    "sensitive personal data disclosure to third parties"
                ),
                regulation_citation=(
                    "IT (Reasonable Security Practices) Rules 2011, Rule 6 — "
                    "Disclosure of Information: SPDI must not be disclosed to "
                    "third parties without the provider's prior written consent, "
                    "except as required by law"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=IndiaAIDecision.APPROVED,
            reason=(
                "Compliant with IT Act 2000 and IT Rules 2011 — all applicable "
                "obligations satisfied"
            ),
            regulation_citation=(
                "Information Technology Act 2000 §43A; IT Rules 2011 "
                "Rules 5 and 6 — all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 4 — India Sectoral AI Requirements
# ---------------------------------------------------------------------------


class IndiaSectoralFilter:
    """
    Layer 4: India Sectoral AI Requirements — RBI, IRDAI, CDSCO.

    Indian financial, insurance, and healthcare regulators have issued
    sector-specific AI governance guidance. Non-applicable sectors receive
    immediate approval. Three principal sectoral controls apply:

    (a) RBI AI Guidance 2024 (Banking) — AI/ML models used in banking and
        credit decisions must operate within a model risk management (MRM)
        framework covering model development, independent validation, ongoing
        monitoring, and governance oversight; absence of a MRM framework for
        credit AI is a supervisory concern;
    (b) IRDAI Guidelines (Insurance) — AI-driven underwriting decisions must
        retain a human oversight pathway; fully automated underwriting without
        the availability of human review is non-compliant with IRDAI guidance
        on fair and transparent insurance practices;
    (c) CDSCO SaMD Guidance (Healthcare) — AI clinical decision support
        software meeting the definition of Software as a Medical Device (SaMD)
        under CDSCO guidance requires regulatory approval before deployment in
        clinical settings; unapproved SaMD AI deployed in clinical practice
        constitutes a violation of the Medical Devices Rules 2017.

    References
    ----------
    RBI — Draft Framework on Model Risk Management (2024)
    IRDAI — Guidelines on Use of AI/ML by Insurers (2024)
    CDSCO — Guidance Document on Software as Medical Device (SaMD) (2022)
    Medical Devices Rules 2017 (India)
    """

    FILTER_NAME = "INDIA_SECTORAL"

    def evaluate(
        self, context: IndiaAIContext, document: IndiaAIDocument
    ) -> FilterResult:
        # Banking — credit AI without model risk management framework
        if (
            context.sector == IndiaSector.BANKING
            and context.is_credit_ai
            and not context.has_model_risk_management
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "RBI AI Guidance 2024 — model risk management required for "
                    "banking credit AI; framework not implemented"
                ),
                regulation_citation=(
                    "Reserve Bank of India — Draft Framework on Model Risk "
                    "Management (2024): AI/ML models used in banking credit "
                    "decisions must have model risk management covering "
                    "validation, monitoring, and governance"
                ),
                requires_logging=True,
            )

        # Insurance — automated underwriting without human review availability
        if (
            context.sector == IndiaSector.INSURANCE
            and context.is_automated_underwriting
            and not context.human_review_available
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "IRDAI Guidelines — human oversight required for AI-driven "
                    "underwriting decisions; human review not available"
                ),
                regulation_citation=(
                    "Insurance Regulatory and Development Authority of India — "
                    "Guidelines on Use of AI/ML by Insurers (2024): "
                    "AI-driven underwriting decisions must have human oversight; "
                    "fully automated underwriting is non-compliant"
                ),
                requires_logging=True,
            )

        # Healthcare — clinical decision support AI without CDSCO approval
        if (
            context.sector == IndiaSector.HEALTHCARE
            and context.is_clinical_decision_support
            and not context.has_cdsco_approval
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=IndiaAIDecision.DENIED,
                reason=(
                    "CDSCO Guidance — clinical decision support AI requires "
                    "CDSCO SaMD approval before clinical deployment; "
                    "approval not obtained"
                ),
                regulation_citation=(
                    "CDSCO Guidance Document on Software as Medical Device "
                    "(SaMD) (2022); Medical Devices Rules 2017 (India): "
                    "clinical decision support AI meeting SaMD definition "
                    "requires CDSCO approval before deployment"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=IndiaAIDecision.APPROVED,
            reason=(
                "Compliant with India sectoral AI requirements — all applicable "
                "sector obligations satisfied"
            ),
            regulation_citation=(
                "RBI AI Guidance 2024; IRDAI AI/ML Guidelines 2024; "
                "CDSCO SaMD Guidance 2022 — all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class IndiaAIGovernanceOrchestrator:
    """
    Four-layer India AI governance orchestrator.

    Evaluation order:
        DPDPDataProtectionFilter  →  MEITYAIAdvisoryFilter  →
        IndiaITActFilter          →  IndiaSectoralFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``FilterResult`` objects and passed
    to ``IndiaAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            DPDPDataProtectionFilter(),
            MEITYAIAdvisoryFilter(),
            IndiaITActFilter(),
            IndiaSectoralFilter(),
        ]

    def evaluate(
        self, context: IndiaAIContext, document: IndiaAIDocument
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : IndiaAIContext
            The AI system processing context to evaluate.
        document : IndiaAIDocument
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
class IndiaAIGovernanceReport:
    """
    Aggregated India AI governance report across all four filters.

    Decision aggregation:
    - Any DENIED result                     → overall_decision is DENIED
    - No DENIED + any REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_REVIEW
    - All APPROVED                          → APPROVED

    Attributes
    ----------
    context : IndiaAIContext
        The AI system context that was evaluated.
    document : IndiaAIDocument
        The document that was evaluated.
    filter_results : list[FilterResult]
        Per-filter results in evaluation order.
    """

    context: IndiaAIContext
    document: IndiaAIDocument
    filter_results: List[FilterResult]

    @property
    def overall_decision(self) -> IndiaAIDecision:
        """
        Aggregate decision across all filters.

        Returns DENIED if any filter denied; REQUIRES_HUMAN_REVIEW if any
        filter requires human review (but none denied); APPROVED otherwise.
        """
        if any(r.is_denied for r in self.filter_results):
            return IndiaAIDecision.DENIED
        if any(
            r.decision == IndiaAIDecision.REQUIRES_HUMAN_REVIEW
            for r in self.filter_results
        ):
            return IndiaAIDecision.REQUIRES_HUMAN_REVIEW
        return IndiaAIDecision.APPROVED

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
            f"India AI Governance Report — user_id={self.context.user_id}",
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


def _compliant_low_risk_general_base() -> tuple[IndiaAIContext, IndiaAIDocument]:
    """
    Base context: fully compliant LOW risk GENERAL sector system.
    Used as the baseline from which failing scenarios are derived.
    """
    context = IndiaAIContext(
        user_id="IN-AI-001",
        sector=IndiaSector.GENERAL,
        ai_risk_level=IndiaAIRiskLevel.LOW,
        # DPDP
        involves_personal_data=False,
        dpdp_legal_basis="legitimate_uses",
        has_dpdp_consent=True,
        involves_childrens_data=False,
        has_parental_consent=False,
        is_data_principal_access_request=False,
        involves_cross_border_transfer=False,
        destination_country="US",
        # MEITY
        can_generate_synthetic_media=False,
        has_ai_generated_label=True,
        is_election_related_ai=False,
        has_election_content_safeguards=True,
        is_generative_ai=False,
        has_bias_hallucination_testing=True,
        # IT Act
        is_body_corporate=True,
        handles_sensitive_personal_data=False,
        has_reasonable_security_practices=True,
        involves_sensitive_personal_data=False,
        has_written_consent=True,
        involves_third_party_disclosure=False,
        has_disclosure_consent=True,
        # Sectoral
        is_credit_ai=False,
        has_model_risk_management=True,
        is_automated_underwriting=False,
        human_review_available=True,
        is_clinical_decision_support=False,
        has_cdsco_approval=False,
    )
    document = IndiaAIDocument(
        document_id="DOC-001",
        document_type="REPORT",
        contains_personal_data=False,
        contains_sensitive_data=False,
        is_ai_output=False,
        classification="PUBLIC",
        data_subject_count=0,
    )
    return context, document


def _demonstrate_scenario(
    title: str,
    context: IndiaAIContext,
    document: IndiaAIDocument,
    orchestrator: IndiaAIGovernanceOrchestrator,
) -> None:
    results = orchestrator.evaluate(context, document)
    report = IndiaAIGovernanceReport(
        context=context,
        document=document,
        filter_results=results,
    )
    print(f"\n{'=' * 70}")
    print(f"Scenario: {title}")
    print("=" * 70)
    print(report.compliance_summary)


if __name__ == "__main__":
    orchestrator = IndiaAIGovernanceOrchestrator()
    base_ctx, base_doc = _compliant_low_risk_general_base()

    # Scenario 1 — fully compliant baseline
    _demonstrate_scenario(
        "Fully Compliant LOW-Risk GENERAL AI System",
        base_ctx,
        base_doc,
        orchestrator,
    )

    # Scenario 2 — personal data without valid legal basis (DPDP §4)
    ctx2 = IndiaAIContext(
        **{
            **base_ctx.__dict__,
            "involves_personal_data": True,
            "dpdp_legal_basis": "none",
        }
    )
    _demonstrate_scenario(
        "Personal Data Without Valid Legal Basis (DPDP §4 Denial)",
        ctx2,
        base_doc,
        orchestrator,
    )

    # Scenario 3 — data principal access request (immediately approved)
    ctx3 = IndiaAIContext(
        **{**base_ctx.__dict__, "is_data_principal_access_request": True}
    )
    _demonstrate_scenario(
        "Data Principal Access Request (DPDP §12 Immediate Approval)",
        ctx3,
        base_doc,
        orchestrator,
    )

    # Scenario 4 — generative AI without bias testing (MEITY Notice 3)
    ctx4 = IndiaAIContext(
        **{
            **base_ctx.__dict__,
            "is_generative_ai": True,
            "ai_risk_level": IndiaAIRiskLevel.HIGH,
            "has_bias_hallucination_testing": False,
        }
    )
    _demonstrate_scenario(
        "Generative AI Without Bias/Hallucination Testing (MEITY Notice 3)",
        ctx4,
        base_doc,
        orchestrator,
    )

    # Scenario 5 — healthcare clinical AI without CDSCO approval
    ctx5 = IndiaAIContext(
        **{
            **base_ctx.__dict__,
            "sector": IndiaSector.HEALTHCARE,
            "is_clinical_decision_support": True,
            "has_cdsco_approval": False,
        }
    )
    _demonstrate_scenario(
        "Healthcare Clinical AI Without CDSCO SaMD Approval (Sectoral Denial)",
        ctx5,
        base_doc,
        orchestrator,
    )

    # Scenario 6 — banking credit AI without model risk management
    ctx6 = IndiaAIContext(
        **{
            **base_ctx.__dict__,
            "sector": IndiaSector.BANKING,
            "is_credit_ai": True,
            "has_model_risk_management": False,
        }
    )
    _demonstrate_scenario(
        "Banking Credit AI Without Model Risk Management (RBI Guidance)",
        ctx6,
        base_doc,
        orchestrator,
    )
