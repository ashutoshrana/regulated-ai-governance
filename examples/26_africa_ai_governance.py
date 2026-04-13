"""
26_africa_ai_governance.py — Multi-jurisdiction AI governance framework for
AI systems subject to African data protection and AI regulation, covering the
three largest African data protection regimes and cross-border transfer rules
under the African Union Data Policy Framework.

Demonstrates a multi-layer governance orchestrator where four filters impose
independent requirements on AI systems deployed in Kenya, Nigeria, and South
Africa, with a cross-border transfer filter enforcing the AU adequacy framework:

    Layer 1  — Kenya Data Protection Act 2019 (DPA) + Kenya National AI
               Strategy 2023:

               Section 30 — Automated Decision-Making: significant automated
                   decisions with no human review require human oversight
                   before execution;
               Section 25 — Sensitive Personal Data: processing sensitive
                   personal data without explicit consent is prohibited;
               Section 31 — Profiling: profiling of data subjects requires
                   prior notice to the data subject.

    Layer 2  — Nigeria Data Protection Act 2023 (NDPA) + NITDA AI Policy:

               Section 34 — Automated Processing: high-risk automated
                   processing without a Data Protection Impact Assessment
                   (DPIA) requires human review;
               Section 25 — Sensitive Data: processing sensitive data without
                   explicit consent is prohibited;
               NITDA AI Policy §3.2 — High-Risk AI Registration: high-risk AI
                   systems must be registered with the Nigeria Information
                   Technology Development Agency (NITDA) before deployment.

    Layer 3  — South Africa Protection of Personal Information Act 2013
               (POPIA) + Financial Sector Conduct Authority (FSCA) AI
               Guidance 2023:

               Section 71 — Automated Decision: automated decisions with
                   significant impact require human review unless human
                   oversight is already in place;
               Section 26 — Special Personal Information: processing special
                   personal information requires explicit consent unless the
                   purpose is legitimate research with appropriate safeguards;
               FSCA AI Guidance 2023 — Financial AI: AI systems deployed in
                   financial services require FSCA notification before
                   go-live.

    Layer 4  — Africa Cross-Border Transfer Filter (AU Data Policy
               Framework 2022):

               Adequate jurisdictions: Kenya (KE), Nigeria (NG), South
                   Africa (ZA), Ghana (GH), Morocco (MA), Tunisia (TN),
                   Egypt (EG) — AU adequacy framework;
               Transfers between adequate jurisdictions are approved;
               Transfers to non-adequate jurisdictions require contractual
                   or equivalent transfer safeguards.

No external dependencies required.

Run:
    python examples/26_africa_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AfricaAIContext:
    """
    Governance review context for an Africa-jurisdiction AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    jurisdiction : str
        ISO alpha-2 country code of the primary deployment jurisdiction.
        Expected values: "KE" (Kenya), "NG" (Nigeria), "ZA" (South Africa).
    sector : str
        Deployment sector: "financial_services", "healthcare", "government",
        "general".
    is_automated_decision : bool
        True if the AI system makes or significantly influences decisions
        about individuals without meaningful human involvement.
    is_significant_decision : bool
        True if the automated decision has a significant impact on the data
        subject's rights, opportunities, or welfare (Kenya DPA §30).
    is_high_risk : bool
        True if the automated processing poses high risk to the rights and
        freedoms of individuals (Nigeria NDPA §34).
    is_high_risk_ai : bool
        True if the AI system is classified as high-risk under Nigeria's
        NITDA AI Policy §3.2, requiring NITDA registration.
    has_human_review : bool
        True if a qualified human reviews and can override automated
        decisions before execution.
    has_explicit_consent : bool
        True if explicit, freely given, specific, and informed consent has
        been obtained for the processing activity.
    has_sensitive_data : bool
        True if the AI system processes sensitive or special category
        personal data (health, biometrics, political opinions, religion,
        race, sexual orientation, criminal records).
    involves_profiling : bool
        True if the AI system profiles individuals based on personal data
        (Kenya DPA §31).
    has_profiling_notice : bool
        True if the data subject has been given prior notice that profiling
        will occur (Kenya DPA §31).
    has_dpia : bool
        True if a Data Protection Impact Assessment has been completed for
        high-risk automated processing (Nigeria NDPA §34).
    has_nitda_registration : bool
        True if the high-risk AI system has been registered with Nigeria's
        NITDA as required by the NITDA AI Policy §3.2.
    is_research_purpose : bool
        True if the processing of special personal information is for
        legitimate research with appropriate safeguards (POPIA §26
        research exemption).
    has_fsca_approval : bool
        True if the financial AI system has received FSCA notification/
        approval as required by FSCA AI Guidance 2023.
    source_jurisdiction : str
        ISO alpha-2 code of the jurisdiction from which data is transferred
        (cross-border transfer source).
    destination_jurisdiction : str
        ISO alpha-2 code of the jurisdiction to which data is transferred
        (cross-border transfer destination).
    has_transfer_safeguards : bool
        True if contractual or equivalent transfer safeguards (e.g. Standard
        Contractual Clauses) are in place for cross-border transfers.
    """

    user_id: str
    jurisdiction: str
    sector: str
    is_automated_decision: bool = False
    is_significant_decision: bool = False
    is_high_risk: bool = False
    is_high_risk_ai: bool = False
    has_human_review: bool = True
    has_explicit_consent: bool = False
    has_sensitive_data: bool = False
    involves_profiling: bool = False
    has_profiling_notice: bool = True
    has_dpia: bool = False
    has_nitda_registration: bool = False
    is_research_purpose: bool = False
    has_fsca_approval: bool = False
    source_jurisdiction: str = "KE"
    destination_jurisdiction: str = "KE"
    has_transfer_safeguards: bool = False


@dataclass(frozen=True)
class AfricaAIDocument:
    """
    Document metadata submitted to the Africa AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    content : str
        Textual content or description of the document being processed.
    """

    document_id: str
    content: str


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single Africa AI governance filter evaluation."""

    filter_name: str
    decision: str = "APPROVED"
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = True

    @property
    def is_denied(self) -> bool:
        """True only if this filter produced a DENIED decision."""
        return self.decision == "DENIED"


