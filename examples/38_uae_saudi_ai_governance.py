"""
38_uae_saudi_ai_governance.py — UAE & Saudi Arabia AI Governance Framework

Implements governance filters for the United Arab Emirates and Kingdom of
Saudi Arabia comprehensive AI regulatory ecosystem covering the UAE Personal
Data Protection Law (Federal Decree-Law No. 45 of 2021), the UAE AI Strategy
2031 with ADGM and DIFC AI Guidance, the Saudi Arabia Personal Data
Protection Law (Royal Decree M/19) with NDMO AI Governance, and GCC
cross-border data and AI controls.

Demonstrates a multi-layer governance framework where four independent
filters enforce distinct requirements of the UAE/KSA regulatory landscape:

    Layer 1  — UAE PDPL data protection (UAEPDPLFilter):

               UAE PDPL Art. 6 Lawful Basis — personal data processing
                   without consent or legitimate basis is denied;
               UAE PDPL Art. 9 Sensitive Data — health/financial/biometric/
                   religious data without explicit consent is denied;
               UAE PDPL Art. 22 Cross-Border Transfer — transfer to non-
                   adequate country without Data Transfer Agreement is denied;
               UAE PDPL Art. 13 Automated Decision-Making — automated
                   decisions without human review mechanism triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 2  — UAE AI Strategy + ADGM/DIFC (UAEAIRegFilter):

               UAE AI Strategy 2031 §4 — high-risk AI without UAE AI Office
                   impact assessment is denied;
               DFSA RPP Module — financial AI in DIFC without DFSA AI
                   Guidance compliance is denied;
               FSRA AI Risk Management Framework — financial AI in ADGM
                   without FSRA AI Risk Management Framework compliance is
                   denied;
               UAE AI Ethics Principles — GenAI application without
                   transparency requirement triggers REQUIRES_HUMAN_REVIEW.

    Layer 3  — Saudi PDPL + NDMO AI governance (SaudiNDMOFilter):

               Saudi PDPL Art. 5 Lawful Basis — processing without consent
                   or legal obligation is denied;
               Saudi PDPL Art. 23 Sensitive Data — health/genetic/biometric/
                   financial/criminal without explicit consent is denied;
               Saudi PDPL Art. 29 Cross-Border Transfer — transfer without
                   SDAIA authorization is denied;
               NDMO Data Governance Framework — AI system without NDMO
                   compliance triggers REQUIRES_HUMAN_REVIEW.

    Layer 4  — GCC cross-border data and AI controls (GCCCrossBorderFilter):

               GCC adequacy framework — personal data to non-GCC country
                   without UAE/Saudi adequacy decision is denied;
               FATF High-Risk jurisdictions — financial AI data to KP/IR/MM
                   is denied;
               SDAIA export approval — Saudi citizen AI training data
                   exported without SDAIA approval is denied;
               GCC national cloud sovereignty — critical data outside UAE/KSA
                   national cloud triggers REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+--------------------------------------+-----------------------------------+
| Use case                             | Primary filters applied           |
+--------------------------------------+-----------------------------------+
| Banking credit-scoring AI (UAE)      | UAEAIRegFilter (DIFC/ADGM)        |
| Insurance underwriting AI (KSA)      | SaudiNDMOFilter (PDPL Art. 23)    |
| HR / hiring decision AI (GCC)        | UAEPDPLFilter (sensitive data)    |
| Generative AI consumer chatbot       | UAEAIRegFilter (GenAI transp.)    |
| Government e-governance AI (KSA)     | SaudiNDMOFilter (NDMO compliant)  |
| Healthcare predictive diagnostics    | SaudiNDMOFilter (PDPL Art. 23)    |
| Cross-border fintech platform        | GCCCrossBorderFilter (FATF)       |
| Cross-border data analytics          | GCCCrossBorderFilter              |
+--------------------------------------+-----------------------------------+

No external dependencies required.

Run:
    python examples/38_uae_saudi_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """
    Result returned by each UAE/Saudi AI governance filter.

    Attributes
    ----------
    filter_name : str
        Identifier for the filter that produced this result.
    decision : str
        One of ``"PERMITTED"``, ``"DENIED"``, ``"REQUIRES_HUMAN_REVIEW"``.
    regulation : str
        Authoritative citation for the regulation that drove the decision.
    reason : str
        Human-readable description of the compliance finding.
    """

    filter_name: str
    decision: str = "PERMITTED"
    regulation: str = ""
    reason: str = ""

    @property
    def is_denied(self) -> bool:
        """``True`` only when ``decision == "DENIED"``."""
        return self.decision == "DENIED"


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# UAE PDPL Art. 22 — countries to which transfer of personal data requires
# a Data Transfer Agreement; these lack UAE adequacy recognition.
UAE_NON_ADEQUATE_COUNTRIES: frozenset[str] = frozenset({"CN", "RU", "KP", "IR", "BY", "SY"})

# Saudi PDPL Art. 29 — countries recognised as adequate by SDAIA or having
# bilateral data-protection instruments with the Kingdom.
SAUDI_ADEQUATE_COUNTRIES: frozenset[str] = frozenset(
    {
        "AE",
        "SA",
        "BH",
        "KW",
        "OM",
        "QA",
        "US",
        "UK",
        "EU_MEMBER",
    }
)

# GCC cross-border framework — jurisdictions with adequate data-protection
# standards recognised by UAE and/or Saudi Arabia.
GCC_ADEQUATE_COUNTRIES: frozenset[str] = frozenset(
    {
        "AE",
        "SA",
        "BH",
        "KW",
        "OM",
        "QA",
        "US",
        "UK",
        "DE",
        "FR",
        "JP",
        "AU",
        "CA",
    }
)

# FATF High-Risk and Non-Cooperative Jurisdictions (current as of 2026)
# subject to enhanced due diligence; financial AI data flows are blocked.
FATF_HIGH_RISK: frozenset[str] = frozenset({"KP", "IR", "MM"})

# GCC national cloud regions approved for sovereign / critical data hosting.
GCC_NATIONAL_CLOUDS: frozenset[str] = frozenset(
    {
        "uae_gov_cloud",
        "ksa_gov_cloud",
        "aws_uae",
        "gcp_doha",
        "azure_uae_north",
        "azure_ksa",
    }
)

# UAE PDPL Art. 9 — sensitive personal data categories requiring explicit
# consent before processing.
_UAE_SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {
        "health",
        "financial",
        "biometric",
        "religious",
    }
)

# Saudi PDPL Art. 23 — sensitive personal data categories requiring explicit
# consent before processing.
_SAUDI_SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {
        "health",
        "genetic",
        "biometric",
        "financial",
        "criminal",
    }
)


# ---------------------------------------------------------------------------
# Layer 1 — UAE PDPL data protection (UAEPDPLFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UAEPDPLFilter:
    """
    Layer 1: UAE Personal Data Protection Law
    (Federal Decree-Law No. 45 of 2021, as amended by Federal Decree-Law
    No. 20 of 2023).

    The UAE PDPL is the UAE's first comprehensive federal data-protection
    statute, establishing obligations for data controllers and processors
    operating in the UAE mainland (excluding DIFC and ADGM which maintain
    separate frameworks).  Four principal controls apply:

    (a) Art. 6 Lawful Basis — personal data must be processed only with
        explicit consent or a recognised legitimate basis (contractual
        necessity, legal obligation, vital interest, public task, or
        legitimate interest balancing test); absence of either results in
        denial;
    (b) Art. 9 Sensitive Data — health, financial, biometric, and data
        revealing religious beliefs require explicit written consent before
        processing; absence results in denial;
    (c) Art. 22 Cross-Border Transfer — transfer to a country not recognised
        as adequate by the UAE Data Office and without a binding Data
        Transfer Agreement (DTA) results in denial;
    (d) Art. 13 Automated Decision-Making — automated decisions producing
        legal or similarly significant effects on individuals require a human
        review mechanism; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    UAE Federal Decree-Law No. 45 of 2021 on the Protection of Personal Data
        Art. 6 Conditions for Processing Personal Data
        Art. 9 Conditions for Processing Sensitive Personal Data
        Art. 13 Processing of Personal Data for Automated Decision Making
        Art. 22 Transfer or Disclosure of Personal Data to Overseas Parties
    UAE Federal Decree-Law No. 20 of 2023 (amendment)
    UAE Data Office — Data Protection Regulations 2022
    """

    FILTER_NAME: str = "UAE_PDPL_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 6 — processing without consent or legitimate basis
        if doc.get("personal_data_processing"):
            if not doc.get("uae_legal_basis"):
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="DENIED",
                    regulation=(
                        "UAE PDPL Art. 6 (Federal Decree-Law No. 45/2021) — "
                        "processing personal data requires consent or a recognised "
                        "legitimate basis"
                    ),
                    reason=(
                        "Personal data processing without consent or legitimate basis "
                        "violates UAE PDPL Art. 6 — a data controller may process "
                        "personal data only when the data subject has given explicit "
                        "consent, or when processing is necessary to fulfil a "
                        "contractual obligation, comply with a legal obligation, "
                        "protect a vital interest, perform a public task, or serve a "
                        "legitimate interest that does not override the data subject's "
                        "rights and freedoms; processing without any of these grounds "
                        "is unlawful under Federal Decree-Law No. 45/2021"
                    ),
                )

        # Art. 9 — sensitive data without explicit consent
        data_category = doc.get("data_category", "")
        if (
            isinstance(data_category, str)
            and data_category.lower() in _UAE_SENSITIVE_CATEGORIES
            and not doc.get("explicit_consent_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "UAE PDPL Art. 9 (Federal Decree-Law No. 45/2021) — explicit "
                    "consent required for health/financial/biometric/religious data"
                ),
                reason=(
                    f"Sensitive personal data category '{data_category}' (health/"
                    "financial/biometric/religious beliefs) without explicit consent "
                    "violates UAE PDPL Art. 9 — processing of sensitive personal data "
                    "requires the data subject's explicit, written, and specific "
                    "consent; general or implied consent is legally insufficient for "
                    "these categories; the controller must maintain auditable records "
                    "of consent for each sensitive data processing activity"
                ),
            )

        # Art. 22 — cross-border transfer to non-adequate country without DTA
        destination_country = doc.get("destination_country", "")
        if (
            isinstance(destination_country, str)
            and destination_country in UAE_NON_ADEQUATE_COUNTRIES
            and not doc.get("data_transfer_agreement")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "UAE PDPL Art. 22 (Federal Decree-Law No. 45/2021) — Data "
                    "Transfer Agreement required for transfer to non-adequate country"
                ),
                reason=(
                    f"Cross-border transfer of personal data to '{destination_country}' "
                    "without a Data Transfer Agreement (DTA) violates UAE PDPL Art. 22 "
                    "— transfers to countries not recognised as adequate by the UAE "
                    "Data Office are only permissible when supported by a binding DTA "
                    "incorporating the UAE standard contractual clauses; the destination "
                    "country has not received an adequacy decision from the UAE Data "
                    "Office and no DTA has been executed"
                ),
            )

        # Art. 13 — automated decision-making without human review mechanism
        if doc.get("automated_decision") and not doc.get("human_review"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "UAE PDPL Art. 13 (Federal Decree-Law No. 45/2021) — human "
                    "review mechanism required for automated decision-making"
                ),
                reason=(
                    "Automated decision-making producing legal or similarly significant "
                    "effects on a data subject without a human review mechanism "
                    "requires human review under UAE PDPL Art. 13 — data subjects "
                    "have the right to object to automated processing and to request "
                    "that a human review any automated decision; the controller must "
                    "implement a mechanism allowing data subjects to exercise this "
                    "right and must document all automated decisions for audit purposes"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="UAE PDPL Arts. 6, 9, 13, 22 (Federal Decree-Law No. 45/2021)",
            reason="UAE PDPL data protection controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 2 — UAE AI Strategy 2031 + ADGM + DIFC (UAEAIRegFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UAEAIRegFilter:
    """
    Layer 2: UAE AI Strategy 2031, ADGM FSRA AI Risk Management Framework,
    and DIFC DFSA AI Guidance.

    The UAE operates three parallel AI governance frameworks: the national
    UAE AI Strategy 2031 administered by the UAE AI Office, the DIFC DFSA
    Regulatory Policy and Process (RPP) Module governing financial firms in
    the Dubai International Financial Centre, and the ADGM FSRA AI Risk
    Management Framework governing financial firms in the Abu Dhabi Global
    Market.  Four principal controls apply:

    (a) UAE AI Strategy 2031 §4 Impact Assessment — high-risk AI systems
        (critical infrastructure, financial services, healthcare, government
        services, autonomous systems) require a mandatory UAE AI Office
        impact assessment before deployment; absence results in denial;
    (b) DFSA RPP Module — financial AI deployed within DIFC jurisdiction
        must comply with DFSA AI Guidance including model risk management,
        explainability, and algorithmic fairness; absence results in denial;
    (c) FSRA AI Risk Management Framework — financial AI deployed within
        ADGM must comply with FSRA AI Risk Management requirements including
        governance, testing, and incident management; absence results in
        denial;
    (d) UAE AI Ethics Principles Transparency — GenAI applications must
        satisfy the UAE AI Ethics Principles transparency requirement
        (disclosure of AI nature to users); absence triggers
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    UAE AI Strategy 2031 — UAE AI Office, Ministry of AI
        §4 Responsible AI — Mandatory AI Impact Assessment for High-Risk AI
    DIFC DFSA Regulatory Policy and Process (RPP) Module, Appendix 5 —
        Guidance on the Use of Artificial Intelligence in Financial Services
        (Dubai Financial Services Authority, 2023)
    ADGM FSRA Guidance on Artificial Intelligence Risk Management Framework
        (Abu Dhabi Global Market Financial Services Regulatory Authority,
        2023)
    UAE AI Ethics Principles — Transparency and Explainability Principle
        (UAE Ministry of AI, Digital Economy and Remote Work Applications)
    """

    FILTER_NAME: str = "UAE_AI_REG_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # UAE AI Strategy 2031 §4 — high-risk AI without UAE AI Office impact assessment
        if doc.get("ai_risk_level") == "high" and not doc.get("uae_ai_impact_assessed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "UAE AI Strategy 2031 §4 Responsible AI — mandatory UAE AI Office "
                    "impact assessment required for high-risk AI systems"
                ),
                reason=(
                    "High-risk AI system deployed without a UAE AI Office impact "
                    "assessment violates UAE AI Strategy 2031 §4 — all high-risk AI "
                    "systems (critical infrastructure, financial services, healthcare, "
                    "government services, autonomous vehicles, and judicial decision "
                    "support) must undergo a mandatory impact assessment administered "
                    "by the UAE AI Office before deployment or significant update; the "
                    "assessment evaluates safety, fairness, transparency, accountability, "
                    "and alignment with UAE national interests and ethical principles"
                ),
            )

        # DFSA RPP Module — financial AI in DIFC without DFSA AI Guidance compliance
        if doc.get("jurisdiction") == "DIFC" and not doc.get("dfsa_ai_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "DIFC DFSA RPP Module Appendix 5 — DFSA AI Guidance compliance "
                    "required for financial AI deployed within DIFC jurisdiction"
                ),
                reason=(
                    "Financial AI system deployed in DIFC without DFSA AI Guidance "
                    "compliance violates DIFC DFSA RPP Module Appendix 5 — all "
                    "DFSA-regulated firms (banks, investment managers, insurance "
                    "companies) operating within the Dubai International Financial "
                    "Centre that deploy AI for credit decisioning, trading, fraud "
                    "detection, or customer risk scoring must comply with DFSA AI "
                    "Guidance; requirements include model risk management, "
                    "explainability to affected customers, algorithmic fairness testing, "
                    "senior management accountability, and ongoing monitoring"
                ),
            )

        # FSRA AI Risk Management Framework — financial AI in ADGM without FSRA compliance
        if doc.get("jurisdiction") == "ADGM" and not doc.get("fsra_ai_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "ADGM FSRA AI Risk Management Framework — FSRA AI Risk Management "
                    "compliance required for financial AI deployed within ADGM"
                ),
                reason=(
                    "Financial AI system deployed in ADGM without FSRA AI Risk "
                    "Management Framework compliance violates ADGM FSRA Guidance on "
                    "Artificial Intelligence Risk Management — all FSRA-regulated "
                    "entities operating in the Abu Dhabi Global Market that use AI "
                    "for regulated activities (lending, investment advice, insurance, "
                    "payments) must comply with the FSRA AI Risk Management Framework; "
                    "requirements include AI governance policies, pre-deployment risk "
                    "assessments, explainability mechanisms, incident reporting, and "
                    "annual model validation by an independent party"
                ),
            )

        # UAE AI Ethics Principles — GenAI without transparency requirement
        if doc.get("genai_application") and not doc.get("uae_transparency_requirement"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "UAE AI Ethics Principles — Transparency Principle requires "
                    "disclosure of AI nature and capabilities to users of GenAI "
                    "applications"
                ),
                reason=(
                    "Generative AI application without UAE AI Ethics Principles "
                    "transparency requirement requires human review — the UAE AI "
                    "Ethics Principles (Ministry of AI, Digital Economy and Remote "
                    "Work Applications) require that users be informed when they are "
                    "interacting with or receiving content from an AI system; GenAI "
                    "applications must clearly disclose the AI-generated nature of "
                    "content, limitations of the system, and provide a mechanism for "
                    "human escalation; deployment without these transparency measures "
                    "requires mandatory human oversight review before going live"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "UAE AI Strategy 2031 §4 + DIFC DFSA RPP Module Appendix 5 + "
                "ADGM FSRA AI Risk Management Framework + UAE AI Ethics Principles"
            ),
            reason="UAE AI regulatory controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 3 — Saudi PDPL + NDMO AI governance (SaudiNDMOFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SaudiNDMOFilter:
    """
    Layer 3: Saudi Arabia Personal Data Protection Law (PDPL, Royal Decree
    M/19 of 1443H / 2021) and NDMO AI Governance Framework.

    The Saudi PDPL, enforced by the Saudi Data and AI Authority (SDAIA),
    establishes comprehensive data protection obligations for organisations
    processing personal data of Saudi residents.  The National Data
    Management Office (NDMO) Data Governance Framework imposes additional
    AI governance requirements.  Four principal controls apply:

    (a) PDPL Art. 5 Lawful Basis — personal data processing requires either
        the data subject's consent or a recognised legal obligation basis;
        absence results in denial;
    (b) PDPL Art. 23 Sensitive Data — health, genetic, biometric, financial,
        and criminal records data require explicit, written consent; absence
        results in denial;
    (c) PDPL Art. 29 Cross-Border Transfer — transfer of personal data
        outside Saudi Arabia requires SDAIA authorisation or recognition of
        adequate protection in the destination country; absence results in
        denial;
    (d) NDMO Data Governance Framework AI Compliance — AI systems processing
        personal data must comply with the NDMO Data Governance Framework
        including data classification, lineage tracking, and AI model
        governance; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Saudi Arabia Personal Data Protection Law (PDPL) — Royal Decree M/19
        of 1443H (2021), as amended 1444H (2023)
        Art. 5 Conditions for Processing Personal Data
        Art. 23 Conditions for Processing Sensitive Data
        Art. 29 Transfer or Disclosure of Personal Data to a Party Outside
                the Kingdom
    Saudi Data and AI Authority (SDAIA) — PDPL Implementing Regulations 2023
    National Data Management Office (NDMO) — Data Governance Framework v2.0
        AI and Advanced Analytics Governance Module
    """

    FILTER_NAME: str = "SAUDI_NDMO_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # PDPL Art. 5 — processing without consent or legal obligation
        if doc.get("personal_data_processing") and not doc.get("saudi_consent_obtained"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "Saudi PDPL Art. 5 (Royal Decree M/19) — consent or legal "
                    "obligation required for processing personal data of Saudi "
                    "residents"
                ),
                reason=(
                    "Personal data processing without consent or legal obligation "
                    "violates Saudi PDPL Art. 5 — a controller may process personal "
                    "data of Saudi residents only when the data subject has given "
                    "explicit consent, when processing is necessary to fulfil a "
                    "contractual obligation with the data subject, when required by "
                    "law or judicial order, or when necessary to protect a vital "
                    "interest; processing for commercial profiling or AI training "
                    "without any of these legal bases is unlawful under Royal "
                    "Decree M/19 and the SDAIA Implementing Regulations 2023"
                ),
            )

        # PDPL Art. 23 — sensitive data without explicit consent
        data_category = doc.get("data_category", "")
        if (
            isinstance(data_category, str)
            and data_category.lower() in _SAUDI_SENSITIVE_CATEGORIES
            and not doc.get("explicit_consent_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "Saudi PDPL Art. 23 (Royal Decree M/19) — explicit consent "
                    "required for health/genetic/biometric/financial/criminal data"
                ),
                reason=(
                    f"Sensitive personal data category '{data_category}' (health/"
                    "genetic/biometric/financial/criminal) without explicit consent "
                    "violates Saudi PDPL Art. 23 — processing of sensitive personal "
                    "data categories requires explicit, specific, and written consent "
                    "from the data subject; consent must identify the exact purpose "
                    "and categories of sensitive data to be processed; general "
                    "consent bundled with terms of service is legally insufficient "
                    "for sensitive data categories under the SDAIA Implementing "
                    "Regulations 2023"
                ),
            )

        # PDPL Art. 29 — cross-border transfer without SDAIA authorisation
        destination_country = doc.get("destination_country", "")
        if (
            isinstance(destination_country, str)
            and destination_country
            and destination_country not in SAUDI_ADEQUATE_COUNTRIES
            and not doc.get("sdaia_authorization")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "Saudi PDPL Art. 29 (Royal Decree M/19) — SDAIA authorisation "
                    "required for cross-border transfer to non-adequate country"
                ),
                reason=(
                    f"Cross-border transfer of personal data to '{destination_country}' "
                    "without SDAIA authorisation violates Saudi PDPL Art. 29 — "
                    "transfers of personal data of Saudi residents to countries not "
                    "recognised as providing adequate protection by SDAIA are "
                    "prohibited without a prior written authorisation from SDAIA; "
                    "authorisation requires demonstrating that the transfer serves "
                    "a legitimate purpose, that adequate safeguards are in place, "
                    "and that the transfer does not conflict with Saudi national "
                    "security or public interest"
                ),
            )

        # NDMO Data Governance Framework — AI system without NDMO compliance
        if not doc.get("ndmo_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "NDMO Data Governance Framework v2.0 — AI and Advanced Analytics "
                    "Governance Module requires NDMO compliance for AI systems "
                    "processing personal data in Saudi Arabia"
                ),
                reason=(
                    "AI system without NDMO Data Governance Framework compliance "
                    "requires human review — the National Data Management Office "
                    "Data Governance Framework v2.0 AI and Advanced Analytics "
                    "Governance Module requires all AI systems in Saudi Arabia that "
                    "process personal data to implement data classification, data "
                    "lineage tracking, AI model governance (including model cards, "
                    "bias assessments, and version control), and incident response "
                    "plans; non-compliant systems must undergo a human governance "
                    "review before processing personal data at scale"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=("Saudi PDPL Arts. 5, 23, 29 (Royal Decree M/19) + NDMO Data Governance Framework v2.0"),
            reason="Saudi PDPL + NDMO AI governance controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 4 — GCC cross-border data and AI controls (GCCCrossBorderFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GCCCrossBorderFilter:
    """
    Layer 4: GCC cross-border data and AI controls.

    The Gulf Cooperation Council (GCC) member states — UAE, Saudi Arabia,
    Bahrain, Kuwait, Oman, and Qatar — share interconnected data governance
    frameworks requiring specific controls for cross-border AI and data flows
    both within and outside the GCC region.  Four principal controls apply:

    (a) GCC Adequacy Framework — personal data transferred to a non-GCC
        country without an UAE or Saudi adequacy decision or equivalent
        safeguard results in denial;
    (b) FATF High-Risk Jurisdictions — financial AI data (transaction
        records, customer risk profiles, AML data) transferred to FATF
        high-risk jurisdictions (North Korea/KP, Iran/IR, Myanmar/MM) for
        AI processing results in denial; UAE and Saudi Arabia are FATF
        member states with binding FATF obligation compliance;
    (c) SDAIA Export Approval — AI model training data containing personal
        data of Saudi citizens exported for model training outside Saudi
        Arabia without SDAIA export approval results in denial;
    (d) GCC National Cloud Sovereignty — critical infrastructure data
        (government, defence, energy, financial) must be hosted on approved
        GCC national cloud regions; hosting on non-approved cloud regions
        triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    UAE PDPL Art. 22 + Saudi PDPL Art. 29 — GCC cross-border adequacy
        determinations and bilateral data protection recognition
    FATF (Financial Action Task Force) — High-Risk and Other Monitored
        Jurisdictions (Black List and Grey List, 2026)
    Saudi PDPL Art. 29 + SDAIA Cross-Border Data Transfer Guidelines 2023
    UAE TRA Cloud First Policy + Saudi NDMO Data Classification Policy —
        National Cloud Sovereignty Requirements for GCC Critical Data
    """

    FILTER_NAME: str = "GCC_CROSS_BORDER_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # GCC adequacy — personal data to non-GCC country without adequacy decision
        destination = doc.get("destination_country", "")
        if doc.get("personal_data") and isinstance(destination, str) and destination not in GCC_ADEQUATE_COUNTRIES:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "UAE PDPL Art. 22 + Saudi PDPL Art. 29 — GCC cross-border adequacy "
                    "framework; personal data to non-adequate country requires UAE/Saudi "
                    "adequacy decision or equivalent safeguard"
                ),
                reason=(
                    f"Transfer of personal data to '{destination}' violates the GCC "
                    "cross-border adequacy framework — neither the UAE Data Office nor "
                    "SDAIA has issued an adequacy determination for this jurisdiction, "
                    "and no equivalent safeguard (DTA, binding corporate rules, or "
                    "SDAIA authorisation) has been documented; transfers to "
                    "jurisdictions outside GCC_ADEQUATE_COUNTRIES are prohibited "
                    "without the relevant regulatory approval from both UAE and Saudi "
                    "data protection authorities"
                ),
            )

        # FATF high-risk — financial AI data to KP/IR/MM
        if doc.get("financial_data") and isinstance(destination, str) and destination in FATF_HIGH_RISK:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "FATF High-Risk Jurisdictions + UAE AML/CFT Framework + "
                    "Saudi SAMA AML Rules — financial AI data to FATF black-listed "
                    "jurisdiction is prohibited"
                ),
                reason=(
                    f"Financial AI data (transaction records, risk profiles, AML data) "
                    f"transferred to FATF high-risk jurisdiction '{destination}' is "
                    "prohibited — UAE and Saudi Arabia are both FATF member states "
                    "with binding obligations to apply enhanced due diligence and "
                    "countermeasures against FATF black-listed jurisdictions (North "
                    "Korea/KP, Iran/IR, Myanmar/MM); transfer of financial AI data "
                    "to these jurisdictions constitutes a potential AML/CFT violation "
                    "and is absolutely prohibited regardless of business purpose"
                ),
            )

        # SDAIA export approval — Saudi citizen AI training data exported without approval
        if doc.get("saudi_citizen_training_data") and not doc.get("sdaia_export_approval"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "Saudi PDPL Art. 29 + SDAIA Cross-Border Data Transfer Guidelines "
                    "2023 — SDAIA export approval required for AI training data "
                    "containing personal data of Saudi citizens"
                ),
                reason=(
                    "Export of AI model training data containing personal data of Saudi "
                    "citizens without SDAIA export approval violates Saudi PDPL Art. 29 "
                    "and SDAIA Cross-Border Data Transfer Guidelines 2023 — AI training "
                    "datasets incorporating personal data of Saudi residents are treated "
                    "as personal data transfers under the PDPL regardless of whether the "
                    "data has been pseudonymised; SDAIA export approval is mandatory "
                    "and requires demonstrating that the foreign recipient has "
                    "equivalent data protection standards, that training data cannot "
                    "be used to re-identify Saudi residents, and that the AI model "
                    "will not be used in ways that harm Saudi national interests"
                ),
            )

        # GCC national cloud sovereignty — critical data outside GCC national cloud
        if doc.get("critical_data") and doc.get("cloud_region") not in GCC_NATIONAL_CLOUDS:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "UAE TRA Cloud First Policy + Saudi NDMO Data Classification "
                    "Policy — critical infrastructure data must be hosted on approved "
                    "GCC national cloud regions"
                ),
                reason=(
                    "Critical infrastructure data (government, defence, energy, "
                    "financial) hosted outside approved GCC national cloud regions "
                    "requires human review under UAE TRA Cloud First Policy and Saudi "
                    "NDMO Data Classification Policy — both the UAE and Saudi Arabia "
                    "mandate that critical and highly sensitive data be processed and "
                    "stored exclusively on approved national cloud infrastructure "
                    "(uae_gov_cloud/ksa_gov_cloud/aws_uae/gcp_doha/azure_uae_north/"
                    "azure_ksa); any exception requires explicit approval from the "
                    "UAE TRA and Saudi NDMO with documented justification"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "UAE PDPL Art. 22 + Saudi PDPL Art. 29 + FATF GCC Member Obligations "
                "+ SDAIA Cross-Border Guidelines 2023 + UAE TRA/Saudi NDMO Cloud Policy"
            ),
            reason="GCC cross-border data and AI controls — compliant",
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class UAELangChainPolicyGuard:
    """
    LangChain integration — wraps the four UAE/Saudi governance filters as a
    LangChain-compatible ``Runnable``-style tool guard.

    Implements ``invoke(doc)`` and ``ainvoke(doc)`` so the guard can be
    inserted into a LangChain chain or used as a tool callback.  Raises
    ``PermissionError`` with the regulation citation when any filter returns
    DENIED.
    """

    def __init__(self, filter_instance: Any | None = None) -> None:
        if filter_instance is not None:
            self._filter = filter_instance
            self._multi = False
        else:
            self._filters: list[Any] = [
                UAEPDPLFilter(),
                UAEAIRegFilter(),
                SaudiNDMOFilter(),
                GCCCrossBorderFilter(),
            ]
            self._multi = True

    def process(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Apply a single wrapped filter; raise on DENIED, pass through otherwise."""
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc

    def invoke(self, doc: dict[str, Any]) -> list[FilterResult]:
        if not self._multi:
            result = self._filter.filter(doc)
            if result.is_denied:
                raise PermissionError(result.regulation)
            return [result]
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(r.regulation)
        return results

    def ainvoke(self, doc: dict[str, Any]) -> list[FilterResult]:
        """Async-compatible entry point (synchronous implementation)."""
        return self.invoke(doc)


