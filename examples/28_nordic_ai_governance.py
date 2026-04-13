"""
28_nordic_ai_governance.py — Nordic/Scandinavian AI Governance Framework

Implements national AI governance frameworks for Sweden, Denmark, and Finland,
supplementing the EU AI Act with jurisdiction-specific Data Protection Authority
guidelines and national GDPR implementation legislation.  A fourth filter governs
cross-border data transfers within the Nordic/EEA zone.

Nordic jurisdictions have each issued AI-specific guidance through their national
Data Protection Authorities (DPAs), building on the General Data Protection
Regulation (EU 2016/679) as implemented in national law.  This example models
the principal compliance controls from each DPA's AI guidance and the relevant
national GDPR-implementing statute.

Demonstrates a multi-layer governance orchestrator where four filters enforce
independent national requirements:

    Layer 1  — Sweden (SwedenAIFilter):

               IMY Guideline §3.2 — Swedish Data Protection Authority (IMY)
                   AI Guidelines 2023: public authority automated decisions
                   require human oversight;
               SFS 2018:218 §3 — Swedish GDPR-implementing Act: sensitive data
                   processing requires explicit consent or an Article 9 legal
                   basis;
               IMY Guideline §4.1 — high-risk AI systems require a transparency
                   notice for affected individuals.

    Layer 2  — Denmark (DenmarkAIFilter):

               Datatilsynet AI Guidance §2.3 — Danish Data Protection Agency
                   AI Guidance 2023: limited/high-risk automated decisions
                   require human review capability;
               Act No. 502/2018 §7 — Danish GDPR Supplementary Act: high-risk
                   AI processing sensitive data requires a DPIA;
               Datatilsynet AI Guidance §3.1 — public sector high-risk AI
                   systems should be registered in the national registry.

    Layer 3  — Finland (FinlandAIFilter):

               Data Protection Act §6 (1050/2018) — Finnish Data Protection
                   Act: sensitive data requires explicit consent or legal basis;
               TSV AI Guidelines §2.2 — Finnish Data Protection Ombudsman
                   (TSV) AI Guidelines 2023: public authority AI decisions
                   require a transparency notice;
               TSV AI Guidelines §3.3 — high-risk AI systems require a Data
                   Protection Impact Assessment.

    Layer 4  — Cross-border (NordicCrossBorderFilter):

               EEA intra-transfer exemption: transfers within the EEA are
                   permitted without additional safeguards;
               GDPR Article 46 — Standard Contractual Clauses or BCRs
                   satisfy transfer requirements to non-adequate countries;
               Jurisdiction-specific national GDPR provisions for transfers to
                   non-adequate countries without GDPR Art. 46 safeguards.

No external dependencies required.

Run:
    python examples/28_nordic_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NordicAIContext:
    """
    Governance review context for an AI system evaluated under Nordic national
    AI governance frameworks (Sweden, Denmark, Finland).

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    jurisdiction : str
        Primary jurisdiction for the AI system: "SE" (Sweden), "DK" (Denmark),
        or "FI" (Finland).
    sector : str
        Operational sector: "public_sector", "healthcare", "financial",
        or "general".
    ai_risk_level : str
        AI system risk classification: "minimal", "limited", "high",
        or "unacceptable".
    is_public_authority : bool
        True if the deploying entity is a public authority or government body.
    has_gdpr_basis : bool
        True if a valid GDPR Article 9 legal basis exists for processing
        sensitive personal data (other than explicit consent).
    has_dpia : bool
        True if a Data Protection Impact Assessment has been completed for
        the AI system.
    is_automated_decision : bool
        True if the AI system makes automated decisions affecting individuals.
    has_human_oversight : bool
        True if the AI system includes mechanisms enabling human oversight
        and intervention in automated decisions.
    involves_sensitive_data : bool
        True if the AI system processes special categories of personal data
        under GDPR Article 9.
    has_explicit_consent : bool
        True if individuals have provided explicit consent for the processing
        of their sensitive personal data.
    is_registered_ai_system : bool
        True if the AI system has been registered in the applicable national
        AI registry (relevant for Denmark public sector).
    has_transparency_notice : bool
        True if affected individuals have received a transparency notice
        describing the AI system and its use of their data.
    source_jurisdiction : str
        Jurisdiction from which the data originates: "SE", "DK", "FI", etc.
    destination_jurisdiction : str
        Destination jurisdiction for cross-border data transfers.
    has_transfer_safeguards : bool
        True if GDPR Article 46 safeguards (Standard Contractual Clauses or
        Binding Corporate Rules) are in place for the transfer.
    """

    user_id: str
    jurisdiction: str           # "SE", "DK", "FI"
    sector: str                 # "public_sector", "healthcare", "financial", "general"
    ai_risk_level: str          # "minimal", "limited", "high", "unacceptable"
    is_public_authority: bool = False
    has_gdpr_basis: bool = False
    has_dpia: bool = False
    is_automated_decision: bool = False
    has_human_oversight: bool = True
    involves_sensitive_data: bool = False
    has_explicit_consent: bool = False
    is_registered_ai_system: bool = False
    has_transparency_notice: bool = False
    source_jurisdiction: str = "SE"
    destination_jurisdiction: str = "SE"
    has_transfer_safeguards: bool = False


@dataclass(frozen=True)
class NordicAIDocument:
    """
    Document metadata submitted to the Nordic AI governance orchestrator.

    Attributes
    ----------
    content : str
        Textual content or description of the document being processed.
    document_id : str
        Unique identifier for the document under review.
    doc_type : str
        Classification of the document, e.g. "ai_decision_record",
        "impact_assessment", "transparency_notice".
    """

    content: str
    document_id: str
    doc_type: str = "ai_decision_record"


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single Nordic AI governance filter evaluation."""

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
# Layer 1 — Sweden (SwedenAIFilter)
# ---------------------------------------------------------------------------


