"""
29_eastern_europe_ai_governance.py — Eastern Europe AI Governance Framework

Implements national AI governance frameworks for Poland, Czech Republic, and
Hungary, supplementing the EU AI Act with jurisdiction-specific Data Protection
Authority guidelines and national GDPR implementation legislation.  A fourth
filter governs cross-border data transfers within the EEA zone.

Each jurisdiction has issued AI-specific guidance through its national Data
Protection Authority (DPA), building on the General Data Protection Regulation
(EU 2016/679) as implemented in national law.  This example models the principal
compliance controls from each DPA's AI guidance and the relevant national
GDPR-implementing statute.

Demonstrates a multi-layer governance orchestrator where four filters enforce
independent national requirements:

    Layer 1  — Poland (PolandAIFilter):

               UODO AI Guideline §3 — Polish Personal Data Protection Office
                   (UODO) AI Guidelines 2023: public authority automated
                   decisions require human oversight;
               Polish GDPR Act Dz.U. 2018 poz. 1000 Art. 9 — sensitive data
                   processing requires explicit consent or an Article 9 legal
                   basis;
               UODO AI Guideline §5 — biometric AI processing requires UODO
                   supervisory review.

    Layer 2  — Czech Republic (CzechRepublicAIFilter):

               ÚOOÚ AI Guidance §2.1 — Czech Office for Personal Data
                   Protection AI Guidance 2023: limited/high-risk automated
                   decisions require human review capability;
               Act 110/2019 Coll. §16 — Czech Personal Data Processing Act:
                   high-risk AI processing sensitive data requires a DPIA;
               ÚOOÚ AI Guidance §4.2 — high-risk AI systems require a
                   transparency notice to data subjects.

    Layer 3  — Hungary (HungaryAIFilter):

               NAIH AI Guideline §3.2 — Hungarian National Authority for Data
                   Protection (NAIH) AI Guidelines 2023: public sector
                   automated AI decisions require human review;
               Privacy Act CXII/2011 §5 — Hungarian Privacy Act: sensitive
                   personal data requires explicit consent or GDPR legal basis;
               NAIH AI Guideline §5.1 — high-risk healthcare AI requires a
                   Data Protection Impact Assessment.

    Layer 4  — Cross-border (EasternEuropeCrossBorderFilter):

               EEA intra-transfer exemption: transfers within the EEA are
                   permitted without additional safeguards;
               GDPR Article 46 — Standard Contractual Clauses or BCRs
                   satisfy transfer requirements to non-adequate countries;
               Jurisdiction-specific national GDPR provisions for transfers to
                   non-adequate countries without GDPR Art. 46 safeguards.

No external dependencies required.

Run:
    python examples/29_eastern_europe_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EasternEuropeAIContext:
    """
    Governance review context for an AI system evaluated under Eastern European
    national AI governance frameworks (Poland, Czech Republic, Hungary).

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    jurisdiction : str
        Primary jurisdiction for the AI system: "PL" (Poland), "CZ" (Czech
        Republic), or "HU" (Hungary).
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
    has_transparency_notice : bool
        True if affected individuals have received a transparency notice
        describing the AI system and its use of their data.
    is_biometric_processing : bool
        True if the AI system processes biometric data to uniquely identify
        individuals.
    has_supervisory_approval : bool
        True if the relevant national supervisory authority has approved the
        AI system deployment (relevant for Polish biometric processing).
    source_jurisdiction : str
        Jurisdiction from which the data originates: "PL", "CZ", "HU", etc.
    destination_jurisdiction : str
        Destination jurisdiction for cross-border data transfers.
    has_transfer_safeguards : bool
        True if GDPR Article 46 safeguards (Standard Contractual Clauses or
        Binding Corporate Rules) are in place for the transfer.
    """

    user_id: str
    jurisdiction: str           # "PL", "CZ", "HU"
    sector: str                 # "public_sector", "healthcare", "financial", "general"
    ai_risk_level: str          # "minimal", "limited", "high", "unacceptable"
    is_public_authority: bool = False
    has_gdpr_basis: bool = False
    has_dpia: bool = False
    is_automated_decision: bool = False
    has_human_oversight: bool = True
    involves_sensitive_data: bool = False
    has_explicit_consent: bool = False
    has_transparency_notice: bool = False
    is_biometric_processing: bool = False
    has_supervisory_approval: bool = False
    source_jurisdiction: str = "PL"
    destination_jurisdiction: str = "PL"
    has_transfer_safeguards: bool = False


@dataclass(frozen=True)
class EasternEuropeAIDocument:
    """
    Document metadata submitted to the Eastern Europe AI governance orchestrator.

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
    """Result of a single Eastern Europe AI governance filter evaluation."""

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
# Layer 1 — Poland (PolandAIFilter)
# ---------------------------------------------------------------------------


