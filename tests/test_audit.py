"""Tests for GovernanceAuditRecord."""

from __future__ import annotations

import json
from datetime import timezone

from regulated_ai_governance.audit import GovernanceAuditRecord


class TestGovernanceAuditRecord:
    def test_creates_with_required_fields(self):
        record = GovernanceAuditRecord(
            regulation="FERPA",
            actor_id="stu-alice",
            action_name="read_transcript",
            permitted=True,
        )
        assert record.regulation == "FERPA"
        assert record.actor_id == "stu-alice"
        assert record.action_name == "read_transcript"
        assert record.permitted is True

    def test_record_id_is_auto_generated_uuid(self):
        r1 = GovernanceAuditRecord(regulation="FERPA", actor_id="a", action_name="x", permitted=True)
        r2 = GovernanceAuditRecord(regulation="FERPA", actor_id="a", action_name="x", permitted=True)
        assert r1.record_id != r2.record_id
        assert len(r1.record_id) == 36  # UUID4 format

    def test_timestamp_is_utc(self):
        record = GovernanceAuditRecord(regulation="HIPAA", actor_id="emp-001", action_name="read_phi", permitted=False)
        assert record.timestamp.tzinfo == timezone.utc

    def test_to_log_entry_is_json_serializable(self):
        record = GovernanceAuditRecord(
            regulation="GLBA",
            actor_id="cust-123",
            action_name="read_account_balance",
            permitted=True,
            context={"session_id": "sess-xyz", "channel": "mobile"},
        )
        entry = record.to_log_entry()
        # Must be JSON-serializable (for log sinks)
        json.dumps(entry)

    def test_to_log_entry_contains_required_fields(self):
        record = GovernanceAuditRecord(
            regulation="FERPA",
            actor_id="stu-bob",
            action_name="export_records",
            permitted=False,
            denial_reason="Action explicitly denied",
            escalation_target="compliance_officer",
        )
        entry = record.to_log_entry()
        assert entry["regulation"] == "FERPA"
        assert entry["actor_id"] == "stu-bob"
        assert entry["action_name"] == "export_records"
        assert entry["permitted"] is False
        assert entry["denial_reason"] == "Action explicitly denied"
        assert entry["escalation_target"] == "compliance_officer"
        assert "record_id" in entry
        assert "timestamp" in entry

    def test_context_fields_are_prefixed_ctx_in_log_entry(self):
        record = GovernanceAuditRecord(
            regulation="FERPA",
            actor_id="stu-alice",
            action_name="read_record",
            permitted=True,
            context={"session_id": "sess-001", "agent_id": "agent-x"},
        )
        entry = record.to_log_entry()
        assert entry["ctx_session_id"] == "sess-001"
        assert entry["ctx_agent_id"] == "agent-x"

    def test_policy_version_defaults_to_1_0(self):
        record = GovernanceAuditRecord(
            regulation="HIPAA",
            actor_id="nurse-001",
            action_name="read_lab_results",
            permitted=True,
        )
        assert record.policy_version == "1.0"
        entry = record.to_log_entry()
        assert entry["policy_version"] == "1.0"