# ---------------------------------------------------------------------------
# Layer 1 — Kenya Data Protection Act 2019 + Kenya National AI Strategy 2023
# ---------------------------------------------------------------------------


class KenyaAIFilter:
    """
    Layer 1: Kenya Data Protection Act 2019 (DPA) and Kenya National AI
    Strategy 2023.

    Kenya's Data Protection Act 2019 (Act No. 24 of 2019) establishes
    fundamental obligations for organisations that collect, process, or
    store personal data of Kenyan residents.  Three principal controls apply
    to AI systems:

    (a) Section 30 — Automated Decision-Making: data subjects have the right
        not to be subject to a decision based solely on automated processing,
        including profiling, if the decision produces significant effects on
        them; such decisions without human review require escalation for human
        oversight;
    (b) Section 25 — Sensitive Personal Data: processing sensitive personal
        data (health, biometrics, political opinions, religion, race, sexual
        orientation, criminal records) without explicit consent is prohibited;
    (c) Section 31 — Profiling: any profiling of data subjects requires that
        prior notice be given to the data subject before profiling commences.

    References
    ----------
    Kenya Data Protection Act 2019 (Act No. 24 of 2019)
    Office of the Data Protection Commissioner (ODPC) — DPA Implementation
    Kenya National AI Strategy 2023
    """

    FILTER_NAME = "KENYA_AI_FILTER"

    def evaluate(
        self, context: AfricaAIContext, document: AfricaAIDocument
    ) -> FilterResult:
        # Section 30 — significant automated decision without human review
        if (
            context.is_automated_decision
            and not context.has_human_review
            and context.is_significant_decision
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Kenya DPA 2019 §30: Significant automated decisions require "
                    "human review"
                ),
                regulation_citation="Kenya Data Protection Act 2019 §30",
                requires_logging=True,
            )

        # Section 25 — sensitive personal data without explicit consent
        if context.has_sensitive_data and not context.has_explicit_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Kenya DPA 2019 §25: Sensitive personal data requires "
                    "explicit consent"
                ),
                regulation_citation="Kenya Data Protection Act 2019 §25",
                requires_logging=True,
            )

        # Section 31 — profiling without prior notice
        if context.involves_profiling and not context.has_profiling_notice:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Kenya DPA 2019 §31: Profiling requires prior notice to "
                    "data subject"
                ),
                regulation_citation="Kenya Data Protection Act 2019 §31",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Compliant with Kenya DPA 2019 obligations",
            regulation_citation="Kenya Data Protection Act 2019",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Nigeria Data Protection Act 2023 + NITDA AI Policy