class PolandAIFilter:
    """
    Layer 1: Poland — UODO AI Guidelines 2023 + Polish GDPR Act Dz.U. 2018.

    The Polish Personal Data Protection Office (Urząd Ochrony Danych
    Osobowych, UODO) issued national AI guidelines in 2023 supplementing the
    EU AI Act.  The Polish GDPR-implementing Act (Dz.U. 2018 poz. 1000)
    provides national rules for personal data processing.  Three principal
    controls apply:

    (a) UODO AI Guideline §3 — Public authority automated decisions require
        human oversight.  Where a public authority uses an AI system to make
        automated decisions affecting individuals, and human oversight is
        absent, the system must be denied;
    (b) Polish GDPR Act Art. 9 — Processing of sensitive personal data
        requires either explicit consent from the data subject or a valid
        legal basis under GDPR Article 9; absence of both results in denial;
    (c) UODO AI Guideline §5 — Biometric AI processing requires review by
        the UODO supervisory authority; absence of supervisory approval
        triggers a requirement for human review.

    References
    ----------
    Poland UODO AI Guidelines 2023 §3
    Poland UODO AI Guidelines 2023 §5
    Poland GDPR Act Dz.U. 2018 poz. 1000 Art. 9
    """

    FILTER_NAME = "POLAND_AI_FILTER"

    def evaluate(
        self, context: EasternEuropeAIContext, document: EasternEuropeAIDocument
    ) -> FilterResult:
        # UODO AI Guideline §3 — public authority automated decision without oversight: denied
        if (
            context.is_public_authority
            and context.is_automated_decision
            and not context.has_human_oversight
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Poland UODO AI Guidelines 2023 §3: Public authority "
                    "automated decisions require human oversight"
                ),
                regulation_citation="Poland UODO AI Guidelines 2023 §3",
                requires_logging=True,
            )

        # Polish GDPR Act Art. 9 — sensitive data without consent or GDPR basis: denied
        if (
            context.involves_sensitive_data
            and not context.has_explicit_consent
            and not context.has_gdpr_basis
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Poland GDPR Act Dz.U. 2018: Sensitive data processing "
                    "requires explicit consent or Art. 9 GDPR basis"
                ),
                regulation_citation="Poland GDPR Act Dz.U. 2018 poz. 1000 Art. 9",
                requires_logging=True,
            )

        # UODO AI Guideline §5 — biometric processing without supervisory approval: requires review
        if context.is_biometric_processing and not context.has_supervisory_approval:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Poland UODO AI Guidelines 2023 §5: Biometric AI processing "
                    "requires UODO supervisory review"
                ),
                regulation_citation="Poland UODO AI Guidelines 2023 §5",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Poland UODO AI Guidelines 2023 and GDPR Act "
                "Dz.U. 2018 governance obligations"
            ),
            regulation_citation="Poland UODO AI Guidelines 2023 + GDPR Act Dz.U. 2018",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Czech Republic (CzechRepublicAIFilter)
# ---------------------------------------------------------------------------


