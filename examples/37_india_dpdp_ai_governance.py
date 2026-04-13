"""
37_india_dpdp_ai_governance.py — India AI Governance Framework

Implements governance filters for India's comprehensive AI regulatory
ecosystem covering the Digital Personal Data Protection Act 2023 (DPDP Act),
the Ministry of Electronics and Information Technology (MeitY) AI Advisory and
Draft AI Policy 2023, India's sectoral AI regulations across financial
services (RBI), healthcare (ICMR), telecom (TRAI), and insurance (IRDAI),
and cross-border AI data-flow obligations under Indian frameworks.

Demonstrates a multi-layer governance framework where four independent
filters enforce distinct requirements of the India regulatory landscape:

    Layer 1  — DPDP Act 2023 data protection (IndiaDPDPFilter):

               DPDP Act §5 Notice + §6 Consent — personal data processing
                   without notice to data principals or without consent
                   is denied;
               DPDP Act §9 + Sensitive Data — financial/health/biometric/
                   children's data without explicit consent is denied;
               DPDP Act §16 Cross-Border Transfer — transfer to RU/CN/KP
                   (non-adequate countries) without DPDP adequacy finding
                   is denied;
               DPDP Act §13 Grievance Redressal — automated processing
                   without right to grievance redressal mechanism triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 2  — MeitY AI governance (MeitYAIFilter):

               MeitY Draft AI Policy 2023 §4.2 — high-risk AI system
                   without mandatory impact assessment is denied;
               MeitY Advisory §3.1 — AI system without explainability
                   mechanism is denied;
               MeitY Advisory March 2024 §2 — GenAI content without
                   labeling or watermark is denied;
               MeitY Draft §5.3 — AI decision affecting citizens without
                   human oversight mechanism triggers REQUIRES_HUMAN_REVIEW.

    Layer 3  — India sectoral AI regulations (IndiaSectoralAIFilter):

               RBI AI/ML Framework 2023 (Circular RBI/2023-24/73) — AI in
                   financial services without RBI AI compliance is denied;
               ICMR AI in Healthcare Guidelines 2023 — AI healthcare
                   system without ICMR ethics review is denied;
               TRAI Recommendations on AI in Telecom 2023 — AI in telecom
                   without TRAI AI consent is denied;
               IRDAI Circular IRDA/SDD/GDL/MISC/115/05/2022 — insurance
                   AI without IRDAI compliance triggers REQUIRES_HUMAN_REVIEW.

    Layer 4  — Cross-border AI data flows (IndiaCrossBorderFilter):

               DPDP Act §16 + DPDP_RESTRICTED_COUNTRIES — personal data of
                   Indian citizens to RU/CN/KP/IR without adequacy finding
                   is denied;
               MeitY cloud empanelment — critical data to non-empanelled
                   cloud without MeitY approval is denied;
               DPDP Act + MeitY clearance — AI model trained on sensitive
                   Indian data exported without DPDP consent + MeitY
                   clearance is denied;
               RBI Circular RBI/2021-22/57 — payment data to non-PCI DSS
                   + non-RBI cloud without RBI circular compliance triggers
                   REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+--------------------------------------+-----------------------------------+
| Use case                             | Primary filters applied           |
+--------------------------------------+-----------------------------------+
| Banking credit-scoring AI            | IndiaSectoralAIFilter (RBI)       |
| Insurance underwriting AI            | IndiaSectoralAIFilter (IRDAI)     |
| HR / hiring decision AI              | IndiaDPDPFilter (sensitive data)  |
| Generative AI citizen chatbot        | MeitYAIFilter (GenAI labeling)    |
| Government e-governance AI           | MeitYAIFilter (impact assessment) |
| Healthcare predictive diagnostics    | IndiaSectoralAIFilter (ICMR)      |
| Telecom network optimisation AI      | IndiaSectoralAIFilter (TRAI)      |
| Cross-border data analytics platform | IndiaCrossBorderFilter            |
+--------------------------------------+-----------------------------------+

No external dependencies required.

Run:
    python examples/37_india_dpdp_ai_governance.py
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
    Result returned by each India AI governance filter.

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

# DPDP Act §16 — countries to which transfer of personal data of Indian
# citizens requires an adequacy determination by the Central Government.
# RU, CN, KP are explicitly non-adequate; IR, SY, CU treated as restricted.
DPDP_RESTRICTED_COUNTRIES: frozenset[str] = frozenset({"RU", "CN", "KP", "IR", "SY", "CU"})

# IndiaCrossBorderFilter — restricted countries for personal data of Indian
# citizens per DPDP §16 + MeitY cross-border guidance.
INDIA_RESTRICTED_COUNTRIES: frozenset[str] = frozenset({"RU", "CN", "KP", "IR"})

# MeitY-empanelled cloud service providers for critical government / regulated
# data hosting in India (as of MeitY empanelment list 2024).
MEITY_EMPANELLED_CLOUDS: frozenset[str] = frozenset(
    {
        "aws_mumbai",
        "gcp_mumbai",
        "azure_india_central",
        "meity_cloud",
    }
)

# DPDP Act — sensitive personal data categories requiring explicit consent
_DPDP_SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {
        "financial",
        "health",
        "biometric",
        "children",
    }
)


# ---------------------------------------------------------------------------
# Layer 1 — DPDP Act 2023 data protection (IndiaDPDPFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndiaDPDPFilter:
    """
    Layer 1: India Digital Personal Data Protection Act 2023 (DPDP Act).

    The DPDP Act is India's comprehensive personal data protection statute
    enacted in August 2023, establishing the rights of data principals and
    obligations of data fiduciaries.  Four principal controls apply:

    (a) DPDP §5 Notice + §6 Consent — personal data must be processed only
        after providing a notice to the data principal and obtaining free,
        specific, informed, unconditional, and unambiguous consent; absence
        of notice or consent results in denial;
    (b) Sensitive Data (§9 + Schedule) — financial, health, biometric, and
        children's data require explicit consent; absence results in denial;
    (c) §16 Cross-Border Transfer — transfer to a non-adequate country
        (RU/CN/KP/IR/SY/CU) without Central Government adequacy finding
        results in denial;
    (d) §13 Grievance Redressal — automated processing without a right to
        grievance redressal mechanism triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Digital Personal Data Protection Act 2023 (DPDP Act), India
        §5 Notice, §6 Consent, §9 Data Fiduciary obligations,
        §13 Grievance Redressal, §16 Transfer of Personal Data Outside India
    Ministry of Electronics and Information Technology (MeitY) —
        DPDP Rules 2025 (draft notified January 2025)
    """

    FILTER_NAME: str = "INDIA_DPDP_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # §5 Notice + §6 Consent — personal data processing without consent or notice
        if doc.get("personal_data_processing"):
            if not doc.get("consent_obtained"):
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="DENIED",
                    regulation=(
                        "DPDP Act 2023 §6 Consent — free, specific, informed, "
                        "unconditional and unambiguous consent required"
                    ),
                    reason=(
                        "Personal data processing without consent from the data "
                        "principal violates DPDP Act 2023 §6 — a data fiduciary "
                        "may process personal data only for a lawful purpose for "
                        "which the data principal has given or is deemed to have "
                        "given her consent; consent must be free, specific, informed, "
                        "unconditional, and unambiguous with a clear affirmative action"
                    ),
                )
            if not doc.get("notice_provided"):
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="DENIED",
                    regulation=(
                        "DPDP Act 2023 §5 Notice — notice to data principal required "
                        "before or at the time of seeking consent"
                    ),
                    reason=(
                        "Personal data processing without providing notice to the "
                        "data principal violates DPDP Act 2023 §5 — the data "
                        "fiduciary must provide the data principal with a notice "
                        "describing the personal data to be processed, the purpose, "
                        "and the manner of exercising rights under the Act, before or "
                        "at the time of seeking consent"
                    ),
                )

        # Sensitive data — financial/health/biometric/children's without explicit consent
        data_category = doc.get("data_category", "")
        if (
            isinstance(data_category, str)
            and data_category.lower() in _DPDP_SENSITIVE_CATEGORIES
            and not doc.get("explicit_consent_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "DPDP Act 2023 §9 + Sensitive Data Schedule — explicit consent "
                    "required for financial/health/biometric/children's data"
                ),
                reason=(
                    f"Sensitive personal data category '{data_category}' (financial/"
                    "health/biometric/children's) without explicit consent violates "
                    "DPDP Act 2023 §9 and the Sensitive Data Schedule — processing "
                    "of these categories requires specific, granular, and explicit "
                    "consent that is separate from general consent for personal data "
                    "processing; general consent is legally insufficient"
                ),
            )

        # §16 Cross-border transfer to non-adequate country
        destination_country = doc.get("destination_country", "")
        if isinstance(destination_country, str) and destination_country in DPDP_RESTRICTED_COUNTRIES:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "DPDP Act 2023 §16 Transfer of Personal Data Outside India — "
                    "Central Government adequacy determination required"
                ),
                reason=(
                    f"Cross-border transfer of personal data to '{destination_country}' "
                    "violates DPDP Act 2023 §16 — the Central Government has not "
                    "issued an adequacy determination for this country; personal data "
                    "of Indian data principals may only be transferred to countries "
                    "notified as adequate by the Central Government after consultation "
                    "with the Data Protection Board of India"
                ),
            )

        # §13 Grievance Redressal — automated processing without grievance mechanism
        if doc.get("automated_processing") and not doc.get("grievance_redressal_available"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "DPDP Act 2023 §13 Grievance Redressal — right to grievance redressal for data principals required"
                ),
                reason=(
                    "Automated processing of personal data without a grievance "
                    "redressal mechanism requires human review under DPDP Act 2023 "
                    "§13 — every data principal has the right to have grievances "
                    "readily addressed by the data fiduciary; automated processing "
                    "systems must provide a clear mechanism for data principals to "
                    "lodge complaints and receive a timely response"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="DPDP Act 2023 §5, §6, §9, §13, §16",
            reason="India DPDP Act 2023 data protection controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 2 — MeitY AI governance (MeitYAIFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeitYAIFilter:
    """
    Layer 2: MeitY AI Advisory and Draft AI Policy 2023.

    The Ministry of Electronics and Information Technology (MeitY) has
    issued AI governance guidance through an AI Advisory (2023), a Draft
    National AI Policy (2023), and an updated Advisory on Generative AI
    (March 2024).  Four principal controls apply:

    (a) MeitY Draft AI Policy §4.2 Mandatory Impact Assessment — high-risk
        AI systems (government services, critical infrastructure, hiring,
        credit scoring, law enforcement) must undergo a mandatory AI impact
        assessment before deployment; absence results in denial;
    (b) MeitY Advisory §3.1 Explainability — AI systems making decisions
        that affect individuals must incorporate explainability mechanisms
        allowing affected persons to understand the basis of AI decisions;
        absence results in denial;
    (c) MeitY Advisory March 2024 §2 GenAI Labeling — generative AI
        content deployed on internet intermediaries or shared publicly must
        be labeled or watermarked to indicate AI generation; absence results
        in denial;
    (d) MeitY Draft §5.3 Human Oversight — AI decisions affecting citizens'
        access to government services, benefits, or rights must include a
        human oversight mechanism; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    MeitY Advisory on AI/ML Tools Deployed on Social Media Intermediaries,
        March 2024 (Advisory No. 3(1)/2023-CERT-In)
    MeitY Draft National Artificial Intelligence Policy 2023 §§ 4.2, 5.3
    MeitY AI Advisory 2023 §3.1 — Explainability and Transparency
    """

    FILTER_NAME: str = "MEITY_AI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # MeitY Draft §4.2 — high-risk AI without mandatory impact assessment
        if doc.get("ai_risk_level") == "high" and not doc.get("impact_assessment_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "MeitY Draft AI Policy 2023 §4.2 — mandatory AI impact assessment "
                    "required for high-risk AI systems before deployment"
                ),
                reason=(
                    "High-risk AI system deployed without a mandatory AI impact "
                    "assessment violates MeitY Draft AI Policy 2023 §4.2 — all "
                    "high-risk AI systems (those affecting government services, "
                    "critical infrastructure, hiring decisions, credit scoring, or "
                    "law enforcement) must undergo a comprehensive impact assessment "
                    "evaluating safety, fairness, accountability, and societal impact "
                    "before deployment or significant update"
                ),
            )

        # MeitY Advisory §3.1 — AI system without explainability mechanism
        if doc.get("ai_decision_system") and not doc.get("explainability_provided"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "MeitY AI Advisory 2023 §3.1 Explainability — AI systems making "
                    "decisions affecting individuals must incorporate explainability"
                ),
                reason=(
                    "AI decision system without an explainability mechanism violates "
                    "MeitY AI Advisory 2023 §3.1 — AI systems that make or assist "
                    "in making decisions affecting individuals (credit, employment, "
                    "healthcare, education, legal) must provide meaningful explanations "
                    "of the basis for such decisions in plain language accessible to "
                    "the affected person; black-box models without interpretability "
                    "mechanisms are non-compliant"
                ),
            )

        # MeitY Advisory March 2024 §2 — GenAI content without labeling or watermark
        if doc.get("genai_content") and not doc.get("genai_labeled"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "MeitY Advisory March 2024 §2 — GenAI content must be labeled "
                    "or watermarked to disclose AI generation"
                ),
                reason=(
                    "Generative AI content deployed without labeling or watermark "
                    "violates MeitY Advisory March 2024 §2 — all AI-generated "
                    "content (synthetic text, images, audio, video, deepfakes) made "
                    "available on internet intermediaries or shared publicly in India "
                    "must be clearly labeled as AI-generated using a technically "
                    "robust watermark or explicit disclosure; this applies to all "
                    "intermediaries under IT Act 2000 §79 safe harbour obligations"
                ),
            )

        # MeitY Draft §5.3 — AI affecting citizens without human oversight
        if doc.get("affects_citizens") and not doc.get("human_oversight"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "MeitY Draft AI Policy 2023 §5.3 Human Oversight — AI decisions "
                    "affecting citizens' rights or government services require human "
                    "oversight mechanism"
                ),
                reason=(
                    "AI system making decisions affecting citizens' access to "
                    "government services, benefits, or rights without a human "
                    "oversight mechanism requires human review under MeitY Draft "
                    "AI Policy 2023 §5.3 — a competent human authority must be able "
                    "to review, override, or halt any AI decision affecting a "
                    "citizen's substantive rights; fully automated sovereign decisions "
                    "without human accountability are not permitted"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "MeitY AI Advisory 2023 §3.1 + MeitY Advisory March 2024 §2 + MeitY Draft AI Policy 2023 §§4.2, 5.3"
            ),
            reason="MeitY AI governance controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 3 — India sectoral AI regulations (IndiaSectoralAIFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndiaSectoralAIFilter:
    """
    Layer 3: India sectoral AI regulations (financial, healthcare, telecom,
    insurance).

    India's sectoral regulators have issued specific AI governance
    requirements for their regulated industries.  Four principal controls
    apply:

    (a) RBI AI/ML Framework 2023 (Circular RBI/2023-24/73) — AI and ML
        models used in financial services (credit scoring, fraud detection,
        risk modelling, algorithmic trading) must comply with RBI's model
        risk management framework; absence results in denial;
    (b) ICMR AI in Healthcare Guidelines 2023 — AI systems used in
        healthcare diagnosis, treatment recommendation, or medical imaging
        must undergo ICMR ethics review; absence results in denial;
    (c) TRAI Recommendations on AI in Telecom 2023 — AI systems used in
        telecom network management, customer data analysis, or service
        quality must obtain TRAI AI consent approval; absence results in
        denial;
    (d) IRDAI Circular IRDA/SDD/GDL/MISC/115/05/2022 — AI systems used in
        insurance underwriting, claims processing, or fraud detection must
        comply with IRDAI guidelines; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    RBI Circular RBI/2023-24/73 — AI/ML Framework for Regulated Entities
    ICMR (Indian Council of Medical Research) — AI in Healthcare 2023
        Guidelines, Ethical Framework
    TRAI (Telecom Regulatory Authority of India) — Recommendations on
        Artificial Intelligence and Big Data in Telecom Sector (2023)
    IRDAI (Insurance Regulatory and Development Authority of India) —
        Circular IRDA/SDD/GDL/MISC/115/05/2022 on Use of Technology in
        Insurance
    """

    FILTER_NAME: str = "INDIA_SECTORAL_AI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # RBI Circular RBI/2023-24/73 — financial AI without RBI AI/ML compliance
        if doc.get("sector") == "financial" and not doc.get("rbi_ai_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "RBI Circular RBI/2023-24/73 — RBI AI/ML Framework 2023 "
                    "compliance required for AI in financial services"
                ),
                reason=(
                    "AI system in financial sector without RBI AI/ML Framework 2023 "
                    "compliance violates RBI Circular RBI/2023-24/73 — all regulated "
                    "entities (banks, NBFCs, payment system operators) deploying AI/ML "
                    "models for credit scoring, fraud detection, risk modelling, or "
                    "algorithmic trading must implement model risk management, "
                    "explainability, fairness testing, and model validation per RBI's "
                    "AI/ML framework before deployment in production"
                ),
            )

        # ICMR AI in Healthcare Guidelines 2023 — healthcare AI without ethics review
        if doc.get("sector") == "healthcare" and not doc.get("icmr_ethics_reviewed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "ICMR AI in Healthcare Guidelines 2023 — ICMR ethics review "
                    "required for AI systems in healthcare diagnosis and treatment"
                ),
                reason=(
                    "AI system in healthcare sector without ICMR ethics review "
                    "violates the ICMR AI in Healthcare Guidelines 2023 — all AI "
                    "systems used for medical diagnosis, treatment recommendation, "
                    "medical imaging analysis, or clinical decision support must "
                    "undergo an ICMR ethics committee review before deployment; the "
                    "review must assess patient safety, data privacy, algorithmic "
                    "bias, and informed consent processes"
                ),
            )

        # TRAI Recommendations on AI in Telecom 2023 — telecom AI without TRAI consent
        if doc.get("sector") == "telecom" and not doc.get("trai_ai_consent"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "TRAI Recommendations on AI in Telecom Sector 2023 — TRAI AI "
                    "consent approval required for AI in telecom"
                ),
                reason=(
                    "AI system in telecom sector without TRAI AI consent approval "
                    "violates TRAI Recommendations on Artificial Intelligence and "
                    "Big Data in Telecom Sector 2023 — telecom service providers "
                    "deploying AI for network management, customer data analytics, "
                    "service quality optimisation, or predictive maintenance must "
                    "obtain TRAI approval and comply with TRAI's AI governance "
                    "framework including data minimisation and purpose limitation"
                ),
            )

        # IRDAI Circular IRDA/SDD/GDL/MISC/115/05/2022 — insurance AI without compliance
        if doc.get("sector") == "insurance" and not doc.get("irdai_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "IRDAI Circular IRDA/SDD/GDL/MISC/115/05/2022 — IRDAI technology "
                    "guidelines compliance required for AI in insurance"
                ),
                reason=(
                    "AI system in insurance sector without IRDAI compliance requires "
                    "human review under IRDAI Circular IRDA/SDD/GDL/MISC/115/05/2022 "
                    "— insurance companies deploying AI for underwriting, claims "
                    "processing, fraud detection, or premium calculation must comply "
                    "with IRDAI's technology use guidelines including explainability "
                    "to policyholders, fairness testing, and audit trail maintenance; "
                    "a human underwriter review is mandated for borderline AI decisions"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "RBI Circular RBI/2023-24/73 + ICMR AI in Healthcare Guidelines 2023 "
                "+ TRAI AI in Telecom Recommendations 2023 + IRDAI Circular "
                "IRDA/SDD/GDL/MISC/115/05/2022"
            ),
            reason="India sectoral AI governance controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border AI data flows (IndiaCrossBorderFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndiaCrossBorderFilter:
    """
    Layer 4: India cross-border data and AI controls.

    Indian law imposes specific controls on cross-border AI data flows
    through the DPDP Act 2023 §16, MeitY empanelment requirements, and
    RBI data localisation circulars.  Four principal controls apply:

    (a) DPDP Act §16 + INDIA_RESTRICTED_COUNTRIES — personal data of Indian
        citizens transferred to RU/CN/KP/IR without DPDP adequacy finding
        results in denial;
    (b) MeitY Cloud Empanelment — critical data (government/financial/health)
        hosted on non-MeitY-empanelled cloud without MeitY approval results
        in denial;
    (c) DPDP Act + MeitY Clearance — AI model trained on sensitive Indian
        data exported without DPDP consent and MeitY clearance results in
        denial;
    (d) RBI Circular RBI/2021-22/57 Data Localisation — payment data to
        non-PCI DSS and non-RBI compliant cloud without RBI circular
        compliance triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Digital Personal Data Protection Act 2023, §16 Transfer Outside India
    MeitY Empanelment of Cloud Service Providers — Empanelment List 2024
    RBI Circular RBI/2021-22/57 — Storage of Payment System Data
        (Data Localisation for payment data in India)
    MeitY Guidelines for Government Departments on Contractual Terms
        Related to Cloud Services 2023
    """

    FILTER_NAME: str = "INDIA_CROSS_BORDER_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # DPDP §16 — personal data of Indian citizens to restricted country
        destination = doc.get("destination_country", "")
        if (
            doc.get("indian_citizens_personal_data")
            and isinstance(destination, str)
            and destination in INDIA_RESTRICTED_COUNTRIES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "DPDP Act 2023 §16 Transfer Outside India — Central Government "
                    "adequacy determination not issued for restricted country"
                ),
                reason=(
                    f"Transfer of personal data of Indian citizens to "
                    f"'{destination}' violates DPDP Act 2023 §16 — "
                    "the Central Government has not issued an adequacy notification "
                    "for this jurisdiction; transfers to RU/CN/KP/IR are prohibited "
                    "until the Data Protection Board of India and Central Government "
                    "complete an adequacy review and issue a formal notification"
                ),
            )

        # MeitY empanelment — critical data to non-empanelled cloud
        cloud_provider = doc.get("cloud_provider", "")
        if doc.get("critical_data") and not doc.get("cloud_empanelled"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "MeitY Cloud Empanelment Policy — critical government/financial/"
                    "health data must be hosted on MeitY-empanelled cloud providers"
                ),
                reason=(
                    f"Critical data (government/financial/health) hosted on "
                    f"'{cloud_provider or 'unknown'}' without MeitY cloud "
                    "empanelment violates MeitY Guidelines for Government Departments "
                    "on Cloud Services 2023 — all critical and sensitive government, "
                    "financial, and health data must be processed and stored on "
                    "MeitY-empanelled cloud service providers "
                    "(aws_mumbai/gcp_mumbai/azure_india_central/meity_cloud); "
                    "non-empanelled foreign cloud providers are prohibited for "
                    "critical data categories"
                ),
            )

        # DPDP + MeitY clearance — AI model trained on sensitive Indian data exported
        if doc.get("sensitive_training_data") and not (
            doc.get("dpdp_export_consent_obtained") and doc.get("meity_clearance_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "DPDP Act 2023 §16 + MeitY AI Policy — AI model trained on "
                    "sensitive Indian data requires DPDP consent + MeitY clearance "
                    "before export"
                ),
                reason=(
                    "Export of AI model trained on sensitive Indian personal data "
                    "without both DPDP Act consent (§16) and MeitY clearance violates "
                    "DPDP Act 2023 §16 and MeitY AI Policy — AI models trained on "
                    "sensitive categories of Indian personal data (health/financial/"
                    "biometric/children's) embody personal data patterns and may not "
                    "be exported without explicit DPDP-compliant consent from data "
                    "principals and a MeitY clearance confirming national security "
                    "and data sovereignty requirements are satisfied"
                ),
            )

        # RBI Circular RBI/2021-22/57 — payment data without RBI cloud compliance
        if doc.get("payment_data") and not doc.get("rbi_cloud_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "RBI Circular RBI/2021-22/57 Storage of Payment System Data — "
                    "payment data must comply with RBI data localisation and PCI DSS "
                    "cloud requirements"
                ),
                reason=(
                    "Payment data transfer or processing without RBI Circular "
                    "RBI/2021-22/57 compliance requires human review — RBI mandates "
                    "that all payment system data (including end-to-end transaction "
                    "details, payment data, and customer data) must be stored only "
                    "in systems located in India; cloud providers used for payment "
                    "data must be PCI DSS certified and comply with RBI data "
                    "localisation requirements; cross-border payment data flows "
                    "require explicit RBI approval"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=("DPDP Act 2023 §16 + MeitY Cloud Empanelment Policy + RBI Circular RBI/2021-22/57"),
            reason="India cross-border AI data flow controls — compliant",
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class IndiaLangChainPolicyGuard:
    """
    LangChain integration — wraps the four India governance filters as a
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
                IndiaDPDPFilter(),
                MeitYAIFilter(),
                IndiaSectoralAIFilter(),
                IndiaCrossBorderFilter(),
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


class IndiaCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps an India governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
    """

    name: str = "IndiaGovernanceGuard"
    description: str = (
        "Enforces India AI governance policies (DPDP Act, MeitY, Sectoral, "
        "Cross-Border) on documents processed by a CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class IndiaAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    India governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``IndiaMAFPolicyMiddleware`` for the Microsoft Agent
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


class IndiaSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps an India governance filter as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``IndiaMAFPolicyMiddleware`` for the Microsoft Agent Framework.
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


class IndiaLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing India governance
    between retrieval and synthesis steps.

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


class IndiaHaystackGovernanceComponent:
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


class IndiaDSPyGovernanceModule:
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


class IndiaMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying India governance filters.

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
    # 1. Personal data without consent → DENIED (DPDP §6)
    # ------------------------------------------------------------------
    _show(
        "DPDP §6 — Personal Data Processing Without Consent",
        IndiaDPDPFilter().filter(
            {
                "personal_data_processing": True,
                "consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Health data without explicit consent → DENIED (DPDP Sensitive)
    # ------------------------------------------------------------------
    _show(
        "DPDP Sensitive Data — Health Data Without Explicit Consent",
        IndiaDPDPFilter().filter(
            {
                "data_category": "health",
                "explicit_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. Transfer to CN → DENIED (DPDP §16)
    # ------------------------------------------------------------------
    _show(
        "DPDP §16 — Cross-Border Transfer to CN",
        IndiaDPDPFilter().filter(
            {
                "destination_country": "CN",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. Automated processing without grievance mechanism → RHR
    # ------------------------------------------------------------------
    _show(
        "DPDP §13 — Automated Processing Without Grievance Redressal",
        IndiaDPDPFilter().filter(
            {
                "automated_processing": True,
                "grievance_redressal_available": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. High-risk AI without impact assessment → DENIED (MeitY §4.2)
    # ------------------------------------------------------------------
    _show(
        "MeitY Draft §4.2 — High-Risk AI Without Impact Assessment",
        MeitYAIFilter().filter(
            {
                "ai_risk_level": "high",
                "impact_assessment_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. GenAI content without labeling → DENIED (MeitY March 2024 §2)
    # ------------------------------------------------------------------
    _show(
        "MeitY March 2024 §2 — GenAI Content Without Labeling",
        MeitYAIFilter().filter(
            {
                "genai_content": True,
                "genai_labeled": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. Financial AI without RBI compliance → DENIED (RBI/2023-24/73)
    # ------------------------------------------------------------------
    _show(
        "RBI/2023-24/73 — Financial AI Without RBI Compliance",
        IndiaSectoralAIFilter().filter(
            {
                "sector": "financial",
                "rbi_ai_compliant": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Payment data without RBI cloud compliance → RHR
    # ------------------------------------------------------------------
    _show(
        "RBI/2021-22/57 — Payment Data Without RBI Cloud Compliance",
        IndiaCrossBorderFilter().filter(
            {
                "payment_data": True,
                "rbi_cloud_compliant": False,
            }
        ),
    )
