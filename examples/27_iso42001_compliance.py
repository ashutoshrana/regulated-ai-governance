"""
27_iso42001_compliance.py — ISO 42001:2023 AI Management System (AIMS)
compliance framework implementing the four principal clause groups of the
international standard for AI management systems.

ISO 42001:2023 is the first international standard specifically addressing AI
management systems (AIMS). It provides requirements for establishing,
implementing, maintaining, and continually improving an AI management system
within the context of an organisation. The standard addresses the responsible
development and use of AI systems, including risk management, data governance,
transparency, and performance evaluation.

Demonstrates a multi-layer governance orchestrator where four filters enforce
independent AIMS requirements drawn from the clause structure of ISO 42001:2023:

    Layer 1  — ISO 42001:2023 Clause 5 — Leadership (PolicyFilter):

               Clause 5.2 — AI Policy: production-deployed AI systems require
                   an established AI policy as a governance foundation;
               Clause 5.1 — Leadership and commitment: top management must
                   establish an AI policy before deploying high-risk systems.

    Layer 2  — ISO 42001:2023 Clause 6 — Planning (RiskFilter):

               Clause 6.1 — Actions to address risks and opportunities: limited
                   and high-risk AI systems require a completed risk assessment
                   before deployment;
               Annex B — AI Impact Assessment: high-risk AI systems additionally
                   require an AI impact assessment covering broader societal
                   and ethical effects;
               Clause 6.1.2 — AI risk treatment: AI systems assessed as
                   unacceptable risk must not be deployed.

    Layer 3  — ISO 42001:2023 Clause 8 — Operations (OperationsFilter):

               Clause 8.4 — AI system life cycle: autonomous AI systems must
                   include human oversight mechanisms enabling intervention;
               Clause 8.3 — Data for AI systems: production systems require
                   a data management governance framework;
               Clause 8.6 — AI system from external providers: third-party AI
                   systems require a supplier evaluation before integration.

    Layer 4  — ISO 42001:2023 Clause 9 — Performance Evaluation
               (PerformanceFilter):

               Clause 9.1 — Monitoring, measurement, analysis and evaluation:
                   limited and high-risk AI systems require an audit trail for
                   ongoing monitoring;
               Clause 7.5 — Documented information: production systems require
                   transparency documentation describing the AI system;
               Clause 10.1 — Nonconformity and corrective action: high-risk
                   AI systems require a defined incident and corrective action
                   process.

No external dependencies required.

Run:
    python examples/27_iso42001_compliance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ISO42001Context:
    """
    Governance review context for an AI system evaluated under ISO 42001:2023.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    organization_type : str
        Type of deploying organisation: "enterprise", "sme", "public_sector".
    ai_system_type : str
        Classification of the AI system: "decision_support", "autonomous",
        "generative", "recommendation".
    risk_level : str
        AI system risk classification: "minimal", "limited", "high",
        "unacceptable".
    has_aims_policy : bool
        True if the organisation has established a documented AI policy as
        required by ISO 42001:2023 Clause 5.2.
    has_risk_assessment : bool
        True if a formal risk assessment has been completed for this AI system
        as required by ISO 42001:2023 Clause 6.1.
    has_impact_assessment : bool
        True if an AI impact assessment has been completed covering broader
        societal and ethical effects (ISO 42001:2023 Annex B).
    has_human_oversight : bool
        True if the AI system includes mechanisms for human oversight and
        intervention as required by ISO 42001:2023 Clause 8.4.
    has_data_governance : bool
        True if a data management governance framework has been established
        for the AI system as required by ISO 42001:2023 Clause 8.3.
    has_transparency_docs : bool
        True if documented information describing the AI system's design,
        intended use, and limitations exists (ISO 42001:2023 Clause 7.5).
    has_incident_process : bool
        True if a nonconformity and corrective action process is in place
        for managing incidents (ISO 42001:2023 Clause 10.1).
    has_audit_trail : bool
        True if the AI system maintains a monitoring and audit trail for
        performance evaluation (ISO 42001:2023 Clause 9.1).
    is_third_party_ai : bool
        True if the AI system or components are sourced from an external
        provider (ISO 42001:2023 Clause 8.6).
    has_supplier_assessment : bool
        True if a supplier evaluation has been completed for the third-party
        AI system (ISO 42001:2023 Clause 8.6).
    deployment_stage : str
        Current stage of deployment: "development", "testing", "production".
    """

    user_id: str
    organization_type: str  # "enterprise", "sme", "public_sector"
    ai_system_type: str  # "decision_support", "autonomous", "generative", "recommendation"
    risk_level: str  # "minimal", "limited", "high", "unacceptable"
    has_aims_policy: bool = False          # Clause 5.2 — AI Policy
    has_risk_assessment: bool = False      # Clause 6.1 — Risk assessment
    has_impact_assessment: bool = False    # Annex B — AI impact assessment
    has_human_oversight: bool = True       # Clause 8.4 — Human oversight
    has_data_governance: bool = False      # Clause 8.3 — Data management
    has_transparency_docs: bool = False    # Clause 7.5 — Documented information
    has_incident_process: bool = False     # Clause 10.1 — Nonconformity
    has_audit_trail: bool = False          # Clause 9.1 — Monitoring
    is_third_party_ai: bool = False        # Clause 8.6 — Third-party AI
    has_supplier_assessment: bool = False  # Clause 8.6 — Supplier evaluation
    deployment_stage: str = "production"  # "development", "testing", "production"


@dataclass(frozen=True)
class ISO42001Document:
    """
    Document metadata submitted to the ISO 42001:2023 governance orchestrator.

    Attributes
    ----------
    content : str
        Textual content or description of the document being processed.
    document_id : str
        Unique identifier for the document under review.
    doc_type : str
        Classification of the document, e.g. "ai_system_record",
        "risk_assessment_report", "policy_document".
    """

    content: str
    document_id: str
    doc_type: str = "ai_system_record"


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single ISO 42001:2023 governance filter evaluation."""

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
# Layer 1 — Clause 5: Leadership (PolicyFilter)
# ---------------------------------------------------------------------------