class CzechRepublicAIFilter:
    """
    Layer 2: Czech Republic — ÚOOÚ AI Guidance 2023 + Act 110/2019 Coll.

    The Czech Office for Personal Data Protection (Úřad pro ochranu osobních
    údajů, ÚOOÚ) issued national AI guidance in 2023.  The Czech Personal
    Data Processing Act (Act No. 110/2019 Coll.) provides national data
    protection rules.  Three principal controls apply:

    (a) ÚOOÚ AI Guidance §2.1 — Limited or high-risk automated decisions
        must retain a human review capability; absence of oversight for such
        decisions triggers a requirement for human review;
    (b) Act 110/2019 Coll. §16 — High-risk AI systems that process sensitive
        personal data require a completed Data Protection Impact Assessment
        before deployment; absence of a DPIA results in denial;
    (c) ÚOOÚ AI Guidance §4.2 — High-risk AI systems must provide a
        transparency notice to data subjects; absence of a notice triggers
        a requirement for human review.

    References
    ----------
    Czech ÚOOÚ AI Guidance 2023 §2.1
    Czech ÚOOÚ AI Guidance 2023 §4.2
    Czech Act 110/2019 Coll. §16 (Personal Data Processing Act)
    """

    FILTER_NAME = "CZECH_REPUBLIC_AI_FILTER"

    def evaluate(
        self, context: EasternEuropeAIContext, document: EasternEuropeAIDocument
    ) -> FilterResult:
        # Act 110/2019 §16 — high-risk + sensitive data + no DPIA: denied
        if (
            context.involves_sensitive_data
            and not context.has_dpia
            and context.ai_risk_level == "high"
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Czech Act 110/2019 Coll. §16: High-risk AI processing "
                    "sensitive data requires DPIA"
                ),
                regulation_citation="Czech Act 110/2019 Coll. §16",
                requires_logging=True,
            )

        # ÚOOÚ AI Guidance §2.1 — limited/high automated decision without oversight: requires review
        if (
            context.is_automated_decision
            and not context.has_human_oversight
            and context.ai_risk_level in {"high", "limited"}
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Czech ÚOOÚ AI Guidance 2023 §2.1: Automated decisions for "
                    "limited/high-risk AI require human review option"
                ),
                regulation_citation="Czech ÚOOÚ AI Guidance 2023 §2.1",
                requires_logging=True,
            )

        # ÚOOÚ AI Guidance §4.2 — high-risk AI without transparency notice: requires review
        if context.ai_risk_level == "high" and not context.has_transparency_notice:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Czech ÚOOÚ AI Guidance 2023 §4.2: High-risk AI systems "
                    "require transparency notice to data subjects"
                ),
                regulation_citation="Czech ÚOOÚ AI Guidance 2023 §4.2",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Czech ÚOOÚ AI Guidance 2023 and Act 110/2019 "
                "Coll. governance obligations"
            ),
            regulation_citation="Czech ÚOOÚ AI Guidance 2023 + Act 110/2019 Coll.",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Hungary (HungaryAIFilter)
# ---------------------------------------------------------------------------