class SwedenAIFilter:
    """
    Layer 1: Sweden — IMY AI Guidelines 2023 + SFS 2018:218.

    The Swedish Data Protection Authority (Integritetsskyddsmyndigheten, IMY)
    issued national AI guidelines in 2023 supplementing the EU AI Act.  The
    Swedish GDPR-implementing Act (SFS 2018:218) provides national rules for
    sensitive data processing.  Three principal controls apply:

    (a) IMY Guideline §3.2 — Public authority automated decisions require
        human oversight.  Where a public authority uses an AI system to make
        automated decisions affecting individuals, and human oversight is
        absent, the system must be denied;
    (b) SFS 2018:218 §3 — Processing of sensitive personal data requires
        either explicit consent from the data subject or a valid legal basis
        under GDPR Article 9; absence of both results in denial;
    (c) IMY Guideline §4.1 — High-risk AI systems must provide affected
        individuals with a transparency notice; absence of such a notice
        triggers a requirement for human review.

    References
    ----------
    Sweden IMY AI Guidelines 2023 §3.2
    Sweden IMY AI Guidelines 2023 §4.1
    Sweden SFS 2018:218 §3 (Act with Supplementary Provisions to the GDPR)
    """

    FILTER_NAME = "SWEDEN_AI_FILTER"

    def evaluate(
        self, context: NordicAIContext, document: NordicAIDocument
    ) -> FilterResult:
        # IMY Guideline §3.2 — public authority automated decision without oversight: denied
        if (
            context.is_automated_decision
            and context.is_public_authority
            and not context.has_human_oversight
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Sweden IMY AI Guidelines 2023 §3.2: Public authority "
                    "automated decisions require human oversight"
                ),
                regulation_citation="Sweden IMY AI Guidelines 2023 §3.2",
                requires_logging=True,
            )

        # SFS 2018:218 §3 — sensitive data without consent or GDPR basis: denied
        if (
            context.involves_sensitive_data
            and not context.has_explicit_consent
            and not context.has_gdpr_basis
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Sweden SFS 2018:218 §3: Sensitive data processing requires "
                    "explicit consent or GDPR Article 9 basis"
                ),
                regulation_citation="Sweden SFS 2018:218 §3",
                requires_logging=True,
            )

        # IMY Guideline §4.1 — high-risk AI without transparency notice: requires review
        if context.ai_risk_level == "high" and not context.has_transparency_notice:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Sweden IMY AI Guidelines 2023 §4.1: High-risk AI systems "
                    "require transparency notice to affected individuals"
                ),
                regulation_citation="Sweden IMY AI Guidelines 2023 §4.1",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Sweden IMY AI Guidelines 2023 and SFS 2018:218 "
                "governance obligations"
            ),
            regulation_citation="Sweden IMY AI Guidelines 2023 + SFS 2018:218",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Denmark (DenmarkAIFilter)