class ISO42001PolicyFilter:
    """
    Layer 1: ISO 42001:2023 Clause 5 — Leadership.

    ISO 42001:2023 Clause 5 establishes requirements for top management
    leadership and commitment to the AI management system.  Two principal
    controls apply:

    (a) Clause 5.2 — AI Policy: the organisation must establish a documented
        AI policy that is appropriate to the purpose of the organisation and
        provides a framework for setting AI objectives; production-deployed
        AI systems without a policy require human review before proceeding;
    (b) Clause 5.1 — Leadership and commitment: top management must establish
        the AI policy; for high-risk AI systems, absence of a policy
        constitutes a fundamental governance failure that must be denied.

    References
    ----------
    ISO 42001:2023 Clause 5 — Leadership
    ISO 42001:2023 Clause 5.1 — Leadership and commitment
    ISO 42001:2023 Clause 5.2 — AI policy
    """

    FILTER_NAME = "ISO42001_POLICY_FILTER"

    def evaluate(
        self, context: ISO42001Context, document: ISO42001Document
    ) -> FilterResult:
        # Clause 5.1 — high-risk system without AI policy: must be denied
        if context.risk_level == "high" and not context.has_aims_policy:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "ISO 42001:2023 Clause 5.1: Top management must establish "
                    "AI policy for high-risk systems"
                ),
                regulation_citation="ISO 42001:2023 Clause 5.1",
                requires_logging=True,
            )

        # Clause 5.2 — production deployment without AI policy: requires review
        if not context.has_aims_policy and context.deployment_stage == "production":
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "ISO 42001:2023 Clause 5.2: AI policy required before "
                    "production deployment"
                ),
                regulation_citation="ISO 42001:2023 Clause 5.2",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Compliant with ISO 42001:2023 Clause 5 Leadership obligations",
            regulation_citation="ISO 42001:2023 Clause 5 — Leadership",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Clause 6: Planning (RiskFilter)
# ---------------------------------------------------------------------------


