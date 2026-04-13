"""
32_gdpr_ai_accountability.py — GDPR AI Accountability Governance Framework

Implements governance filters for the General Data Protection Regulation
(GDPR, Regulation 2016/679) covering automated individual decision-making
(Art. 22), transparency and information obligations (Arts. 12–14), Data
Protection Impact Assessments (Art. 35), data minimisation and privacy by
design (Arts. 5/25).

Demonstrates a multi-layer accountability framework where four independent
filters enforce distinct requirements of the Regulation:

    Layer 1  — Automated decision-making (GDPRAutomatedDecisionFilter):

               GDPR Art. 22(1) — Automated decisions with legal or
                   significant effects require an appropriate legal basis
                   (explicit consent, contract necessity, or EU/MS law);
                   absence results in denial;
               GDPR Art. 22(3) + Recital 71 — Right to obtain an
                   explanation and to challenge automated decisions must
                   be implemented; absence results in denial;
               GDPR Art. 22(4) + Art. 9 — Automated decisions based on
                   special category data require explicit consent; absence
                   results in denial;
               GDPR Art. 21(2) — Profiling for direct marketing requires
                   an objection mechanism; absence triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 2  — Transparency (GDPRTransparencyFilter):

               GDPR Art. 13(1) — Privacy notice must be provided at time
                   of personal data collection; absence results in denial;
               GDPR Art. 13(2)(f) + Recital 60 — Automated processing
                   logic must be disclosed in the privacy notice; absence
                   results in denial;
               GDPR Art. 13(1)(f) — Third-country transfer safeguards
                   must be disclosed; absence results in denial;
               GDPR Art. 13(2)(a) — Retention period or criteria must be
                   specified; absence triggers REQUIRES_HUMAN_REVIEW.

    Layer 3  — Data Protection Impact Assessment (GDPRDPIAFilter):

               GDPR Art. 35(1) — High-risk processing requires a DPIA
                   before processing begins; absence results in denial;
               GDPR Art. 35(3)(c) — Systematic monitoring of a publicly
                   accessible area at large scale requires DPIA; absence
                   results in denial;
               GDPR Art. 35(3)(b) — Large-scale processing of special
                   category data requires DPIA; absence results in denial;
               GDPR Art. 36(1) — If DPIA shows unacceptable residual
                   risks, prior consultation with the supervisory authority
                   is required; triggers REQUIRES_HUMAN_REVIEW.

    Layer 4  — Data minimisation + privacy by design
               (GDPRDataMinimisationFilter):

               GDPR Art. 5(1)(c) — Personal data must be limited to what
                   is necessary (data minimisation); excess results in
                   denial;
               GDPR Art. 5(1)(b) + Art. 89 — AI training on personal
                   data requires documented purpose compatibility or
                   anonymisation; absence results in denial;
               GDPR Art. 5(1)(e) — Data must not be kept beyond the
                   retention period (storage limitation); violation results
                   in denial;
               GDPR Art. 25 — Privacy by design and by default measures
                   must be implemented when required; absence triggers
                   REQUIRES_HUMAN_REVIEW.

No external dependencies required.

Run:
    python examples/32_gdpr_ai_accountability.py
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
    Result returned by each GDPR governance filter.

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
# Layer 1 — Automated decision-making (GDPRAutomatedDecisionFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GDPRAutomatedDecisionFilter:
    """
    Layer 1: GDPR Art. 22 — Automated individual decision-making, including
    profiling.

    The GDPR restricts fully automated individual decision-making that
    produces legal or similarly significant effects.  Four principal controls
    apply:

    (a) Art. 22(1) — Automated decisions with legal or significant effects
        must rest on one of three legal bases: explicit consent, contract
        necessity, or authorisation by EU/Member State law; absence of a
        recognised legal basis results in denial;
    (b) Art. 22(3) + Recital 71 — When automated decisions are permitted,
        the data subject has the right to obtain a meaningful explanation of
        the decision and to contest it; absence of this safeguard results in
        denial;
    (c) Art. 22(4) + Art. 9 — Automated decisions based on special category
        data (health, biometric, racial or ethnic origin, etc.) require
        explicit consent regardless of the Art. 22(1) legal basis; absence
        results in denial;
    (d) Art. 21(2) — Data subjects have the absolute right to object to
        profiling for direct marketing purposes; an objection mechanism must
        be available; absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    GDPR 2016/679 Art. 22 (Automated individual decision-making)
    GDPR 2016/679 Art. 9  (Special category data)
    GDPR 2016/679 Art. 21(2) (Right to object — direct marketing)
    GDPR 2016/679 Recital 71 (Right to explanation)
    """

    FILTER_NAME: str = "GDPR_AUTOMATED_DECISION_FILTER"

    _VALID_ART22_BASES: frozenset = frozenset(
        {
            "explicit_consent",
            "contract_necessity",
            "eu_member_state_law",
        }
    )

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 22(1) — automated decision with legal/significant effect but no valid legal basis
        if (
            doc.get("automated_decision")
            and doc.get("legal_or_significant_effect")
            and doc.get("legal_basis_art22") not in self._VALID_ART22_BASES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 22(1): Automated decisions with legal or significant "
                    "effects require explicit consent, contract necessity, or "
                    "EU/MS authorisation"
                ),
                regulation_citation="GDPR 2016/679 Art. 22(1)",
                requires_logging=True,
            )

        # Art. 22(3) + Recital 71 — automated decision without right to explanation
        if (
            doc.get("automated_decision")
            and doc.get("legal_or_significant_effect")
            and not doc.get("right_to_explanation_provided")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 22(3) + Recital 71: Data subjects have the right to "
                    "obtain an explanation of the decision and to challenge it"
                ),
                regulation_citation="GDPR 2016/679 Art. 22(3) + Recital 71",
                requires_logging=True,
            )

        # Art. 22(4) + Art. 9 — automated decision on special category data without explicit consent
        if (
            doc.get("automated_decision")
            and doc.get("special_category_data")
            and not doc.get("explicit_consent_special_category")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 22(4) + Art. 9: Automated decisions based on special "
                    "category data (health, biometric, racial origin, etc.) require "
                    "explicit consent"
                ),
                regulation_citation="GDPR 2016/679 Art. 22(4) + Art. 9",
                requires_logging=True,
            )

        # Art. 21(2) — automated profiling without opt-out mechanism: requires review
        if doc.get("automated_profiling") and not doc.get("opt_out_mechanism"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "GDPR Art. 21(2): Data subjects have the right to object to "
                    "profiling for direct marketing; objection mechanism must be "
                    "available"
                ),
                regulation_citation="GDPR 2016/679 Art. 21(2)",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="GDPR Art. 22 automated decision-making — compliant",
            regulation_citation="GDPR 2016/679 Art. 22",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Transparency (GDPRTransparencyFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GDPRTransparencyFilter:
    """
    Layer 2: GDPR Arts. 12–14 — Information obligations and transparency.

    Controllers collecting personal data must provide prescribed information
    to data subjects.  When AI systems process personal data, additional
    disclosure obligations apply.  Four principal controls apply:

    (a) Art. 13(1) — A privacy notice containing the controller's identity,
        processing purposes, legal basis, and data subject rights must be
        provided at the time of collection; absence results in denial;
    (b) Art. 13(2)(f) + Recital 60 — Where personal data are used in
        automated processing, the privacy notice must include meaningful
        information about the logic involved; absence results in denial;
    (c) Art. 13(1)(f) — Transfers to third countries must be disclosed
        along with the applicable safeguards (SCCs, adequacy decision, BCRs,
        etc.); absence results in denial;
    (d) Art. 13(2)(a) — The period for which personal data will be stored
        (or the criteria used to determine it) must be specified; absence
        triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    GDPR 2016/679 Art. 12 (Transparent information)
    GDPR 2016/679 Art. 13 (Information — data collected from data subject)
    GDPR 2016/679 Art. 14 (Information — data not obtained from data subject)
    GDPR 2016/679 Recital 60 (Transparency principle)
    """

    FILTER_NAME: str = "GDPR_TRANSPARENCY_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 13(1) — personal data collection without privacy notice: denied
        if doc.get("personal_data_collection") and not doc.get("privacy_notice_provided"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 13(1): Data controller must provide privacy notice at "
                    "time of collection (identity, purposes, legal basis, retention, "
                    "rights)"
                ),
                regulation_citation="GDPR 2016/679 Art. 13(1)",
                requires_logging=True,
            )

        # Art. 13(2)(f) + Recital 60 — AI processing personal data without logic disclosure
        if (
            doc.get("ai_system")
            and doc.get("personal_data_processing")
            and not doc.get("ai_logic_disclosed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 13(2)(f) + Recital 60: Automated processing logic must "
                    "be disclosed in privacy notice including meaningful information "
                    "about the logic involved"
                ),
                regulation_citation="GDPR 2016/679 Art. 13(2)(f) + Recital 60",
                requires_logging=True,
            )

        # Art. 13(1)(f) — cross-border transfer without safeguards disclosure
        if doc.get("cross_border_transfer") and not doc.get("transfer_safeguards_disclosed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 13(1)(f): Third-country transfers must be disclosed "
                    "with the safeguards used (SCCs, adequacy, BCRs, etc.)"
                ),
                regulation_citation="GDPR 2016/679 Art. 13(1)(f)",
                requires_logging=True,
            )

        # Art. 13(2)(a) — retention period missing: requires review
        if doc.get("data_retention_period_missing"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "GDPR Art. 13(2)(a): Privacy notice must specify data retention "
                    "period or criteria used to determine it"
                ),
                regulation_citation="GDPR 2016/679 Art. 13(2)(a)",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="GDPR Arts. 13/14/12 transparency obligations — compliant",
            regulation_citation="GDPR 2016/679 Arts. 13/14/12",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Data Protection Impact Assessment (GDPRDPIAFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GDPRDPIAFilter:
    """
    Layer 3: GDPR Art. 35 — Data Protection Impact Assessment + Art. 36
    prior consultation.

    Before undertaking processing likely to result in high risk to natural
    persons, controllers must carry out a DPIA.  Where the DPIA reveals
    unacceptable residual risks, prior consultation with the supervisory
    authority is mandatory.  Four principal controls apply:

    (a) Art. 35(1) — Processing likely to result in high risk requires a
        DPIA before processing begins; absence results in denial;
    (b) Art. 35(3)(c) — Systematic monitoring of a publicly accessible
        area on a large scale requires a DPIA; absence results in denial;
    (c) Art. 35(3)(b) — Large-scale processing of special category data
        or criminal conviction data requires a DPIA; absence results in
        denial;
    (d) Art. 36(1) — If the DPIA shows high residual risks that the
        controller cannot mitigate alone, the supervisory authority must
        be consulted; triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    GDPR 2016/679 Art. 35 (Data protection impact assessment)
    GDPR 2016/679 Art. 36 (Prior consultation)
    """

    FILTER_NAME: str = "GDPR_DPIA_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 35(1) — high-risk processing without DPIA: denied
        if doc.get("high_risk_processing") and not doc.get("dpia_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 35(1): Processing likely to result in high risk to "
                    "natural persons requires a DPIA before processing begins"
                ),
                regulation_citation="GDPR 2016/679 Art. 35(1)",
                requires_logging=True,
            )

        # Art. 35(3)(c) — systematic public monitoring without DPIA: denied
        if doc.get("systematic_monitoring_public") and not doc.get("dpia_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 35(3)(c): Systematic monitoring of a publicly accessible "
                    "area on a large scale requires DPIA"
                ),
                regulation_citation="GDPR 2016/679 Art. 35(3)(c)",
                requires_logging=True,
            )

        # Art. 35(3)(b) — large-scale special category data without DPIA: denied
        if doc.get("large_scale_special_category") and not doc.get("dpia_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 35(3)(b): Large-scale processing of special category "
                    "data or criminal conviction data requires DPIA"
                ),
                regulation_citation="GDPR 2016/679 Art. 35(3)(b)",
                requires_logging=True,
            )

        # Art. 36(1) — DPIA completed but residual risks unacceptable: requires review
        if (
            doc.get("high_risk_processing")
            and doc.get("dpia_completed")
            and not doc.get("residual_risks_acceptable")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "GDPR Art. 36(1): If DPIA shows high residual risks, controller "
                    "must consult supervisory authority before processing"
                ),
                regulation_citation="GDPR 2016/679 Art. 36(1)",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="GDPR Art. 35 DPIA — compliant",
            regulation_citation="GDPR 2016/679 Art. 35",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Data minimisation + privacy by design (GDPRDataMinimisationFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GDPRDataMinimisationFilter:
    """
    Layer 4: GDPR Art. 5(1)(c) data minimisation + Art. 25 privacy by design
    and by default + Art. 5(1)(e) storage limitation.

    The data minimisation, purpose limitation, and storage limitation
    principles under Art. 5 are fundamental constraints on all personal data
    processing.  Art. 25 requires that these principles be embedded in systems
    by design.  Four principal controls apply:

    (a) Art. 5(1)(c) — Excessive data collection beyond what is adequate,
        relevant, and necessary for the purpose results in denial;
    (b) Art. 5(1)(b) + Art. 89 — AI training on personal data requires
        documented purpose compatibility or appropriate safeguards
        (pseudonymisation/anonymisation); absence results in denial;
    (c) Art. 5(1)(e) — Retaining personal data beyond the necessary period
        violates the storage limitation principle; results in denial;
    (d) Art. 25 — When privacy by design is required by the processing
        context, technical and organisational measures must be implemented;
        absence triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    GDPR 2016/679 Art. 5(1)(b) (Purpose limitation)
    GDPR 2016/679 Art. 5(1)(c) (Data minimisation)
    GDPR 2016/679 Art. 5(1)(e) (Storage limitation)
    GDPR 2016/679 Art. 25     (Data protection by design and by default)
    GDPR 2016/679 Art. 89     (Safeguards for research/archiving)
    """

    FILTER_NAME: str = "GDPR_DATA_MINIMISATION_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Art. 5(1)(c) — excessive data collection: denied
        if doc.get("excessive_data_collection"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 5(1)(c): Personal data must be adequate, relevant, and "
                    "limited to what is necessary (data minimisation principle)"
                ),
                regulation_citation="GDPR 2016/679 Art. 5(1)(c)",
                requires_logging=True,
            )

        # Art. 5(1)(b) + Art. 89 — AI training without documented purpose limitation: denied
        if doc.get("ai_training_data") and not doc.get("purpose_limitation_documented"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 5(1)(b) + Art. 89: AI training on personal data requires "
                    "documented purpose compatibility or anonymisation/pseudonymisation"
                ),
                regulation_citation="GDPR 2016/679 Art. 5(1)(b) + Art. 89",
                requires_logging=True,
            )

        # Art. 5(1)(e) — retention period exceeded: denied
        if doc.get("retention_period_exceeded"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "GDPR Art. 5(1)(e): Personal data must not be kept longer than "
                    "necessary for the processing purpose (storage limitation)"
                ),
                regulation_citation="GDPR 2016/679 Art. 5(1)(e)",
                requires_logging=True,
            )

        # Art. 25 — privacy by design required but not implemented: requires review
        if doc.get("privacy_by_design_required") and not doc.get("privacy_by_design_implemented"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "GDPR Art. 25: Data protection by design and by default — "
                    "technical and organisational measures must implement data "
                    "protection principles by design"
                ),
                regulation_citation="GDPR 2016/679 Art. 25",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="GDPR Arts. 5/25 data minimisation and privacy by design — compliant",
            regulation_citation="GDPR 2016/679 Arts. 5/25",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Integration wrappers
# ---------------------------------------------------------------------------


class GDPRLangChainPolicyGuard:
    """
    LangChain integration — wraps the four GDPR governance filters as a
    LangChain-compatible ``Runnable``-style tool guard.

    Implements ``invoke(input_doc)`` and ``ainvoke(input_doc)`` so the guard
    can be inserted into a LangChain chain or used as a tool callback.  Raises
    ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def invoke(self, input_doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(input_doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"GDPR governance DENIED: {r.reason}")
        return results

    def ainvoke(self, input_doc: dict[str, Any]) -> list[FilterResult]:
        """Async-compatible entry point (synchronous implementation)."""
        return self.invoke(input_doc)


class GDPRCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps the four GDPR governance filters as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    name: str = "GDPRGovernanceGuard"
    description: str = "Enforces GDPR 2016/679 governance policies on documents processed by a CrewAI agent."

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def _run(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"GDPR governance DENIED: {r.reason}")
        return results


class GDPRAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    GDPR governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``GDPRMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
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
                raise PermissionError(f"GDPR governance DENIED: {r.reason}")
        return results


class GDPRSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps GDPR governance filters as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``GDPRMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def enforce_governance(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"GDPR governance DENIED: {r.reason}")
        return results


class GDPRLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing GDPR governance
    between retrieval and synthesis steps.

    Implements ``process_event(doc)`` compatible with LlamaIndex
    ``WorkflowStep`` protocol (LlamaIndex 0.14.x).  Raises ``PermissionError``
    when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def process_event(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"GDPR governance DENIED: {r.reason}")
        return results


class GDPRHaystackGovernanceComponent:
    """
    Haystack integration — ``@component``-compatible governance filter for
    Haystack 2.x pipelines (current: Haystack 2.27.0).

    Implements ``run(documents)`` following the Haystack component protocol so
    it can be inserted into a Haystack pipeline.  Filters each document dict
    individually; denied documents are excluded from the output.
    """

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [doc for doc in documents if not any(f.filter(doc).is_denied for f in self._filters)]
        return {"documents": passed}


class GDPRDSPyGovernanceModule:
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
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def forward(self, doc: dict[str, Any], **kwargs: Any) -> Any:
        for f in self._filters:
            result = f.filter(doc)
            if result.is_denied:
                raise PermissionError(f"GDPR governance DENIED: {result.reason}")
        return self._module(doc, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)


class GDPRMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying GDPR governance filters.

    MAF is the enterprise successor to AutoGen and Semantic Kernel (released
    2025).  Implements ``process(message, next_handler)`` so this middleware
    can be registered in an MAF agent pipeline.  Raises ``PermissionError``
    when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            GDPRAutomatedDecisionFilter(),
            GDPRTransparencyFilter(),
            GDPRDPIAFilter(),
            GDPRDataMinimisationFilter(),
        ]

    def process(self, message: dict[str, Any], next_handler: Any) -> Any:
        for f in self._filters:
            result = f.filter(message)
            if result.is_denied:
                raise PermissionError(f"GDPR governance DENIED: {result.reason}")
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
    # 1. Automated decision with legal effect but no valid legal basis → DENIED
    # ------------------------------------------------------------------
    _show(
        "Art. 22(1) — Automated Credit Decision Without Valid Legal Basis",
        GDPRAutomatedDecisionFilter().filter(
            {
                "automated_decision": True,
                "legal_or_significant_effect": True,
                "legal_basis_art22": "legitimate_interest",
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Automated decision without right to explanation → DENIED (Art. 22(3))
    # ------------------------------------------------------------------
    _show(
        "Art. 22(3) — Automated Decision Without Right to Explanation",
        GDPRAutomatedDecisionFilter().filter(
            {
                "automated_decision": True,
                "legal_or_significant_effect": True,
                "legal_basis_art22": "explicit_consent",
                "right_to_explanation_provided": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. No privacy notice at data collection → DENIED (Art. 13(1))
    # ------------------------------------------------------------------
    _show(
        "Art. 13(1) — Personal Data Collection Without Privacy Notice",
        GDPRTransparencyFilter().filter(
            {
                "personal_data_collection": True,
                "privacy_notice_provided": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. High-risk processing without DPIA → DENIED (Art. 35(1))
    # ------------------------------------------------------------------
    _show(
        "Art. 35(1) — High-Risk AI Processing Without DPIA",
        GDPRDPIAFilter().filter(
            {
                "high_risk_processing": True,
                "dpia_completed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. Excessive data collection → DENIED (Art. 5(1)(c))
    # ------------------------------------------------------------------
    _show(
        "Art. 5(1)(c) — Excessive Personal Data Collection",
        GDPRDataMinimisationFilter().filter(
            {
                "excessive_data_collection": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. AI training data without purpose documentation → DENIED (Art. 5(1)(b))
    # ------------------------------------------------------------------
    _show(
        "Art. 5(1)(b) + Art. 89 — AI Training Without Purpose Limitation",
        GDPRDataMinimisationFilter().filter(
            {
                "ai_training_data": True,
                "purpose_limitation_documented": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. DPIA completed but residual risks unacceptable → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "Art. 36(1) — DPIA Shows Unacceptable Residual Risks",
        GDPRDPIAFilter().filter(
            {
                "high_risk_processing": True,
                "dpia_completed": True,
                "residual_risks_acceptable": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Retention period exceeded → DENIED (Art. 5(1)(e))
    # ------------------------------------------------------------------
    _show(
        "Art. 5(1)(e) — Personal Data Retained Beyond Necessary Period",
        GDPRDataMinimisationFilter().filter(
            {
                "retention_period_exceeded": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Fully compliant GDPR AI system — all 4 filters pass
    # ------------------------------------------------------------------
    compliant_doc = {
        # Automated decisions
        "automated_decision": True,
        "legal_or_significant_effect": True,
        "legal_basis_art22": "explicit_consent",
        "right_to_explanation_provided": True,
        "special_category_data": False,
        "explicit_consent_special_category": True,
        "automated_profiling": False,
        "opt_out_mechanism": True,
        # Transparency
        "personal_data_collection": True,
        "privacy_notice_provided": True,
        "ai_system": True,
        "personal_data_processing": True,
        "ai_logic_disclosed": True,
        "cross_border_transfer": False,
        "transfer_safeguards_disclosed": True,
        "data_retention_period_missing": False,
        # DPIA
        "high_risk_processing": True,
        "dpia_completed": True,
        "residual_risks_acceptable": True,
        "systematic_monitoring_public": False,
        "large_scale_special_category": False,
        # Data minimisation
        "excessive_data_collection": False,
        "ai_training_data": True,
        "purpose_limitation_documented": True,
        "retention_period_exceeded": False,
        "privacy_by_design_required": True,
        "privacy_by_design_implemented": True,
    }
    filters = [
        GDPRAutomatedDecisionFilter(),
        GDPRTransparencyFilter(),
        GDPRDPIAFilter(),
        GDPRDataMinimisationFilter(),
    ]
    print("\n" + "=" * 70)
    print("Scenario: Fully Compliant GDPR AI System — All 4 Filters")
    for f in filters:
        r = f.filter(compliant_doc)
        print(f"  [{r.decision}] {f.FILTER_NAME}")
    print("=" * 70)