# ---------------------------------------------------------------------------


class NigeriaAIFilter:
    """
    Layer 2: Nigeria Data Protection Act 2023 (NDPA) and Nigeria Information
    Technology Development Agency (NITDA) AI Policy.

    Nigeria's Data Protection Act 2023 (Act No. 37 of 2023) establishes a
    comprehensive data protection regime aligned with international standards.
    Three principal controls apply to AI systems:

    (a) Section 34 — Automated Processing: high-risk automated processing
        that may produce adverse effects on data subjects requires a Data
        Protection Impact Assessment (DPIA) before deployment; absence of a
        DPIA for high-risk automated systems requires human review;
    (b) Section 25 — Sensitive Data: processing sensitive personal data
        without explicit consent is prohibited;
    (c) NITDA AI Policy §3.2 — AI System Registration: high-risk AI systems
        must be registered with NITDA before deployment to ensure accountability
        and oversight.

    References
    ----------
    Nigeria Data Protection Act 2023 (Act No. 37 of 2023)
    Nigeria Data Protection Commission (NDPC) — NDPA Implementation
    NITDA Artificial Intelligence Policy §3.2 — High-Risk AI Registration
    """

    FILTER_NAME = "NIGERIA_AI_FILTER"

    def evaluate(
        self, context: AfricaAIContext, document: AfricaAIDocument
    ) -> FilterResult:
        # Section 34 — high-risk automated processing without DPIA
        if (
            context.is_automated_decision
            and context.is_high_risk
            and not context.has_dpia
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Nigeria NDPA 2023 §34: High-risk automated processing "
                    "requires DPIA"
                ),
                regulation_citation="Nigeria Data Protection Act 2023 §34",
                requires_logging=True,
            )

        # Section 25 — sensitive data without explicit consent
        if context.has_sensitive_data and not context.has_explicit_consent:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Nigeria NDPA 2023 §25: Sensitive data requires explicit "
                    "consent"
                ),
                regulation_citation="Nigeria Data Protection Act 2023 §25",
                requires_logging=True,
            )

        # NITDA AI Policy §3.2 — high-risk AI system without NITDA registration
        if context.is_high_risk_ai and not context.has_nitda_registration:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Nigeria NITDA AI Policy §3.2: High-risk AI systems require "
                    "NITDA registration"
                ),
                regulation_citation="Nigeria NITDA AI Policy §3.2",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Compliant with Nigeria NDPA 2023 obligations",
            regulation_citation="Nigeria Data Protection Act 2023",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — South Africa POPIA 2013 + FSCA AI Guidance 2023
# ---------------------------------------------------------------------------