# ---------------------------------------------------------------------------


class DenmarkAIFilter:
    """
    Layer 2: Denmark — Datatilsynet AI Guidance 2023 + Act No. 502/2018.

    The Danish Data Protection Agency (Datatilsynet) issued national AI
    guidance in 2023.  The Danish Act on Supplementary Provisions to the
    GDPR (Act No. 502/2018, as amended) provides national data protection
    rules.  Three principal controls apply:

    (a) Datatilsynet AI Guidance §2.3 — Limited or high-risk automated
        decisions must retain a human review capability; absence of oversight
        for such decisions triggers a requirement for human review;
    (b) Act No. 502/2018 §7 — High-risk AI systems that process sensitive
        personal data require a completed Data Protection Impact Assessment
        before deployment; absence of a DPIA results in denial;
    (c) Datatilsynet AI Guidance §3.1 — Public sector high-risk AI systems
        should be registered in the national AI registry; absence of
        registration triggers a requirement for human review.

    References
    ----------
    Denmark Datatilsynet AI Guidance 2023 §2.3
    Denmark Datatilsynet AI Guidance 2023 §3.1
    Denmark Act No. 502/2018 §7 (Data Protection Act)
    """

    FILTER_NAME = "DENMARK_AI_FILTER"

    def evaluate(
        self, context: NordicAIContext, document: NordicAIDocument
    ) -> FilterResult:
        # Act No. 502/2018 §7 — high-risk + sensitive data + no DPIA: denied
        if (
            context.involves_sensitive_data
            and not context.has_dpia
            and context.ai_risk_level == "high"
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Denmark Act 502/2018 §7: High-risk AI processing sensitive "
                    "data requires DPIA"
                ),
                regulation_citation="Denmark Act No. 502/2018 §7",
                requires_logging=True,
            )

        # Datatilsynet AI Guidance §2.3 — limited/high automated decision without oversight
        if (
            context.is_automated_decision
            and not context.has_human_oversight
            and context.ai_risk_level in {"high", "limited"}
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Denmark Datatilsynet AI Guidance 2023 §2.3: Limited/high-risk "
                    "automated decisions require human review capability"
                ),
                regulation_citation="Denmark Datatilsynet AI Guidance 2023 §2.3",
                requires_logging=True,
            )

        # Datatilsynet AI Guidance §3.1 — public sector high-risk without registry
        if (
            context.sector == "public_sector"
            and context.ai_risk_level == "high"
            and not context.is_registered_ai_system
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Denmark Datatilsynet AI Guidance 2023 §3.1: Public sector "
                    "high-risk AI systems should be registered"
                ),
                regulation_citation="Denmark Datatilsynet AI Guidance 2023 §3.1",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Denmark Datatilsynet AI Guidance 2023 and "
                "Act No. 502/2018 governance obligations"
            ),
            regulation_citation="Denmark Datatilsynet AI Guidance 2023 + Act No. 502/2018",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Finland (FinlandAIFilter)
# ---------------------------------------------------------------------------