class ISO42001RiskFilter:
    """
    Layer 2: ISO 42001:2023 Clause 6 — Planning.

    ISO 42001:2023 Clause 6 establishes requirements for planning the AI
    management system, including risk assessment and treatment.  Three principal
    controls apply:

    (a) Clause 6.1 — Actions to address risks and opportunities: limited and
        high-risk AI systems require a completed risk assessment that identifies
        and evaluates risks associated with the AI system;
    (b) Annex B — AI Impact Assessment: high-risk AI systems additionally
        require an AI impact assessment that evaluates broader societal,
        ethical, and human rights implications;
    (c) Clause 6.1.2 — AI risk treatment: unacceptable risk AI systems must
        not be deployed; no treatment option can render deployment acceptable.

    References
    ----------
    ISO 42001:2023 Clause 6 — Planning
    ISO 42001:2023 Clause 6.1 — Actions to address risks and opportunities
    ISO 42001:2023 Clause 6.1.2 — AI risk treatment
    ISO 42001:2023 Annex B — AI impact assessment
    """

    FILTER_NAME = "ISO42001_RISK_FILTER"

    def evaluate(
        self, context: ISO42001Context, document: ISO42001Document
    ) -> FilterResult:
        # Clause 6.1.2 — unacceptable risk must not be deployed
        if context.risk_level == "unacceptable":
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "ISO 42001:2023 Clause 6.1.2: Unacceptable risk AI systems "
                    "must not be deployed"
                ),
                regulation_citation="ISO 42001:2023 Clause 6.1.2",
                requires_logging=True,
            )

        # Clause 6.1 — limited/high risk without risk assessment: denied
        if (
            context.risk_level in {"high", "limited"}
            and not context.has_risk_assessment
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "ISO 42001:2023 Clause 6.1: Risk assessment required for "
                    "limited and high-risk AI systems"
                ),
                regulation_citation="ISO 42001:2023 Clause 6.1",
                requires_logging=True,
            )

        # Annex B — high-risk without impact assessment: requires human review
        if context.risk_level == "high" and not context.has_impact_assessment:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "ISO 42001:2023 Annex B: AI impact assessment required for "
                    "high-risk systems"
                ),
                regulation_citation="ISO 42001:2023 Annex B",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Compliant with ISO 42001:2023 Clause 6 Planning obligations",
            regulation_citation="ISO 42001:2023 Clause 6 — Planning",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 3 — Clause 8: Operations (OperationsFilter)
# ---------------------------------------------------------------------------


class ISO42001OperationsFilter:
    """
    Layer 3: ISO 42001:2023 Clause 8 — Operations.

    ISO 42001:2023 Clause 8 establishes requirements for implementing and
    controlling AI system operations.  Three principal controls apply:

    (a) Clause 8.4 — AI system life cycle: autonomous AI systems must
        include human oversight mechanisms that enable authorised personnel to
        monitor, intervene, and override AI outputs; autonomous systems
        without such mechanisms must be denied;
    (b) Clause 8.3 — Data for AI systems: organisations must establish a
        data management governance framework addressing data quality, provenance,
        and appropriate use; production systems without data governance require
        human review;
    (c) Clause 8.6 — AI system from external providers: AI systems or
        components sourced from third parties require a supplier evaluation
        addressing the provider's AI governance practices before integration.

    References
    ----------
    ISO 42001:2023 Clause 8 — Operations
    ISO 42001:2023 Clause 8.3 — Data for AI systems
    ISO 42001:2023 Clause 8.4 — AI system life cycle
    ISO 42001:2023 Clause 8.6 — AI system from external providers
    """

    FILTER_NAME = "ISO42001_OPERATIONS_FILTER"

    def evaluate(
        self, context: ISO42001Context, document: ISO42001Document
    ) -> FilterResult:
        # Clause 8.4 — autonomous system without human oversight: denied
        if (
            context.ai_system_type == "autonomous"
            and not context.has_human_oversight
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "ISO 42001:2023 Clause 8.4: Autonomous AI systems require "
                    "human oversight mechanisms"
                ),
                regulation_citation="ISO 42001:2023 Clause 8.4",
                requires_logging=True,
            )

        # Clause 8.3 — production without data governance: requires review
        if (
            not context.has_data_governance
            and context.deployment_stage == "production"
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "ISO 42001:2023 Clause 8.3: Data management governance "
                    "required in production"
                ),
                regulation_citation="ISO 42001:2023 Clause 8.3",
                requires_logging=True,
            )

        # Clause 8.6 — third-party AI without supplier assessment: requires review
        if context.is_third_party_ai and not context.has_supplier_assessment:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "ISO 42001:2023 Clause 8.6: Third-party AI systems require "
                    "supplier evaluation"
                ),
                regulation_citation="ISO 42001:2023 Clause 8.6",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason="Compliant with ISO 42001:2023 Clause 8 Operations obligations",
            regulation_citation="ISO 42001:2023 Clause 8 — Operations",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Layer 4 — Clause 9: Performance Evaluation (PerformanceFilter)
# ---------------------------------------------------------------------------