class HungaryAIFilter:
    """
    Layer 3: Hungary — NAIH AI Guidelines 2023 + Privacy Act CXII/2011.

    The Hungarian National Authority for Data Protection and Freedom of
    Information (Nemzeti Adatvédelmi és Információszabadság Hatóság, NAIH)
    issued national AI guidelines in 2023.  The Hungarian Privacy Act
    (Act CXII of 2011) implements the GDPR in national law.  Three principal
    controls apply:

    (a) NAIH AI Guideline §3.2 — Public sector automated AI decisions require
        human review capability; absence of oversight in such decisions
        results in denial;
    (b) Privacy Act CXII/2011 §5 — Sensitive personal data requires either
        explicit consent or a valid GDPR legal basis; absence of both results
        in denial;
    (c) NAIH AI Guideline §5.1 — High-risk healthcare AI systems require a
        completed Data Protection Impact Assessment; absence of a DPIA
        triggers a requirement for human review.

    References
    ----------
    Hungary NAIH AI Guidelines 2023 §3.2
    Hungary NAIH AI Guidelines 2023 §5.1
    Hungary Privacy Act CXII/2011 §5
    """

    FILTER_NAME = "HUNGARY_AI_FILTER"

    def evaluate(
        self, context: EasternEuropeAIContext, document: EasternEuropeAIDocument
    ) -> FilterResult:
        # NAIH AI Guideline §3.2 — public authority automated decision without oversight: denied
        if (
            context.is_automated_decision
            and context.is_public_authority
            and not context.has_human_oversight
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Hungary NAIH AI Guidelines 2023 §3.2: Public sector "
                    "automated AI decisions require human review"
                ),
                regulation_citation="Hungary NAIH AI Guidelines 2023 §3.2",
                requires_logging=True,
            )

        # Privacy Act CXII/2011 §5 — sensitive data without consent or GDPR basis: denied
        if (
            context.involves_sensitive_data
            and not context.has_explicit_consent
            and not context.has_gdpr_basis
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "Hungary Privacy Act CXII/2011 §5: Sensitive personal data "
                    "requires explicit consent or GDPR legal basis"
                ),
                regulation_citation="Hungary Privacy Act CXII/2011 §5",
                requires_logging=True,
            )

        # NAIH AI Guideline §5.1 — high-risk healthcare AI without DPIA: requires review
        if (
            context.sector == "healthcare"
            and context.ai_risk_level == "high"
            and not context.has_dpia
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "Hungary NAIH AI Guidelines 2023 §5.1: High-risk healthcare "
                    "AI requires Data Protection Impact Assessment"
                ),
                regulation_citation="Hungary NAIH AI Guidelines 2023 §5.1",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with Hungary NAIH AI Guidelines 2023 and Privacy "
                "Act CXII/2011 governance obligations"
            ),
            regulation_citation="Hungary NAIH AI Guidelines 2023 + Privacy Act CXII/2011",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Cross-border (EasternEuropeCrossBorderFilter)
# ---------------------------------------------------------------------------