class FinlandAIFilter:
    """
    Layer 3: Finland — TSV AI Guidelines 2023 + Data Protection Act 1050/2018.

    The Finnish Data Protection Ombudsman (Tietosuojavaltuutetun toimisto, TSV)
    issued national AI guidelines in 2023.  The Finnish Data Protection Act
    (1050/2018) implements the GDPR in national law.  Three principal controls
    apply:

    (a) Data Protection Act §6 (1050/2018) — Sensitive personal data requires
        either explicit consent or a valid legal basis; absence of both results
        in denial;
    (b) TSV AI Guidelines §2.2 — Public authority AI decisions must be
        accompanied by a transparency notice for affected individuals; absence
        results in denial;
    (c) TSV AI Guidelines §3.3 — High-risk AI systems require a completed Data
        Protection Impact Assessment; absence triggers a requirement for human
        review.

    References
    ----------
    Finland TSV AI Guidelines 2023 §2.2
    Finland TSV AI Guidelines 2023 §3.3
    Finland Data Protection Act 1050/2018 §6
    """

    FILTER_NAME = "FINLAND_AI_FILTER"

    def evaluate(
        self, context: NordicAIContext, document: NordicAIDocument
    ) -> FilterResult:
        # Data Protection Act §6 — sensitive data without consent or legal basis: denied
        if (
            context.involves_sensitive_data
            and not context.has_explicit_consent
            and not context.has_gdpr_basis
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Finland Data Protection Act 1050/2018 §6: Sensitive data "
                    "requires explicit consent or legal basis"
                ),
                regulation_citation="Finland Data Protection Act 1050/2018 §6",
                requires_logging=True,
            )

        # TSV AI Guidelines §2.2 — public authority AI without transparency notice: denied
        if (
            context.is_automated_decision
            and context.is_public_authority
            and not context.has_transparency_notice
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Finland TSV AI Guidelines 2023 §2.2: Public authority AI "
                    "decisions require transparency notice"
                ),
                regulation_citation="Finland TSV AI Guidelines 2023 §2.2",
                requires_logging=True,
            )

        # TSV AI Guidelines §3.3 — high-risk AI without DPIA: requires human review
        if context.ai_risk_level == "high" and not context.has_dpia:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Finland TSV AI Guidelines 2023 §3.3: High-risk AI systems "
                    "require Data Protection Impact Assessment"
                ),
                regulation_citation="Finland TSV AI Guidelines 2023 §3.3",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Finland TSV AI Guidelines 2023 and "
                "Data Protection Act 1050/2018 governance obligations"
            ),
            regulation_citation="Finland TSV AI Guidelines 2023 + Data Protection Act 1050/2018",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border (NordicCrossBorderFilter)
# ---------------------------------------------------------------------------


