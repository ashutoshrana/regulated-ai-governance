"""
regulations/iso42001.py — ISO/IEC 42001:2023 AI Management System governance.

Provides governance-layer controls aligned with ISO/IEC 42001:2023 (Information
Technology — Artificial Intelligence — Management system for organizations).
ISO 42001 is the first and only international management system standard
specifically for AI systems, and serves as the primary conformity assessment
path for the EU AI Act Article 40 (harmonized standards).

**Scope**: AI system lifecycle governance, data quality and provenance
validation, risk and impact assessment checkpoints, human oversight
enforcement, and third-party AI component accountability. This module
addresses the Annex A controls that apply directly to agentic AI systems
and RAG retrieval pipelines.

Relevant Annex A Controls
--------------------------

  **A.5.2** (AI System Risk Assessment):
    Organizations shall establish, implement, and maintain an AI risk assessment
    process. For agentic AI, this maps to evaluating retrieval and generation
    risks (hallucination rate, data leakage probability, bias amplification)
    before deployment and during operation.

  **A.5.3** (AI System Impact Assessment):
    DPIA-equivalent for AI: assess societal, individual, and organizational
    impact before deployment. For high-risk AI (EU AI Act Annex III), a
    documented AIIA is required.

  **A.6.2.5** (Deployment of AI System):
    Approval gates before a RAG pipeline or agent goes to production. Maps to
    enforcing a ``DeploymentApprovalGate`` that blocks execution until
    deployment approval is recorded.

  **A.6.2.6** (Operation and Monitoring):
    Ongoing drift detection, response quality monitoring, retrieval accuracy
    tracking, and anomaly detection for the deployed AI system.

  **A.6.2.10** (Defined Use and Misuse of AI System):
    Explicit scoping of permitted and prohibited use cases. For agentic AI,
    this maps to an ``OperatingScope`` that blocks out-of-scope actions.

  **A.7.2** (Data for Development and Enhancement of AI System):
    All data sources feeding the RAG knowledge base must be documented.

  **A.7.5** (Data Acquisition and Collection):
    Lawful basis and provenance for all documents in the knowledge base.

  **A.7.6** (Data Provenance):
    Traceable chain of custody for every document in the vector store.

  **A.9.5** (Human Oversight Aspects):
    Mechanisms for human review of AI outputs in high-stakes decisions. Maps
    to an escalation rule that routes high-stakes actions to human review.

  **A.10.2** (Suppliers of AI System Components):
    Third-party LLM APIs, embedding models, and vector DB providers must be
    assessed and documented.

Defense-in-depth layer
------------------------
ISO 42001 controls sit at the governance layer of the AI system lifecycle:

    Deployment:  A.6.2.5 — approval gates before production
    Operation:   A.6.2.6 / A.6.2.10 — scope + drift monitoring
    Data:        A.7.2 / A.7.5 / A.7.6 — provenance + quality
    Risk:        A.5.2 / A.5.3 — risk + impact assessment
    Oversight:   A.9.5 — human review for high-stakes decisions
    Supply chain: A.10.2 — third-party component governance

Usage
------

.. code-block:: python

    from regulated_ai_governance.regulations.iso42001 import (
        ISO42001OperatingScope,
        ISO42001DeploymentRecord,
        ISO42001DataProvenanceRecord,
        ISO42001GovernancePolicy,
    )

    scope = ISO42001OperatingScope(
        system_id="rag_assistant_v2",
        permitted_use_cases=frozenset({
            "answer_customer_faq",
            "summarize_knowledge_article",
            "search_product_catalog",
        }),
        prohibited_use_cases=frozenset({
            "generate_legal_advice",
            "make_credit_decisions",
            "diagnose_medical_conditions",
        }),
        deployment_approved=True,
        deployment_approver="cto_alice",
        human_oversight_required_for=frozenset({"financial_recommendation"}),
    )

    policy = ISO42001GovernancePolicy(
        scope=scope,
        audit_sink=my_aiops_log.append,
    )
    decision = policy.evaluate_action("answer_customer_faq")
    print(decision.permitted)          # True
    print(policy.last_audit_record.to_log_entry())
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Operating Scope
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ISO42001OperatingScope:
    """
    Defines the ISO/IEC 42001:2023 operating boundaries for an AI system.

    Maps to:
    - **A.6.2.10** — Defined Use and Misuse of AI System
    - **A.6.2.5** — Deployment of AI System (approval gate)
    - **A.9.5** — Human Oversight Aspects

    Attributes:
        system_id: Unique identifier for the AI system (e.g. RAG pipeline name
            and version).  Written into every audit record.
        permitted_use_cases: Frozenset of action/use-case names that are
            explicitly permitted under this operating scope.  Any action not
            in this set is blocked unless ``permit_unlisted`` is True.
        prohibited_use_cases: Frozenset of action names that are explicitly
            prohibited regardless of any other policy (A.6.2.10 misuse
            prevention).  Takes precedence over ``permitted_use_cases``.
        deployment_approved: True if the system has received a formal deployment
            approval (A.6.2.5 deployment gate).  If False, all actions are
            blocked with a ``deployment_not_approved`` reason.
        deployment_approver: Identifier of the person or process that granted
            deployment approval.  Required if ``deployment_approved`` is True.
        human_oversight_required_for: Actions that must be routed to human
            review before execution (A.9.5 human oversight aspects).
        permit_unlisted: If True, actions not in ``permitted_use_cases`` are
            permitted by default (open-scope mode).  Defaults to False (deny
            all unlisted — most restrictive, recommended for high-risk AI).
    """

    system_id: str
    permitted_use_cases: frozenset[str] = field(default_factory=frozenset)
    prohibited_use_cases: frozenset[str] = field(default_factory=frozenset)
    deployment_approved: bool = False
    deployment_approver: str = ""
    human_oversight_required_for: frozenset[str] = field(default_factory=frozenset)
    permit_unlisted: bool = False

    def is_deployment_approved(self) -> bool:
        """Return True if the system has formal deployment approval (A.6.2.5)."""
        return self.deployment_approved

    def is_prohibited(self, action_name: str) -> bool:
        """Return True if *action_name* is explicitly prohibited (A.6.2.10)."""
        return action_name in self.prohibited_use_cases

    def is_permitted(self, action_name: str) -> bool:
        """
        Return True if *action_name* is within the permitted operating scope.

        Non-prohibited check is the caller's responsibility.
        """
        if self.permit_unlisted:
            return True
        return action_name in self.permitted_use_cases

    def requires_human_oversight(self, action_name: str) -> bool:
        """Return True if *action_name* requires human review (A.9.5)."""
        return action_name in self.human_oversight_required_for


# ---------------------------------------------------------------------------
# Data Provenance Record
# ---------------------------------------------------------------------------


@dataclass
class ISO42001DataProvenanceRecord:
    """
    Documents the chain of custody for a data source in the AI knowledge base.

    Maps to ISO/IEC 42001:2023 Annex A controls:
    - **A.7.2** — Data for Development and Enhancement of AI System
    - **A.7.5** — Data Acquisition and Collection (lawful basis)
    - **A.7.6** — Data Provenance

    Attributes:
        source_id: Unique identifier for the data source.
        source_type: Category of source (e.g. ``"internal_docs"``,
            ``"web_crawl"``, ``"third_party_feed"``).
        lawful_basis: Legal justification for processing this data
            (e.g. ``"legitimate_interest"``, ``"consent"``, ``"contract"``).
        collection_timestamp_utc: When the data was collected/ingested.
        data_quality_validated: Whether data quality checks (A.7.3) have been
            performed.
        quality_validation_notes: Summary of quality validation results.
        processor_id: Identifier of the person/system that processed this source.
        annex_a_controls: ISO 42001 Annex A control IDs documented by this record.
    """

    source_id: str
    source_type: str
    lawful_basis: str
    collection_timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data_quality_validated: bool = False
    quality_validation_notes: str = ""
    processor_id: str = ""
    annex_a_controls: list[str] = field(default_factory=lambda: ["A.7.2", "A.7.5", "A.7.6"])

    def to_log_entry(self) -> str:
        """Serialize to a structured JSON log entry for AI system documentation."""
        return json.dumps(
            {
                "framework": "ISO_IEC_42001_2023",
                "record_type": "data_provenance",
                "annex_a_controls": sorted(self.annex_a_controls),
                "source_id": self.source_id,
                "source_type": self.source_type,
                "lawful_basis": self.lawful_basis,
                "data_quality_validated": self.data_quality_validated,
                "quality_validation_notes": self.quality_validation_notes,
                "processor_id": self.processor_id,
                "collection_timestamp_utc": self.collection_timestamp_utc,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """SHA-256 hash for tamper-evidence in the AI system documentation."""
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()


# ---------------------------------------------------------------------------
# Deployment Record
# ---------------------------------------------------------------------------


@dataclass
class ISO42001DeploymentRecord:
    """
    Documents a formal deployment approval for an AI system (A.6.2.5).

    Required before any AI system goes to production under ISO 42001.
    Captures the risk assessment outcome (A.5.2) and impact assessment
    outcome (A.5.3) that were the basis for the approval decision.

    Attributes:
        system_id: Unique identifier for the AI system.
        system_version: Version string of the deployed system.
        approver_id: Identifier of the person granting deployment approval.
        approval_timestamp_utc: When approval was granted.
        risk_level: Risk assessment outcome (e.g. ``"low"``, ``"medium"``, ``"high"``).
        risk_assessment_notes: Summary of A.5.2 risk assessment findings.
        impact_assessment_completed: Whether AIIA (A.5.3) was completed.
        impact_assessment_notes: Summary of A.5.3 impact assessment findings.
        intended_use: Documented intended use cases (A.6.2.10).
        prohibited_use: Documented prohibited use cases (A.6.2.10).
        third_party_components: List of third-party AI components assessed (A.10.2).
        annex_a_controls: ISO 42001 Annex A control IDs covered by this record.
    """

    system_id: str
    system_version: str
    approver_id: str
    approval_timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    risk_level: str = "medium"
    risk_assessment_notes: str = ""
    impact_assessment_completed: bool = False
    impact_assessment_notes: str = ""
    intended_use: list[str] = field(default_factory=list)
    prohibited_use: list[str] = field(default_factory=list)
    third_party_components: list[dict[str, str]] = field(default_factory=list)
    annex_a_controls: list[str] = field(default_factory=lambda: ["A.5.2", "A.5.3", "A.6.2.5", "A.6.2.10", "A.10.2"])

    def to_log_entry(self) -> str:
        """Serialize to a structured JSON log entry for AI system documentation."""
        return json.dumps(
            {
                "framework": "ISO_IEC_42001_2023",
                "record_type": "deployment_approval",
                "annex_a_controls": sorted(self.annex_a_controls),
                "system_id": self.system_id,
                "system_version": self.system_version,
                "approver_id": self.approver_id,
                "risk_level": self.risk_level,
                "risk_assessment_notes": self.risk_assessment_notes,
                "impact_assessment_completed": self.impact_assessment_completed,
                "impact_assessment_notes": self.impact_assessment_notes,
                "intended_use": sorted(self.intended_use),
                "prohibited_use": sorted(self.prohibited_use),
                "third_party_components": self.third_party_components,
                "approval_timestamp_utc": self.approval_timestamp_utc,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """SHA-256 hash for tamper-evidence in the AI system documentation."""
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()


# ---------------------------------------------------------------------------
# Audit Record
# ---------------------------------------------------------------------------


@dataclass
class ISO42001AuditRecord:
    """
    Structured audit record for an ISO/IEC 42001:2023 governance evaluation.

    Attributes:
        system_id: AI system identifier.
        actor_id: Authenticated principal identifier.
        action_name: The action or use case that was evaluated.
        permitted: Whether the action was permitted under the operating scope.
        denial_reason: Reason for denial if ``permitted`` is False.
        human_oversight_required: Whether human review was triggered (A.9.5).
        annex_a_controls: Annex A control IDs applied during this evaluation.
        timestamp_utc: ISO 8601 UTC timestamp.
        session_id: Correlation ID for the session.
    """

    system_id: str
    actor_id: str
    action_name: str
    permitted: bool
    denial_reason: str | None = None
    human_oversight_required: bool = False
    annex_a_controls: list[str] = field(
        default_factory=lambda: [
            "A.5.2",
            "A.6.2.5",
            "A.6.2.6",
            "A.6.2.10",
            "A.9.5",
        ]
    )
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = ""

    def to_log_entry(self) -> str:
        """Serialize to a structured JSON log line for AISEM / AI governance audit."""
        return json.dumps(
            {
                "framework": "ISO_IEC_42001_2023",
                "annex_a_controls": sorted(self.annex_a_controls),
                "event": "ai_governance_evaluation",
                "system_id": self.system_id,
                "actor_id": self.actor_id,
                "action_name": self.action_name,
                "permitted": self.permitted,
                "denial_reason": self.denial_reason,
                "human_oversight_required": self.human_oversight_required,
                "timestamp_utc": self.timestamp_utc,
                "session_id": self.session_id,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """SHA-256 hash for tamper-evidence in the AI system audit trail."""
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()


# ---------------------------------------------------------------------------
# Governance Policy
# ---------------------------------------------------------------------------


class ISO42001GovernancePolicy:
    """
    ISO/IEC 42001:2023 AI Management System governance policy.

    Three controls applied in order:

    1. **A.6.2.5 Deployment gate** — Block all actions if the AI system has
       not received formal deployment approval.
    2. **A.6.2.10 Prohibited use check** — Block actions that are explicitly
       prohibited under the defined use/misuse scope.
    3. **A.6.2.10 Permitted use check** — Block actions outside the permitted
       operating scope (unless ``permit_unlisted=True``).

    Human oversight routing (A.9.5): actions in ``human_oversight_required_for``
    are flagged with ``human_oversight_required=True`` in the audit record and
    can be wired to an escalation sink.

    Args:
        scope: ``ISO42001OperatingScope`` defining the system's operating
            boundaries.
        audit_sink: Optional callable receiving each ``ISO42001AuditRecord``.
        session_id: Correlation ID included in audit records.
        annex_a_controls: Override the default Annex A control IDs in audit
            records.
    """

    _DEFAULT_CONTROLS = [
        "A.5.2",
        "A.6.2.5",
        "A.6.2.6",
        "A.6.2.10",
        "A.9.5",
    ]

    def __init__(
        self,
        scope: ISO42001OperatingScope,
        audit_sink: Any | None = None,
        session_id: str = "",
        annex_a_controls: list[str] | None = None,
    ) -> None:
        self._scope = scope
        self._audit_sink = audit_sink
        self._session_id = session_id
        self._annex_a_controls = annex_a_controls or list(self._DEFAULT_CONTROLS)
        self._last_audit: ISO42001AuditRecord | None = None

    @property
    def last_audit_record(self) -> ISO42001AuditRecord | None:
        """The ``ISO42001AuditRecord`` produced by the most recent evaluation."""
        return self._last_audit

    @property
    def system_id(self) -> str:
        """The AI system ID from the operating scope."""
        return self._scope.system_id

    def evaluate_action(
        self,
        action_name: str,
        actor_id: str = "",
        context: dict[str, Any] | None = None,
    ) -> ISO42001PolicyDecision:
        """
        Evaluate *action_name* against the ISO 42001 operating scope.

        Args:
            action_name: The action or use case to evaluate.
            actor_id: Authenticated principal identifier.
            context: Optional context dict.

        Returns:
            An ``ISO42001PolicyDecision`` with permit/deny and oversight flag.
        """
        _ = context  # reserved for future enrichment

        # A.6.2.5: deployment gate
        if not self._scope.is_deployment_approved():
            return self._emit_and_return(
                action_name=action_name,
                actor_id=actor_id,
                permitted=False,
                denial_reason=(
                    f"AI system '{self._scope.system_id}' has not received "
                    "deployment approval (ISO 42001 A.6.2.5). Action blocked."
                ),
                human_oversight=False,
            )

        # A.6.2.10: prohibited use check
        if self._scope.is_prohibited(action_name):
            return self._emit_and_return(
                action_name=action_name,
                actor_id=actor_id,
                permitted=False,
                denial_reason=(
                    f"Action '{action_name}' is in the prohibited use cases "
                    f"for system '{self._scope.system_id}' (ISO 42001 A.6.2.10)."
                ),
                human_oversight=False,
            )

        # A.6.2.10: permitted use check
        if not self._scope.is_permitted(action_name):
            return self._emit_and_return(
                action_name=action_name,
                actor_id=actor_id,
                permitted=False,
                denial_reason=(
                    f"Action '{action_name}' is outside the permitted operating "
                    f"scope for system '{self._scope.system_id}' (ISO 42001 A.6.2.10)."
                ),
                human_oversight=False,
            )

        # A.9.5: human oversight check
        human_oversight = self._scope.requires_human_oversight(action_name)

        return self._emit_and_return(
            action_name=action_name,
            actor_id=actor_id,
            permitted=True,
            denial_reason=None,
            human_oversight=human_oversight,
        )

    def _emit_and_return(
        self,
        action_name: str,
        actor_id: str,
        permitted: bool,
        denial_reason: str | None,
        human_oversight: bool,
    ) -> ISO42001PolicyDecision:
        record = ISO42001AuditRecord(
            system_id=self._scope.system_id,
            actor_id=actor_id,
            action_name=action_name,
            permitted=permitted,
            denial_reason=denial_reason,
            human_oversight_required=human_oversight,
            annex_a_controls=self._annex_a_controls,
            session_id=self._session_id,
        )
        self._last_audit = record
        if self._audit_sink is not None:
            self._audit_sink(record)

        return ISO42001PolicyDecision(
            permitted=permitted,
            denial_reason=denial_reason,
            human_oversight_required=human_oversight,
        )


@dataclass
class ISO42001PolicyDecision:
    """
    Result of an ISO 42001 governance evaluation.

    Attributes:
        permitted: Whether the action is permitted under the operating scope.
        denial_reason: Human-readable reason if ``permitted`` is False.
        human_oversight_required: True if A.9.5 requires routing to human review.
    """

    permitted: bool
    denial_reason: str | None = None
    human_oversight_required: bool = False
