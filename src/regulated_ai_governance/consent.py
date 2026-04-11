"""
consent.py — Consent management for regulated AI data processing.

Provides structured consent records and a lightweight in-memory consent store
for tracking whether a data subject has given consent for specific processing
purposes.

Consent is a core GDPR lawful basis (Art. 6(1)(a)) and is required for certain
HIPAA disclosures not covered by the treatment/payment/operations exceptions.
CCPA consent tracking is required for opt-in flows involving sensitive personal
information (CPRA § 1798.121).

Design
------
``ConsentRecord`` represents a single consent grant or revocation.
``ConsentStore`` is an in-memory registry for quick consent lookups during
agent execution. In production, persist records to a durable store and inject
a load function.

Usage::

    from regulated_ai_governance.consent import ConsentRecord, ConsentStore, ConsentStatus

    store = ConsentStore()

    # Record consent
    record = ConsentRecord.grant(
        subject_id="stu-alice",
        purpose="academic_ai_tutoring",
        regulation="FERPA",
        granted_by="alice@univ.edu",
    )
    store.record(record)

    # Check consent before processing
    if store.is_consented("stu-alice", "academic_ai_tutoring"):
        run_tutoring_agent(student_id="stu-alice")
    else:
        raise PermissionError("Consent not granted for academic_ai_tutoring")
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ConsentStatus(Enum):
    """The status of a consent record."""

    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"


@dataclass
class ConsentRecord:
    """
    A single consent grant or revocation for a specific processing purpose.

    Attributes:
        consent_id: UUID for this consent record.
        subject_id: Identifier of the data subject (student, patient, consumer).
        purpose: The processing purpose covered by this consent.
        status: Current consent status.
        regulation: Regulation under which consent is tracked.
        granted_by: Who granted consent (subject themselves, guardian, etc.).
        recorded_at: UTC timestamp when this record was created.
        expires_at: UTC timestamp when consent expires, or None if indefinite.
        revoked_at: UTC timestamp when consent was revoked, or None.
        metadata: Additional context (e.g. IP address, consent UI version).
    """

    subject_id: str
    purpose: str
    status: ConsentStatus
    regulation: str
    granted_by: str
    consent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def grant(
        cls,
        subject_id: str,
        purpose: str,
        regulation: str,
        granted_by: str,
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConsentRecord:
        """
        Factory: create a GRANTED consent record.

        Args:
            subject_id: Identifier of the consenting data subject.
            purpose: Processing purpose being consented to.
            regulation: Applicable regulation (``"GDPR"``, ``"HIPAA"``, ``"CCPA"``).
            granted_by: Who granted consent (typically the subject or their guardian).
            expires_at: Optional expiry timestamp.
            metadata: Optional context dict.

        Returns:
            A ``ConsentRecord`` with ``status=GRANTED``.
        """
        return cls(
            subject_id=subject_id,
            purpose=purpose,
            status=ConsentStatus.GRANTED,
            regulation=regulation,
            granted_by=granted_by,
            expires_at=expires_at,
            metadata=metadata or {},
        )

    @classmethod
    def revoke(
        cls,
        subject_id: str,
        purpose: str,
        regulation: str,
        revoked_by: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConsentRecord:
        """
        Factory: create a REVOKED consent record.

        GDPR Art. 7(3): the data subject has the right to withdraw consent at
        any time. Revocation must be as easy as granting consent.

        Args:
            subject_id: Identifier of the data subject revoking consent.
            purpose: Processing purpose being revoked.
            regulation: Applicable regulation.
            revoked_by: Who initiated the revocation.
            metadata: Optional context dict.

        Returns:
            A ``ConsentRecord`` with ``status=REVOKED`` and ``revoked_at`` set.
        """
        return cls(
            subject_id=subject_id,
            purpose=purpose,
            status=ConsentStatus.REVOKED,
            regulation=regulation,
            granted_by=revoked_by,
            revoked_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )

    def is_active(self) -> bool:
        """
        Return True if consent is currently active (GRANTED and not expired).
        """
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at is not None and datetime.now(timezone.utc) > self.expires_at:
            return False
        return True

    def to_audit_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation for audit logging."""
        return {
            "consent_id": self.consent_id,
            "subject_id": self.subject_id,
            "purpose": self.purpose,
            "status": self.status.value,
            "regulation": self.regulation,
            "granted_by": self.granted_by,
            "recorded_at": self.recorded_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }


class ConsentStore:
    """
    In-memory registry of consent records for quick lookup during agent execution.

    In production, replace the internal dict with a database-backed store by
    injecting a ``load_fn`` at construction time.

    Args:
        load_fn: Optional callable ``(subject_id, purpose) -> ConsentRecord | None``
            called on cache miss. Use to back the store with a real database.
    """

    def __init__(
        self,
        load_fn: Any | None = None,
    ) -> None:
        self._records: dict[tuple[str, str], list[ConsentRecord]] = {}
        self._load_fn = load_fn

    def record(self, consent: ConsentRecord) -> None:
        """
        Add *consent* to the store.

        Args:
            consent: The ``ConsentRecord`` to store.
        """
        key = (consent.subject_id, consent.purpose)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(consent)

    def latest(self, subject_id: str, purpose: str) -> ConsentRecord | None:
        """
        Return the most recent consent record for *subject_id* and *purpose*.

        Consults the ``load_fn`` on cache miss if one was provided.

        Args:
            subject_id: Data subject identifier.
            purpose: Processing purpose.

        Returns:
            The most recent ``ConsentRecord``, or None if no record exists.
        """
        key = (subject_id, purpose)
        records = self._records.get(key)
        if not records and self._load_fn is not None:
            loaded = self._load_fn(subject_id, purpose)
            if loaded is not None:
                self.record(loaded)
                records = self._records.get(key)
        if not records:
            return None
        return max(records, key=lambda r: r.recorded_at)

    def is_consented(self, subject_id: str, purpose: str) -> bool:
        """
        Return True if the most recent consent record is active (GRANTED, not expired).

        Args:
            subject_id: Data subject identifier.
            purpose: Processing purpose.

        Returns:
            True if consent is active; False otherwise.
        """
        record = self.latest(subject_id, purpose)
        if record is None:
            return False
        return record.is_active()

    def history(self, subject_id: str, purpose: str) -> list[ConsentRecord]:
        """
        Return the full consent history for *subject_id* and *purpose*.

        Args:
            subject_id: Data subject identifier.
            purpose: Processing purpose.

        Returns:
            List of ``ConsentRecord`` objects in chronological order.
        """
        key = (subject_id, purpose)
        return sorted(self._records.get(key, []), key=lambda r: r.recorded_at)