class SouthAfricaAIFilter:
    """
    Layer 3: South Africa Protection of Personal Information Act 2013 (POPIA)
    and Financial Sector Conduct Authority (FSCA) AI Guidance 2023.

    South Africa's POPIA (Act No. 4 of 2013, in force July 1, 2020) is a
    comprehensive data protection law modelled on the EU Data Protection
    Directive.  Three principal controls apply to AI systems:

    (a) Section 71 — Automated Decision: data subjects have the right not to
        be subject to a decision which results in legal or similar significant
        effects and which is based solely on automated processing; such
        automated decisions without human review require escalation;
    (b) Section 26 — Special Personal Information: processing of special
        personal information (religion, race, health, sexual orientation,
        criminal behaviour, biometrics, trade union membership, political
        persuasion) requires explicit consent unless the purpose is legitimate
        research with appropriate safeguards;
    (c) FSCA AI Guidance 2023 — Financial Services AI: AI systems deployed in
        the financial services sector require FSCA notification before
        go-live.

    References
    ----------
    Protection of Personal Information Act 2013 (South Africa, Act No. 4)
    Information Regulator South Africa — POPIA Implementation Guidance
    Financial Sector Conduct Authority (FSCA) AI Guidance 2023
    """

    FILTER_NAME = "SOUTH_AFRICA_AI_FILTER"

    def evaluate(
        self, context: AfricaAIContext, document: AfricaAIDocument
    ) -> FilterResult:
        # Section 71 — automated decision without human review
        if context.is_automated_decision and not context.has_human_review:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "POPIA 2013 §71: Automated decisions with significant impact "
                    "require human review"
                ),
                regulation_citation="POPIA 2013 §71",
                requires_logging=True,
            )

        # Section 26 — special personal information without consent or research exemption
        if context.has_sensitive_data and not (
            context.has_explicit_consent or context.is_research_purpose
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "POPIA 2013 §26: Processing special personal information "
                    "requires explicit consent"
                ),
                regulation_citation="POPIA 2013 §26",
                requires_logging=True,
            )

        # FSCA AI Guidance 2023 — financial services AI without FSCA approval
        if context.sector == "financial_services" and not context.has_fsca_approval:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "FSCA AI Guidance 2023: Financial AI systems require FSCA "
                    "notification"
                ),
                regulation_citation="FSCA AI Guidance 2023",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Compliant with POPIA 2013 and FSCA AI Guidance obligations",
            regulation_citation="South Africa POPIA 2013",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Africa Cross-Border Transfer Filter (AU Data Policy Framework 2022)
# ---------------------------------------------------------------------------