class EasternEuropeCrossBorderFilter:
    """
    Layer 4: Eastern Europe + EEA cross-border data transfer framework.

    All EEA member states (including the Eastern European EU members and other
    EEA members) constitute an adequate transfer zone under GDPR.  Transfers
    within this zone require no additional safeguards.  Transfers to non-EEA
    destinations require either GDPR Article 46 mechanisms (Standard
    Contractual Clauses or Binding Corporate Rules) or are prohibited.

    Jurisdiction-specific national provisions govern the denial message for
    transfers to non-adequate countries without Article 46 safeguards.

    References
    ----------
    GDPR Article 45 — Transfers on the basis of an adequacy decision
    GDPR Article 46 — Transfers subject to appropriate safeguards
    Poland UODO — National transfer restriction provisions
    Czech ÚOOÚ — National transfer restriction provisions
    Hungary NAIH — National transfer restriction provisions
    """

    FILTER_NAME = "EASTERN_EUROPE_CROSS_BORDER_FILTER"

    # EEA member states: EU member states + EEA non-EU members (NO, IS, LI)
    _EEA_JURISDICTIONS: frozenset = frozenset({
        "PL", "CZ", "HU", "DE", "FR", "NL", "BE", "AT", "IT", "ES", "PT",
        "RO", "BG", "HR", "SK", "SI", "EE", "LV", "LT", "GR", "CY", "MT",
        "LU", "IE", "SE", "DK", "FI", "NO", "IS", "LI",
    })

    def evaluate(
        self, context: EasternEuropeAIContext, document: EasternEuropeAIDocument
    ) -> FilterResult:
        dest = context.destination_jurisdiction

        # Intra-EEA transfer — no additional safeguards required
        if dest in self._EEA_JURISDICTIONS:
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
                    "SCCs or BCRs satisfy GDPR Art. 46 transfer requirements"
                ),
                regulation_citation="GDPR Article 46 — Appropriate safeguards",
                requires_logging=True,
            )

        # Non-EEA destination without safeguards — jurisdiction-specific denial
        jurisdiction_denials = {
            "PL": (
                "Poland UODO: Transfer outside EEA requires GDPR Art. 46 mechanism",
                "Poland UODO — GDPR Art. 46 transfer requirement",
            ),
            "CZ": (
                "Czech ÚOOÚ: Transfer to non-adequate country requires appropriate safeguards",
                "Czech ÚOOÚ — GDPR Art. 46 transfer requirement",
            ),
            "HU": (
                "Hungary NAIH: Transfer to non-adequate third country requires GDPR Art. 46 safeguards",
                "Hungary NAIH — GDPR Art. 46 transfer requirement",
            ),
        }

        reason, citation = jurisdiction_denials.get(
            context.source_jurisdiction,
            (
                "Eastern Europe GDPR: Cross-border transfer requires adequate protection",
                "Eastern Europe GDPR — Cross-border transfer framework",
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


class EasternEuropeAIGovernanceOrchestrator:
    """
    Four-filter Eastern Europe AI governance orchestrator.

    Evaluation order:
        PolandAIFilter  →  CzechRepublicAIFilter  →  HungaryAIFilter  →
        EasternEuropeCrossBorderFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``FilterResult`` objects and passed
    to ``EasternEuropeAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            PolandAIFilter(),
            CzechRepublicAIFilter(),
            HungaryAIFilter(),
            EasternEuropeCrossBorderFilter(),
        ]

    def evaluate(
        self, context: EasternEuropeAIContext, document: EasternEuropeAIDocument
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : EasternEuropeAIContext
            The AI system governance context to evaluate.
        document : EasternEuropeAIDocument
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
class EasternEuropeAIGovernanceReport:
    """
    Aggregated Eastern Europe AI governance compliance report across all four
    filters.

    Decision aggregation:
    - Any DENIED result                     → overall_decision is "DENIED"
    - No DENIED + any REQUIRES_HUMAN_REVIEW → "REQUIRES_HUMAN_REVIEW"
    - All APPROVED                          → "APPROVED"

    is_compliant is True unless overall_decision is "DENIED".
    REQUIRES_HUMAN_REVIEW indicates a compliance gap that must be addressed
    but does not constitute a prohibition on processing.

    Attributes
    ----------
    context : EasternEuropeAIContext
        The AI system context that was evaluated.
    document : EasternEuropeAIDocument
        The document that was evaluated.
    filter_results : list[FilterResult]
        Per-filter results in evaluation order.
    """

    context: EasternEuropeAIContext
    document: EasternEuropeAIDocument
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
                f"Eastern Europe AI Governance Report — user_id={self.context.user_id}"
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


def _compliant_base() -> tuple[EasternEuropeAIContext, EasternEuropeAIDocument]:
    """
    Base context: fully compliant Polish general-sector AI system with
    minimal risk, all controls satisfied, intra-EEA transfer.
    Used as the baseline from which failing scenarios are derived.
    """
    context = EasternEuropeAIContext(
        user_id="EE-AI-001",
        jurisdiction="PL",
        sector="general",
        ai_risk_level="minimal",
        is_public_authority=False,
        has_gdpr_basis=True,
        has_dpia=True,
        is_automated_decision=False,
        has_human_oversight=True,
        involves_sensitive_data=False,
        has_explicit_consent=True,
        has_transparency_notice=True,
        is_biometric_processing=False,
        has_supervisory_approval=False,
        source_jurisdiction="PL",
        destination_jurisdiction="PL",
        has_transfer_safeguards=False,
    )
    document = EasternEuropeAIDocument(
        content="Eastern Europe AI decision record — minimal risk general sector",
        document_id="DOC-EE-001",
        doc_type="ai_decision_record",
    )
    return context, document


def _demonstrate_scenario(
    title: str,
    context: EasternEuropeAIContext,
    document: EasternEuropeAIDocument,
    orchestrator: EasternEuropeAIGovernanceOrchestrator,
) -> None:
    results = orchestrator.evaluate(context, document)
    report = EasternEuropeAIGovernanceReport(
        context=context,
        document=document,
        filter_results=results,
    )
    print(f"\n{'=' * 70}")
    print(f"Scenario: {title}")
    print("=" * 70)
    print(report.compliance_summary)


if __name__ == "__main__":
    orchestrator = EasternEuropeAIGovernanceOrchestrator()
    base_ctx, base_doc = _compliant_base()

    # Scenario 1 — fully compliant baseline
    _demonstrate_scenario(
        "Fully Compliant Polish General-Sector Minimal-Risk System",
        base_ctx,
        base_doc,
        orchestrator,
    )

    # Scenario 2 — Poland: public authority automated decision without oversight (UODO §3)
    ctx2 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "is_public_authority": True,
            "is_automated_decision": True,
            "has_human_oversight": False,
        }
    )
    _demonstrate_scenario(
        "Poland — Public Authority Automated Decision Without Oversight (UODO §3)",
        ctx2,
        base_doc,
        orchestrator,
    )

    # Scenario 3 — Poland: sensitive data without consent or GDPR basis (GDPR Act Art. 9)
    ctx3 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "involves_sensitive_data": True,
            "has_explicit_consent": False,
            "has_gdpr_basis": False,
        }
    )
    _demonstrate_scenario(
        "Poland — Sensitive Data Without Consent or GDPR Basis (GDPR Act Dz.U. 2018 Art. 9)",
        ctx3,
        base_doc,
        orchestrator,
    )

    # Scenario 4 — Poland: biometric processing without supervisory approval (UODO §5)
    ctx4 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "is_biometric_processing": True,
            "has_supervisory_approval": False,
        }
    )
    _demonstrate_scenario(
        "Poland — Biometric Processing Without Supervisory Approval (UODO §5)",
        ctx4,
        base_doc,
        orchestrator,
    )

    # Scenario 5 — Czech Republic: high-risk sensitive data without DPIA (Act 110/2019 §16)
    ctx5 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "CZ",
            "ai_risk_level": "high",
            "involves_sensitive_data": True,
            "has_dpia": False,
            "has_transparency_notice": True,
        }
    )
    _demonstrate_scenario(
        "Czech Republic — High-Risk Sensitive Data Without DPIA (Act 110/2019 §16)",
        ctx5,
        base_doc,
        orchestrator,
    )

    # Scenario 6 — Czech Republic: limited-risk automated decision without oversight (ÚOOÚ §2.1)
    ctx6 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "CZ",
            "ai_risk_level": "limited",
            "is_automated_decision": True,
            "has_human_oversight": False,
        }
    )
    _demonstrate_scenario(
        "Czech Republic — Limited-Risk Automated Decision Without Oversight (ÚOOÚ §2.1)",
        ctx6,
        base_doc,
        orchestrator,
    )

    # Scenario 7 — Hungary: public authority automated decision without oversight (NAIH §3.2)
    ctx7 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "HU",
            "is_automated_decision": True,
            "is_public_authority": True,
            "has_human_oversight": False,
        }
    )
    _demonstrate_scenario(
        "Hungary — Public Sector Automated AI Decision Without Oversight (NAIH §3.2)",
        ctx7,
        base_doc,
        orchestrator,
    )

    # Scenario 8 — Hungary: high-risk healthcare AI without DPIA (NAIH §5.1)
    ctx8 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "jurisdiction": "HU",
            "sector": "healthcare",
            "ai_risk_level": "high",
            "has_dpia": False,
        }
    )
    _demonstrate_scenario(
        "Hungary — High-Risk Healthcare AI Without DPIA (NAIH §5.1)",
        ctx8,
        base_doc,
        orchestrator,
    )

    # Scenario 9 — cross-border transfer to non-EEA without safeguards (Polish denial)
    ctx9 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "source_jurisdiction": "PL",
            "destination_jurisdiction": "US",
            "has_transfer_safeguards": False,
        }
    )
    _demonstrate_scenario(
        "Cross-Border — PL→US Without Safeguards (Poland UODO Denial)",
        ctx9,
        base_doc,
        orchestrator,
    )

    # Scenario 10 — cross-border with SCCs (compliant)
    ctx10 = EasternEuropeAIContext(
        **{
            **base_ctx.__dict__,
            "source_jurisdiction": "HU",
            "destination_jurisdiction": "SG",
            "has_transfer_safeguards": True,
        }
    )
    _demonstrate_scenario(
        "Cross-Border — HU→SG With SCCs (GDPR Art. 46 Compliant)",
        ctx10,
        base_doc,
        orchestrator,
    )