class UAECrewAIGovernanceGuard:
    """
    CrewAI integration — wraps a UAE/Saudi governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
    """

    name: str = "UAEGovernanceGuard"
    description: str = (
        "Enforces UAE/Saudi AI governance policies (UAE PDPL, UAE AI Reg, "
        "Saudi NDMO, GCC Cross-Border) on documents processed by a CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class UAEAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    UAE/Saudi governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``UAEMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` with the regulation citation when
    the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def generate_reply(
        self,
        messages: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        doc = messages or {}
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class UAESemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps a UAE/Saudi governance filter as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``UAEMAFPolicyMiddleware`` for the Microsoft Agent Framework.
    Raises ``PermissionError`` with the regulation citation when the filter
    returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def enforce_governance(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class UAELlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing UAE/Saudi
    governance between retrieval and synthesis steps.

    Implements ``process_event(doc)`` compatible with LlamaIndex
    ``WorkflowStep`` protocol (LlamaIndex 0.14.x).  Raises ``PermissionError``
    with the regulation citation when the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def process_event(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class UAEHaystackGovernanceComponent:
    """
    Haystack integration — ``@component``-compatible governance filter for
    Haystack 2.x pipelines (current: Haystack 2.27.0).

    Implements ``run(documents)`` following the Haystack component protocol.
    Filters each document dict individually; denied documents are excluded
    from the output.  Does not raise; returns only permitted documents.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [doc for doc in documents if not self._filter.filter(doc).is_denied]
        return {"documents": passed}


class UAEDSPyGovernanceModule:
    """
    DSPy integration — governance-enforcing wrapper for DSPy ``Module``
    objects (DSPy >= 2.5.0, Pydantic v2).

    Implements ``forward(doc, **kwargs)`` and delegates to the wrapped module
    only after the filter passes.  Raises ``PermissionError`` with the
    regulation citation when the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any, module: Any) -> None:
        self._filter = filter_instance
        self._module = module

    def forward(self, doc: dict[str, Any], **kwargs: Any) -> Any:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return self._module(doc, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)


class UAEMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying UAE/Saudi governance filters.

    MAF is the enterprise successor to AutoGen and Semantic Kernel (released
    2025).  Implements ``process(message, next_handler)`` so this middleware
    can be registered in an MAF agent pipeline.  Raises ``PermissionError``
    with the regulation citation when the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def process(self, message: dict[str, Any], next_handler: Any) -> Any:
        result = self._filter.filter(message)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return next_handler(message)


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------


def _show(title: str, result: FilterResult) -> None:
    print("=" * 70)
    print(f"Scenario : {title}")
    print(f"  Decision   : {result.decision}")
    print(f"  Regulation : {result.regulation}")
    print(f"  Reason     : {result.reason}")
    print(f"  is_denied  : {result.is_denied}")
    print("=" * 70)


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # 1. UAE PDPL — personal data without legal basis → DENIED (Art. 6)
    # ------------------------------------------------------------------
    _show(
        "UAE PDPL Art. 6 — Personal Data Without Legal Basis",
        UAEPDPLFilter().filter(
            {
                "personal_data_processing": True,
                "uae_legal_basis": None,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. UAE PDPL — health data without explicit consent → DENIED (Art. 9)
    # ------------------------------------------------------------------
    _show(
        "UAE PDPL Art. 9 — Health Data Without Explicit Consent",
        UAEPDPLFilter().filter(
            {
                "data_category": "health",
                "explicit_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. UAE PDPL — transfer to CN without DTA → DENIED (Art. 22)
    # ------------------------------------------------------------------
    _show(
        "UAE PDPL Art. 22 — Cross-Border Transfer to CN Without DTA",
        UAEPDPLFilter().filter(
            {
                "destination_country": "CN",
                "data_transfer_agreement": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. UAE PDPL — automated decision without human review → RHR (Art. 13)
    # ------------------------------------------------------------------
    _show(
        "UAE PDPL Art. 13 — Automated Decision Without Human Review",
        UAEPDPLFilter().filter(
            {
                "automated_decision": True,
                "human_review": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. UAE AI Reg — high-risk AI without impact assessment → DENIED
    # ------------------------------------------------------------------
    _show(
        "UAE AI Strategy §4 — High-Risk AI Without Impact Assessment",
        UAEAIRegFilter().filter(
            {
                "ai_risk_level": "high",
                "uae_ai_impact_assessed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. UAE AI Reg — DIFC financial AI without DFSA compliance → DENIED
    # ------------------------------------------------------------------
    _show(
        "DFSA RPP Module — DIFC Financial AI Without Compliance",
        UAEAIRegFilter().filter(
            {
                "jurisdiction": "DIFC",
                "dfsa_ai_compliant": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. Saudi NDMO — personal data without Saudi consent → DENIED
    # ------------------------------------------------------------------
    _show(
        "Saudi PDPL Art. 5 — Personal Data Without Consent",
        SaudiNDMOFilter().filter(
            {
                "personal_data_processing": True,
                "saudi_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Saudi NDMO — biometric data without explicit consent → DENIED
    # ------------------------------------------------------------------
    _show(
        "Saudi PDPL Art. 23 — Biometric Data Without Explicit Consent",
        SaudiNDMOFilter().filter(
            {
                "data_category": "biometric",
                "explicit_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. GCC — personal data to non-adequate country → DENIED
    # ------------------------------------------------------------------
    _show(
        "GCC Adequacy — Personal Data to Non-Adequate Country",
        GCCCrossBorderFilter().filter(
            {
                "personal_data": True,
                "destination_country": "VN",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. GCC — financial AI data to KP → DENIED (FATF)
    # ------------------------------------------------------------------
    _show(
        "FATF High-Risk — Financial AI Data to KP",
        GCCCrossBorderFilter().filter(
            {
                "financial_data": True,
                "destination_country": "KP",
            }
        ),
    )
