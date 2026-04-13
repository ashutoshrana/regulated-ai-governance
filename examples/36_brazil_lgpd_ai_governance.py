"""
36_brazil_lgpd_ai_governance.py — Brazil AI Governance Framework

Implements governance filters for Brazil's comprehensive AI regulatory
ecosystem covering the Lei Geral de Proteção de Dados (LGPD, Law 13.709/2018),
the Autoridade Nacional de Proteção de Dados (ANPD) AI guidelines, Brazil's
sectoral AI regulations for financial services, health, and telecom, and
cross-border AI data-flow obligations under Brazilian frameworks.

Demonstrates a multi-layer governance framework where four independent
filters enforce distinct requirements of the Brazil regulatory landscape:

    Layer 1  — LGPD data protection (BrazilLGPDFilter):

               LGPD Art. 7 Lawfulness — personal data processing without
                   one of the 10 legal bases (consent/legitimate interest/
                   contract/legal obligation/vital interests/legitimate
                   interests/research/credit protection/health/judicial)
                   is denied;
               LGPD Art. 11 Sensitive Data — sensitive personal data
                   (racial/ethnic origin/religious/political/union/health/
                   sexual/genetic/biometric) without explicit consent or
                   legal obligation is denied;
               LGPD Art. 33 International Transfer — cross-border transfer
                   to country without ANPD adequacy finding or contractual
                   safeguards is denied (adequate: EU/UK; others need
                   standard contractual clauses or BCR);
               LGPD Art. 20 Automated Decisions — automated decision
                   significantly affecting individual rights without review
                   mechanism triggers REQUIRES_HUMAN_REVIEW.

    Layer 2  — ANPD AI guidelines (ANPDAIFilter):

               LGPD Art. 38 + ANPD Resolution CD/ANPD 02/2022 — AI system
                   processing personal data without DPIA where high-risk
                   processing is involved is denied;
               LGPD Art. 9(V) + ANPD AI Guidelines 2023 §4.2 — AI profiling
                   without transparency about automated logic to data
                   subjects is denied;
               LGPD Art. 10 §3 + ANPD Resolution CD/ANPD 02/2022 §6 —
                   legitimate interest as AI processing basis without LIA
                   is denied;
               Lei 12.414/2011 Cadastro Positivo + ANPD credit data
                   guidance — AI credit scoring without SERASA/SCR
                   compliance triggers REQUIRES_HUMAN_REVIEW.

    Layer 3  — Brazil sectoral AI regulations (BrazilSectoralAIFilter):

               CMN Resolution 4.993/2022 + Circular BCB 3.979 — AI in
                   banking/financial services without BCdB algorithmic
                   trading/credit model notification is denied;
               CFM Resolution 2.314/2022 + LGPD Art. 11(II)(f) — AI health
                   system processing patient data without CFM ethical
                   guidelines compliance is denied;
               ANATEL Resolution 740/2020 + ANATEL AI Guidelines 2023 —
                   AI in telecom without ANATEL AI ethics framework
                   compliance is denied;
               TSE Resolution 23.732/2024 — AI-generated electoral content
                   without deepfake labeling triggers REQUIRES_HUMAN_REVIEW.

    Layer 4  — Cross-border AI data flows (BrazilCrossBorderFilter):

               LGPD Art. 33(I)/(II) + ANPD adequacy list — personal data
                   to CN/RU/KP without ANPD adequacy finding or standard
                   contractual clauses is denied;
               Lei 9.613/1998 AML + Coaf Resolution 36/2021 + FATF
                   standards — financial AI data to non-FATF compliant
                   jurisdiction is denied;
               LGPD Art. 33(V) + sectoral regulations — AI system
                   processing Brazilian citizens' data hosted outside
                   Brazil without ANPD authorization is denied;
               LGPD Art. 11 + ANPD Resolution CD/ANPD 02/2022 §8 —
                   cross-border transfer of sensitive biometric data
                   without ANPD notification triggers REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+--------------------------------------+-----------------------------------+
| Use case                             | Primary filters applied           |
+--------------------------------------+-----------------------------------+
| Retail banking credit scoring AI     | BrazilSectoralAIFilter, CrossBorder|
| Insurance AI underwriting platform   | ANPDAIFilter (DPIA), Sectoral     |
| HR / hiring decision AI              | BrazilLGPDFilter (sensitive data) |
| Generative AI customer chatbot       | BrazilLGPDFilter (Art. 20)        |
| Government citizen-service AI        | ANPDAIFilter (transparency)       |
| Healthcare predictive diagnostics    | BrazilSectoralAIFilter (CFM)      |
| Electoral campaign AI                | BrazilSectoralAIFilter (TSE)      |
| Cross-border data analytics platform | BrazilCrossBorderFilter           |
+--------------------------------------+-----------------------------------+

No external dependencies required.

Run:
    python examples/36_brazil_lgpd_ai_governance.py
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
    Result returned by each Brazil AI governance filter.

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
# Layer 1 — LGPD data protection (BrazilLGPDFilter)
# ---------------------------------------------------------------------------

# ANPD adequacy-designated countries (EU, UK as of ANPD 2023 adequacy decisions)
_ANPD_ADEQUACY_COUNTRIES: frozenset[str] = frozenset(
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

# LGPD Art. 11 — Sensitive personal data categories
_LGPD_SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {
        "racial_ethnic_origin",
        "religious_belief",
        "political_opinion",
        "union_membership",
        "health",
        "sexual_orientation",
        "genetic",
        "biometric",
    }
)

# LGPD Art. 7 — 10 legal bases for personal data processing
_LGPD_LEGAL_BASES: frozenset[str] = frozenset(
    {
        "consent",
        "legal_obligation",
        "public_policy",
        "research",
        "contract_performance",
        "regular_exercise_of_rights",
        "vital_interests",
        "legitimate_interests",
        "credit_protection",
        "health_protection",
    }
)


@dataclass(frozen=True)
class BrazilLGPDFilter:
    """
    Layer 1: Brazil Lei Geral de Proteção de Dados (LGPD, Law 13.709/2018).

    The LGPD is Brazil's comprehensive personal data protection law,
    modeled on GDPR and enforced by the Autoridade Nacional de Proteção
    de Dados (ANPD).  Four principal controls apply:

    (a) Art. 7 Lawfulness — personal data must be processed on one of
        10 legal bases (consent/legal obligation/public policy/research/
        contract performance/exercise of rights/vital interests/
        legitimate interests/credit protection/health protection);
        absence of any legal basis results in denial;
    (b) Art. 11 Sensitive Data — sensitive personal data categories
        (racial/ethnic origin/religious belief/political opinion/union
        membership/health/sexual orientation/genetic/biometric) require
        explicit consent or legal obligation; absence results in denial;
    (c) Art. 33 International Transfer — transfer to a country without
        ANPD adequacy finding requires standard contractual clauses or
        binding corporate rules; adequate countries are EU and UK;
        absence of safeguards results in denial;
    (d) Art. 20 Automated Decisions — automated decisions significantly
        affecting individual rights (credit, employment, insurance,
        public benefits) without a human review mechanism trigger
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Lei Geral de Proteção de Dados Pessoais (LGPD), Law 13.709/2018,
        Arts. 7, 11, 20, 33
    ANPD Resolution CD/ANPD 01/2021 — ANPD internal regulations
    ANPD Resolution CD/ANPD 02/2022 — high-risk processing and DPIA
    ANPD Adequacy Decisions: EU (2023), UK (2023)
    """

    FILTER_NAME: str = "BRAZIL_LGPD_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 7 — personal data processing without a valid legal basis
        if doc.get("personal_data_processing"):
            legal_basis = doc.get("legal_basis", "")
            if not legal_basis or (
                isinstance(legal_basis, str)
                and legal_basis.lower() not in _LGPD_LEGAL_BASES
            ):
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="DENIED",
                    regulation="LGPD Art. 7 Lawfulness — 10 legal bases required",
                    reason=(
                        "Personal data processing without one of the 10 LGPD legal "
                        "bases violates Art. 7 — a valid basis (consent, legal "
                        "obligation, contract performance, legitimate interests, "
                        "vital interests, research, credit protection, health "
                        "protection, regular exercise of rights, or public policy) "
                        "is required for all personal data processing activities"
                    ),
                )

        # Art. 11 — sensitive personal data without explicit consent or legal obligation
        data_category = doc.get("data_category", "")
        if (
            isinstance(data_category, str)
            and data_category.lower() in _LGPD_SENSITIVE_CATEGORIES
            and not doc.get("explicit_consent_obtained")
            and not doc.get("legal_obligation_applies")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="LGPD Art. 11 Sensitive Data — explicit consent or legal obligation",
                reason=(
                    f"Sensitive personal data category '{data_category}' "
                    "(racial/ethnic origin/religious belief/political opinion/"
                    "union membership/health/sexual orientation/genetic/biometric) "
                    "requires explicit consent or legal obligation under LGPD "
                    "Art. 11 — general consent is insufficient for sensitive "
                    "personal data categories"
                ),
            )

        # Art. 33 — cross-border transfer to country without ANPD adequacy or contractual safeguards
        transfer_country = doc.get("transfer_country", "")
        if (
            doc.get("cross_border_transfer")
            and transfer_country
            and transfer_country not in _ANPD_ADEQUACY_COUNTRIES
            and not doc.get("standard_contractual_clauses_in_place")
            and not doc.get("binding_corporate_rules_in_place")
            and not doc.get("anpd_specific_authorization")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "LGPD Art. 33 International Transfer — ANPD adequacy or "
                    "contractual safeguards required"
                ),
                reason=(
                    f"Cross-border data transfer to '{transfer_country}' without "
                    "ANPD adequacy finding or contractual safeguards violates "
                    "LGPD Art. 33 — standard contractual clauses (SCCs), binding "
                    "corporate rules (BCR), or ANPD-specific authorization are "
                    "required for transfers outside adequate jurisdictions (EU/UK)"
                ),
            )

        # Art. 20 — automated decision significantly affecting rights without human review
        if (
            doc.get("automated_decision_significant_effect")
            and not doc.get("human_review_mechanism_available")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="LGPD Art. 20 Right to Review Automated Decisions",
                reason=(
                    "Automated decision significantly affecting individual rights "
                    "without a human review mechanism requires human oversight "
                    "under LGPD Art. 20 — data subjects have the right to request "
                    "review by a human agent for automated decisions affecting "
                    "credit, employment, insurance, or public benefit eligibility"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="LGPD Arts. 7, 11, 20, 33",
            reason="Brazil LGPD personal data protection controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 2 — ANPD AI guidelines (ANPDAIFilter)
# ---------------------------------------------------------------------------

# ANPD Resolution CD/ANPD 02/2022 — high-risk AI processing categories requiring DPIA
_ANPD_HIGH_RISK_PROCESSING: frozenset[str] = frozenset(
    {
        "biometric_identification",
        "large_scale_profiling",
        "systematic_monitoring",
        "automated_decision_making",
        "sensitive_data_processing",
        "vulnerable_persons",
        "new_technology_deployment",
    }
)


@dataclass(frozen=True)
class ANPDAIFilter:
    """
    Layer 2: Brazil ANPD (Autoridade Nacional de Proteção de Dados) AI guidelines.

    The ANPD has issued specific guidance on AI governance through
    Resolution CD/ANPD 02/2022 and the ANPD AI Guidelines 2023.  Four
    principal controls apply:

    (a) LGPD Art. 38 + ANPD Resolution CD/ANPD 02/2022 — AI systems
        performing high-risk personal data processing (biometric
        identification, large-scale profiling, systematic monitoring,
        automated decision-making, sensitive data processing, processing
        of vulnerable persons, new technology deployment) require a
        mandatory Data Protection Impact Assessment (DPIA); absence
        results in denial;
    (b) LGPD Art. 9(V) + ANPD AI Guidelines 2023 §4.2 — AI profiling
        systems must provide transparency to data subjects about the
        automated decision logic used; absence results in denial;
    (c) LGPD Art. 10 §3 + ANPD Resolution CD/ANPD 02/2022 §6 —
        legitimate interest used as AI processing legal basis requires
        a documented Legitimate Interest Assessment (LIA); absence
        results in denial;
    (d) Lei 12.414/2011 Cadastro Positivo + ANPD credit data guidance —
        AI credit scoring systems must comply with SERASA/SCR (Sistema
        de Informações de Crédito) regulations; non-compliance triggers
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    LGPD (Law 13.709/2018) Arts. 9(V), 10 §3, 38
    ANPD Resolution CD/ANPD 02/2022 — risk assessment methodology
    ANPD AI Guidelines 2023 — transparency and accountability in AI
    Lei 12.414/2011 Cadastro Positivo (credit scoring)
    Banco Central do Brasil SCR (Sistema de Informações de Crédito)
    """

    FILTER_NAME: str = "ANPD_AI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # LGPD Art. 38 + ANPD Resolution 02/2022 — high-risk processing without DPIA
        processing_type = doc.get("processing_type", "")
        if (
            isinstance(processing_type, str)
            and processing_type.lower() in _ANPD_HIGH_RISK_PROCESSING
            and not doc.get("dpia_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "LGPD Art. 38 + ANPD Resolution CD/ANPD 02/2022 — DPIA required "
                    "for high-risk processing"
                ),
                reason=(
                    f"High-risk AI processing type '{processing_type}' without a "
                    "completed Data Protection Impact Assessment (DPIA) violates "
                    "LGPD Art. 38 and ANPD Resolution CD/ANPD 02/2022 — a DPIA "
                    "must be conducted and documented before deployment of AI "
                    "systems performing high-risk personal data processing"
                ),
            )

        # LGPD Art. 9(V) + ANPD AI Guidelines 2023 §4.2 — profiling without transparency
        if (
            doc.get("ai_profiling_active")
            and not doc.get("automated_logic_disclosed_to_data_subjects")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "LGPD Art. 9(V) Transparent Processing + ANPD AI Guidelines 2023 §4.2"
                ),
                reason=(
                    "AI profiling system without transparency about automated decision "
                    "logic to data subjects violates LGPD Art. 9(V) and ANPD AI "
                    "Guidelines 2023 §4.2 — data subjects must be informed about the "
                    "existence, criteria, and purpose of AI profiling before or at the "
                    "point of data collection"
                ),
            )

        # LGPD Art. 10 §3 + ANPD Resolution 02/2022 §6 — legitimate interest without LIA
        if (
            doc.get("legal_basis") == "legitimate_interests"
            and doc.get("ai_system_active")
            and not doc.get("legitimate_interest_assessment_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "LGPD Art. 10 §3 + ANPD Resolution CD/ANPD 02/2022 §6 — "
                    "LIA required for legitimate interest basis"
                ),
                reason=(
                    "Legitimate interest as AI processing legal basis without a "
                    "documented Legitimate Interest Assessment (LIA) violates "
                    "LGPD Art. 10 §3 and ANPD Resolution CD/ANPD 02/2022 §6 — "
                    "a three-part LIA (purpose/necessity/balancing test) must "
                    "be completed and documented before legitimate interest may "
                    "be relied upon for AI processing"
                ),
            )

        # Lei 12.414/2011 + ANPD credit guidance — AI credit scoring without SERASA/SCR compliance
        if (
            doc.get("ai_credit_scoring_active")
            and not doc.get("serasa_scr_compliance_verified")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "Lei 12.414/2011 Cadastro Positivo + ANPD Credit Data Guidance — "
                    "SERASA/SCR compliance required"
                ),
                reason=(
                    "AI credit scoring system without verified SERASA/SCR (Sistema de "
                    "Informações de Crédito) compliance requires human review under "
                    "Lei 12.414/2011 and ANPD credit data guidance — credit scoring "
                    "AI must demonstrate compliance with Cadastro Positivo regulations "
                    "and BCB credit reporting system requirements before autonomous "
                    "credit decisions may be issued"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "LGPD Arts. 9(V), 10 §3, 38 + ANPD Resolution CD/ANPD 02/2022 + "
                "ANPD AI Guidelines 2023"
            ),
            reason="Brazil ANPD AI governance controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 3 — Brazil sectoral AI regulations (BrazilSectoralAIFilter)
# ---------------------------------------------------------------------------

# Regulated financial AI contexts under CMN/BCdB framework
_BRAZIL_FINANCIAL_AI_CONTEXTS: frozenset[str] = frozenset(
    {
        "algorithmic_trading",
        "credit_model",
        "risk_model",
        "anti_fraud_model",
        "underwriting_model",
    }
)


@dataclass(frozen=True)
class BrazilSectoralAIFilter:
    """
    Layer 3: Brazil sectoral AI regulations (financial, health, telecom, electoral).

    Brazil's sectoral regulators have issued specific AI governance
    requirements for their regulated industries.  Four principal controls
    apply:

    (a) CMN Resolution 4.993/2022 + Circular BCB 3.979 — AI systems in
        banking and financial services (algorithmic trading, credit models,
        risk models, anti-fraud, underwriting) must be notified to the
        Banco Central do Brasil (BCdB); absence results in denial;
    (b) CFM Resolution 2.314/2022 + LGPD Art. 11(II)(f) — AI health
        systems processing patient data must comply with Conselho Federal
        de Medicina (CFM) digital health ethical guidelines; absence
        results in denial;
    (c) ANATEL Resolution 740/2020 + ANATEL AI Guidelines 2023 — AI
        systems operating in the telecom sector must demonstrate compliance
        with ANATEL AI ethics framework; absence results in denial;
    (d) TSE Resolution 23.732/2024 — AI-generated content used in
        Brazilian electoral campaigns (deepfakes, synthetic media) must
        include mandatory labeling disclosing AI generation; absence
        triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    CMN (Conselho Monetário Nacional) Resolution 4.993/2022 — model risk
        management for financial institutions
    Circular BCB (Banco Central do Brasil) 3.979 — algorithmic trading
        and model notification
    CFM (Conselho Federal de Medicina) Resolution 2.314/2022 — digital
        health and AI ethics
    LGPD Art. 11(II)(f) — health data legal basis for AI
    ANATEL (Agência Nacional de Telecomunicações) Resolution 740/2020
    ANATEL AI Guidelines 2023 — AI ethics for telecom
    TSE (Tribunal Superior Electoral) Resolution 23.732/2024 — AI use
        in electoral campaigns and deepfake labeling
    """

    FILTER_NAME: str = "BRAZIL_SECTORAL_AI_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # CMN Resolution 4.993/2022 + Circular BCB 3.979 — financial AI without BCdB notification
        financial_ai_context = doc.get("financial_ai_context", "")
        if (
            isinstance(financial_ai_context, str)
            and financial_ai_context.lower() in _BRAZIL_FINANCIAL_AI_CONTEXTS
            and not doc.get("bcb_model_notification_filed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "CMN Resolution 4.993/2022 + Circular BCB 3.979 — BCdB model "
                    "notification required for financial AI systems"
                ),
                reason=(
                    f"Financial AI system in context '{financial_ai_context}' without "
                    "Banco Central do Brasil (BCdB) model notification violates CMN "
                    "Resolution 4.993/2022 and Circular BCB 3.979 — all algorithmic "
                    "trading, credit, risk, anti-fraud, and underwriting AI models "
                    "used by regulated financial institutions must be notified to "
                    "BCdB before deployment"
                ),
            )

        # CFM Resolution 2.314/2022 + LGPD Art. 11(II)(f) — health AI without CFM ethical guidelines
        if (
            doc.get("health_ai_system_active")
            and doc.get("patient_data_processed")
            and not doc.get("cfm_ethical_guidelines_compliant")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "CFM Resolution 2.314/2022 Digital Health + LGPD Art. 11(II)(f) — "
                    "CFM ethical guidelines compliance required"
                ),
                reason=(
                    "AI health system processing patient data without compliance with "
                    "Conselho Federal de Medicina (CFM) Resolution 2.314/2022 "
                    "digital health ethical guidelines violates medical AI governance "
                    "obligations — all health AI systems must adhere to CFM ethical "
                    "principles for digital health including patient autonomy, "
                    "transparency, and non-maleficence before processing health data"
                ),
            )

        # ANATEL Resolution 740/2020 + ANATEL AI Guidelines 2023 — telecom AI without ANATEL compliance
        if (
            doc.get("telecom_ai_system_active")
            and not doc.get("anatel_ai_ethics_framework_compliant")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "ANATEL Resolution 740/2020 + ANATEL AI Guidelines 2023 — "
                    "ANATEL AI ethics framework compliance required"
                ),
                reason=(
                    "AI system operating in Brazilian telecom sector without ANATEL "
                    "AI Ethics Framework compliance violates ANATEL Resolution "
                    "740/2020 and ANATEL AI Guidelines 2023 — telecom AI systems "
                    "must demonstrate compliance with ANATEL's AI ethics principles "
                    "(transparency, accountability, fairness, safety) before "
                    "deployment in regulated telecommunications infrastructure"
                ),
            )

        # TSE Resolution 23.732/2024 — AI-generated electoral content without deepfake labeling
        if (
            doc.get("ai_generated_electoral_content")
            and not doc.get("tse_deepfake_labeling_applied")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "TSE Resolution 23.732/2024 — mandatory AI labeling for "
                    "electoral content"
                ),
                reason=(
                    "AI-generated content used in Brazilian electoral campaigns "
                    "without TSE-mandated deepfake labeling requires human review "
                    "under TSE Resolution 23.732/2024 — all synthetic or AI-generated "
                    "electoral content (deepfakes, voice cloning, synthetic images) "
                    "must be clearly labeled as AI-generated before dissemination "
                    "in electoral contexts"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "CMN Resolution 4.993/2022 + Circular BCB 3.979 + CFM Resolution "
                "2.314/2022 + ANATEL Resolution 740/2020 + TSE Resolution 23.732/2024"
            ),
            reason="Brazil sectoral AI governance controls — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border AI data flows (BrazilCrossBorderFilter)
# ---------------------------------------------------------------------------

# Countries restricted by ANPD under LGPD Art. 33
_ANPD_RESTRICTED_COUNTRIES: frozenset[str] = frozenset({"CN", "RU", "KP"})

# FATF (Financial Action Task Force) non-compliant / high-risk jurisdictions
# Non-compliant = on FATF Black List (as of 2025: DPRK, Iran, Myanmar, Russia, Syria)
# High-risk monitored = on FATF Grey List (subset listed here for financial AI controls)
_FATF_NONCOMPLIANT_JURISDICTIONS: frozenset[str] = frozenset(
    {
        "KP",  # North Korea — FATF Black List
        "IR",  # Iran — FATF Black List
        "MM",  # Myanmar — FATF Black List
        "RU",  # Russia — FATF Black List
        "SY",  # Syria — FATF Black List
    }
)


@dataclass(frozen=True)
class BrazilCrossBorderFilter:
    """
    Layer 4: Cross-border AI data flows under Brazilian framework.

    Brazilian law imposes specific controls on cross-border AI data flows
    through LGPD Art. 33, Lei 9.613/1998 (AML), Coaf Resolution 36/2021,
    and sectoral regulations.  Four principal controls apply:

    (a) LGPD Art. 33(I)/(II) + ANPD adequacy list — personal data to
        CN/RU/KP without ANPD adequacy finding or standard contractual
        clauses is denied;
    (b) Lei 9.613/1998 AML + Coaf Resolution 36/2021 + FATF standards —
        financial AI data to FATF non-compliant jurisdiction (KP/IR/MM/
        RU/SY) is denied;
    (c) LGPD Art. 33(V) + sectoral regulations — AI system processing
        Brazilian citizens' data hosted outside Brazil without ANPD
        authorization is denied;
    (d) LGPD Art. 11 + ANPD Resolution CD/ANPD 02/2022 §8 — cross-border
        transfer of sensitive biometric data without ANPD notification
        triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    LGPD (Law 13.709/2018) Art. 33 international transfers
    ANPD Resolution CD/ANPD 02/2022 §8 — sensitive data cross-border rules
    Lei 9.613/1998 — Anti-Money Laundering and terrorist financing
    Coaf (Conselho de Controle de Atividades Financeiras) Resolution 36/2021
    FATF (Financial Action Task Force) Black List and Grey List (2025)
    """

    FILTER_NAME: str = "BRAZIL_CROSS_BORDER_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # LGPD Art. 33(I)/(II) — personal data to CN/RU/KP without ANPD adequacy or SCCs
        personal_data_country = doc.get("personal_data_transfer_country", "")
        if (
            personal_data_country in _ANPD_RESTRICTED_COUNTRIES
            and not doc.get("anpd_adequacy_confirmed")
            and not doc.get("standard_contractual_clauses_in_place")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "LGPD Art. 33(I)/(II) + ANPD adequacy list — restricted: CN/RU/KP"
                ),
                reason=(
                    f"Personal data transfer to '{personal_data_country}' without "
                    "ANPD adequacy confirmation or standard contractual clauses "
                    "is prohibited under LGPD Art. 33 — CN, RU, and KP are not "
                    "on the ANPD adequacy list and require standard contractual "
                    "clauses or binding corporate rules before data may be "
                    "transferred"
                ),
            )

        # Lei 9.613/1998 AML + Coaf Resolution 36/2021 — financial AI data to FATF non-compliant jurisdiction
        financial_transfer_country = doc.get("financial_ai_data_transfer_country", "")
        if (
            doc.get("financial_ai_data_transfer")
            and financial_transfer_country in _FATF_NONCOMPLIANT_JURISDICTIONS
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "Lei 9.613/1998 AML + Coaf Resolution 36/2021 + FATF standards — "
                    "financial AI data transfer to FATF non-compliant jurisdiction denied"
                ),
                reason=(
                    f"Financial AI data transfer to '{financial_transfer_country}' "
                    "violates Lei 9.613/1998 Anti-Money Laundering requirements and "
                    "Coaf Resolution 36/2021 — FATF non-compliant jurisdictions "
                    "(KP/IR/MM/RU/SY) on the FATF Black List are prohibited "
                    "destinations for financial AI data under Brazilian AML law"
                ),
            )

        # LGPD Art. 33(V) — AI processing Brazilian citizens' data hosted outside Brazil without ANPD authorization
        if (
            doc.get("processes_brazilian_citizens_data")
            and doc.get("data_hosted_outside_brazil")
            and not doc.get("anpd_authorization_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation=(
                    "LGPD Art. 33(V) + sectoral regulations — ANPD authorization "
                    "required for offshore hosting of Brazilian citizens' data"
                ),
                reason=(
                    "AI system processing Brazilian citizens' personal data hosted "
                    "outside Brazil without ANPD authorization violates LGPD "
                    "Art. 33(V) — specific ANPD authorization or demonstration of "
                    "equivalent protection standards is required for offshore "
                    "hosting and processing of Brazilian citizens' personal data"
                ),
            )

        # LGPD Art. 11 + ANPD Resolution 02/2022 §8 — cross-border sensitive
        # biometric transfer without ANPD notification
        cross_border_biometric = doc.get("cross_border_sensitive_data_type", "")
        if (
            doc.get("cross_border_sensitive_data_transfer")
            and isinstance(cross_border_biometric, str)
            and cross_border_biometric.lower() in {"biometric", "genetic", "health"}
            and not doc.get("anpd_notification_provided")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "LGPD Art. 11 + ANPD Resolution CD/ANPD 02/2022 §8 — ANPD "
                    "notification required for cross-border sensitive biometric "
                    "data transfer"
                ),
                reason=(
                    "Cross-border transfer of sensitive biometric data without "
                    "ANPD notification requires human review under LGPD Art. 11 "
                    "and ANPD Resolution CD/ANPD 02/2022 §8 — ANPD must be "
                    "notified before cross-border transfers of biometric, genetic, "
                    "or health data and an adequacy review must be completed"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation=(
                "LGPD Art. 33 + Lei 9.613/1998 + Coaf Resolution 36/2021 + "
                "ANPD Resolution CD/ANPD 02/2022 §8"
            ),
            reason="Brazil cross-border AI data flow controls — compliant",
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class BrazilLangChainPolicyGuard:
    """
    LangChain integration — wraps the four Brazil governance filters as a
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
                BrazilLGPDFilter(),
                ANPDAIFilter(),
                BrazilSectoralAIFilter(),
                BrazilCrossBorderFilter(),
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


class BrazilCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps a Brazil governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
    """

    name: str = "BrazilGovernanceGuard"
    description: str = (
        "Enforces Brazil AI governance policies (LGPD, ANPD, Sectoral, "
        "Cross-Border) on documents processed by a CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class BrazilAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    Brazil governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``BrazilMAFPolicyMiddleware`` for the Microsoft Agent
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


class BrazilSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps a Brazil governance filter as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``BrazilMAFPolicyMiddleware`` for the Microsoft Agent Framework.
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


class BrazilLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing Brazil governance
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


class BrazilHaystackGovernanceComponent:
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


class BrazilDSPyGovernanceModule:
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


class BrazilMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying Brazil governance filters.

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
    # 1. Personal data without legal basis → DENIED (LGPD Art. 7)
    # ------------------------------------------------------------------
    _show(
        "LGPD Art. 7 — Personal Data Processing Without Legal Basis",
        BrazilLGPDFilter().filter(
            {
                "personal_data_processing": True,
                "legal_basis": "",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Health data without explicit consent → DENIED (LGPD Art. 11)
    # ------------------------------------------------------------------
    _show(
        "LGPD Art. 11 — Health Data Without Explicit Consent",
        BrazilLGPDFilter().filter(
            {
                "data_category": "health",
                "explicit_consent_obtained": False,
                "legal_obligation_applies": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. Cross-border transfer to CN without SCCs → DENIED (LGPD Art. 33)
    # ------------------------------------------------------------------
    _show(
        "LGPD Art. 33 — Cross-Border Transfer to CN Without Safeguards",
        BrazilLGPDFilter().filter(
            {
                "cross_border_transfer": True,
                "transfer_country": "CN",
                "standard_contractual_clauses_in_place": False,
                "binding_corporate_rules_in_place": False,
                "anpd_specific_authorization": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. Automated decision without human review → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "LGPD Art. 20 — Automated Decision Without Human Review Mechanism",
        BrazilLGPDFilter().filter(
            {
                "automated_decision_significant_effect": True,
                "human_review_mechanism_available": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. High-risk AI without DPIA → DENIED (ANPD Resolution 02/2022)
    # ------------------------------------------------------------------
    _show(
        "ANPD Resolution 02/2022 — Biometric AI Without DPIA",
        ANPDAIFilter().filter(
            {
                "processing_type": "biometric_identification",
                "dpia_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. Financial AI without BCdB notification → DENIED
    # ------------------------------------------------------------------
    _show(
        "CMN Resolution 4.993/2022 — Algorithmic Trading Without BCdB Notification",
        BrazilSectoralAIFilter().filter(
            {
                "financial_ai_context": "algorithmic_trading",
                "bcb_model_notification_filed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. Electoral AI content without TSE labeling → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "TSE Resolution 23.732/2024 — Electoral Deepfake Without Labeling",
        BrazilSectoralAIFilter().filter(
            {
                "ai_generated_electoral_content": True,
                "tse_deepfake_labeling_applied": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Financial AI data to FATF non-compliant jurisdiction → DENIED
    # ------------------------------------------------------------------
    _show(
        "Lei 9.613/1998 AML — Financial AI Data to KP (FATF Black List)",
        BrazilCrossBorderFilter().filter(
            {
                "financial_ai_data_transfer": True,
                "financial_ai_data_transfer_country": "KP",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Biometric data cross-border without ANPD notification → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "ANPD Resolution 02/2022 §8 — Biometric Cross-Border Without ANPD Notification",
        BrazilCrossBorderFilter().filter(
            {
                "cross_border_sensitive_data_transfer": True,
                "cross_border_sensitive_data_type": "biometric",
                "anpd_notification_provided": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. Compliant scenario → PERMITTED
    # ------------------------------------------------------------------
    _show(
        "Fully Compliant — Consent Basis, EU Transfer, DPIA Completed",
        BrazilLGPDFilter().filter(
            {
                "personal_data_processing": True,
                "legal_basis": "consent",
                "cross_border_transfer": True,
                "transfer_country": "DE",
            }
        ),
    )
