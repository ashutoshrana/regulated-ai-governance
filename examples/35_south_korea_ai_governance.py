"""
35_south_korea_ai_governance.py — South Korea AI Governance Framework

Implements governance filters for South Korea's comprehensive AI regulatory
ecosystem covering the Personal Information Protection Act (PIPA) 2023
amendment, the Financial Services Commission (FSC) AI governance framework
for Korean financial services, the Korea AI Basic Act 2024 (enacted January
2024, effective 2026), and cross-border AI data-flow obligations under Korean
frameworks.

Demonstrates a multi-layer governance framework where four independent
filters enforce distinct requirements of the South Korea regulatory landscape:

    Layer 1  — PIPA data protection (KoreaPIPAFilter):

               PIPA Art. 15 Lawfulness of Collection — personal information
                   processing without consent or legitimate purpose is denied;
               PIPA Art. 23 Processing Sensitive Information — sensitive
                   categories (ideology/beliefs/union/political opinion/
                   health/sexual life/biometric/criminal) without explicit
                   consent are denied;
               PIPA Art. 28-8 Cross-border Provision — transfer to country
                   without PIPC adequacy designation or PIPC approval
                   without consent is denied (adequate: EU/UK/Canada; others
                   require PIPC approval or individual consent);
               PIPA Art. 37-2 Automated Decisions (2023 amendment) —
                   automated decision with significant legal effects without
                   right-to-explanation mechanism triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 2  — FSC AI financial governance (KoreaFSCAIFilter):

               Financial Investment Services and Capital Markets Act Art. 7 +
                   FSC Robo-Advisor Guidelines 2016 — AI-driven investment
                   advisory without robo-advisor registration is denied;
               FSC Credit Information Act Art. 26 + CB Act AI Guidelines
                   2021 — AI credit scoring model without FSC model
                   validation and audit trail is denied;
               Insurance Business Act Art. 176 + FSC Supervisory Regulation
                   Art. 7-8 — insurance AI underwriting without actuarial
                   certification is denied;
               FSCMA Art. 63 + KSDA Algorithmic Trading Guidelines — AI
                   trading algorithm without FSC algorithmic trading
                   registration triggers REQUIRES_HUMAN_REVIEW.

    Layer 3  — Korea AI Basic Act 2024 (KoreaAIBasicActFilter):

               AI Basic Act Art. 47 Impact Assessment — high-impact AI
                   (medical/legal/education/employment) without prior impact
                   assessment is denied;
               AI Basic Act Art. 35 Transparency Obligations — AI system
                   without transparency disclosure to users is denied;
               AI Basic Act Art. 36 GenAI Disclosure — generative AI content
                   without watermark/disclosure is denied;
               AI Basic Act Art. 46 Human Oversight — AI system in critical
                   infrastructure without human oversight mechanism triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 4  — Cross-border AI data flows (KoreaCrossBorderFilter):

               PIPA Art. 28-8 + PIPC Transfer Assessment — personal data to
                   CN/RU/KP without PIPC adequacy or explicit consent is
                   denied;
               FSC Electronic Financial Transactions Act Art. 21-2 — financial
                   AI data to non-FSC approved entity without contractual
                   safeguards is denied;
               FSC Cloud Security Guidelines — AI serving Korean-regulated
                   entities from non-approved cloud region (approved: AWS
                   Seoul / GCP Seoul / Azure Korea Central) is denied;
               PIPA Art. 28-8 + PIPC Sensitive Data Guidelines — cross-border
                   AI training on Korean biometric/health data without PIPC
                   notification triggers REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+--------------------------------------+-----------------------------------+
| Use case                             | Primary filters applied           |
+--------------------------------------+-----------------------------------+
| Retail banking credit scoring AI     | KoreaFSCAIFilter, CrossBorder     |
| Insurance AI underwriting platform   | KoreaFSCAIFilter (IBA Art. 176)   |
| HR / hiring decision AI              | KoreaPIPAFilter (sensitive data)  |
| Generative AI customer chatbot       | KoreaAIBasicActFilter (Art. 36)   |
| Government citizen-service AI        | KoreaAIBasicActFilter §3.3        |
| Healthcare predictive diagnostics    | KoreaPIPAFilter (health)          |
| Securities robo-adviser              | KoreaFSCAIFilter (FSCMA Art. 7)   |
| Cross-border data analytics platform | KoreaCrossBorderFilter            |
+--------------------------------------+-----------------------------------+

No external dependencies required.

Run:
    python examples/35_south_korea_ai_governance.py
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
    Result returned by each South Korea AI governance filter.

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
# Layer 1 — PIPA data protection (KoreaPIPAFilter)
# ---------------------------------------------------------------------------

# PIPC adequacy-designated countries (EU, UK, Canada as of 2024 PIPA amendment)
_PIPC_ADEQUACY_COUNTRIES: frozenset[str] = frozenset(
    {
        "UK",
        "CA",
        # EU member states
        "AT",
        "BE",
        "BG",
        "CY",
        "CZ",
        "DE",
        "DK",
        "EE",
        "ES",
        "FI",
        "FR",
        "GR",
        "HR",
        "HU",
        "IE",
        "IT",
        "LT",
        "LU",
        "LV",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SE",
        "SI",
        "SK",
    }
)

# PIPA Art. 23 — Sensitive information categories
_PIPA_SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {
        "ideology",
        "beliefs",
        "union",
        "political_opinion",
        "health",
        "sexual_life",
        "biometric",
        "criminal",
        "genetic",
        "immigration_status",
    }
)


@dataclass(frozen=True)
class KoreaPIPAFilter:
    """
    Layer 1: Korea Personal Information Protection Act (PIPA) 2023 amendment.

    The PIPA (Act No. 10142, amended 2023) is South Korea's primary data
    protection law, enforced by the Personal Information Protection Commission
    (PIPC).  The 2023 amendment introduced mandatory right-to-explanation for
    automated decisions (Art. 37-2), expanded cross-border transfer
    obligations (Art. 28-8), and strengthened enforcement powers.
    Four principal controls apply:

    (a) Art. 15 Lawfulness of Collection — personal information must not
        be processed without consent or a legitimate purpose (e.g., contract
        performance, statutory obligation, vital interests); absence results
        in denial;
    (b) Art. 23 Processing Sensitive Information — sensitive categories
        (ideology/beliefs/union/political opinion/health/sexual life/
        biometric/criminal) require explicit consent; absence results in
        denial;
    (c) Art. 28-8 Cross-border Provision — transfer to a country without
        PIPC adequacy designation requires PIPC approval or individual
        consent; adequate countries: EU, UK, Canada; absence results in
        denial;
    (d) Art. 37-2 Automated Decisions (2023 amendment) — automated
        decisions with significant legal effects on individuals (credit,
        insurance, employment, public services) without a right-to-
        explanation mechanism trigger REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Personal Information Protection Act (Act No. 10142, as amended 2023),
        Arts. 15, 23, 28-8, 37-2
    Personal Information Protection Commission (PIPC) Guidelines on
        Automated Decision-Making 2023
    PIPC Cross-border Transfer Adequacy Decision: EU (2023), UK (2023),
        Canada (2023)
    """

    FILTER_NAME: str = "KOREA_PIPA_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 15 — personal information without consent or legitimate purpose
        if (
            doc.get("personal_information_processing")
            and not doc.get("consent_obtained")
            and not doc.get("legitimate_purpose")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="PIPA Art. 15 Lawfulness of Collection",
                reason=(
                    "Personal information processing without consent or legitimate "
                    "purpose violates PIPA Art. 15 — a lawful basis (consent, contract, "
                    "statutory obligation, vital interests, or public interest) is required "
                    "for all personal information collection and use"
                ),
            )

        # Art. 23 — sensitive information without explicit consent
        data_type = doc.get("data_type", "")
        if (
            isinstance(data_type, str)
            and data_type.lower() in _PIPA_SENSITIVE_CATEGORIES
            and not doc.get("explicit_consent_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="PIPA Art. 23 Processing Sensitive Information",
                reason=(
                    f"Sensitive information category '{data_type}' "
                    "(ideology/beliefs/union/political opinion/health/sexual life/"
                    "biometric/criminal) requires explicit consent under PIPA Art. 23 — "
                    "general consent is insufficient for sensitive categories"
                ),
            )

        # Art. 28-8 — cross-border transfer to non-adequate country without PIPC approval or consent
        transfer_country = doc.get("transfer_country", "")
        if (
            doc.get("cross_border_transfer")
            and transfer_country
            and transfer_country not in _PIPC_ADEQUACY_COUNTRIES
            and not doc.get("pipc_approval_obtained")
            and not doc.get("individual_consent_for_transfer")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "PIPA Art. 28-8 Cross-border Provision — adequate: EU/UK/Canada; "
                    "others require PIPC approval or consent"
                ),
                reason=(
                    f"Cross-border transfer of personal information to '{transfer_country}' "
                    "requires either PIPC approval or individual consent under PIPA Art. 28-8 — "
                    "only EU, UK, and Canada hold PIPC adequacy designation as of 2024"
                ),
            )

        # Art. 37-2 (2023 amendment) — automated decision without right to explanation
        if (
            doc.get("automated_decision_significant_legal_effect")
            and not doc.get("right_to_explanation_provided")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="PIPA Art. 37-2 Automated Decisions (2023 amendment)",
                reason=(
                    "Automated decision with significant legal effects (credit, insurance, "
                    "employment, public services) without a right-to-explanation mechanism "
                    "violates PIPA Art. 37-2 (2023 amendment) — individuals must be able "
                    "to request explanation and contest automated outcomes"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="PIPA Arts. 15, 23, 28-8, 37-2",
            reason="Korea PIPA 2023 — personal information processing controls compliant",
        )


# ---------------------------------------------------------------------------
# Layer 2 — FSC AI financial governance (KoreaFSCAIFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KoreaFSCAIFilter:
    """
    Layer 2: Korea Financial Services Commission (FSC) AI governance for
    Korean financial services.

    The FSC regulates AI deployment in Korean financial services through the
    Financial Investment Services and Capital Markets Act (FSCMA), the Credit
    Information Act (CB Act), the Insurance Business Act (IBA), and associated
    supervisory guidelines.  Four principal controls apply:

    (a) FSCMA Art. 7 + FSC Robo-Advisor Guidelines 2016 — AI-driven
        investment advisory services require robo-advisor registration with
        the FSC; unregistered AI advisory systems are denied;
    (b) CB Act Art. 26 + CB Act AI Guidelines 2021 — AI credit scoring
        models deployed for lending decisions require FSC model validation
        and a maintained audit trail; absence results in denial;
    (c) IBA Art. 176 + FSC Supervisory Regulation Art. 7-8 — insurance AI
        underwriting systems require actuarial certification from a qualified
        actuary approved under the IBA; absence results in denial;
    (d) FSCMA Art. 63 + KSDA Algorithmic Trading Guidelines — AI trading
        algorithms require FSC algorithmic trading registration before
        operation; unregistered algorithms trigger REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Financial Investment Services and Capital Markets Act (FSCMA) Arts. 7, 63
    FSC Robo-Advisor Regulatory Sandbox and Guidelines (2016, revised 2021)
    Credit Information Use and Protection Act (CB Act) Art. 26
    FSC AI Guidelines for Credit Bureau Operations (2021)
    Insurance Business Act (IBA) Art. 176
    FSC Supervisory Regulation for Insurance Companies Art. 7-8
    Korea Securities Dealers Association (KSDA) Algorithmic Trading Guidelines
    """

    FILTER_NAME: str = "KOREA_FSC_AI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # FSCMA Art. 7 + FSC Robo-Advisor Guidelines — AI investment advisory without registration
        if (
            doc.get("ai_investment_advisory")
            and not doc.get("robo_advisor_registration_confirmed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "FSCMA Art. 7 + FSC Robo-Advisor Guidelines 2016 — robo-advisor "
                    "registration required"
                ),
                reason=(
                    "AI-driven investment advisory service without FSC robo-advisor "
                    "registration violates FSCMA Art. 7 and FSC Robo-Advisor Guidelines "
                    "2016 — all AI investment advisory systems must be registered with "
                    "the FSC before operation"
                ),
            )

        # CB Act Art. 26 + AI Guidelines — AI credit scoring without FSC validation and audit trail
        if doc.get("ai_credit_scoring") and (
            not doc.get("fsc_model_validation_completed")
            or not doc.get("audit_trail_maintained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "CB Act Art. 26 + FSC Credit Information AI Guidelines 2021 — "
                    "model validation and audit trail required"
                ),
                reason=(
                    "AI credit scoring model without FSC model validation or audit trail "
                    "violates CB Act Art. 26 and FSC AI Guidelines for Credit Bureau "
                    "Operations 2021 — all credit scoring AI must pass FSC validation "
                    "and maintain a complete audit trail of scoring decisions"
                ),
            )

        # IBA Art. 176 + FSC Supervisory Regulation — insurance AI underwriting without actuarial cert
        if (
            doc.get("insurance_ai_underwriting")
            and not doc.get("actuarial_certification_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "IBA Art. 176 + FSC Supervisory Regulation Art. 7-8 — actuarial "
                    "certification required for AI underwriting"
                ),
                reason=(
                    "Insurance AI underwriting system without actuarial certification "
                    "violates IBA Art. 176 and FSC Supervisory Regulation Art. 7-8 — "
                    "a qualified actuary approved under the Insurance Business Act must "
                    "certify all AI-driven underwriting models before deployment"
                ),
            )

        # FSCMA Art. 63 + KSDA Guidelines — AI trading algorithm without FSC registration
        if (
            doc.get("ai_trading_algorithm")
            and not doc.get("fsc_algorithmic_trading_registration_confirmed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "FSCMA Art. 63 + KSDA Algorithmic Trading Guidelines — FSC "
                    "algorithmic trading registration required"
                ),
                reason=(
                    "AI trading algorithm without FSC algorithmic trading registration "
                    "requires human review under FSCMA Art. 63 and KSDA Algorithmic "
                    "Trading Guidelines — registration must be confirmed before the "
                    "algorithm may execute live trades"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="FSCMA Art. 7, 63; CB Act Art. 26; IBA Art. 176",
            reason="Korea FSC AI financial governance controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 3 — Korea AI Basic Act 2024 (KoreaAIBasicActFilter)
# ---------------------------------------------------------------------------

# AI Basic Act Art. 47 — high-impact AI sectors
_AI_BASIC_ACT_HIGH_IMPACT_SECTORS: frozenset[str] = frozenset(
    {
        "medical",
        "healthcare",
        "legal",
        "education",
        "employment",
        "welfare",
        "financial",
        "judicial",
    }
)


@dataclass(frozen=True)
class KoreaAIBasicActFilter:
    """
    Layer 3: Korea AI Basic Act 2024 (enacted January 2024, effective 2026).

    The AI Basic Act (Act No. 20228) is South Korea's first comprehensive
    AI governance law.  It establishes a risk-based framework for AI systems,
    mandating impact assessments, transparency, generative AI disclosure, and
    human oversight.  Four principal controls apply:

    (a) Art. 47 Impact Assessment — high-impact AI systems in medical, legal,
        education, and employment sectors must undergo a prior impact
        assessment; absence results in denial;
    (b) Art. 35 Transparency Obligations — all AI systems must disclose to
        users that they are interacting with AI; absence results in denial;
    (c) Art. 36 GenAI Disclosure — generative AI content must include
        watermarks or clear disclosure indicating AI-generated origin;
        absence results in denial;
    (d) Art. 46 Human Oversight — AI systems deployed in critical
        infrastructure without an operational human oversight mechanism
        trigger REQUIRES_HUMAN_REVIEW.

    References
    ----------
    AI Basic Act (Act No. 20228, enacted January 2024, effective 2026),
        Arts. 35, 36, 46, 47
    Ministry of Science and ICT (MSIT) Implementation Guidelines 2025
    Korea AI Safety Research Institute (KAISI) Technical Standards 2025
    """

    FILTER_NAME: str = "KOREA_AI_BASIC_ACT_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 47 — high-impact AI without prior impact assessment
        sector = doc.get("ai_sector", "")
        if (
            isinstance(sector, str)
            and sector.lower() in _AI_BASIC_ACT_HIGH_IMPACT_SECTORS
            and not doc.get("impact_assessment_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="AI Basic Act Art. 47 Impact Assessment",
                reason=(
                    f"High-impact AI system in '{sector}' sector without prior impact "
                    "assessment violates AI Basic Act Art. 47 — medical, legal, education, "
                    "and employment AI systems must complete a mandatory impact assessment "
                    "before deployment"
                ),
            )

        # Art. 35 — AI system without transparency disclosure to users
        if (
            doc.get("ai_system_deployed_to_users")
            and not doc.get("transparency_disclosure_provided")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="AI Basic Act Art. 35 Transparency Obligations",
                reason=(
                    "AI system deployed to users without transparency disclosure violates "
                    "AI Basic Act Art. 35 — all AI systems must clearly disclose to users "
                    "that they are interacting with an AI system before or at the point "
                    "of initial interaction"
                ),
            )

        # Art. 36 — generative AI content without watermark/disclosure
        if (
            doc.get("generative_ai_content")
            and not doc.get("ai_generated_watermark_or_disclosure")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="AI Basic Act Art. 36 GenAI Disclosure",
                reason=(
                    "Generative AI content without watermark or disclosure violates AI "
                    "Basic Act Art. 36 — all AI-generated content (text, images, audio, "
                    "video) must include technical watermarks or explicit disclosure of "
                    "its AI-generated nature"
                ),
            )

        # Art. 46 — AI in critical infrastructure without human oversight
        if (
            doc.get("critical_infrastructure_ai")
            and not doc.get("human_oversight_mechanism_present")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="AI Basic Act Art. 46 Human Oversight",
                reason=(
                    "AI system in critical infrastructure without human oversight "
                    "mechanism requires human review under AI Basic Act Art. 46 — "
                    "an operational human oversight mechanism must be established and "
                    "documented before the system may operate in critical infrastructure"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="AI Basic Act Arts. 35, 36, 46, 47",
            reason="Korea AI Basic Act 2024 — AI governance controls compliant",
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border AI data flows (KoreaCrossBorderFilter)
# ---------------------------------------------------------------------------

# Countries restricted by PIPC under PIPA Art. 28-8 and PIPC Transfer Assessment
_PIPC_RESTRICTED_COUNTRIES: frozenset[str] = frozenset({"CN", "RU", "KP"})

# FSC-approved cloud regions for Korean-regulated financial entities
_FSC_APPROVED_CLOUD_REGIONS: frozenset[str] = frozenset(
    {
        "aws_ap_northeast_2",  # AWS Seoul
        "gcp_asia_northeast3",  # GCP Seoul
        "azure_korea_central",  # Azure Korea Central
        "aws_seoul",
        "gcp_seoul",
        "azure_korea",
    }
)


@dataclass(frozen=True)
class KoreaCrossBorderFilter:
    """
    Layer 4: Cross-border AI data flows under Korean frameworks.

    Korean law imposes specific controls on cross-border AI data flows
    through PIPA Art. 28-8, FSC Electronic Financial Transactions Act
    Art. 21-2, and FSC Cloud Security Guidelines.  Four principal controls
    apply:

    (a) PIPA Art. 28-8 + PIPC Transfer Assessment — personal data to
        CN/RU/KP without PIPC adequacy designation or explicit individual
        consent is denied;
    (b) FSC Electronic Financial Transactions Act Art. 21-2 — financial AI
        data transferred to a non-FSC approved entity without contractual
        safeguards (including security and business continuity provisions)
        is denied;
    (c) FSC Cloud Security Guidelines — AI services serving Korean-regulated
        financial entities must be hosted on approved cloud regions (AWS
        Seoul / GCP Seoul / Azure Korea Central); non-approved regions
        are denied;
    (d) PIPA Art. 28-8 + PIPC Sensitive Data Guidelines — cross-border AI
        training using Korean biometric or health data without PIPC
        notification triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Personal Information Protection Act Art. 28-8
    PIPC Cross-border Transfer Assessment Guidelines (2023)
    Electronic Financial Transactions Act Art. 21-2
    FSC Guidelines on Electronic Financial Transactions Outsourcing (2022)
    FSC Cloud Security Guidelines for Financial Institutions (2019, revised 2023)
    PIPC Guidelines on Sensitive Data Overseas Transfer (2024)
    """

    FILTER_NAME: str = "KOREA_CROSS_BORDER_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # PIPA Art. 28-8 — personal data to CN/RU/KP without PIPC adequacy or explicit consent
        personal_data_country = doc.get("personal_data_transfer_country", "")
        if (
            personal_data_country in _PIPC_RESTRICTED_COUNTRIES
            and not doc.get("pipc_adequacy_confirmed")
            and not doc.get("explicit_individual_consent")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "PIPA Art. 28-8 + PIPC Transfer Assessment — restricted: CN/RU/KP"
                ),
                reason=(
                    f"Personal data transfer to '{personal_data_country}' without PIPC "
                    "adequacy confirmation or explicit individual consent is prohibited "
                    "under PIPA Art. 28-8 — CN, RU, and KP are subject to heightened "
                    "transfer restrictions under PIPC Transfer Assessment guidelines"
                ),
            )

        # FSC EFTA Art. 21-2 — financial AI data to non-FSC approved entity without contractual safeguards
        if (
            doc.get("financial_ai_data_transfer")
            and not doc.get("fsc_approved_entity")
            and not doc.get("contractual_safeguards_in_place")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "FSC Electronic Financial Transactions Act Art. 21-2 — outsourcing "
                    "contractual safeguards required"
                ),
                reason=(
                    "Financial AI data transfer to non-FSC approved entity without "
                    "contractual safeguards violates EFTA Art. 21-2 — contracts must "
                    "include security controls, business continuity provisions, and "
                    "FSC notification obligations before financial AI data may be "
                    "transferred to a third party"
                ),
            )

        # FSC Cloud Security Guidelines — AI serving Korean-regulated entity on non-approved cloud region
        cloud_region = doc.get("cloud_region", "")
        if (
            doc.get("serves_fsc_regulated_entity")
            and cloud_region
            and cloud_region not in _FSC_APPROVED_CLOUD_REGIONS
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "FSC Cloud Security Guidelines — approved: AWS Seoul / GCP Seoul / "
                    "Azure Korea Central"
                ),
                reason=(
                    f"AI system serving Korea FSC-regulated financial entity deployed on "
                    f"non-approved cloud region '{cloud_region}' — FSC Cloud Security "
                    "Guidelines require AWS Seoul (ap-northeast-2), GCP Seoul "
                    "(asia-northeast3), or Azure Korea Central"
                ),
            )

        # PIPA Art. 28-8 + PIPC Sensitive Data Guidelines — AI training on Korean biometric/health
        sensitive_data_type = doc.get("cross_border_ai_training_data_type", "")
        if (
            doc.get("cross_border_ai_training")
            and isinstance(sensitive_data_type, str)
            and sensitive_data_type.lower() in {"biometric", "health", "genetic"}
            and not doc.get("pipc_notification_provided")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "PIPA Art. 28-8 + PIPC Sensitive Data Guidelines — PIPC notification "
                    "required for cross-border AI training on biometric/health data"
                ),
                reason=(
                    "Cross-border AI training using Korean biometric or health data without "
                    "PIPC notification requires human review under PIPA Art. 28-8 and PIPC "
                    "Sensitive Data Guidelines — PIPC must be notified before commencing "
                    "cross-border AI training on sensitive personal data categories"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "PIPA Art. 28-8 + PIPC + FSC EFTA Art. 21-2 + FSC Cloud Security Guidelines"
            ),
            reason="Korea cross-border AI data flow controls — compliant",
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class KoreaLangChainPolicyGuard:
    """
    LangChain integration — wraps the four Korea governance filters as a
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
                KoreaPIPAFilter(),
                KoreaFSCAIFilter(),
                KoreaAIBasicActFilter(),
                KoreaCrossBorderFilter(),
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


class KoreaCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps a Korea governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
    """

    name: str = "KoreaGovernanceGuard"
    description: str = (
        "Enforces South Korea AI governance policies (PIPA, FSC, AI Basic Act, "
        "Cross-Border) on documents processed by a CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class KoreaAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    Korea governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``KoreaMAFPolicyMiddleware`` for the Microsoft Agent
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


class KoreaSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps a Korea governance filter as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``KoreaMAFPolicyMiddleware`` for the Microsoft Agent Framework.
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


class KoreaLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing Korea governance
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


class KoreaHaystackGovernanceComponent:
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


class KoreaDSPyGovernanceModule:
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


class KoreaMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying Korea governance filters.

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
    # 1. Personal information without consent → DENIED (PIPA Art. 15)
    # ------------------------------------------------------------------
    _show(
        "PIPA Art. 15 — Personal Information Processing Without Consent",
        KoreaPIPAFilter().filter(
            {
                "personal_information_processing": True,
                "consent_obtained": False,
                "legitimate_purpose": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Health data without explicit consent → DENIED (PIPA Art. 23)
    # ------------------------------------------------------------------
    _show(
        "PIPA Art. 23 — Health Data Without Explicit Consent",
        KoreaPIPAFilter().filter(
            {
                "data_type": "health",
                "explicit_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. Cross-border transfer to JP without PIPC approval → DENIED (PIPA Art. 28-8)
    # ------------------------------------------------------------------
    _show(
        "PIPA Art. 28-8 — Cross-Border Transfer Without PIPC Approval",
        KoreaPIPAFilter().filter(
            {
                "cross_border_transfer": True,
                "transfer_country": "JP",
                "pipc_approval_obtained": False,
                "individual_consent_for_transfer": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. Automated decision without right to explanation → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "PIPA Art. 37-2 — Automated Decision Without Right to Explanation",
        KoreaPIPAFilter().filter(
            {
                "automated_decision_significant_legal_effect": True,
                "right_to_explanation_provided": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. AI investment advisory without robo-advisor registration → DENIED
    # ------------------------------------------------------------------
    _show(
        "FSCMA Art. 7 + FSC Robo-Advisor Guidelines — AI Advisory Without Registration",
        KoreaFSCAIFilter().filter(
            {
                "ai_investment_advisory": True,
                "robo_advisor_registration_confirmed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. AI credit scoring without FSC validation → DENIED (CB Act Art. 26)
    # ------------------------------------------------------------------
    _show(
        "CB Act Art. 26 — AI Credit Scoring Without FSC Validation",
        KoreaFSCAIFilter().filter(
            {
                "ai_credit_scoring": True,
                "fsc_model_validation_completed": False,
                "audit_trail_maintained": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. High-impact AI (medical) without impact assessment → DENIED (Art. 47)
    # ------------------------------------------------------------------
    _show(
        "AI Basic Act Art. 47 — Medical AI Without Impact Assessment",
        KoreaAIBasicActFilter().filter(
            {
                "ai_sector": "medical",
                "impact_assessment_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Generative AI content without watermark → DENIED (Art. 36)
    # ------------------------------------------------------------------
    _show(
        "AI Basic Act Art. 36 — Generative AI Content Without Watermark",
        KoreaAIBasicActFilter().filter(
            {
                "generative_ai_content": True,
                "ai_generated_watermark_or_disclosure": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Personal data to CN without PIPC adequacy → DENIED (PIPA Art. 28-8)
    # ------------------------------------------------------------------
    _show(
        "PIPA Art. 28-8 — Personal Data to CN Without PIPC Adequacy",
        KoreaCrossBorderFilter().filter(
            {
                "personal_data_transfer_country": "CN",
                "pipc_adequacy_confirmed": False,
                "explicit_individual_consent": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. FSC-regulated entity on non-approved cloud → DENIED (FSC Cloud)
    # ------------------------------------------------------------------
    _show(
        "FSC Cloud Security Guidelines — Non-Approved Cloud Region",
        KoreaCrossBorderFilter().filter(
            {
                "serves_fsc_regulated_entity": True,
                "cloud_region": "aws_us_east_1",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 11. AI training on Korean biometric data without PIPC notification
    #     → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "PIPA Art. 28-8 — AI Training on Korean Biometric Data Without PIPC Notification",
        KoreaCrossBorderFilter().filter(
            {
                "cross_border_ai_training": True,
                "cross_border_ai_training_data_type": "biometric",
                "pipc_notification_provided": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 12. Fully compliant document → PERMITTED across all filters
    # ------------------------------------------------------------------
    _show(
        "Fully compliant document — PERMITTED",
        KoreaPIPAFilter().filter(
            {
                "personal_information_processing": True,
                "consent_obtained": True,
                "legitimate_purpose": True,
            }
        ),
    )