class ISO42001PerformanceFilter:
    """
    Layer 4: ISO 42001:2023 Clause 9 — Performance Evaluation.

    ISO 42001:2023 Clause 9 establishes requirements for monitoring, measuring,
    analysing, and evaluating the AI management system.  Three principal
    controls apply:

    (a) Clause 9.1 — Monitoring, measurement, analysis and evaluation: limited
        and high-risk AI systems require an audit trail enabling retrospective
        review of AI system behaviour and decisions;
    (b) Clause 7.5 — Documented information: AI systems deployed in production
        require documented information describing the system's design, intended
        use, limitations, and operational parameters;
    (c) Clause 10.1 — Nonconformity and corrective action: high-risk AI systems
        require a defined incident management and corrective action process
        enabling timely response to failures and unintended outcomes.

    References
    ----------
    ISO 42001:2023 Clause 7.5 — Documented information
    ISO 42001:2023 Clause 9 — Performance evaluation
    ISO 42001:2023 Clause 9.1 — Monitoring, measurement, analysis and evaluation
    ISO 42001:2023 Clause 10.1 — Nonconformity and corrective action
    """

    FILTER_NAME = "ISO42001_PERFORMANCE_FILTER"

    def evaluate(
        self, context: ISO42001Context, document: ISO42001Document
    ) -> FilterResult:
        # Clause 9.1 — limited/high risk without audit trail: denied
        if (
            context.risk_level in {"high", "limited"}
            and not context.has_audit_trail
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="DENIED",
                reason=(
                    "ISO 42001:2023 Clause 9.1: Monitoring and audit trail "
                    "required for limited/high-risk AI"
                ),
                regulation_citation="ISO 42001:2023 Clause 9.1",
                requires_logging=True,
            )

        # Clause 7.5 — production without transparency docs: requires review
        if (
            not context.has_transparency_docs
            and context.deployment_stage == "production"
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "ISO 42001:2023 Clause 7.5: Documented information required "
                    "for production AI systems"
                ),
                regulation_citation="ISO 42001:2023 Clause 7.5",
                requires_logging=True,
            )

        # Clause 10.1 — high-risk without incident process: requires review
        if context.risk_level == "high" and not context.has_incident_process:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision="REQUIRES_HUMAN_REVIEW",
                reason=(
                    "ISO 42001:2023 Clause 10.1: Nonconformity and corrective "
                    "action process required for high-risk AI"
                ),
                regulation_citation="ISO 42001:2023 Clause 10.1",
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision="APPROVED",
            reason=(
                "Compliant with ISO 42001:2023 Clause 9 Performance Evaluation "
                "obligations"
            ),
            regulation_citation="ISO 42001:2023 Clause 9 — Performance Evaluation",
            requires_logging=False,
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class ISO42001GovernanceOrchestrator:
    """
    Four-filter ISO 42001:2023 AI management system governance orchestrator.

    Evaluation order:
        ISO42001PolicyFilter  →  ISO42001RiskFilter  →
        ISO42001OperationsFilter  →  ISO42001PerformanceFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all conformity gaps simultaneously.
    Results are collected as a list of ``FilterResult`` objects and passed
    to ``ISO42001ComplianceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            ISO42001PolicyFilter(),
            ISO42001RiskFilter(),
            ISO42001OperationsFilter(),
            ISO42001PerformanceFilter(),
        ]

    def evaluate(
        self, context: ISO42001Context, document: ISO42001Document
    ) -> List[FilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : ISO42001Context
            The AI system governance context to evaluate.
        document : ISO42001Document
            The document being processed by the AI system.

        Returns
        -------
        list[FilterResult]
            One result per filter, in evaluation order.
        """
        return [f.evaluate(context, document) for f in self._filters]


# ---------------------------------------------------------------------------
# Aggregated compliance report
# ---------------------------------------------------------------------------


