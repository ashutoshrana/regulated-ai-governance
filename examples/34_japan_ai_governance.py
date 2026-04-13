"""
34_japan_ai_governance.py — Japan AI Governance Framework

Implements governance filters for Japan's comprehensive AI regulatory
ecosystem covering the Act on Protection of Personal Information (APPI)
2022 amendment, the Financial Services Agency (FSA) AI governance
framework for financial services, the Cabinet Office AI Strategy 2022
combined with METI AI Governance Guidelines v1.1, and Japan's cross-border
data-flow obligations under APPI and FSA frameworks.

Demonstrates a multi-layer governance framework where four independent
filters enforce distinct requirements of the Japan regulatory landscape:

    Layer 1  — APPI data protection (JapanAPPIFilter):

               APPI Art. 15 Purpose Specification + Art. 17 Acquisition
                   by Deception — personal information processed without
                   consent or legitimate purpose is denied;
               APPI Art. 20 Prohibition on Acquisition of Specially
                   Considered PI — sensitive categories (race/creed/social
                   status/medical/criminal/disability) without explicit
                   consent are denied;
               APPI Art. 28 Cross-border Transfer — transfer to countries
                   without PPC adequacy designation (EU, UK; others require
                   individual consent or equivalent protection) without
                   consent is denied;
               APPI Art. 23 Disclosure + PPC AI Guidelines 2023 §3.2 —
                   automated profiling affecting individual rights without
                   an opt-out mechanism triggers REQUIRES_HUMAN_REVIEW.

    Layer 2  — FSA AI financial governance (JapanFSAAIFilter):

               Financial Instruments and Exchange Act Art. 40 Suitability
                   Principle — AI-driven financial product recommendation
                   without suitability documentation is denied;
               FSA Guidelines for Customer-Oriented Business Conduct 2017
                   Principle 3 — AI credit scoring without explainability
                   to borrower is denied;
               Insurance Business Act Art. 113 + FSA Supervisory
                   Guidelines III-2-9 — insurance AI underwriting without
                   Actuarial Opinion and Documentation is denied;
               FSA Supervisory Guidelines Financial Conglomerates — AI
                   financial model without FSA Stress Testing under
                   systemic risk scenarios triggers REQUIRES_HUMAN_REVIEW.

    Layer 3  — METI / Cabinet Office AI governance (JapanAIGovernanceFilter):

               METI AI Governance Guideline v1.1 §4 — high-impact AI
                   system without METI self-assessment (10 governance
                   items) is denied;
               Japan AI Strategy 2022 §2.1 + METI Guideline v1.1 §4.8 —
                   AI system without human oversight mechanism is denied;
               METI Generative AI Guidelines 2023 §3 — generative AI
                   without METI GenAI compliance documentation (8
                   principles) is denied;
               Cabinet Office AI Utilization Strategy §3.3 — AI for
                   public services without risk assessment triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 4  — Cross-border AI data flows (JapanCrossBorderFilter):

               APPI Art. 28 + PPC Transfer Assessment — personal data to
                   CN/RU/KP without PPC adequacy or equivalent protection
                   is denied;
               Japan Anti-Money Laundering Act FIEA + FSA AML/CFT
                   guidelines — financial AI data to non-FATF compliant
                   jurisdiction is denied;
               FSA Cloud Governance Framework — AI system serving
                   Japan-regulated financial entities hosted on a
                   non-approved cloud region (approved: AWS Tokyo / GCP
                   Tokyo / Azure Japan East) is denied;
               APPI Art. 28 + PPC US adequacy pending — personal data of
                   Japanese nationals to US without consent or SCCs
                   equivalent triggers REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+--------------------------------------+-----------------------------------+
| Use case                             | Primary filters applied           |
+--------------------------------------+-----------------------------------+
| Retail banking credit scoring AI     | JapanFSAAIFilter, CrossBorder     |
| Insurance AI underwriting platform   | JapanFSAAIFilter (Act 113)        |
| HR / hiring decision AI              | JapanAPPIFilter (sensitive data)  |
| Generative AI customer chatbot       | JapanAIGovernanceFilter (GenAI)   |
| Government citizen-service AI        | JapanAIGovernanceFilter §3.3      |
| Healthcare predictive diagnostics    | JapanAPPIFilter (medical)         |
| Securities robo-adviser              | JapanFSAAIFilter (FIEA Art. 40)   |
| Cross-border data analytics platform | JapanCrossBorderFilter            |
+--------------------------------------+-----------------------------------+

No external dependencies required.

Run:
    python examples/34_japan_ai_governance.py
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
    Result returned by each Japan AI governance filter.

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
# Layer 1 — APPI data protection (JapanAPPIFilter)
# ---------------------------------------------------------------------------

# PPC adequacy-designated countries (EU/UK as of 2024 amendment; others
# require individual consent or equivalent protection under APPI Art. 28)
_APPI_ADEQUACY_COUNTRIES: frozenset[str] = frozenset(
    {
        "UK",
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

# APPI Art. 20 — Specially Considered Personal Information (sensitive)
_APPI_SPECIALLY_CONSIDERED_PI: frozenset[str] = frozenset(
    {
        "race",
        "creed",
        "social_status",
        "medical",
        "health",
        "criminal",
        "disability",
        "sexual_orientation",
        "religion",
    }
)


@dataclass(frozen=True)
class JapanAPPIFilter:
    """
    Layer 1: Japan Act on Protection of Personal Information (APPI) 2022 amendment.

    The APPI (Act No. 57 of 2003, substantially amended 2022) regulates the
    handling of personal information by business operators.  The 2022
    amendment strengthened cross-border transfer rules, added opt-out
    obligations for third-party provision, and aligned enforcement with GDPR
    adequacy standards.  Four principal controls apply:

    (a) Art. 15 Purpose Specification + Art. 17 Acquisition by Deception —
        personal information must not be processed without consent or a
        legitimate purpose; absence results in denial;
    (b) Art. 20 Prohibition on Acquisition of Specially Considered PI —
        sensitive categories (race/creed/social status/medical/criminal/
        disability) require explicit consent; absence results in denial;
    (c) Art. 28 Cross-border Transfer — transfer to countries without PPC
        adequacy designation requires individual consent or equivalent
        protection; the PPC adequacy list includes EU and UK; absence of
        consent for non-adequate countries results in denial;
    (d) Art. 23 Disclosure + PPC AI Guidelines 2023 §3.2 — automated
        profiling affecting individual rights (e.g., credit, insurance,
        employment) without an opt-out mechanism triggers
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Act on Protection of Personal Information (Act No. 57 of 2003),
        as amended 2022 (effective April 1, 2022), Arts. 15, 17, 20, 23, 28
    Personal Information Protection Commission (PPC) Guidelines on
        the Use of AI Systems 2023 §3.2
    PPC Cross-border Transfer Adequacy Decision: EU (2019), UK (2021)
    """

    FILTER_NAME: str = "JAPAN_APPI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 15 + Art. 17 — personal information without consent or legitimate purpose
        if (
            doc.get("personal_information_processing")
            and not doc.get("consent_obtained")
            and not doc.get("legitimate_purpose")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="APPI Art. 15 Purpose Specification + Art. 17 Acquisition by Deception",
                reason=(
                    "Personal information processing without consent or legitimate purpose "
                    "violates APPI Art. 15 (Purpose Specification) and Art. 17 (Prohibition "
                    "on Acquisition by Deception or Other Improper Means)"
                ),
            )

        # Art. 20 — Specially Considered Personal Information without explicit consent
        data_type = doc.get("data_type", "")
        if (
            isinstance(data_type, str)
            and data_type.lower() in _APPI_SPECIALLY_CONSIDERED_PI
            and not doc.get("explicit_consent_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="APPI Art. 20 Prohibition on Acquisition of Specially Considered PI",
                reason=(
                    f"Specially Considered Personal Information category '{data_type}' "
                    "(race/creed/social status/medical/criminal/disability) requires "
                    "explicit consent under APPI Art. 20"
                ),
            )

        # Art. 28 — cross-border transfer to non-adequate country without consent
        transfer_country = doc.get("transfer_country", "")
        if (
            doc.get("cross_border_transfer")
            and transfer_country
            and transfer_country not in _APPI_ADEQUACY_COUNTRIES
            and not doc.get("individual_consent_for_transfer")
            and not doc.get("equivalent_protection_confirmed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="APPI Art. 28 Cross-border Transfer — PPC adequacy list: EU/UK",
                reason=(
                    f"Cross-border transfer of personal information to '{transfer_country}' "
                    "requires individual consent or equivalent protection confirmation under "
                    "APPI Art. 28 — country lacks PPC adequacy designation "
                    "(adequate countries: EU member states, UK)"
                ),
            )

        # Art. 23 + PPC AI Guidelines 2023 §3.2 — automated profiling without opt-out
        if (
            doc.get("automated_profiling_affecting_rights")
            and not doc.get("opt_out_mechanism_provided")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="APPI Art. 23 Disclosure + PPC AI Guidelines 2023 §3.2",
                reason=(
                    "Automated profiling affecting individual rights (credit/insurance/"
                    "employment) without an opt-out mechanism — APPI Art. 23 Disclosure "
                    "and PPC AI Guidelines 2023 §3.2 require human review and opt-out option"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="APPI 2022",
            reason="APPI personal information protection obligations — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 2 — FSA AI financial governance (JapanFSAAIFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JapanFSAAIFilter:
    """
    Layer 2: Japan Financial Services Agency (FSA) AI governance for
    financial services.

    The FSA oversees the responsible use of AI in Japan's financial sector
    through the Financial Instruments and Exchange Act (FIEA), the Insurance
    Business Act, and supervisory guidelines on customer-oriented business
    conduct.  Four principal controls apply:

    (a) FIEA Art. 40 Suitability Principle — AI-driven financial product
        recommendations must be accompanied by documented suitability
        assessment confirming the product matches the customer's knowledge,
        experience, financial condition, and purpose; absence results in
        denial;
    (b) FSA Guidelines for Customer-Oriented Business Conduct 2017
        Principle 3 — AI credit scoring must include explainability
        documentation enabling the borrower to understand the basis of
        the decision; absence results in denial;
    (c) Insurance Business Act Art. 113 + FSA Supervisory Guidelines
        III-2-9 — AI-driven insurance underwriting must be accompanied by
        an Actuarial Opinion and Documentation validating model soundness;
        absence results in denial;
    (d) FSA Supervisory Guidelines (Financial Conglomerates) — AI
        financial models must demonstrate compliance with FSA Stress
        Testing requirements under systemic risk scenarios; absence
        triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Financial Instruments and Exchange Act (Act No. 25 of 1948) Art. 40
    FSA Guidelines for Customer-Oriented Business Conduct (2017) Principle 3
    Insurance Business Act (Act No. 105 of 1995) Art. 113
    FSA Supervisory Guidelines: Insurance Company Examination (III-2-9)
    FSA Supervisory Guidelines: Financial Conglomerates — Stress Testing
    """

    FILTER_NAME: str = "JAPAN_FSA_AI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # FIEA Art. 40 — AI financial product recommendation without suitability documentation
        if (
            doc.get("ai_financial_product_recommendation")
            and not doc.get("suitability_documentation_present")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="Financial Instruments and Exchange Act Art. 40 Suitability Principle",
                reason=(
                    "AI-driven financial product recommendation without suitability "
                    "documentation violates FIEA Art. 40 Suitability Principle — must "
                    "document that the product matches the customer's knowledge, experience, "
                    "financial condition, and investment purpose"
                ),
            )

        # FSA Customer-Oriented Business Conduct Principle 3 — AI credit scoring without explainability
        if (
            doc.get("ai_credit_scoring")
            and not doc.get("explainability_to_borrower_documented")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="FSA Guidelines for Customer-Oriented Business Conduct 2017 Principle 3",
                reason=(
                    "AI credit scoring without explainability documentation to the borrower "
                    "violates FSA Customer-Oriented Business Conduct Guidelines 2017 "
                    "Principle 3 — borrower must be able to understand the basis of the "
                    "credit decision"
                ),
            )

        # Insurance Business Act Art. 113 + FSA Supervisory III-2-9 — AI underwriting without Actuarial Opinion
        if (
            doc.get("ai_insurance_underwriting")
            and not doc.get("actuarial_opinion_and_documentation_present")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "Insurance Business Act Art. 113 + FSA Supervisory Guidelines III-2-9"
                ),
                reason=(
                    "Insurance AI underwriting without Actuarial Opinion and Documentation "
                    "violates Insurance Business Act Art. 113 and FSA Supervisory Guidelines "
                    "III-2-9 — model soundness must be validated by qualified actuary"
                ),
            )

        # FSA Supervisory Guidelines (Financial Conglomerates) — AI model without FSA Stress Testing
        if (
            doc.get("ai_financial_model_in_production")
            and not doc.get("fsa_stress_testing_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "FSA Supervisory Guidelines: Financial Conglomerates — Stress Testing"
                ),
                reason=(
                    "AI financial model without FSA Stress Testing under systemic risk "
                    "scenarios — FSA Supervisory Guidelines for Financial Conglomerates "
                    "require stress testing before deployment; human review mandatory"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="FSA AI Governance Framework (FIEA Art. 40 + Customer-Oriented Conduct + IBA Art. 113)",
            reason="FSA AI financial governance obligations — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 3 — METI / Cabinet Office AI governance (JapanAIGovernanceFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JapanAIGovernanceFilter:
    """
    Layer 3: Japan Cabinet Office AI Strategy 2022 + METI AI Governance
    Guidelines v1.1.

    Japan's AI governance framework is co-ordinated between the Cabinet
    Office (AI Strategy 2022, Human-Centered AI principles) and the Ministry
    of Economy, Trade and Industry (METI AI Governance Guidelines v1.1,
    METI Generative AI Guidelines 2023).  Together they establish a voluntary
    but de facto governance baseline for AI systems.  Four principal controls
    apply:

    (a) METI AI Governance Guideline v1.1 §4 — high-impact AI systems must
        complete a METI self-assessment against the 10 governance items
        (safety, security, fairness, privacy, transparency, accountability,
        innovation, human oversight, diversity, and wellbeing); absence
        results in denial;
    (b) Japan AI Strategy 2022 §2.1 + METI Guideline v1.1 §4.8 — AI
        systems must incorporate a human oversight mechanism enabling
        intervention, correction, and shutdown; absence results in denial;
    (c) METI Generative AI Guidelines 2023 §3 — generative AI systems must
        document compliance with the 8 METI GenAI principles (safety,
        security, privacy, transparency, fairness, accountability,
        innovation, and human-centeredness); absence results in denial;
    (d) Cabinet Office AI Utilization Strategy §3.3 — AI systems for
        public services must complete a Cabinet Office risk assessment
        before deployment; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Japan AI Strategy 2022 (Cabinet Office, April 2022) §§2.1, 3.3
    METI AI Governance Guidelines for Implementation v1.1 (2022) §§4, 4.8
    METI Governance Guidelines for Utilization of AI Technology by
        Businesses (Generative AI) 2023 §3
    Cabinet Office AI Utilization Strategy §3.3
    """

    FILTER_NAME: str = "JAPAN_AI_GOVERNANCE_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # METI AI Governance Guideline v1.1 §4 — high-impact AI without METI self-assessment
        if (
            doc.get("high_impact_ai_system")
            and not doc.get("meti_ai_governance_self_assessment_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="METI AI Governance Guideline v1.1 §4 — 10 governance items",
                reason=(
                    "High-impact AI system without METI AI Governance Guideline v1.1 §4 "
                    "self-assessment — must complete assessment against all 10 governance "
                    "items (safety, security, fairness, privacy, transparency, "
                    "accountability, innovation, human oversight, diversity, wellbeing)"
                ),
            )

        # Japan AI Strategy 2022 §2.1 + METI v1.1 §4.8 — AI system without human oversight
        if (
            doc.get("ai_system_deployed")
            and not doc.get("human_oversight_mechanism_present")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="Japan AI Strategy 2022 §2.1 Human-centered AI + METI Guideline v1.1 §4.8",
                reason=(
                    "AI system without human oversight mechanism violates Japan AI Strategy "
                    "2022 §2.1 (Human-centered AI) and METI AI Governance Guideline v1.1 §4.8 "
                    "— must implement intervention, correction, and shutdown capabilities"
                ),
            )

        # METI Generative AI Guidelines 2023 §3 — generative AI without compliance documentation
        if (
            doc.get("generative_ai_system")
            and not doc.get("meti_genai_guidelines_compliance_documented")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="METI Generative AI Guidelines 2023 §3 — 8 principles",
                reason=(
                    "Generative AI system without METI Generative AI Guidelines 2023 §3 "
                    "compliance documentation — must document compliance with all 8 METI "
                    "GenAI principles (safety, security, privacy, transparency, fairness, "
                    "accountability, innovation, human-centeredness)"
                ),
            )

        # Cabinet Office AI Utilization Strategy §3.3 — public services AI without risk assessment
        if (
            doc.get("ai_for_public_services")
            and not doc.get("cabinet_office_risk_assessment_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="Cabinet Office AI Utilization Strategy §3.3",
                reason=(
                    "AI system for public services without Cabinet Office AI Utilization "
                    "Strategy §3.3 risk assessment — human review required before deployment "
                    "to ensure alignment with national AI strategy and public interest"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "Japan AI Strategy 2022 + METI AI Governance Guidelines v1.1 + "
                "METI GenAI Guidelines 2023"
            ),
            reason="Japan AI governance (METI + Cabinet Office) obligations — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border AI data flows (JapanCrossBorderFilter)
# ---------------------------------------------------------------------------

_PPC_RESTRICTED_COUNTRIES: frozenset[str] = frozenset({"CN", "RU", "KP"})

_FSA_APPROVED_CLOUD_REGIONS: frozenset[str] = frozenset(
    {
        "aws_tokyo",
        "gcp_tokyo",
        "azure_japan_east",
    }
)

_FATF_NON_COMPLIANT_JURISDICTIONS: frozenset[str] = frozenset(
    {
        "KP",  # North Korea (FATF blacklist)
        "IR",  # Iran (FATF blacklist)
        "MM",  # Myanmar (grey list)
        "YE",  # Yemen (grey list)
        "SY",  # Syria (grey list)
        "LY",  # Libya (grey list)
    }
)


@dataclass(frozen=True)
class JapanCrossBorderFilter:
    """
    Layer 4: Japan cross-border AI data flow controls.

    Japan's cross-border AI data governance operates under APPI Art. 28
    (PPC adequacy list), the Financial Instruments and Exchange Act /
    Anti-Money Laundering Act for financial data, and the FSA Cloud
    Governance Framework for regulated financial entities.  Four principal
    controls apply:

    (a) APPI Art. 28 + PPC Transfer Assessment — personal data transferred
        to CN/RU/KP (PPC-restricted countries) without PPC adequacy or
        equivalent protection is denied;
    (b) Japan Anti-Money Laundering Act FIEA + FSA AML/CFT guidelines —
        financial AI data transferred to a FATF non-compliant jurisdiction
        is denied;
    (c) FSA Cloud Governance Framework — AI systems serving Japan-regulated
        financial entities must be hosted on an approved cloud region (AWS
        Tokyo / GCP Tokyo / Azure Japan East); non-approved regions result
        in denial;
    (d) APPI Art. 28 + PPC US adequacy pending — personal data of Japanese
        nationals transferred to the US without individual consent or
        SCCs-equivalent safeguards triggers REQUIRES_HUMAN_REVIEW (US is
        not on the PPC adequacy list as of 2024).

    References
    ----------
    Act on Protection of Personal Information (APPI) Art. 28
    PPC Transfer Impact Assessment guidelines
    Japan Act on Prevention of Transfer of Criminal Proceeds (AML Act)
    Financial Instruments and Exchange Act (FIEA) — AML/CFT provisions
    FSA AML/CFT Guidelines (2018, updated 2024)
    FSA Cloud Governance Framework (2023 revision)
    """

    FILTER_NAME: str = "JAPAN_CROSS_BORDER_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # APPI Art. 28 + PPC — personal data to CN/RU/KP without adequacy or equivalent protection
        transfer_country = doc.get("personal_data_transfer_country", "")
        if (
            transfer_country in _PPC_RESTRICTED_COUNTRIES
            and not doc.get("ppc_adequacy_or_equivalent_confirmed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="APPI Art. 28 + PPC Transfer Assessment — restricted: CN/RU/KP",
                reason=(
                    f"Personal data transfer to '{transfer_country}' without PPC adequacy "
                    "designation or equivalent protection confirmation is prohibited under "
                    "APPI Art. 28 — Transfer Impact Assessment required for CN/RU/KP"
                ),
            )

        # Japan AML Act + FSA AML/CFT — financial AI data to FATF non-compliant jurisdiction
        financial_data_jurisdiction = doc.get("financial_ai_data_transfer_jurisdiction", "")
        if financial_data_jurisdiction in _FATF_NON_COMPLIANT_JURISDICTIONS:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="Japan AML Act FIEA + FSA AML/CFT Guidelines",
                reason=(
                    f"Financial AI data transfer to FATF non-compliant jurisdiction "
                    f"'{financial_data_jurisdiction}' is prohibited under the Japan "
                    "Anti-Money Laundering Act and FSA AML/CFT Guidelines — all financial "
                    "AI data flows must comply with FATF standards"
                ),
            )

        # FSA Cloud Governance Framework — financial AI on non-approved cloud region
        cloud_region = doc.get("cloud_region", "")
        if (
            doc.get("serves_fsa_regulated_entity")
            and cloud_region
            and cloud_region not in _FSA_APPROVED_CLOUD_REGIONS
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "FSA Cloud Governance Framework — approved: AWS Tokyo/GCP Tokyo/Azure Japan East"
                ),
                reason=(
                    f"AI system serving Japan FSA-regulated financial entity deployed on "
                    f"non-approved cloud region '{cloud_region}' — FSA Cloud Governance "
                    "Framework requires AWS Tokyo, GCP Tokyo, or Azure Japan East"
                ),
            )

        # APPI Art. 28 + PPC US adequacy pending — Japanese nationals' data to US without safeguards
        if (
            doc.get("japanese_nationals_personal_data")
            and doc.get("transfer_destination") == "US"
            and not doc.get("individual_consent_for_us_transfer")
            and not doc.get("sccs_equivalent_safeguards")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="APPI Art. 28 + PPC US adequacy pending (2024)",
                reason=(
                    "Transfer of Japanese nationals' personal data to the US requires "
                    "individual consent or SCCs-equivalent safeguards under APPI Art. 28 — "
                    "US does not have PPC adequacy designation as of 2024; human review "
                    "required to confirm lawful transfer basis"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="APPI Art. 28 + PPC + Japan AML Act + FSA Cloud Governance",
            reason="Japan cross-border AI data flow controls — compliant",
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class JapanLangChainPolicyGuard:
    """
    LangChain integration — wraps the four Japan governance filters as a
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
            self._filters = [
                JapanAPPIFilter(),
                JapanFSAAIFilter(),
                JapanAIGovernanceFilter(),
                JapanCrossBorderFilter(),
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


class JapanCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps a Japan governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
    """

    name: str = "JapanGovernanceGuard"
    description: str = (
        "Enforces Japan AI governance policies (APPI, FSA, METI/Cabinet Office, "
        "Cross-Border) on documents processed by a CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class JapanAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    Japan governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``JapanMAFPolicyMiddleware`` for the Microsoft Agent
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


class JapanSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps a Japan governance filter as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``JapanMAFPolicyMiddleware`` for the Microsoft Agent Framework.
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


class JapanLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing Japan governance
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


class JapanHaystackGovernanceComponent:
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


class JapanDSPyGovernanceModule:
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


class JapanMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying Japan governance filters.

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
    # 1. Personal information without consent → DENIED (APPI Art. 15+17)
    # ------------------------------------------------------------------
    _show(
        "APPI Art. 15+17 — Personal Information Processing Without Consent",
        JapanAPPIFilter().filter(
            {
                "personal_information_processing": True,
                "consent_obtained": False,
                "legitimate_purpose": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Medical data without explicit consent → DENIED (APPI Art. 20)
    # ------------------------------------------------------------------
    _show(
        "APPI Art. 20 — Medical Data Without Explicit Consent",
        JapanAPPIFilter().filter(
            {
                "data_type": "medical",
                "explicit_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. Cross-border transfer to China without consent → DENIED (APPI Art. 28)
    # ------------------------------------------------------------------
    _show(
        "APPI Art. 28 — Cross-Border Transfer to CN Without Consent",
        JapanAPPIFilter().filter(
            {
                "cross_border_transfer": True,
                "transfer_country": "CN",
                "individual_consent_for_transfer": False,
                "equivalent_protection_confirmed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. Automated profiling without opt-out → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "APPI Art. 23 + PPC AI Guidelines §3.2 — Automated Profiling Without Opt-out",
        JapanAPPIFilter().filter(
            {
                "automated_profiling_affecting_rights": True,
                "opt_out_mechanism_provided": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. AI product recommendation without suitability → DENIED (FIEA Art. 40)
    # ------------------------------------------------------------------
    _show(
        "FIEA Art. 40 — AI Financial Product Recommendation Without Suitability Docs",
        JapanFSAAIFilter().filter(
            {
                "ai_financial_product_recommendation": True,
                "suitability_documentation_present": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. AI credit scoring without explainability → DENIED (FSA Principle 3)
    # ------------------------------------------------------------------
    _show(
        "FSA Principle 3 — AI Credit Scoring Without Explainability",
        JapanFSAAIFilter().filter(
            {
                "ai_credit_scoring": True,
                "explainability_to_borrower_documented": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. High-impact AI without METI self-assessment → DENIED (METI v1.1 §4)
    # ------------------------------------------------------------------
    _show(
        "METI AI Governance Guideline v1.1 §4 — No METI Self-Assessment",
        JapanAIGovernanceFilter().filter(
            {
                "high_impact_ai_system": True,
                "meti_ai_governance_self_assessment_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Generative AI without METI GenAI compliance → DENIED (METI GenAI §3)
    # ------------------------------------------------------------------
    _show(
        "METI GenAI Guidelines 2023 §3 — No GenAI Compliance Documentation",
        JapanAIGovernanceFilter().filter(
            {
                "generative_ai_system": True,
                "meti_genai_guidelines_compliance_documented": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Personal data to CN without PPC adequacy → DENIED (APPI Art. 28)
    # ------------------------------------------------------------------
    _show(
        "APPI Art. 28 — Personal Data to CN Without PPC Adequacy",
        JapanCrossBorderFilter().filter(
            {
                "personal_data_transfer_country": "CN",
                "ppc_adequacy_or_equivalent_confirmed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. FSA-regulated entity on non-approved cloud → DENIED (FSA Cloud)
    # ------------------------------------------------------------------
    _show(
        "FSA Cloud Governance — Non-Approved Cloud Region for FSA-Regulated Entity",
        JapanCrossBorderFilter().filter(
            {
                "serves_fsa_regulated_entity": True,
                "cloud_region": "aws_us_east_1",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 11. Japanese nationals' data to US without safeguards → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "APPI Art. 28 — Japanese Nationals Data to US Without SCCs Equivalent",
        JapanCrossBorderFilter().filter(
            {
                "japanese_nationals_personal_data": True,
                "transfer_destination": "US",
                "individual_consent_for_us_transfer": False,
                "sccs_equivalent_safeguards": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 12. Fully compliant document → PERMITTED across all filters
    # ------------------------------------------------------------------
    _show(
        "Fully compliant document — PERMITTED",
        JapanAPPIFilter().filter(
            {
                "personal_information_processing": True,
                "consent_obtained": True,
                "legitimate_purpose": True,
            }
        ),
    )
