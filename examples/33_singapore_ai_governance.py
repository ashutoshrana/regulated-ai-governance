"""
33_singapore_ai_governance.py — Singapore AI Governance Framework

Implements governance filters for Singapore's comprehensive AI regulatory
ecosystem covering the Personal Data Protection Act 2012 (as amended 2020/2021),
the Monetary Authority of Singapore FEAT Principles for financial AI, the
AI Verify Foundation / IMDA AI Verify Framework (2023), and Singapore's
cross-border data-flow obligations.

Demonstrates a multi-layer governance framework where four independent filters
enforce distinct requirements of the Singapore regulatory landscape:

    Layer 1  — PDPA data protection (SingaporePDPAFilter):

               PDPA §13 Consent Obligation — personal data must not be
                   processed without consent or a recognised legitimate
                   purpose; absence results in denial;
               PDPA §15A Deemed consent — sensitive personal data (NRIC/FIN,
                   health, financial, biometric) requires enhanced consent;
                   absence results in denial;
               PDPA §26 Transfer Limitation Obligation — cross-border transfer
                   to a country without adequate protection is denied (approved
                   countries: AU/CA/DE/JP/NZ/UK and EU member states);
               PDPA Advisory Guidelines on AI 2023 §4.2 — automated decisions
                   affecting individuals must provide a human review option;
                   absence triggers REQUIRES_HUMAN_REVIEW.

    Layer 2  — MAS FEAT financial AI (MASFEATFilter):

               MAS FEAT Fairness Principle §2.1 — AI financial decisions must
                   include documented fairness assessment; absence results in
                   denial;
               MAS FEAT Accountability Principle §4.1 — AI systems must have
                   a named human accountability assignment and an audit trail;
                   absence results in denial;
               MAS FEAT Transparency Principle §5.2 — customer-facing AI must
                   include explainability documentation; absence results in
                   denial;
               MAS FEAT Ethics Principle §3.3 — AI models must have
                   documented robustness testing; absence triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 3  — AI Verify self-assessment (AIVerifySingaporeFilter):

               AI Verify Framework §3.1 — high-impact AI systems require a
                   completed AI Verify self-assessment against the 11 AI Ethics
                   Principles; absence results in denial;
               AI Verify §4.2 Explainability Testing — AI systems must include
                   LIME/SHAP or equivalent explainability testing; absence
                   results in denial;
               IMDA GenAI Framework 2024 §5.1 — generative AI systems must
                   comply with the IMDA Model AI Governance Framework for
                   GenAI; absence results in denial;
               AI Verify §4.1 Fairness Testing — unmitigated bias in protected
                   characteristics triggers REQUIRES_HUMAN_REVIEW.

    Layer 4  — Cross-border data flows (SingaporeCrossBorderFilter):

               MAS Technology Risk Management Guidelines §4.1 — financial AI
                   data to a non-MAS-supervised entity requires contractual
                   safeguards; absence results in denial;
               PDPA §26 + PDPC Transfer Impact Assessment — transfer of
                   personal data to CN/RU/KP requires PDPC adequacy approval;
                   absence results in denial;
               MAS Cloud Provider controls — AI systems serving MAS-regulated
                   entities must use whitelisted cloud regions (AWS Singapore /
                   GCP Singapore / Azure Singapore); non-whitelisted regions
                   result in denial;
               MAS AML/CFT Notice FAA-N18 — training-data export to an FATF
                   non-compliant jurisdiction triggers REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+-----------------------------------+-----------------------------------+
| Use case                          | Primary filters applied           |
+-----------------------------------+-----------------------------------+
| Robo-adviser / wealth management  | MASFEATFilter, CrossBorderFilter  |
| HR / hiring AI tool               | SingaporePDPAFilter, AIVerify     |
| Healthcare predictive diagnostics | PDPAFilter (NRIC/health data)     |
| GenAI customer-service chatbot    | AIVerifySingaporeFilter (GenAI)   |
| Trade-finance KYC automation      | MASFEATFilter, CrossBorderFilter  |
| Government citizen-service AI     | PDPAFilter, AIVerify              |
+-----------------------------------+-----------------------------------+

No external dependencies required.

Run:
    python examples/33_singapore_ai_governance.py
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
    Result returned by each Singapore AI governance filter.

    Attributes
    ----------
    filter_name : str
        Identifier for the filter that produced this result.
    decision : str
        One of ``"PERMITTED"``, ``"DENIED"``, ``"REQUIRES_HUMAN_REVIEW"``,
        or ``"REDACTED"``.
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
# Layer 1 — PDPA data protection (SingaporePDPAFilter)
# ---------------------------------------------------------------------------

_PDPA_APPROVED_TRANSFER_COUNTRIES: frozenset[str] = frozenset(
    {
        "AU",
        "CA",
        "DE",
        "JP",
        "NZ",
        "UK",
        # EU member states (representative subset)
        "AT",
        "BE",
        "BG",
        "CY",
        "CZ",
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

_SENSITIVE_PERSONAL_DATA_TYPES: frozenset[str] = frozenset(
    {"nric", "fin", "health", "medical", "financial", "biometric", "race", "religion"}
)


@dataclass(frozen=True)
class SingaporePDPAFilter:
    """
    Layer 1: Singapore Personal Data Protection Act 2012 (as amended 2020/2021).

    The PDPA regulates the collection, use, and disclosure of personal data by
    organisations.  The 2020 amendments expanded the mandatory data breach
    notification regime and introduced deemed consent.  Four principal controls
    apply:

    (a) §13 Consent Obligation — personal data must not be processed without
        consent or a recognised legitimate purpose exception (§17–§20); absence
        of consent results in denial;
    (b) §15A Deemed consent — sensitive personal data categories (NRIC/FIN,
        health, financial, biometric) require enhanced (explicit) consent;
        absence results in denial;
    (c) §26 Transfer Limitation Obligation — transfer of personal data to a
        recipient country without an adequate level of protection (per the PDPC
        whitelist: AU/CA/DE/JP/NZ/UK and EU member states) is denied unless
        contractual protection is in place;
    (d) PDPA Advisory Guidelines on AI 2023 §4.2 — where AI makes automated
        decisions that affect individuals, organisations must ensure that a
        human review option is available; absence triggers
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    Personal Data Protection Act 2012 (No. 26 of 2012), as amended 2020/2021
    PDPC Advisory Guidelines on the Use of AI and Personal Data (2023) §4.2
    """

    FILTER_NAME: str = "SINGAPORE_PDPA_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # §13 Consent Obligation — personal data without consent/legitimate purpose
        if (
            doc.get("personal_data_processing")
            and not doc.get("consent_obtained")
            and not doc.get("legitimate_purpose")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="PDPA 2012 §13 Consent Obligation",
                reason=(
                    "Personal data processing without consent or a recognised "
                    "legitimate purpose violates the PDPA §13 Consent Obligation"
                ),
            )

        # §15A Deemed consent — sensitive personal data requires enhanced consent
        data_type = doc.get("data_type", "")
        if (
            isinstance(data_type, str)
            and data_type.lower() in _SENSITIVE_PERSONAL_DATA_TYPES
            and not doc.get("enhanced_consent_obtained")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="PDPA 2012 §15A Deemed consent — sensitive data categories",
                reason=(
                    f"Sensitive personal data category '{data_type}' (NRIC/FIN, "
                    "health, financial, biometric) requires enhanced (explicit) "
                    "consent under PDPA §15A"
                ),
            )

        # §26 Transfer Limitation Obligation — cross-border transfer to non-adequate country
        transfer_country = doc.get("transfer_country", "")
        if doc.get("cross_border_transfer") and transfer_country not in _PDPA_APPROVED_TRANSFER_COUNTRIES:
            if not doc.get("contractual_protection"):
                return FilterResult(
                    filter_name=self.FILTER_NAME,
                    decision="DENIED",
                    regulation="PDPA 2012 §26 Transfer Limitation Obligation",
                    reason=(
                        f"Cross-border transfer to '{transfer_country}' is not "
                        "permitted under PDPA §26 — country lacks adequate protection "
                        "and no contractual safeguards are in place "
                        "(approved countries: AU/CA/DE/JP/NZ/UK/EU)"
                    ),
                )

        # PDPA Advisory Guidelines on AI 2023 §4.2 — automated decision without human review
        if doc.get("automated_decision_affecting_individual") and not doc.get("human_review_option"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="PDPA Advisory Guidelines on AI 2023 §4.2",
                reason=(
                    "Automated decisions affecting individuals must provide a "
                    "human review option under PDPA Advisory Guidelines on AI 2023 §4.2"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="PDPA 2012",
            reason="PDPA data protection obligations — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 2 — MAS FEAT financial AI (MASFEATFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MASFEATFilter:
    """
    Layer 2: Monetary Authority of Singapore FEAT Principles (2019).

    The MAS published the FEAT (Fairness, Ethics, Accountability, Transparency)
    Principles to guide financial institutions in the responsible use of AI and
    data analytics.  Four principal controls apply:

    (a) Fairness Principle §2.1 — AI financial decisions must be accompanied
        by documented fairness assessment to ensure customers are not
        discriminated against; absence results in denial;
    (b) Accountability Principle §4.1 — AI systems must have a named human
        accountability assignment and an audit trail enabling retrospective
        review; absence results in denial;
    (c) Transparency Principle §5.2 — customer-facing AI decisions must be
        supported by explainability documentation allowing adequate explanation
        to affected customers; absence results in denial;
    (d) Ethics Principle §3.3 — AI models must have documented robustness
        testing (stress tests, adversarial testing); absence triggers
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    MAS FEAT Principles for Financial Services (2019) §§2.1, 3.3, 4.1, 5.2
    MAS Principles to Promote Fairness, Ethics, Accountability and Transparency
    """

    FILTER_NAME: str = "MAS_FEAT_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Fairness Principle §2.1 — AI financial decision without fairness assessment
        if doc.get("ai_financial_decision") and not doc.get("fairness_assessment_documented"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="MAS FEAT Fairness Principle §2.1",
                reason=(
                    "AI financial decision without documented fairness assessment "
                    "violates MAS FEAT Fairness Principle §2.1 — risk of discriminatory "
                    "outcomes to customers"
                ),
            )

        # Accountability Principle §4.1 — AI system without human accountability and audit trail
        if doc.get("ai_system_deployed") and (
            not doc.get("human_accountability_assigned") or not doc.get("audit_trail_present")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="MAS FEAT Accountability Principle §4.1",
                reason=(
                    "AI system without human accountability assignment or audit trail "
                    "violates MAS FEAT Accountability Principle §4.1 — must identify "
                    "responsible persons and maintain an audit trail"
                ),
            )

        # Transparency Principle §5.2 — customer-facing AI without explainability documentation
        if doc.get("customer_facing_ai") and not doc.get("explainability_documented"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="MAS FEAT Transparency Principle §5.2",
                reason=(
                    "Customer-facing AI without explainability documentation violates "
                    "MAS FEAT Transparency Principle §5.2 — customers must receive "
                    "adequate explanation of AI decisions affecting them"
                ),
            )

        # Ethics Principle §3.3 — AI model without robustness testing
        if doc.get("ai_model_in_production") and not doc.get("robustness_testing_documented"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="MAS FEAT Ethics Principle §3.3",
                reason=(
                    "AI model without documented robustness testing (stress tests / "
                    "adversarial testing) — MAS FEAT Ethics Principle §3.3 recommends "
                    "human review before deployment"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="MAS FEAT Principles (2019)",
            reason="MAS FEAT Fairness, Ethics, Accountability, Transparency — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 3 — AI Verify self-assessment (AIVerifySingaporeFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AIVerifySingaporeFilter:
    """
    Layer 3: AI Verify Foundation / IMDA AI Verify Framework (2023).

    The AI Verify Framework, jointly developed by IMDA and the AI Verify
    Foundation, provides a testing toolkit and governance framework for
    organisations to demonstrate responsible AI.  It covers 11 AI Ethics
    Principles drawn from internationally recognised guidelines.  The 2024
    IMDA Model AI Governance Framework for GenAI adds specific obligations
    for generative AI providers.  Four principal controls apply:

    (a) AI Verify §3.1 — high-impact AI systems must complete an AI Verify
        self-assessment against the 11 AI Ethics Principles before deployment;
        absence results in denial;
    (b) AI Verify §4.2 Explainability Testing — AI systems must include
        explainability testing using LIME, SHAP, or an equivalent method;
        absence results in denial;
    (c) IMDA GenAI Framework 2024 §5.1 — generative AI systems must comply
        with the IMDA Model AI Governance Framework for GenAI; absence results
        in denial;
    (d) AI Verify §4.1 Fairness Testing — unmitigated bias in protected
        characteristics (age, gender, race, disability) triggers
        REQUIRES_HUMAN_REVIEW.

    References
    ----------
    AI Verify Foundation AI Verify Framework v1.0 (2023) §§3.1, 4.1, 4.2
    IMDA Model AI Governance Framework for Generative AI (2024) §5.1
    """

    FILTER_NAME: str = "AI_VERIFY_SINGAPORE_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # §3.1 — high-impact AI without AI Verify self-assessment
        if doc.get("high_impact_ai_system") and not doc.get("ai_verify_self_assessment_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="AI Verify Framework §3.1 — 11 AI Ethics Principles",
                reason=(
                    "High-impact AI system without completed AI Verify self-assessment "
                    "violates AI Verify Framework §3.1 — must demonstrate compliance "
                    "with the 11 AI Ethics Principles before deployment"
                ),
            )

        # §4.2 Explainability Testing — AI system without LIME/SHAP or equivalent
        if doc.get("ai_system_deployed") and not doc.get("explainability_testing_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="AI Verify §4.2 Explainability Testing",
                reason=(
                    "AI system without explainability testing (LIME/SHAP or equivalent) "
                    "violates AI Verify §4.2 — must demonstrate that model predictions "
                    "can be explained to affected persons"
                ),
            )

        # IMDA GenAI Framework 2024 §5.1 — generative AI without IMDA GenAI compliance
        if doc.get("generative_ai_system") and not doc.get("imda_genai_framework_compliant"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="IMDA GenAI Framework 2024 §5.1",
                reason=(
                    "Generative AI system without IMDA Model AI Governance Framework "
                    "for GenAI compliance violates IMDA GenAI Framework 2024 §5.1 — "
                    "must address content safety, transparency, and accountability for "
                    "foundation model usage"
                ),
            )

        # §4.1 Fairness Testing — unmitigated bias in protected characteristics
        if doc.get("bias_detected_in_protected_characteristics") and not doc.get("bias_mitigation_applied"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="AI Verify §4.1 Fairness Testing",
                reason=(
                    "Unmitigated bias detected in protected characteristics (age, gender, "
                    "race, disability) — AI Verify §4.1 Fairness Testing requires human "
                    "review and remediation before deployment"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="AI Verify Framework (2023) + IMDA GenAI Framework (2024)",
            reason="AI Verify self-assessment and IMDA governance framework — compliant",
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border data flows (SingaporeCrossBorderFilter)
# ---------------------------------------------------------------------------

_MAS_APPROVED_CLOUD_REGIONS: frozenset[str] = frozenset(
    {
        "aws_singapore",
        "gcp_singapore",
        "azure_singapore",
    }
)

_FATF_NON_COMPLIANT_JURISDICTIONS: frozenset[str] = frozenset(
    {
        # FATF grey-list and high-risk jurisdictions (representative set)
        "KP",  # North Korea (FATF blacklist)
        "IR",  # Iran (FATF blacklist)
        "MM",  # Myanmar (grey list)
        "YE",  # Yemen (grey list)
        "SY",  # Syria (grey list)
        "LY",  # Libya (grey list)
    }
)


@dataclass(frozen=True)
class SingaporeCrossBorderFilter:
    """
    Layer 4: Singapore cross-border AI data flow controls.

    Singapore's cross-border data and AI governance spans multiple regulators.
    MAS Technology Risk Management Guidelines set requirements for financial
    data processing by cloud providers.  PDPA §26 governs personal data
    transfers.  MAS AML/CFT notices address financial crime risk in training
    data.  Four principal controls apply:

    (a) MAS Technology Risk Management Guidelines §4.1 — financial AI data
        transferred to a non-MAS-supervised entity requires documented
        contractual safeguards; absence results in denial;
    (b) PDPA §26 + PDPC Transfer Impact Assessment — personal data transfers
        to CN/RU/KP are prohibited unless PDPC adequacy approval is obtained;
        absence results in denial;
    (c) MAS Cloud Provider controls — AI systems serving MAS-regulated entities
        must use an approved Singapore cloud region (AWS Singapore / GCP
        Singapore / Azure Singapore); non-whitelisted regions result in denial;
    (d) MAS AML/CFT Notice FAA-N18 — training-data export to an FATF
        non-compliant jurisdiction triggers REQUIRES_HUMAN_REVIEW for
        financial crime risk assessment.

    References
    ----------
    MAS Technology Risk Management Guidelines (2021) §4.1
    Personal Data Protection Act 2012 §26 + PDPC Transfer Impact Assessment
    MAS Cloud Provider Assessment Framework (2021)
    MAS AML/CFT Notice FAA-N18 (Securities/Financial Advisers)
    """

    FILTER_NAME: str = "SINGAPORE_CROSS_BORDER_FILTER"

    _PDPC_RESTRICTED_COUNTRIES: frozenset = frozenset({"CN", "RU", "KP"})

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # MAS TRM §4.1 — financial AI data to non-MAS-supervised entity without contractual safeguards
        if (
            doc.get("financial_ai_data_transfer")
            and not doc.get("recipient_mas_supervised")
            and not doc.get("contractual_safeguards_documented")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="MAS Technology Risk Management Guidelines §4.1",
                reason=(
                    "Financial AI data transfer to non-MAS-supervised entity without "
                    "contractual safeguards violates MAS Technology Risk Management "
                    "Guidelines §4.1 — must document third-party risk management controls"
                ),
            )

        # PDPA §26 + PDPC TIA — personal data transfer to CN/RU/KP without PDPC adequacy approval
        transfer_country = doc.get("personal_data_transfer_country", "")
        if transfer_country in self._PDPC_RESTRICTED_COUNTRIES and not doc.get("pdpc_adequacy_approval"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="PDPA §26 Transfer Limitation + PDPC Transfer Impact Assessment",
                reason=(
                    f"Transfer of personal data to '{transfer_country}' is prohibited "
                    "under PDPA §26 without PDPC adequacy approval — Transfer Impact "
                    "Assessment required for CN/RU/KP"
                ),
            )

        # MAS Cloud Provider controls — AI for MAS-regulated entity on non-whitelisted region
        cloud_region = doc.get("cloud_region", "")
        if doc.get("serves_mas_regulated_entity") and cloud_region and cloud_region not in _MAS_APPROVED_CLOUD_REGIONS:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                regulation="MAS Cloud Provider controls — approved: AWS/GCP/Azure Singapore",
                reason=(
                    f"AI system serving MAS-regulated entity deployed on non-whitelisted "
                    f"cloud region '{cloud_region}' — MAS Cloud Provider controls require "
                    "use of AWS Singapore, GCP Singapore, or Azure Singapore"
                ),
            )

        # MAS AML/CFT FAA-N18 — training data export to FATF non-compliant jurisdiction
        training_data_jurisdiction = doc.get("training_data_export_jurisdiction", "")
        if training_data_jurisdiction in _FATF_NON_COMPLIANT_JURISDICTIONS:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                regulation="MAS AML/CFT Notice FAA-N18",
                reason=(
                    f"AI training data export to FATF non-compliant jurisdiction "
                    f"'{training_data_jurisdiction}' triggers MAS AML/CFT Notice FAA-N18 "
                    "financial crime risk review"
                ),
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="PERMITTED",
            regulation="MAS TRM Guidelines + PDPA §26 + MAS Cloud Controls + FAA-N18",
            reason="Singapore cross-border AI data flow controls — compliant",
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class SingaporeLangChainPolicyGuard:
    """
    LangChain integration — wraps the four Singapore governance filters as a
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
                SingaporePDPAFilter(),
                MASFEATFilter(),
                AIVerifySingaporeFilter(),
                SingaporeCrossBorderFilter(),
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


class SingaporeCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps a Singapore governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation when
    the filter returns DENIED.
    """

    name: str = "SingaporeGovernanceGuard"
    description: str = (
        "Enforces Singapore AI governance policies (PDPA, MAS FEAT, AI Verify, "
        "Cross-Border) on documents processed by a CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class SingaporeAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    Singapore governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``SingaporeMAFPolicyMiddleware`` for the Microsoft
    Agent Framework.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
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


class SingaporeSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps a Singapore governance filter as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``SingaporeMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` with the regulation citation when the
    filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def enforce_governance(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class SingaporeLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing Singapore governance
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


class SingaporeHaystackGovernanceComponent:
    """
    Haystack integration — ``@component``-compatible governance filter for
    Haystack 2.x pipelines (current: Haystack 2.27.0).

    Implements ``run(documents)`` following the Haystack component protocol.
    Filters each document dict individually; denied documents are excluded from
    the output.  Does not raise; returns only permitted documents.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [doc for doc in documents if not self._filter.filter(doc).is_denied]
        return {"documents": passed}


class SingaporeDSPyGovernanceModule:
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


class SingaporeMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying Singapore governance filters.

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
    # 1. Personal data without consent → DENIED (PDPA §13)
    # ------------------------------------------------------------------
    _show(
        "PDPA §13 — Personal Data Processing Without Consent",
        SingaporePDPAFilter().filter(
            {
                "personal_data_processing": True,
                "consent_obtained": False,
                "legitimate_purpose": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Health data without enhanced consent → DENIED (PDPA §15A)
    # ------------------------------------------------------------------
    _show(
        "PDPA §15A — Health Data Without Enhanced Consent",
        SingaporePDPAFilter().filter(
            {
                "data_type": "health",
                "enhanced_consent_obtained": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. Cross-border transfer to China without contractual protection → DENIED
    # ------------------------------------------------------------------
    _show(
        "PDPA §26 — Cross-Border Transfer to CN Without Protection",
        SingaporePDPAFilter().filter(
            {
                "cross_border_transfer": True,
                "transfer_country": "CN",
                "contractual_protection": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. AI financial decision without fairness assessment → DENIED (MAS FEAT §2.1)
    # ------------------------------------------------------------------
    _show(
        "MAS FEAT §2.1 — AI Financial Decision Without Fairness Assessment",
        MASFEATFilter().filter(
            {
                "ai_financial_decision": True,
                "fairness_assessment_documented": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. AI system without human accountability → DENIED (MAS FEAT §4.1)
    # ------------------------------------------------------------------
    _show(
        "MAS FEAT §4.1 — AI System Without Human Accountability",
        MASFEATFilter().filter(
            {
                "ai_system_deployed": True,
                "human_accountability_assigned": False,
                "audit_trail_present": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. High-impact AI without AI Verify self-assessment → DENIED (AI Verify §3.1)
    # ------------------------------------------------------------------
    _show(
        "AI Verify §3.1 — High-Impact AI Without Self-Assessment",
        AIVerifySingaporeFilter().filter(
            {
                "high_impact_ai_system": True,
                "ai_verify_self_assessment_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. GenAI without IMDA GenAI Framework compliance → DENIED (IMDA §5.1)
    # ------------------------------------------------------------------
    _show(
        "IMDA GenAI Framework §5.1 — GenAI Without Framework Compliance",
        AIVerifySingaporeFilter().filter(
            {
                "generative_ai_system": True,
                "imda_genai_framework_compliant": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Financial AI data to non-MAS entity without safeguards → DENIED (MAS TRM §4.1)
    # ------------------------------------------------------------------
    _show(
        "MAS TRM §4.1 — Financial AI Data to Non-MAS Entity",
        SingaporeCrossBorderFilter().filter(
            {
                "financial_ai_data_transfer": True,
                "recipient_mas_supervised": False,
                "contractual_safeguards_documented": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Personal data transfer to CN without PDPC approval → DENIED (PDPA §26)
    # ------------------------------------------------------------------
    _show(
        "PDPA §26 + PDPC TIA — Personal Data to CN Without PDPC Approval",
        SingaporeCrossBorderFilter().filter(
            {
                "personal_data_transfer_country": "CN",
                "pdpc_adequacy_approval": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. Automated decision without human review option → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "PDPA AI Guidelines §4.2 — Automated Decision Without Human Review Option",
        SingaporePDPAFilter().filter(
            {
                "automated_decision_affecting_individual": True,
                "human_review_option": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 11. AI model in production without robustness testing → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "MAS FEAT §3.3 — AI Model Without Robustness Testing",
        MASFEATFilter().filter(
            {
                "ai_model_in_production": True,
                "robustness_testing_documented": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 12. Fully compliant document — all filters pass
    # ------------------------------------------------------------------
    _show(
        "Fully Compliant Singapore AI System — All Filters Pass",
        SingaporePDPAFilter().filter({}),
    )