@dataclass
class ISO42001ComplianceReport:
    """
    Aggregated ISO 42001:2023 AIMS compliance report across all four filters.

    Decision aggregation:
    - Any DENIED result                     → overall_decision is "DENIED"
    - No DENIED + any REQUIRES_HUMAN_REVIEW → "REQUIRES_HUMAN_REVIEW"
    - All APPROVED                          → "APPROVED"

    is_compliant is True unless overall_decision is "DENIED".
    REQUIRES_HUMAN_REVIEW is not a denial but indicates a conformity gap
    that must be addressed before the system can be considered fully conforming.

    Attributes
    ----------
    context : ISO42001Context
        The AI system context that was evaluated.
    document : ISO42001Document
        The document that was evaluated.
    filter_results : list[FilterResult]
        Per-filter results in evaluation order.
    """

    context: ISO42001Context
    document: ISO42001Document
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
        the identified conformity gaps are addressed.
        """
        return self.overall_decision != "DENIED"

    @property
    def conformity_level(self) -> str:
        """
        ISO 42001:2023 AIMS conformity level.

        Returns "FULL" if all filters are APPROVED, "PARTIAL" if any filter
        is REQUIRES_HUMAN_REVIEW (but none DENIED), "NON_CONFORMING" if any
        filter is DENIED.
        """
        if any(r.is_denied for r in self.filter_results):
            return "NON_CONFORMING"
        if any(r.decision == "REQUIRES_HUMAN_REVIEW" for r in self.filter_results):
            return "PARTIAL"
        return "FULL"

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary across all four filters.

        Returns a multi-line string listing each filter name, its decision,
        and either the approval reason or the denial/review reason.
        """
        lines: List[str] = [
            f"ISO 42001:2023 AIMS Compliance Report — user_id={self.context.user_id}",
            (
                f"Organization: {self.context.organization_type}  |  "
                f"AI System: {self.context.ai_system_type}  |  "
                f"Risk Level: {self.context.risk_level}  |  "
                f"Overall Decision: {self.overall_decision}  |  "
                f"Conformity: {self.conformity_level}"
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


def _compliant_enterprise_base() -> tuple[ISO42001Context, ISO42001Document]:
    """
    Base context: fully conforming enterprise decision-support system with
    limited risk level, all AIMS controls satisfied, in production.
    Used as the baseline from which failing scenarios are derived.
    """
    context = ISO42001Context(
        user_id="ISO-AI-001",
        organization_type="enterprise",
        ai_system_type="decision_support",
        risk_level="limited",
        has_aims_policy=True,
        has_risk_assessment=True,
        has_impact_assessment=True,
        has_human_oversight=True,
        has_data_governance=True,
        has_transparency_docs=True,
        has_incident_process=True,
        has_audit_trail=True,
        is_third_party_ai=False,
        has_supplier_assessment=False,
        deployment_stage="production",
    )
    document = ISO42001Document(
        content="Enterprise AI decision-support system compliance record",
        document_id="DOC-ISO-001",
        doc_type="ai_system_record",
    )
    return context, document


def _demonstrate_scenario(
    title: str,
    context: ISO42001Context,
    document: ISO42001Document,
    orchestrator: ISO42001GovernanceOrchestrator,
) -> None:
    results = orchestrator.evaluate(context, document)
    report = ISO42001ComplianceReport(
        context=context,
        document=document,
        filter_results=results,
    )
    print(f"\n{'=' * 70}")
    print(f"Scenario: {title}")
    print("=" * 70)
    print(report.compliance_summary)


if __name__ == "__main__":
    orchestrator = ISO42001GovernanceOrchestrator()
    base_ctx, base_doc = _compliant_enterprise_base()

    # Scenario 1 — fully conforming baseline
    _demonstrate_scenario(
        "Fully Conforming Enterprise Decision-Support System",
        base_ctx,
        base_doc,
        orchestrator,
    )

    # Scenario 2 — high-risk system without AI policy (Clause 5.1 denial)
    ctx2 = ISO42001Context(
        **{
            **base_ctx.__dict__,
            "risk_level": "high",
            "has_aims_policy": False,
        }
    )
    _demonstrate_scenario(
        "High-Risk System — No AI Policy (Clause 5.1 Denial)",
        ctx2,
        base_doc,
        orchestrator,
    )

    # Scenario 3 — autonomous system without human oversight (Clause 8.4 denial)
    ctx3 = ISO42001Context(
        **{
            **base_ctx.__dict__,
            "ai_system_type": "autonomous",
            "has_human_oversight": False,
        }
    )
    _demonstrate_scenario(
        "Autonomous System — No Human Oversight (Clause 8.4 Denial)",
        ctx3,
        base_doc,
        orchestrator,
    )

    # Scenario 4 — unacceptable risk system (Clause 6.1.2 denial)
    ctx4 = ISO42001Context(
        **{
            **base_ctx.__dict__,
            "risk_level": "unacceptable",
        }
    )
    _demonstrate_scenario(
        "Unacceptable Risk System — Deployment Prohibited (Clause 6.1.2)",
        ctx4,
        base_doc,
        orchestrator,
    )

    # Scenario 5 — production system missing multiple controls (partial conformity)
    ctx5 = ISO42001Context(
        **{
            **base_ctx.__dict__,
            "has_data_governance": False,
            "has_transparency_docs": False,
            "is_third_party_ai": True,
            "has_supplier_assessment": False,
        }
    )
    _demonstrate_scenario(
        "Production System — Multiple Partial Conformity Gaps",
        ctx5,
        base_doc,
        orchestrator,
    )
