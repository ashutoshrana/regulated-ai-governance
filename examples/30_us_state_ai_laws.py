"""
30_us_state_ai_laws.py — US State AI Laws Governance Framework

Implements US state-level AI governance filters for Colorado, Illinois,
Virginia, and a multi-state cross-border applicability filter.  Each filter
enforces the principal compliance controls from its respective enacted
statute, consuming a plain ``dict`` document representation.

Demonstrates a multi-layer governance framework where four independent
state-law filters enforce distinct requirements:

    Layer 1  — Colorado (ColoradoSB205Filter):

               Colorado AI Act 2024 (SB 24-205, effective Feb 1, 2026) +
               Colorado Privacy Act AI provisions (CRS §6-1-1306):
               CRS §6-1-1702 — high-risk AI systems require an algorithmic
                   impact assessment before deployment;
               CRS §6-1-1306(1)(a)(IV) — automated employment decisions
                   require a human review option;
               Colorado AI Act §6-1-1704 — biometric data in AI systems
                   requires written consent;
               Colorado AI Act §6-1-1703 — high-risk AI requires bias and
                   discrimination testing before deployment.

    Layer 2  — Illinois (IllinoisBIPAAIFilter):

               Illinois Biometric Information Privacy Act (740 ILCS 14,
               effective 2008, amended 2023):
               740 ILCS 14/15(b) — biometric identifier collection requires
                   a written release; per-violation damages of $1,000–$5,000;
               740 ILCS 14/15(a) — biometric data requires a written
                   retention and destruction policy before collection;
               740 ILCS 14/15(d) — biometric data disclosure to third
                   parties is prohibited without written consent;
               Illinois AI Video Interview Act (820 ILCS 42):
               820 ILCS 42/10 — AI video interviews require advance
                   disclosure of AI use and the characteristics assessed.

    Layer 3  — Virginia (VirginiaAIProvisionsFilter):

               Virginia Consumer Data Protection Act AI provisions
               (Va. Code §59.1-577 et seq.):
               Va. Code §59.1-579 — profiling for consequential decisions
                   requires a human review option;
               Va. Code §59.1-578(A) — sensitive personal data in AI
                   processing requires opt-in consent;
               Va. Code §59.1-581 — high-risk AI processing requires a data
                   protection assessment;
               Va. Code §59.1-578(B) — AI processing of minor data requires
                   verifiable parental consent.

    Layer 4  — Multi-state cross-border (USStateAICrossBorderFilter):

               Multi-state applicability: Colorado/Illinois/Virginia/Texas/
               Connecticut/California:
               740 ILCS 14 BIPA — applies to Illinois residents' biometric
                   data regardless of processing location;
               Colorado AI Act §6-1-1702 — applies to Colorado residents
                   regardless of AI system location;
               Multi-state consumer AI rights — automated decision opt-out
                   required for VA/TX/CT residents;
               Cal. Civ. Code §1798.185(a)(16) — CPRA requires disclosure
                   of automated decision-making logic to California residents.

No external dependencies required.

Run:
    python examples/30_us_state_ai_laws.py
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
    Result returned by each US state AI governance filter.

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
# Layer 1 — Colorado (ColoradoSB205Filter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ColoradoSB205Filter:
    """
    Layer 1: Colorado AI Act 2024 (SB 24-205) + Colorado Privacy Act AI
    provisions (CRS §6-1-1306).

    The Colorado AI Act 2024 (Senate Bill 24-205, effective February 1, 2026)
    establishes comprehensive requirements for developers and deployers of
    high-risk AI systems affecting Colorado consumers.  The Colorado Privacy
    Act (CPA) adds supplemental AI-specific obligations for automated
    decisions.  Four principal controls apply:

    (a) CRS §6-1-1702 — High-risk AI systems require an algorithmic impact
        assessment to be completed before deployment.  Absence of the
        assessment when ``high_risk_ai`` is True results in denial;
    (b) CRS §6-1-1306(1)(a)(IV) — Automated employment decisions require
        an option for human review.  Absence of ``human_oversight`` when
        ``automated_employment_decision`` is True results in denial;
    (c) Colorado AI Act §6-1-1704 — Biometric data used in AI systems
        requires written consent.  Absence of ``written_consent`` when
        ``biometric_identifier`` is True results in denial;
    (d) Colorado AI Act §6-1-1703 — High-risk AI must complete bias and
        discrimination testing.  Absence of ``bias_testing_completed`` when
        ``high_risk_ai`` is True triggers a REQUIRES_HUMAN_REVIEW decision.

    References
    ----------
    Colorado AI Act 2024 (SB 24-205) CRS §6-1-1701 et seq.
    Colorado Privacy Act (CPA) CRS §6-1-1306
    """

    FILTER_NAME: str = "COLORADO_SB205_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # CRS §6-1-1702 — high-risk AI without impact assessment: denied
        if doc.get("high_risk_ai") and not doc.get("impact_assessment_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Colorado AI Act 2024 §6-1-1702 — high-risk AI systems "
                    "require impact assessment before deployment"
                ),
                regulation_citation="Colorado AI Act 2024 (SB 24-205) CRS §6-1-1702",
                requires_logging=True,
            )

        # CRS §6-1-1306(1)(a)(IV) — automated employment decision without human review: denied
        if doc.get("automated_employment_decision") and not doc.get("human_oversight"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "CRS §6-1-1306(1)(a)(IV) — automated employment decisions "
                    "require human review option"
                ),
                regulation_citation="Colorado Privacy Act CRS §6-1-1306(1)(a)(IV)",
                requires_logging=True,
            )

        # Colorado AI Act §6-1-1704 — biometric identifier without written consent: denied
        if doc.get("biometric_identifier") and not doc.get("written_consent"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Colorado AI Act §6-1-1704 — biometric data in AI systems "
                    "requires written consent"
                ),
                regulation_citation="Colorado AI Act 2024 (SB 24-205) CRS §6-1-1704",
                requires_logging=True,
            )

        # Colorado AI Act §6-1-1703 — high-risk AI without bias testing: requires review
        if doc.get("high_risk_ai") and not doc.get("bias_testing_completed"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Colorado AI Act §6-1-1703 — high-risk AI requires "
                    "bias/discrimination testing"
                ),
                regulation_citation="Colorado AI Act 2024 (SB 24-205) CRS §6-1-1703",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Colorado AI Act 2024 (SB 24-205) §6-1-1701 et seq. — compliant"
            ),
            regulation_citation="Colorado AI Act 2024 (SB 24-205) CRS §6-1-1701 et seq.",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Illinois (IllinoisBIPAAIFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IllinoisBIPAAIFilter:
    """
    Layer 2: Illinois Biometric Information Privacy Act (740 ILCS 14) +
    Illinois AI Video Interview Act (820 ILCS 42).

    The Illinois Biometric Information Privacy Act (BIPA), effective 2008 and
    amended in 2023, imposes strict requirements on private entities collecting,
    storing, or disclosing biometric identifiers.  The Illinois AI Video
    Interview Act (2020) adds disclosure obligations for AI-driven employment
    screening.  Four principal controls apply:

    (a) 740 ILCS 14/15(b) — Biometric identifiers (fingerprint, retina, iris,
        voiceprint, face geometry, hand geometry) require a written release
        before collection.  Absence of ``biipa_written_consent`` results in
        denial with per-violation damages of $1,000–$5,000;
    (b) 740 ILCS 14/15(a) — Entities collecting biometric data must first
        establish a written retention and destruction policy.  Absence of
        ``biipa_retention_policy`` results in denial;
    (c) 820 ILCS 42/10 — Employers using AI in video interviews must disclose
        the use of AI and the characteristics it will assess before the
        interview.  Absence of ``ai_video_disclosure`` results in denial;
    (d) 740 ILCS 14/15(d) — Biometric data may not be disclosed to third
        parties without written consent.  Presence of ``third_party_sharing``
        without ``biipa_written_consent`` results in denial.

    References
    ----------
    Illinois Biometric Information Privacy Act 740 ILCS 14 (2008, am. 2023)
    Illinois AI Video Interview Act 820 ILCS 42 (2020)
    """

    FILTER_NAME: str = "ILLINOIS_BIPA_AI_FILTER"

    # Biometric identifiers covered by BIPA
    _BIPA_IDENTIFIERS: frozenset = frozenset({
        "fingerprint",
        "retina",
        "iris",
        "voiceprint",
        "face_geometry",
        "hand_geometry",
    })

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        biometric_type = doc.get("biometric_data_type")
        is_bipa_biometric = biometric_type in self._BIPA_IDENTIFIERS

        # 740 ILCS 14/15(b) — biometric identifier without written release: denied
        if is_bipa_biometric and not doc.get("biipa_written_consent"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "740 ILCS 14/15(b) — biometric identifier collection requires "
                    "written release; $1,000–$5,000 per violation"
                ),
                regulation_citation="Illinois BIPA 740 ILCS 14/15(b)",
                requires_logging=True,
            )

        # 740 ILCS 14/15(a) — biometric identifier without retention/destruction policy: denied
        if is_bipa_biometric and not doc.get("biipa_retention_policy"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "740 ILCS 14/15(a) — biometric data requires written "
                    "retention/destruction policy"
                ),
                regulation_citation="Illinois BIPA 740 ILCS 14/15(a)",
                requires_logging=True,
            )

        # 820 ILCS 42/10 — AI video interview without pre-interview disclosure: denied
        if doc.get("video_interview_ai") and not doc.get("ai_video_disclosure"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "820 ILCS 42/10 — AI video interview requires disclosure of AI "
                    "use and assessed characteristics before interview"
                ),
                regulation_citation="Illinois AI Video Interview Act 820 ILCS 42/10",
                requires_logging=True,
            )

        # 740 ILCS 14/15(d) — biometric data shared with third party without consent: denied
        if (
            doc.get("biometric_data_type")
            and doc.get("third_party_sharing")
            and not doc.get("biipa_written_consent")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "740 ILCS 14/15(d) — biometric data disclosure to third party "
                    "prohibited without written consent"
                ),
                regulation_citation="Illinois BIPA 740 ILCS 14/15(d)",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="740 ILCS 14 BIPA — compliant",
            regulation_citation="Illinois BIPA 740 ILCS 14",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Virginia (VirginiaAIProvisionsFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VirginiaAIProvisionsFilter:
    """
    Layer 3: Virginia Consumer Data Protection Act AI provisions
    (Va. Code §59.1-577 et seq.).

    The Virginia Consumer Data Protection Act (VCDPA) includes AI-specific
    obligations for controllers and processors handling personal data of
    Virginia residents.  Four principal controls apply:

    (a) Va. Code §59.1-579 — Profiling for consequential decisions must include
        a human review option.  Absence of ``human_review_available`` when both
        ``automated_profiling`` and ``consequential_decision`` are True triggers
        REQUIRES_HUMAN_REVIEW;
    (b) Va. Code §59.1-578(A) — Sensitive personal data used in AI processing
        requires opt-in consent.  Absence of ``consent_obtained`` when
        ``sensitive_data_ai_processing`` is True results in denial;
    (c) Va. Code §59.1-581 — High-risk AI processing requires a data protection
        assessment before deployment.  Absence of ``data_protection_assessment``
        when ``ai_system_type == "high_risk"`` results in denial;
    (d) Va. Code §59.1-578(B) — AI processing of minor data requires verifiable
        parental consent.  Presence of ``child_data_ai`` without verifiable
        parental consent results in unconditional denial.

    References
    ----------
    Virginia Consumer Data Protection Act (VCDPA) Va. Code §59.1-577 et seq.
    """

    FILTER_NAME: str = "VIRGINIA_AI_PROVISIONS_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # Va. Code §59.1-578(B) — child data in AI: denied (checked first — highest severity)
        if doc.get("child_data_ai"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Va. Code §59.1-578(B) — AI processing of minor data "
                    "prohibited without verifiable parental consent"
                ),
                regulation_citation="Virginia VCDPA Va. Code §59.1-578(B)",
                requires_logging=True,
            )

        # Va. Code §59.1-578(A) — sensitive data in AI without opt-in consent: denied
        if doc.get("sensitive_data_ai_processing") and not doc.get("consent_obtained"):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Va. Code §59.1-578(A) — sensitive personal data in AI "
                    "processing requires opt-in consent"
                ),
                regulation_citation="Virginia VCDPA Va. Code §59.1-578(A)",
                requires_logging=True,
            )

        # Va. Code §59.1-581 — high-risk AI without data protection assessment: denied
        if (
            doc.get("ai_system_type") == "high_risk"
            and not doc.get("data_protection_assessment")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Va. Code §59.1-581 — high-risk AI processing requires "
                    "data protection assessment"
                ),
                regulation_citation="Virginia VCDPA Va. Code §59.1-581",
                requires_logging=True,
            )

        # Va. Code §59.1-579 — automated profiling for consequential decisions without review: requires review
        if (
            doc.get("automated_profiling")
            and doc.get("consequential_decision")
            and not doc.get("human_review_available")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Va. Code §59.1-579 — profiling for consequential decisions "
                    "requires human review option"
                ),
                regulation_citation="Virginia VCDPA Va. Code §59.1-579",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Va. Code §59.1-577 VCDPA AI provisions — compliant",
            regulation_citation="Virginia VCDPA Va. Code §59.1-577 et seq.",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Multi-state cross-border (USStateAICrossBorderFilter)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class USStateAICrossBorderFilter:
    """
    Layer 4: US multi-state AI law applicability framework.

    Where a consumer resides in a state with enacted AI or privacy law, those
    obligations attach to the data controller regardless of where the AI
    system is physically operated.  Four cross-border rules apply:

    (a) Illinois (BIPA) — Illinois residents' biometric data is protected
        under 740 ILCS 14 regardless of where the AI system processes it.
        Absence of ``biipa_written_consent`` for ``consumer_state == "Illinois"``
        with biometric data results in denial;
    (b) Colorado — The Colorado AI Act §6-1-1702 applies to Colorado
        residents regardless of AI system location.  High-risk AI without an
        impact assessment for Colorado residents results in denial;
    (c) Virginia / Texas / Connecticut — These states require an opt-out from
        automated consequential decisions for their residents.  Absence of
        ``opt_out_offered`` triggers REQUIRES_HUMAN_REVIEW;
    (d) California (CPRA) — Cal. Civ. Code §1798.185(a)(16) requires
        disclosure of automated decision-making logic to California residents.
        Absence of ``ccpa_ai_disclosure`` for California residents results in
        denial.

    References
    ----------
    Illinois BIPA 740 ILCS 14
    Colorado AI Act 2024 (SB 24-205) CRS §6-1-1702
    Virginia VCDPA Va. Code §59.1-579
    Texas TDPSA Tex. Bus. & Com. Code §541 et seq.
    Connecticut CTDPA Conn. Gen. Stat. §42-515 et seq.
    California CPRA Cal. Civ. Code §1798.185(a)(16)
    """

    FILTER_NAME: str = "US_STATE_AI_CROSS_BORDER_FILTER"

    # States requiring automated decision opt-out
    _OPT_OUT_STATES: frozenset = frozenset({"Virginia", "Texas", "Connecticut"})

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        consumer_state = doc.get("consumer_state", "")

        # Illinois BIPA — Illinois residents' biometric data requires written consent
        if (
            consumer_state == "Illinois"
            and doc.get("biometric_data_type")
            and not doc.get("biipa_written_consent")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "740 ILCS 14 BIPA — Illinois residents' biometric data requires "
                    "written consent regardless of processing location"
                ),
                regulation_citation="Illinois BIPA 740 ILCS 14",
                requires_logging=True,
            )

        # Colorado AI Act — applies to Colorado residents regardless of AI system location
        if (
            consumer_state == "Colorado"
            and doc.get("high_risk_ai")
            and not doc.get("impact_assessment_completed")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Colorado AI Act §6-1-1702 — applies to Colorado residents "
                    "regardless of AI system location"
                ),
                regulation_citation="Colorado AI Act 2024 (SB 24-205) CRS §6-1-1702",
                requires_logging=True,
            )

        # California CPRA — automated decision-making disclosure required for CA residents
        if (
            consumer_state == "California"
            and doc.get("ai_decision_making")
            and not doc.get("ccpa_ai_disclosure")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Cal. Civ. Code §1798.185(a)(16) — CPRA requires disclosure "
                    "of automated decision-making logic to CA residents"
                ),
                regulation_citation="California CPRA Cal. Civ. Code §1798.185(a)(16)",
                requires_logging=True,
            )

        # VA/TX/CT — automated consequential decision opt-out required
        if (
            consumer_state in self._OPT_OUT_STATES
            and doc.get("automated_decision")
            and doc.get("consequential_decision")
            and not doc.get("opt_out_offered")
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Multi-state consumer AI rights — automated decision opt-out "
                    "required for VA/TX/CT residents"
                ),
                regulation_citation=(
                    "Virginia VCDPA Va. Code §59.1-579; "
                    "Texas TDPSA Tex. Bus. & Com. Code §541; "
                    "Connecticut CTDPA Conn. Gen. Stat. §42-515"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="US State AI Law multi-jurisdiction — compliant",
            regulation_citation=(
                "US State AI Laws: CO/IL/VA/TX/CT/CA — multi-jurisdiction framework"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Integration wrappers
# ---------------------------------------------------------------------------


class USStateAILangChainPolicyGuard:
    """
    LangChain integration — wraps the four US State AI governance filters as a
    LangChain-compatible ``Runnable``-style tool guard.

    Implements ``invoke(input_doc)`` and ``ainvoke(input_doc)`` so the guard
    can be inserted into a LangChain chain or used as a tool callback.  Raises
    ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def invoke(self, input_doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(input_doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"US State AI governance DENIED: {r.reason}")
        return results

    def ainvoke(self, input_doc: dict[str, Any]) -> list[FilterResult]:
        """Async-compatible entry point (synchronous implementation)."""
        return self.invoke(input_doc)


class USStateAICrewAIGovernanceGuard:
    """
    CrewAI integration — wraps the four US State AI governance filters as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    name: str = "USStateAIGovernanceGuard"
    description: str = (
        "Enforces US state AI governance policies on documents processed "
        "by a CrewAI agent."
    )

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def _run(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"US State AI governance DENIED: {r.reason}")
        return results


class USStateAIAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    US State AI governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``USStateAIMAFPolicyMiddleware`` for the Microsoft
    Agent Framework.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
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
                raise PermissionError(f"US State AI governance DENIED: {r.reason}")
        return results


class USStateAISemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps US State AI governance filters as an SK
    ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``USStateAIMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def enforce_governance(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"US State AI governance DENIED: {r.reason}")
        return results


class USStateAILlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing US State AI governance
    between retrieval and synthesis steps.

    Implements ``process_event(doc)`` compatible with LlamaIndex
    ``WorkflowStep`` protocol (LlamaIndex 0.14.x).  Raises ``PermissionError``
    when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def process_event(self, doc: dict[str, Any]) -> list[FilterResult]:
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(f"US State AI governance DENIED: {r.reason}")
        return results


class USStateAIHaystackGovernanceComponent:
    """
    Haystack integration — ``@component``-compatible governance filter for
    Haystack 2.x pipelines (current: Haystack 2.27.0).

    Implements ``run(documents)`` following the Haystack component protocol so
    it can be inserted into a Haystack pipeline.  Filters each document dict
    individually; denied documents are excluded from the output.
    """

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [
            doc
            for doc in documents
            if not any(f.filter(doc).is_denied for f in self._filters)
        ]
        return {"documents": passed}


class USStateAIDSPyGovernanceModule:
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
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def forward(self, doc: dict[str, Any], **kwargs: Any) -> Any:
        for f in self._filters:
            result = f.filter(doc)
            if result.is_denied:
                raise PermissionError(f"US State AI governance DENIED: {result.reason}")
        return self._module(doc, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)


class USStateAIMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying US State AI governance filters.

    MAF is the enterprise successor to AutoGen and Semantic Kernel (released
    2025).  Implements ``process(message, next_handler)`` so this middleware
    can be registered in an MAF agent pipeline.  Raises ``PermissionError``
    when any filter returns DENIED.
    """

    def __init__(self) -> None:
        self._filters = [
            ColoradoSB205Filter(),
            IllinoisBIPAAIFilter(),
            VirginiaAIProvisionsFilter(),
            USStateAICrossBorderFilter(),
        ]

    def process(self, message: dict[str, Any], next_handler: Any) -> Any:
        for f in self._filters:
            result = f.filter(message)
            if result.is_denied:
                raise PermissionError(f"US State AI governance DENIED: {result.reason}")
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
    # 1. Colorado: high-risk AI without impact assessment → DENIED
    # ------------------------------------------------------------------
    _show(
        "Colorado — High-Risk AI Without Impact Assessment (§6-1-1702)",
        ColoradoSB205Filter().filter({
            "high_risk_ai": True,
            "impact_assessment_completed": False,
            "bias_testing_completed": True,
        }),
    )

    # ------------------------------------------------------------------
    # 2. Illinois: biometric collection without written consent → DENIED
    # ------------------------------------------------------------------
    _show(
        "Illinois BIPA — Face Geometry Collection Without Written Consent (740 ILCS 14/15(b))",
        IllinoisBIPAAIFilter().filter({
            "biometric_data_type": "face_geometry",
            "biipa_written_consent": False,
            "biipa_retention_policy": True,
        }),
    )

    # ------------------------------------------------------------------
    # 3. Virginia: automated profiling without human review → REQUIRES_HUMAN_REVIEW
    # ------------------------------------------------------------------
    _show(
        "Virginia VCDPA — Automated Profiling Without Human Review (Va. Code §59.1-579)",
        VirginiaAIProvisionsFilter().filter({
            "automated_profiling": True,
            "consequential_decision": True,
            "human_review_available": False,
        }),
    )

    # ------------------------------------------------------------------
    # 4. Cross-border: Illinois resident + biometric data → DENIED
    # ------------------------------------------------------------------
    _show(
        "Cross-Border — Illinois Resident + Biometric Data Without Consent (BIPA extraterritorial)",
        USStateAICrossBorderFilter().filter({
            "consumer_state": "Illinois",
            "biometric_data_type": "voiceprint",
            "biipa_written_consent": False,
        }),
    )

    # ------------------------------------------------------------------
    # 5. Fully compliant document passing all 4 filters → APPROVED
    # ------------------------------------------------------------------
    compliant_doc = {
        "high_risk_ai": True,
        "impact_assessment_completed": True,
        "bias_testing_completed": True,
        "automated_employment_decision": False,
        "human_oversight": True,
        "biometric_identifier": False,
        "written_consent": True,
        "biometric_data_type": None,
        "biipa_written_consent": True,
        "biipa_retention_policy": True,
        "video_interview_ai": False,
        "ai_video_disclosure": True,
        "third_party_sharing": False,
        "automated_profiling": False,
        "consequential_decision": False,
        "human_review_available": True,
        "sensitive_data_ai_processing": False,
        "consent_obtained": True,
        "ai_system_type": "low_risk",
        "data_protection_assessment": True,
        "child_data_ai": False,
        "consumer_state": "New York",
        "ai_decision_making": False,
        "ccpa_ai_disclosure": True,
        "automated_decision": False,
        "opt_out_offered": True,
    }
    filters = [
        ColoradoSB205Filter(),
        IllinoisBIPAAIFilter(),
        VirginiaAIProvisionsFilter(),
        USStateAICrossBorderFilter(),
    ]
    print("\n" + "=" * 70)
    print("Scenario: Fully Compliant Document — All 4 Filters")
    for f in filters:
        r = f.filter(compliant_doc)
        print(f"  [{r.decision}] {f.FILTER_NAME}")
    print("=" * 70)