class NordicCrossBorderFilter:
    """
    Layer 4: Nordic + EEA cross-border data transfer framework.

    All EEA member states (including the Nordic countries and other EEA
    members) constitute an adequate transfer zone under GDPR.  Transfers
    within this zone require no additional safeguards.  Transfers to
    non-EEA destinations require either GDPR Article 46 mechanisms (Standard
    Contractual Clauses or Binding Corporate Rules) or are prohibited.

    Jurisdiction-specific national provisions govern the denial message for
    transfers to non-adequate countries without Article 46 safeguards.

    References
    ----------
    GDPR Article 45 — Transfers on the basis of an adequacy decision
    GDPR Article 46 — Transfers subject to appropriate safeguards
    Sweden SFS 2018:218 §33
    Denmark Act No. 502/2018 §25
    Finland Data Protection Act 1050/2018 §33
    """

    FILTER_NAME = "NORDIC_CROSS_BORDER_FILTER"

    # EEA member states (Nordic + non-Nordic EEA)
    _NORDIC_EEA: frozenset = frozenset({"SE", "DK", "FI", "NO", "IS", "LI"})
    _EU_MEMBER_STATES: frozenset = frozenset({
        "DE", "FR", "NL", "BE", "AT", "IT", "ES", "PT",
        "PL", "CZ", "HU", "RO", "BG", "HR", "SK", "SI",
        "EE", "LV", "LT", "GR", "CY", "MT", "LU", "IE",
    })

    @property
    def _adequate_jurisdictions(self) -> frozenset:
        return self._NORDIC_EEA | self._EU_MEMBER_STATES

    def evaluate(
        self, context: NordicAIContext, document: NordicAIDocument
    ) -> FilterResult:
        dest = context.destination_jurisdiction

        # Intra-EEA transfer — no additional safeguards required
        if dest in self._adequate_jurisdictions:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason=(
                    "EEA: Intra-EEA transfer — no additional safeguards required"
                ),
                regulation_citation="GDPR Article 45 — EEA adequacy",
                requires_logging=False,
            )

        # Non-EEA destination with GDPR Art. 46 safeguards (SCCs or BCRs)
        if context.has_transfer_safeguards:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="APPROVED",
                reason=(
                    "Standard Contractual Clauses or BCRs satisfy GDPR Art. 46 "
                    "transfer requirements"
                ),
                regulation_citation="GDPR Article 46 — Appropriate safeguards",
                requires_logging=True,
            )

        # Non-EEA destination without safeguards — jurisdiction-specific denial
        jurisdiction_denials = {
            "SE": (
                "Sweden SFS 2018:218 §33: Transfer to non-adequate country "
                "requires GDPR Art. 46 safeguards",
                "Sweden SFS 2018:218 §33",
            ),
            "DK": (
                "Denmark Act 502/2018 §25: Transfer to non-adequate country "
                "requires appropriate safeguards",
                "Denmark Act No. 502/2018 §25",
            ),
            "FI": (
                "Finland Data Protection Act 1050/2018 §33: Transfer to "
                "non-adequate country requires GDPR Art. 46 mechanism",
                "Finland Data Protection Act 1050/2018 §33",
            ),
        }

        reason, citation = jurisdiction_denials.get(
            context.source_jurisdiction,
            (
                "Nordic GDPR: Cross-border transfer requires adequate protection",
                "Nordic GDPR — Cross-border transfer framework",
            ),
        )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="DENIED",
            reason=reason,
            regulation_citation=citation,
            requires_logging=True,
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class NordicAIGovernanceOrchestrator:
    """
    Four-filter Nordic AI governance orchestrator.

    Evaluation order:
        SwedenAIFilter  →  DenmarkAIFilter  →  FinlandAIFilter  →
        NordicCrossBorderFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``FilterResult`` objects and passed
    to ``NordicAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            SwedenAIFilter(),
            DenmarkAIFilter(),
            FinlandAIFilter(),
            NordicCrossBorderFilter(),
        ]

    def evaluate(
        self, context: NordicAIContext, document: NordicAIDocument
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : NordicAIContext
            The AI system governance context to evaluate.
        document : NordicAIDocument
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
class NordicAIGovernanceReport:
    """
    Aggregated Nordic AI governance compliance report across all four filters.

    Decision aggregation:
    - Any DENIED result                     → overall_decision is "DENIED"
    - No DENIED + any REQUIRES_HUMAN_REVIEW → "REQUIRES_HUMAN_REVIEW"
    - All APPROVED                          → "APPROVED"

    is_compliant is True unless overall_decision is "DENIED".
    REQUIRES_HUMAN_REVIEW indicates a compliance gap that must be addressed
    but does not constitute a prohibition on processing.

    Attributes
    ----------
    context : NordicAIContext
        The AI system context that was evaluated.
    document : NordicAIDocument
        The document that was evaluated.
    filter_results : list[FilterResult]
        Per-filter results in evaluation order.
    """

    context: NordicAIContext
    document: NordicAIDocument
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

        REQUIRES_HUMAN_REVIEW is not a prohibition — the system may proceed
        once the identified compliance gaps are resolved.
        """
        return self.overall_decision != "DENIED"

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary across all four filters.

        Returns a multi-line string listing the jurisdiction, sector, risk
        level, overall decision, and each filter's result with its reason.
        """
        lines: List[str] = [
            (
                f"Nordic AI Governance Report — user_id={self.context.user_id}"
            ),
            (
                f"Jurisdiction: {self.context.jurisdiction}  |  "
                f"Sector: {self.context.sector}  |  "
                f"Risk Level: {self.context.ai_risk_level}  |  "
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


def _compliant_base() -> tuple[NordicAIContext, NordicAIDocument]:
    """
    Base context: fully compliant Swedish general-sector AI system with
    minimal risk, all controls satisfied, intra-EEA transfer.
    Used as the baseline from which failing scenarios are derived.
    """
    context = NordicAIContext(
        user_id="NORDIC-AI-001",
        jurisdiction="SE",
        sector="general",
        ai_risk_level="minimal",
        is_public_authority=False,
        has_gdpr_basis=True,
        has_dpia=True,
        is_automated_decision=False,
        has_human_oversight=True,
        involves_sensitive_data=False,
        has_explicit_consent=True,
        is_registered_ai_system=True,
        has_transparency_notice=True,
        source_jurisdiction="SE",
        destination_jurisdiction="SE",
        has_transfer_safeguards=False,
    )
    document = NordicAIDocument(
        content="Nordic AI decision record — minimal risk general sector",
        document_id="DOC-NORDIC-001",
        doc_type="ai_decision_record",
    )
    return context, document


def _demonstrate_scenario(
    title: str,
    context: NordicAIContext,
    document: NordicAIDocument,
    orchestrator: NordicAIGovernanceOrchestrator,
) -> None:
    results = orchestrator.evaluate(context, document)
    report = NordicAIGovernanceReport(
        context=context,
        document=document,
        filter_results=results,
    )
    print(f"\n{'=' * 70}")
    print(f"Scenario: {title}")
    print("=" * 70)
    print(report.compliance_summary)


if __name__ == "__main__":
    orchestrator = NordicAIGovernanceOrchestrator()
    base_ctx, base_doc = _compliant_base()

    # Scenario 1 — fully compliant baseline
    _demonstrate_scenario(
        "Fully Compliant Swedish General-Sector Minimal-Risk System",
        base_ctx,
        base_doc,
        orchestrator,
    )

    # Scenario 2 — Sweden: public authority automated decision without oversight (IMY §3.2)
    ctx2 = NordicAIContext(
        **{
            **base_ctx.__dict__,
            "is_public_authority": True,
            "is_automated_decision": True,
            "has_human_oversight": False,
        }
    )
    _demonstrate_scenario(
        "Sweden — Public Authority Automated Decision Without Oversight (IMY §3.2)",
        ctx2,
        base_doc,
        orchestrator,
    )

    # Scenario 3 — Sweden: sensitive data without consent or GDPR basis (SFS 2018:218 §3)
    ctx3 = NordicAIContext(
        **{
            **base_ctx.__dict__,
            "involves_sensitive_data": True,
            "has_explicit_consent": False,
            "has_gdpr_basis": False,
        }
    )
    _demonstrate_scenario(
        "Sweden — Sensitive Data Without Consent or GDPR Basis (SFS 2018:218 §3)",
        ctx3,
        base_doc,
        orchestrator,
    )

    # Scenario 4 — Denmark: high-risk sensitive data without DPIA (Act 502/2018 §7)
    ctx4 = NordicAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "DK",
            "ai_risk_level": "high",
            "involves_sensitive_data": True,
            "has_dpia": False,
        }
    )
    _demonstrate_scenario(
        "Denmark — High-Risk Sensitive Data Without DPIA (Act 502/2018 §7)",
        ctx4,
        base_doc,
        orchestrator,
    )

    # Scenario 5 — Finland: public authority AI without transparency notice (TSV §2.2)
    ctx5 = NordicAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "FI",
            "is_public_authority": True,
            "is_automated_decision": True,
            "has_transparency_notice": False,
        }
    )
    _demonstrate_scenario(
        "Finland — Public Authority AI Without Transparency Notice (TSV §2.2)",
        ctx5,
        base_doc,
        orchestrator,
    )

    # Scenario 6 — cross-border transfer to non-EEA without safeguards (Swedish denial)
    ctx6 = NordicAIContext(
        **{
            **base_ctx.__dict__,
            "source_jurisdiction": "SE",
            "destination_jurisdiction": "US",
            "has_transfer_safeguards": False,
        }
    )
    _demonstrate_scenario(
        "Cross-Border — SE→US Without Safeguards (SFS 2018:218 §33 Denial)",
        ctx6,
        base_doc,
        orchestrator,
    )

    # Scenario 7 — cross-border with SCCs (compliant)
    ctx7 = NordicAIContext(
        **{
            **base_ctx.__dict__,
            "source_jurisdiction": "FI",
            "destination_jurisdiction": "SG",
            "has_transfer_safeguards": True,
        }
    )
    _demonstrate_scenario(
        "Cross-Border — FI→SG With SCCs (GDPR Art. 46 Compliant)",
        ctx7,
        base_doc,
        orchestrator,
    )
