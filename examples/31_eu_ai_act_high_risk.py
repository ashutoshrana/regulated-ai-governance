"""
31_eu_ai_act_high_risk.py — EU AI Act High-Risk Systems Governance Framework

Implements governance filters for the EU Artificial Intelligence Act
(Regulation 2024/1689, in force August 2024) covering Annex III high-risk AI
system categories, conformity assessment, Fundamental Rights Impact Assessment,
technical requirements, transparency obligations, and cross-border/GPAI rules.

Demonstrates a multi-layer governance framework where four independent filters
enforce distinct requirements of the Act:

    Layer 1  — High-risk category gate (EUAIActHighRiskCategoryFilter):

               EU AI Act 2024/1689 Annex III — eight high-risk categories
                   require conformity assessment before market placement or
                   deployment; absence of completed assessment results in
                   denial (Art. 43);
               Employment/law enforcement categories trigger third-party
                   conformity assessment obligation (Art. 43(1));
               Migration/justice categories require a Fundamental Rights
                   Impact Assessment under Art. 27;
               Art. 5 — Prohibited AI practices are denied unconditionally;
               Art. 49/71 — Compliant high-risk systems must be registered in
                   the EU AI database before deployment.

    Layer 2  — Technical requirements (EUAIActTechnicalRequirementsFilter):

               Art. 9  — Risk management system required throughout lifecycle;
               Art. 10 — Data governance and quality measures documented;
               Art. 11 + Annex IV — Technical documentation prepared before
                   market placement;
               Art. 14 — Human oversight measures enabling intervention/
                   override;
               Art. 15 — Accuracy, robustness, and cybersecurity requirements
                   (documented test results required — REQUIRES_HUMAN_REVIEW).

    Layer 3  — Transparency (EUAIActTransparencyFilter):

               Art. 50(1) — AI systems interacting with natural persons must
                   disclose AI identity;
               Art. 50(4) — AI-generated/manipulated content must be labeled
                   as artificially generated;
               Art. 50(3) — Emotion recognition and biometric categorisation
                   AI must inform exposed persons;
               Art. 13  — High-risk AI must provide instructions for use to
                   deployers (REQUIRES_HUMAN_REVIEW if absent).

    Layer 4  — Cross-border + GPAI (EUAIActCrossBorderFilter):

               Art. 2(1)(c) + export control — High-risk AI export to
                   high-surveillance jurisdictions (China, Russia) prohibited;
               Art. 53 — GPAI model providers must maintain and provide
                   technical documentation to the AI Office;
               Art. 55 — GPAI models with systemic risk require adversarial
                   testing and incident reporting;
               Art. 53(1)(c) — GPAI model providers must implement a
                   copyright compliance policy (REQUIRES_HUMAN_REVIEW).

No external dependencies required.

Run:
    python examples/31_eu_ai_act_high_risk.py
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
    Result returned by each EU AI Act governance filter.

    Attributes
    ----------
    filter_name : str
        Identifier for the filter that produced this result.
    decision : str
        One of ``"APPROVED"``, ``"DENIED"``, or ``"REQUIRES_HUMAN_REVIEW"``.
    reason : str
        Human-readable description of the compliance finding.
    regulation_citation : str
        Authoritative citation for the regulation that drove the decision.
    requires_logging : bool
        True if this result must be written to a compliance audit log.
    """

    filter_name: str
    decision: str = "APPROVED"
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = True

    @property
    def is_denied(self) -> bool:
        """``True`` only when ``decision == "DENIED"``."""
        return self.decision == "DENIED"


