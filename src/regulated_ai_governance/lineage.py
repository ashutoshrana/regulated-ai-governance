"""
lineage.py — Data lineage tracking for regulated AI pipelines.

Provides structured lineage records that document how data flows through an
AI pipeline — from source retrieval through context assembly to LLM output.
Lineage records answer the auditor question: "where did this data come from,
who accessed it, and what was it used for?"

Regulatory drivers
------------------
- **GDPR Art. 30** (Record of Processing Activities): document sources, purposes,
  and recipients of personal data processing.
- **HIPAA § 164.528** (Accounting of disclosures): patients may request an
  accounting of disclosures for up to six years.
- **FERPA 34 CFR § 99.32** (Record of access): institutions must maintain a
  record of each request for access and each disclosure made.
- **SOC 2 CC7.2** (Monitoring): log anomalies in data processing pipelines.

Usage::

    from regulated_ai_governance.lineage import DataLineageRecord, LineageTracker

    tracker = LineageTracker()

    record = tracker.record_retrieval(
        pipeline_id="rag-pipeline-001",
        subject_id="stu-alice",
        source_system="vector_store",
        document_ids=["doc-1", "doc-2"],
        query="enrollment status",
        regulation="FERPA",
        actor_id="agent-advisor",
    )

    # Later: record what was sent to the LLM
    tracker.record_llm_input(
        pipeline_id="rag-pipeline-001",
        document_ids=["doc-1"],  # after compliance filter
        model_id="gpt-4o",
    )
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class LineageEventType(Enum):
    """Type of lineage event in the data processing pipeline."""

    RETRIEVAL = "RETRIEVAL"  # Documents retrieved from a source
    COMPLIANCE_FILTER = "COMPLIANCE_FILTER"  # Documents filtered for compliance
    CONTEXT_ASSEMBLY = "CONTEXT_ASSEMBLY"  # Context window assembled
    LLM_INPUT = "LLM_INPUT"  # Data sent to LLM
    LLM_OUTPUT = "LLM_OUTPUT"  # LLM response received
    TOOL_CALL = "TOOL_CALL"  # Agent tool execution
    DISCLOSURE = "DISCLOSURE"  # Data disclosed to external system


@dataclass
class DataLineageRecord:
    """
    A single event in the data lineage trail for a regulated AI pipeline run.

    Attributes:
        record_id: UUID for this lineage record.
        pipeline_id: Identifier grouping all records for one pipeline execution.
        event_type: Type of lineage event.
        subject_id: Data subject whose data was processed (student, patient, etc.).
        source_system: System or component that produced or processed the data.
        document_ids: List of document or record identifiers involved.
        regulation: Applicable regulation (``"FERPA"``, ``"HIPAA"``, ``"GDPR"``).
        actor_id: Identifier of the agent, user, or system that triggered the event.
        query: Query or intent that triggered the event, if applicable.
        metadata: Additional event-specific context.
        recorded_at: UTC timestamp when this record was created.
    """

    pipeline_id: str
    event_type: LineageEventType
    subject_id: str
    source_system: str
    document_ids: list[str]
    regulation: str
    actor_id: str
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_audit_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation for audit logging."""
        return {
            "record_id": self.record_id,
            "pipeline_id": self.pipeline_id,
            "event_type": self.event_type.value,
            "subject_id": self.subject_id,
            "source_system": self.source_system,
            "document_ids": self.document_ids,
            "document_count": len(self.document_ids),
            "regulation": self.regulation,
            "actor_id": self.actor_id,
            "query": self.query,
            "metadata": self.metadata,
            "recorded_at": self.recorded_at.isoformat(),
        }


class LineageTracker:
    """
    Tracks data lineage across a regulated AI pipeline execution.

    Maintains an ordered list of ``DataLineageRecord`` events for each
    ``pipeline_id``. In production, replace the in-memory store by injecting
    a ``sink`` callable that writes to a durable audit system.

    Args:
        sink: Optional callable ``(DataLineageRecord) -> None`` called for every
            recorded event. Defaults to in-memory storage only.
    """

    def __init__(self, sink: Any | None = None) -> None:
        self._records: list[DataLineageRecord] = []
        self._sink = sink

    def record(self, lineage_record: DataLineageRecord) -> DataLineageRecord:
        """
        Add *lineage_record* to the tracker and call the sink if configured.

        Args:
            lineage_record: The ``DataLineageRecord`` to store.

        Returns:
            The same record (for chaining).
        """
        self._records.append(lineage_record)
        if self._sink is not None:
            self._sink(lineage_record)
        return lineage_record

    def record_retrieval(
        self,
        pipeline_id: str,
        subject_id: str,
        source_system: str,
        document_ids: list[str],
        regulation: str,
        actor_id: str,
        query: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DataLineageRecord:
        """
        Record a document retrieval event.

        Args:
            pipeline_id: Execution identifier.
            subject_id: Data subject whose documents were retrieved.
            source_system: Source system (e.g. ``"vector_store"``, ``"database"``).
            document_ids: List of retrieved document IDs.
            regulation: Applicable regulation.
            actor_id: Agent or user that triggered the retrieval.
            query: Query that triggered the retrieval.
            metadata: Additional context.

        Returns:
            The created ``DataLineageRecord``.
        """
        return self.record(
            DataLineageRecord(
                pipeline_id=pipeline_id,
                event_type=LineageEventType.RETRIEVAL,
                subject_id=subject_id,
                source_system=source_system,
                document_ids=document_ids,
                regulation=regulation,
                actor_id=actor_id,
                query=query,
                metadata=metadata or {},
            )
        )

    def record_compliance_filter(
        self,
        pipeline_id: str,
        subject_id: str,
        before_ids: list[str],
        after_ids: list[str],
        regulation: str,
        actor_id: str,
        filter_reason: str = "",
    ) -> DataLineageRecord:
        """
        Record the output of a compliance filter step.

        Args:
            pipeline_id: Execution identifier.
            subject_id: Data subject.
            before_ids: Document IDs before filtering.
            after_ids: Document IDs after filtering (subset of before_ids).
            regulation: Applicable regulation.
            actor_id: Component that applied the filter.
            filter_reason: Human-readable description of the filter applied.

        Returns:
            The created ``DataLineageRecord``.
        """
        removed = len(before_ids) - len(after_ids)
        return self.record(
            DataLineageRecord(
                pipeline_id=pipeline_id,
                event_type=LineageEventType.COMPLIANCE_FILTER,
                subject_id=subject_id,
                source_system="compliance_filter",
                document_ids=after_ids,
                regulation=regulation,
                actor_id=actor_id,
                metadata={
                    "before_count": len(before_ids),
                    "after_count": len(after_ids),
                    "removed_count": removed,
                    "filter_reason": filter_reason,
                },
            )
        )

    def pipeline_records(self, pipeline_id: str) -> list[DataLineageRecord]:
        """
        Return all lineage records for *pipeline_id* in chronological order.

        Args:
            pipeline_id: Execution identifier to filter by.

        Returns:
            List of ``DataLineageRecord`` objects.
        """
        return [r for r in self._records if r.pipeline_id == pipeline_id]

    def to_audit_trail(self, pipeline_id: str) -> list[dict[str, Any]]:
        """
        Return a JSON-serialisable audit trail for *pipeline_id*.

        Args:
            pipeline_id: Execution identifier.

        Returns:
            List of audit dicts in chronological order.
        """
        return [r.to_audit_dict() for r in self.pipeline_records(pipeline_id)]