class AfricaCrossBorderFilter:
    """
    Layer 4: Africa Cross-Border Data Transfer Filter based on the African
    Union Data Policy Framework 2022.

    The African Union Data Policy Framework (2022) establishes a continental
    approach to data governance, including principles for cross-border data
    transfers.  National laws implementing these principles include:

    Kenya DPA 2019 §48 — transfers to non-adequate countries require
        contractual or equivalent safeguards;
    Nigeria NDPA 2023 §43 — cross-border transfers require demonstration of
        adequate protections in the receiving jurisdiction;
    POPIA 2013 §72 — transfers outside South Africa require a level of
        protection equivalent to POPIA standards.

    Adequate jurisdictions (AU adequacy framework — indicative):
        Kenya (KE), Nigeria (NG), South Africa (ZA), Ghana (GH),
        Morocco (MA), Tunisia (TN), Egypt (EG).

    References
    ----------
    African Union Data Policy Framework 2022
    Kenya Data Protection Act 2019 §48
    Nigeria Data Protection Act 2023 §43
    Protection of Personal Information Act 2013 (South Africa) §72
    """

    FILTER_NAME = "AFRICA_CROSS_BORDER_FILTER"

    # Jurisdictions deemed adequate under the AU Data Policy Framework
    _ADEQUATE_JURISDICTIONS: frozenset = frozenset(
        {"KE", "NG", "ZA", "GH", "MA", "TN", "EG"}
    )

    def _source_citation(self, source_jurisdiction: str) -> str:
        """Return the transfer restriction citation for the source jurisdiction."""
        citations = {
            "KE": (
                "Kenya DPA 2019 §48: Transfer to non-adequate country requires "
                "safeguards"
            ),
            "NG": (
                "Nigeria NDPA 2023 §43: Cross-border transfer requires adequate "
                "protections"
            ),
            "ZA": (
                "POPIA 2013 §72: Transfer outside South Africa requires adequate "
                "protection"
            ),
        }
        return citations.get(
            source_jurisdiction,
            "Africa AI Governance: Cross-border transfer requires adequate safeguards",
        )

    def evaluate(
        self, context: AfricaAIContext, document: AfricaAIDocument
    ) -> FilterResult:
        src = context.source_jurisdiction
        dst = context.destination_jurisdiction

        # Both jurisdictions adequate — transfer approved under AU framework
        if (
            src in self._ADEQUATE_JURISDICTIONS
            and dst in self._ADEQUATE_JURISDICTIONS
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason=(
                    "Transfer between adequate AU jurisdictions — approved under "
                    "AU Data Policy Framework 2022"
                ),
                regulation_citation=(
                    "AU Data Policy Framework 2022: adequate jurisdiction transfer"
                ),
                requires_logging=False,
            )

        # Destination not adequate and no safeguards in place
        if (
            dst not in self._ADEQUATE_JURISDICTIONS
            and not context.has_transfer_safeguards
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    f"Transfer to non-adequate jurisdiction ({dst}) without "
                    "contractual safeguards is prohibited"
                ),
                regulation_citation=self._source_citation(src),
                requires_logging=True,
            )

        # Safeguards in place — approved
        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Contractual safeguards satisfy transfer requirements"
            ),
            regulation_citation=(
                "Contractual safeguards satisfy transfer requirements"
            ),
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class AfricaAIGovernanceOrchestrator:
    """
    Four-filter Africa AI governance orchestrator.

    Evaluation order:
        KenyaAIFilter  →  NigeriaAIFilter  →
        SouthAfricaAIFilter  →  AfricaCrossBorderFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``FilterResult`` objects and passed
    to ``AfricaAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            KenyaAIFilter(),
            NigeriaAIFilter(),
            SouthAfricaAIFilter(),
            AfricaCrossBorderFilter(),
        ]

    def evaluate(
        self, context: AfricaAIContext, document: AfricaAIDocument
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : AfricaAIContext
            The AI system processing context to evaluate.
        document : AfricaAIDocument
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
class AfricaAIGovernanceReport:
    """
    Aggregated Africa AI governance report across all four filters.

    Decision aggregation:
    - Any DENIED result                     → overall_decision is "DENIED"
    - No DENIED + any REQUIRES_HUMAN_REVIEW → "REQUIRES_HUMAN_REVIEW"
    - All APPROVED                          → "APPROVED"

    is_compliant is True unless overall_decision is "DENIED".
    REQUIRES_HUMAN_REVIEW is not a denial but indicates a compliance gap
    that must be addressed before the system can be considered fully compliant.

    Attributes
    ----------
    context : AfricaAIContext
        The AI system context that was evaluated.
    document : AfricaAIDocument
        The document that was evaluated.
    filter_results : list[FilterResult]
        Per-filter results in evaluation order.
    """

    context: AfricaAIContext
    document: AfricaAIDocument
    filter_results: List[FilterResult]

    @property
    def overall_decision(self) -> str:
        """
        Aggregate decision across all filters.

        Returns "DENIED" if any filter denied; "REQUIRES_HUMAN_REVIEW" if any
        filter requires human review (but none denied); "APPROVED" otherwise.
        """
        if any(r.is_denied for r in self.filter_results):
            return "DENIED"
        if any(r.decision == "REQUIRES_HUMAN_REVIEW" for r in self.filter_results):
            return "REQUIRES_HUMAN_REVIEW"
        return "APPROVED"

    @property
    def is_compliant(self) -> bool:
        """
        True unless overall_decision is "DENIED".

        REQUIRES_HUMAN_REVIEW is not a denial — the system may proceed once
        human review is completed.
        """
        return self.overall_decision != "DENIED"

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary across all four filters.

        Returns a multi-line string listing each filter name, its decision,
        and either the approval reason or the denial/review reason.
        """
        lines: List[str] = [
            (
                f"Africa AI Governance Report — user_id={self.context.user_id}"
            ),
            (
                f"Jurisdiction: {self.context.jurisdiction}  |  "
                f"Sector: {self.context.sector}  |  "
                f"Overall Decision: {self.overall_decision}"
            ),
            "",
        ]
        for result in self.filter_results:
            lines.append(f"  [{result.decision}]  {result.filter_name}")
            if result.reason:
                lines.append(f"    Reason: {result.reason}")
            if result.regulation_citation:
                lines.append(f"    Citation: {result.regulation_citation}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_general_ke_base() -> tuple[AfricaAIContext, AfricaAIDocument]:
    """
    Base context: fully compliant general-sector Kenya system.
    Used as the baseline from which failing scenarios are derived.
    """
    context = AfricaAIContext(
        user_id="AF-AI-001",
        jurisdiction="KE",
        sector="general",
        is_automated_decision=False,
        is_significant_decision=False,
        is_high_risk=False,
        is_high_risk_ai=False,
        has_human_review=True,
        has_explicit_consent=True,
        has_sensitive_data=False,
        involves_profiling=False,
        has_profiling_notice=True,
        has_dpia=True,
        has_nitda_registration=True,
        is_research_purpose=False,
        has_fsca_approval=True,
        source_jurisdiction="KE",
        destination_jurisdiction="KE",
        has_transfer_safeguards=False,
    )
    document = AfricaAIDocument(
        document_id="DOC-AF-001",
        content="General compliance document for Kenya AI system",
    )
    return context, document


def _demonstrate_scenario(
    title: str,
    context: AfricaAIContext,
    document: AfricaAIDocument,
    orchestrator: AfricaAIGovernanceOrchestrator,
) -> None:
    results = orchestrator.evaluate(context, document)
    report = AfricaAIGovernanceReport(
        context=context,
        document=document,
        filter_results=results,
    )
    print(f"\n{'=' * 70}")
    print(f"Scenario: {title}")
    print("=" * 70)
    print(report.compliance_summary)


if __name__ == "__main__":
    orchestrator = AfricaAIGovernanceOrchestrator()
    base_ctx, base_doc = _compliant_general_ke_base()

    # Scenario 1 — fully compliant baseline
    _demonstrate_scenario(
        "Fully Compliant General-Sector Kenya AI System",
        base_ctx,
        base_doc,
        orchestrator,
    )

    # Scenario 2 — Kenya: significant automated decision without human review
    ctx2 = AfricaAIContext(
        **{
            **base_ctx.__dict__,
            "is_automated_decision": True,
            "is_significant_decision": True,
            "has_human_review": False,
        }
    )
    _demonstrate_scenario(
        "Kenya: Significant Automated Decision — No Human Review",
        ctx2,
        base_doc,
        orchestrator,
    )

    # Scenario 3 — Nigeria: high-risk automated processing without DPIA
    ctx3 = AfricaAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "NG",
            "is_automated_decision": True,
            "is_high_risk": True,
            "has_dpia": False,
        }
    )
    _demonstrate_scenario(
        "Nigeria: High-Risk Automated Processing — No DPIA",
        ctx3,
        base_doc,
        orchestrator,
    )

    # Scenario 4 — Cross-border: transfer to non-adequate jurisdiction without safeguards
    ctx4 = AfricaAIContext(
        **{
            **base_ctx.__dict__,
            "source_jurisdiction": "ZA",
            "destination_jurisdiction": "US",
            "has_transfer_safeguards": False,
        }
    )
    _demonstrate_scenario(
        "Cross-Border: Transfer to Non-Adequate Jurisdiction — No Safeguards",
        ctx4,
        base_doc,
        orchestrator,
    )