# ---------------------------------------------------------------------------
# Layer 1 — High-risk category gate (EUAIActHighRiskCategoryFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EUAIActHighRiskCategoryFilter:
    """
    Layer 1: EU AI Act 2024/1689 Annex III — High-risk AI system categories.

    The EU AI Act (Regulation 2024/1689) designates eight categories of AI
    systems as high-risk under Annex III.  These systems are subject to
    mandatory conformity assessment (Art. 43) before being placed on the market
    or put into service.  Certain categories additionally require third-party
    assessment or a Fundamental Rights Impact Assessment (Art. 27).  Five
    principal controls apply:

    (a) Annex III §1–§4 categories (biometric identification, critical
        infrastructure, education/vocational training) — require completed
        conformity assessment; absence results in denial citing Art. 43;
    (b) Annex III §5–§6 categories (employment/workers management, essential
        services, law enforcement) — require completed third-party conformity
        assessment; absence results in denial citing Art. 43(1);
    (c) Annex III §7–§8 categories (migration/asylum, administration of
        justice) — require a Fundamental Rights Impact Assessment; absence
        results in denial citing Art. 27;
    (d) Art. 5 prohibited practices — real-time remote biometric surveillance,
        social scoring, manipulation of vulnerable groups — denied
        unconditionally;
    (e) Annex III high-risk systems with conformity assessment completed but
        not yet registered in the EU AI database — REQUIRES_HUMAN_REVIEW
        citing Art. 49/71.

    References
    ----------
    EU AI Act 2024/1689 Annex III
    EU AI Act 2024/1689 Art. 5  (Prohibited practices)
    EU AI Act 2024/1689 Art. 27 (Fundamental Rights Impact Assessment)
    EU AI Act 2024/1689 Art. 43 (Conformity assessment)
    EU AI Act 2024/1689 Art. 49 + 71 (EU AI database registration)
    """

    FILTER_NAME: str = "EU_AI_ACT_HIGH_RISK_CATEGORY_FILTER"

    # Annex III §1–§4 categories
    _CATEGORY_ASSESSMENT_REQUIRED: frozenset = frozenset(
        {
            "biometric_identification",
            "critical_infrastructure",
            "education_vocational",
        }
    )

    # Annex III §5–§6 categories (third-party assessment)
    _CATEGORY_THIRD_PARTY_REQUIRED: frozenset = frozenset(
        {
            "employment_workers_management",
            "essential_services",
            "law_enforcement",
        }
    )

    # Annex III §7–§8 categories (FRIA required)
    _CATEGORY_FRIA_REQUIRED: frozenset = frozenset(
        {
            "migration_asylum",
            "administration_justice",
        }
    )

    # All Annex III high-risk categories combined
    _ALL_HIGH_RISK_CATEGORIES: frozenset = frozenset(
        {
            "biometric_identification",
            "critical_infrastructure",
            "education_vocational",
            "employment_workers_management",
            "essential_services",
            "law_enforcement",
            "migration_asylum",
            "administration_justice",
        }
    )

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        category = doc.get("ai_system_category")

        # Art. 5 — prohibited AI practices: denied unconditionally (highest priority)
        if doc.get("prohibited_ai_practice"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 5: Prohibited AI practices — real-time remote "
                    "biometric surveillance, social scoring, manipulation of "
                    "vulnerable groups"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 5",
                requires_logging=True,
            )

        # Annex III §1–§4 — conformity assessment required
        if category in self._CATEGORY_ASSESSMENT_REQUIRED and not doc.get("conformity_assessment_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 43: Annex III high-risk AI systems require "
                    "conformity assessment before market placement"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 43",
                requires_logging=True,
            )

        # Annex III §5–§6 — third-party conformity assessment required
        if category in self._CATEGORY_THIRD_PARTY_REQUIRED and not doc.get("conformity_assessment_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 43(1): High-risk AI in employment/law "
                    "enforcement requires third-party conformity assessment"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 43(1)",
                requires_logging=True,
            )

        # Annex III §7–§8 — Fundamental Rights Impact Assessment required
        if category in self._CATEGORY_FRIA_REQUIRED and not doc.get("fundamental_rights_impact_assessment"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 27: High-risk AI in migration/justice requires "
                    "Fundamental Rights Impact Assessment before deployment"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 27",
                requires_logging=True,
            )

        # Art. 49/71 — high-risk system with assessment completed but not in EU database
        if (
            category in self._ALL_HIGH_RISK_CATEGORIES
            and doc.get("conformity_assessment_completed")
            and not doc.get("eu_database_registered")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "EU AI Act Art. 49/71: High-risk AI systems must be registered in EU AI database before deployment"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 49/71",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=("EU AI Act 2024/1689 Annex III — high-risk category assessment compliant"),
            regulation_citation="EU AI Act 2024/1689 Annex III",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Technical requirements (EUAIActTechnicalRequirementsFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EUAIActTechnicalRequirementsFilter:
    """
    Layer 2: EU AI Act Arts. 9–15 — Technical requirements for high-risk AI.

    High-risk AI systems must meet a set of technical requirements before
    market placement or deployment.  Five principal controls apply:

    (a) Art. 9 — A documented risk management system covering the full
        lifecycle is mandatory; absence results in denial;
    (b) Art. 10 — Training, validation, and testing data must be subject to
        documented data governance and quality measures; absence results in
        denial;
    (c) Art. 11 + Annex IV — Technical documentation must be prepared and
        kept up to date; absence results in denial;
    (d) Art. 14 — Human oversight measures enabling intervention and override
        must be incorporated by design; absence results in denial;
    (e) Art. 15 — Accuracy, robustness, and cybersecurity requirements must be
        satisfied and documented with test results; absence triggers
        REQUIRES_HUMAN_REVIEW.

    All five controls apply only when ``high_risk_ai`` is True.

    References
    ----------
    EU AI Act 2024/1689 Art. 9  (Risk management system)
    EU AI Act 2024/1689 Art. 10 (Data and data governance)
    EU AI Act 2024/1689 Art. 11 + Annex IV (Technical documentation)
    EU AI Act 2024/1689 Art. 14 (Human oversight)
    EU AI Act 2024/1689 Art. 15 (Accuracy, robustness, cybersecurity)
    """

    FILTER_NAME: str = "EU_AI_ACT_TECHNICAL_REQUIREMENTS_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        if not doc.get("high_risk_ai"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason="EU AI Act Arts. 9-15 technical requirements — compliant",
                regulation_citation="EU AI Act 2024/1689 Arts. 9-15",
                requires_logging=False,
            )

        # Art. 9 — risk management system required
        if not doc.get("risk_management_system"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 9: High-risk AI systems require documented "
                    "risk management system throughout lifecycle"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 9",
                requires_logging=True,
            )

        # Art. 10 — data governance required
        if not doc.get("data_governance_documented"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 10: High-risk AI training/validation data "
                    "requires documented data governance and quality measures"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 10",
                requires_logging=True,
            )

        # Art. 11 + Annex IV — technical documentation required
        if not doc.get("technical_documentation_prepared"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 11 + Annex IV: High-risk AI systems require "
                    "technical documentation before market placement"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 11 + Annex IV",
                requires_logging=True,
            )

        # Art. 14 — human oversight measures required
        if not doc.get("human_oversight_measures"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 14: High-risk AI systems require human oversight "
                    "measures enabling intervention and override"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 14",
                requires_logging=True,
            )

        # Art. 15 — accuracy/robustness/cybersecurity testing required
        if not doc.get("accuracy_robustness_tested"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "EU AI Act Art. 15: High-risk AI systems must meet accuracy, "
                    "robustness, and cybersecurity requirements (documented test "
                    "results required)"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 15",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="EU AI Act Arts. 9-15 technical requirements — compliant",
            regulation_citation="EU AI Act 2024/1689 Arts. 9-15",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Transparency (EUAIActTransparencyFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EUAIActTransparencyFilter:
    """
    Layer 3: EU AI Act Arts. 13/50/52 — Transparency and information
    obligations.

    The EU AI Act imposes distinct transparency requirements on different types
    of AI systems.  Four principal controls apply:

    (a) Art. 50(1) — AI systems intended to interact with natural persons must
        notify those persons that they are interacting with an AI system,
        unless this is obvious from context; absence of disclosure results in
        denial;
    (b) Art. 50(4) — AI-generated or manipulated content (including deepfakes)
        must be labeled as artificially generated or manipulated; absence
        results in denial;
    (c) Art. 50(3) — Emotion recognition systems and biometric categorisation
        AI must inform persons exposed to such processing; absence results in
        denial;
    (d) Art. 13 — High-risk AI systems must be accompanied by instructions for
        use enabling deployers to understand accuracy limits, intended purpose,
        and maintenance requirements; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    EU AI Act 2024/1689 Art. 13 (Transparency and provision of information)
    EU AI Act 2024/1689 Art. 50(1) (AI interaction disclosure)
    EU AI Act 2024/1689 Art. 50(3) (Emotion recognition disclosure)
    EU AI Act 2024/1689 Art. 50(4) (AI-generated content labeling)
    """

    FILTER_NAME: str = "EU_AI_ACT_TRANSPARENCY_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 50(1) — AI interacts with humans without AI disclosure: denied
        if doc.get("ai_interacts_with_humans") and not doc.get("ai_disclosure_made"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 50(1): AI systems interacting with natural "
                    "persons must disclose AI identity unless obvious from context"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 50(1)",
                requires_logging=True,
            )

        # Art. 50(4) — synthetic content without labeling: denied
        if doc.get("synthetic_content_generated") and not doc.get("ai_generated_labeling"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 50(4): AI-generated/manipulated content "
                    "(deepfakes) must be labeled as artificially generated"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 50(4)",
                requires_logging=True,
            )

        # Art. 50(3) — emotion recognition without disclosure: denied
        if doc.get("emotion_recognition_system") and not doc.get("emotion_recognition_disclosure"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 50(3): Emotion recognition and biometric "
                    "categorisation AI must inform exposed natural persons"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 50(3)",
                requires_logging=True,
            )

        # Art. 13 — high-risk AI without instructions for use: requires review
        if doc.get("high_risk_ai") and not doc.get("instructions_for_use_provided"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "EU AI Act Art. 13: High-risk AI systems must provide "
                    "instructions for use to deployers (accuracy, limitations, "
                    "maintenance)"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 13",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=("EU AI Act Arts. 13/50/52 transparency obligations — compliant"),
            regulation_citation="EU AI Act 2024/1689 Arts. 13/50/52",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border + GPAI (EUAIActCrossBorderFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EUAIActCrossBorderFilter:
    """
    Layer 4: EU AI Act Art. 2 — Territorial scope + GPAI model rules
    Arts. 51–55.

    The EU AI Act applies extraterritorially to AI systems placed on the EU
    market or affecting EU persons, regardless of where the provider is
    established.  Additional rules govern General Purpose AI (GPAI) models.
    Four principal controls apply:

    (a) Art. 2(1)(c) + EU strategic autonomy export policy — High-risk AI
        system export to high-surveillance jurisdictions (China, Russia) is
        prohibited under EU strategic autonomy policy;
    (b) Art. 53 — GPAI model providers must maintain technical documentation
        and make it available to the AI Office on request; absence results in
        denial;
    (c) Art. 55 — GPAI models with systemic risk (as designated by the AI
        Office) require adversarial testing and incident reporting; absence of
        completed adversarial testing results in denial;
    (d) Art. 53(1)(c) — GPAI model providers must implement a copyright
        compliance policy consistent with the Text and Data Mining Directive;
        absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    EU AI Act 2024/1689 Art. 2  (Scope)
    EU AI Act 2024/1689 Art. 51 (GPAI model classification)
    EU AI Act 2024/1689 Art. 53 (GPAI obligations)
    EU AI Act 2024/1689 Art. 55 (GPAI systemic risk)
    """

    FILTER_NAME: str = "EU_AI_ACT_CROSS_BORDER_FILTER"

    # High-surveillance jurisdictions prohibited under EU strategic autonomy policy
    _PROHIBITED_EXPORT_DESTINATIONS: frozenset = frozenset({"China", "Russia"})

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        destination = doc.get("destination_country")

        # Art. 2(1)(c) + export control — high-risk AI to prohibited jurisdictions
        if destination in self._PROHIBITED_EXPORT_DESTINATIONS and doc.get("high_risk_ai"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 2(1)(c) + export control: High-risk AI system "
                    "export to high-surveillance jurisdictions prohibited under EU "
                    "strategic autonomy policy"
                ),
                regulation_citation=("EU AI Act 2024/1689 Art. 2(1)(c) + EU strategic autonomy export control"),
                requires_logging=True,
            )

        # Art. 53 — GPAI model without technical documentation: denied
        if doc.get("gpai_model") and not doc.get("gpai_technical_documentation"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 53: GPAI model providers must maintain technical "
                    "documentation and provide to AI Office on request"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 53",
                requires_logging=True,
            )

        # Art. 55 — GPAI systemic risk without adversarial testing: denied
        if doc.get("gpai_systemic_risk") and not doc.get("adversarial_testing_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "EU AI Act Art. 55: GPAI models with systemic risk require "
                    "adversarial testing and incident reporting to AI Office"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 55",
                requires_logging=True,
            )

        # Art. 53(1)(c) — GPAI model without copyright compliance policy: requires review
        if doc.get("gpai_model") and not doc.get("copyright_compliance_policy"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "EU AI Act Art. 53(1)(c): GPAI model providers must implement "
                    "copyright compliance policy (Text and Data Mining Directive)"
                ),
                regulation_citation="EU AI Act 2024/1689 Art. 53(1)(c)",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=("EU AI Act 2024/1689 cross-border and GPAI — compliant"),
            regulation_citation="EU AI Act 2024/1689 Arts. 2/51-55",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Integration wrappers
# ---------------------------------------------------------------------------


class EUAIActLangChainPolicyGuard:
    """
    LangChain integration — wraps the four EU AI Act governance filters as a
    LangChain-compatible ``Runnable``-style tool guard.

    Implements ``invoke(input_doc)`` and ``ainvoke(input_doc)`` so the guard
    can be inserted into a LangChain chain or used as a tool callback.  Raises
    ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def invoke(self, input_doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(input_doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {r.reason}")
        return results

    def ainvoke(self, input_doc: dict[str, Any]) -> list[FilterResult]:
        """Async-compatible entry point (synchronous implementation)."""
        return self.invoke(input_doc)


class EUAIActCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps the four EU AI Act governance filters as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    name: str = "EUAIActGovernanceGuard"
    description: str = "Enforces EU AI Act 2024/1689 governance policies on documents processed by a CrewAI agent."

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def _run(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {r.reason}")
        return results


class EUAIActAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    EU AI Act governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``EUAIActMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def generate_reply(
        self,
        messages: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[FilterResult]:
        doc = messages or {}
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {r.reason}")
        return results


class EUAIActSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps EU AI Act governance filters as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``EUAIActMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def enforce_governance(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {r.reason}")
        return results


class EUAIActLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing EU AI Act governance
    between retrieval and synthesis steps.

    Implements ``process_event(doc)`` compatible with LlamaIndex
    ``WorkflowStep`` protocol (LlamaIndex 0.14.x).  Raises ``PermissionError``
    when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def process_event(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {r.reason}")
        return results


class EUAIActHaystackGovernanceComponent:
    """
    Haystack integration — ``@component``-compatible governance filter for
    Haystack 2.x pipelines (current: Haystack 2.27.0).

    Implements ``run(documents)`` following the Haystack component protocol so
    it can be inserted into a Haystack pipeline.  Filters each document dict
    individually; denied documents are excluded from the output.
    """

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [doc for doc in documents if not any(f.filter(doc).is_denied for f in self._filters)]
        return {"documents": passed}


class EUAIActDSPyGovernanceModule:
    """
    DSPy integration — governance-enforcing wrapper for DSPy ``Module``
    objects (DSPy >= 2.5.0, Pydantic v2).

    Implements ``forward(doc, **kwargs)`` and delegates to the wrapped module
    only after all four filters pass.  Raises ``PermissionError`` when any
    filter returns DENIED.
    """

    def __init__(self, module: Any) -> None:
        self._module = module
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def forward(self, doc: dict[str, Any], **kwargs: Any) -> Any:
        for f in self._filters:
            result = f.filter(doc)
            if result.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {result.reason}")
        return self._module(doc, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)


class EUAIActMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying EU AI Act governance filters.

    MAF is the enterprise successor to AutoGen and Semantic Kernel (released
    2025).  Implements ``process(message, next_handler)`` so this middleware
    can be registered in an MAF agent pipeline.  Raises ``PermissionError``
    when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            EUAIActHighRiskCategoryFilter(),
            EUAIActTechnicalRequirementsFilter(),
            EUAIActTransparencyFilter(),
            EUAIActCrossBorderFilter(),
        ]

    def process(self, message: dict[str, Any], next_handler: Any) -> Any:
        for f in self._filters:
            result = f.filter(message)
            if result.is_denied:
                raise PermissionError(f"EU AI Act governance DENIED: {result.reason}")
        return next_handler(message)


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------


def _show(title: str, result: FilterResult) -> None:
    print("=" * 70)
    print(f"Scenario: {title}")
    print(f"  Decision  : {result.decision}")
    print(f"  Reason    : {result.reason}")
    print(f"  Citation  : {result.regulation_citation}")
    print(f"  Logging   : {result.requires_logging}")
    print("=" * 70)


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # 1. Annex III biometric identification without conformity assessment → DENIED
    # ------------------------------------------------------------------
    _show(
        "Annex III — Biometric Identification Without Conformity Assessment (Art. 43)",
        EUAIActHighRiskCategoryFilter().filter(
            {
                "ai_system_category": "biometric_identification",
                "conformity_assessment_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Prohibited AI practice → DENIED (Art. 5)
    # ------------------------------------------------------------------
    _show(
        "Art. 5 — Prohibited AI Practice (Real-Time Remote Biometric Surveillance)",
        EUAIActHighRiskCategoryFilter().filter(
            {
                "prohibited_ai_practice": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. High-risk AI without risk management system → DENIED (Art. 9)
    # ------------------------------------------------------------------
    _show(
        "Art. 9 — High-Risk AI Without Risk Management System",
        EUAIActTechnicalRequirementsFilter().filter(
            {
                "high_risk_ai": True,
                "risk_management_system": False,
                "data_governance_documented": True,
                "technical_documentation_prepared": True,
                "human_oversight_measures": True,
                "accuracy_robustness_tested": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. AI interacting with humans without disclosure → DENIED (Art. 50(1))
    # ------------------------------------------------------------------
    _show(
        "Art. 50(1) — AI Chatbot Without Disclosure of AI Identity",
        EUAIActTransparencyFilter().filter(
            {
                "ai_interacts_with_humans": True,
                "ai_disclosure_made": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. High-risk AI exported to China → DENIED (Art. 2(1)(c))
    # ------------------------------------------------------------------
    _show(
        "Art. 2(1)(c) — High-Risk AI Export to China (Prohibited Jurisdiction)",
        EUAIActCrossBorderFilter().filter(
            {
                "destination_country": "China",
                "high_risk_ai": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. GPAI model without technical documentation → DENIED (Art. 53)
    # ------------------------------------------------------------------
    _show(
        "Art. 53 — GPAI Model Without Technical Documentation",
        EUAIActCrossBorderFilter().filter(
            {
                "gpai_model": True,
                "gpai_technical_documentation": False,
                "copyright_compliance_policy": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. GPAI systemic risk without adversarial testing → DENIED (Art. 55)
    # ------------------------------------------------------------------
    _show(
        "Art. 55 — GPAI Systemic Risk Without Adversarial Testing",
        EUAIActCrossBorderFilter().filter(
            {
                "gpai_model": True,
                "gpai_technical_documentation": True,
                "gpai_systemic_risk": True,
                "adversarial_testing_completed": False,
                "copyright_compliance_policy": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. High-risk AI without accuracy/robustness testing → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "Art. 15 — High-Risk AI Without Accuracy/Robustness Testing",
        EUAIActTechnicalRequirementsFilter().filter(
            {
                "high_risk_ai": True,
                "risk_management_system": True,
                "data_governance_documented": True,
                "technical_documentation_prepared": True,
                "human_oversight_measures": True,
                "accuracy_robustness_tested": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Fully compliant high-risk AI document — all 4 filters pass
    # ------------------------------------------------------------------
    compliant_doc = {
        "ai_system_category": "education_vocational",
        "conformity_assessment_completed": True,
        "eu_database_registered": True,
        "fundamental_rights_impact_assessment": True,
        "prohibited_ai_practice": False,
        "high_risk_ai": True,
        "risk_management_system": True,
        "data_governance_documented": True,
        "technical_documentation_prepared": True,
        "human_oversight_measures": True,
        "accuracy_robustness_tested": True,
        "ai_interacts_with_humans": True,
        "ai_disclosure_made": True,
        "synthetic_content_generated": False,
        "ai_generated_labeling": True,
        "emotion_recognition_system": False,
        "emotion_recognition_disclosure": True,
        "instructions_for_use_provided": True,
        "destination_country": "Germany",
        "gpai_model": False,
        "gpai_technical_documentation": True,
        "gpai_systemic_risk": False,
        "adversarial_testing_completed": True,
        "copyright_compliance_policy": True,
    }
    filters = [
        EUAIActHighRiskCategoryFilter(),
        EUAIActTechnicalRequirementsFilter(),
        EUAIActTransparencyFilter(),
        EUAIActCrossBorderFilter(),
    ]
    print("\n" + "=" * 70)
    print("Scenario: Fully Compliant High-Risk AI System — All 4 Filters")
    for f in filters:
        r = f.filter(compliant_doc)
        print(f"  [{r.decision}] {f.FILTER_NAME}")
    print("=" * 70)
