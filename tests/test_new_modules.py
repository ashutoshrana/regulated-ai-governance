"""
Tests for v0.2.0 regulated-ai-governance modules:
regulations/gdpr, regulations/ccpa, regulations/soc2,
integrations/autogen, integrations/llama_index, integrations/semantic_kernel,
integrations/haystack, pii_detector, consent, lineage.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from regulated_ai_governance.consent import ConsentRecord, ConsentStatus, ConsentStore
from regulated_ai_governance.integrations.autogen import GovernedAutoGenAgent
from regulated_ai_governance.integrations.haystack import GovernedHaystackComponent
from regulated_ai_governance.integrations.llama_index import GovernedQueryEngine
from regulated_ai_governance.integrations.semantic_kernel import GovernedKernelPlugin
from regulated_ai_governance.lineage import DataLineageRecord, LineageEventType, LineageTracker
from regulated_ai_governance.pii_detector import PIICategory, PIIDetector
from regulated_ai_governance.policy import ActionPolicy
from regulated_ai_governance.regulations.ccpa import (
    CCPAConsumerRequest,
    CCPADataInventoryRecord,
    make_ccpa_processing_policy,
)
from regulated_ai_governance.regulations.gdpr import (
    GDPRProcessingRecord,
    GDPRSubjectRequest,
    make_gdpr_processing_policy,
)
from regulated_ai_governance.regulations.soc2 import (
    SOC2ControlTestResult,
    SOC2TrustCategory,
    make_soc2_agent_policy,
)

# ===========================================================================
# GDPR
# ===========================================================================


class TestGDPRPolicy:
    def test_standard_action_permitted(self) -> None:
        policy = make_gdpr_processing_policy()
        permitted, _ = policy.permits("read_consented_data")
        assert permitted

    def test_high_risk_action_denied(self) -> None:
        policy = make_gdpr_processing_policy()
        permitted, reason = policy.permits("profiling")
        assert not permitted
        assert "denied" in reason.lower() or "profiling" in reason.lower()

    def test_unknown_action_denied_when_require_all(self) -> None:
        policy = make_gdpr_processing_policy()
        permitted, _ = policy.permits("unregistered_action")
        assert not permitted

    def test_custom_allowed_actions(self) -> None:
        policy = make_gdpr_processing_policy(allowed_actions={"custom_action"})
        permitted, _ = policy.permits("custom_action")
        assert permitted

    def test_escalation_rule_for_profiling(self) -> None:
        policy = make_gdpr_processing_policy()
        rule = policy.escalation_for("run_profiling_pipeline")
        assert rule is not None
        assert "dpo" in rule.escalate_to.lower() or "officer" in rule.escalate_to.lower()


class TestGDPRSubjectRequest:
    def test_grant_factory_sets_defaults(self) -> None:
        req = GDPRSubjectRequest(subject_id="user-1", request_type="erasure")
        assert req.regulation == "GDPR"
        assert req.request_id is not None

    def test_response_deadline_is_30_days(self) -> None:
        req = GDPRSubjectRequest(subject_id="user-1", request_type="access")
        diff = req.response_deadline - req.requested_at
        assert 29 <= diff.days <= 30

    def test_processing_record_to_ropa_dict_json_serialisable(self) -> None:
        record = GDPRProcessingRecord(
            controller="acme-corp",
            purpose="ai_tutoring",
            legal_basis="consent",
            data_categories=["academic_records"],
            recipients=["llm-provider"],
            retention_days=365,
        )
        d = record.to_ropa_dict()
        json.dumps(d)  # should not raise
        assert d["regulation"] == "GDPR"
        assert d["legal_basis"] == "consent"


# ===========================================================================
# CCPA
# ===========================================================================


class TestCCPAPolicy:
    def test_standard_action_permitted(self) -> None:
        policy = make_ccpa_processing_policy()
        permitted, _ = policy.permits("read_consented_data")
        assert permitted

    def test_sell_pi_denied(self) -> None:
        policy = make_ccpa_processing_policy()
        permitted, _ = policy.permits("sell_personal_information")
        assert not permitted

    def test_escalation_for_sensitive_pi(self) -> None:
        policy = make_ccpa_processing_policy()
        rule = policy.escalation_for("process_sensitive_health_data")
        assert rule is not None


class TestCCPAConsumerRequest:
    def test_response_deadline_is_45_days(self) -> None:
        req = CCPAConsumerRequest(consumer_id="ca-user-1", request_type="delete")
        diff = req.response_deadline - req.requested_at
        assert 44 <= diff.days <= 45

    def test_to_request_dict_json_serialisable(self) -> None:
        req = CCPAConsumerRequest(consumer_id="ca-user-1", request_type="know")
        json.dumps(req.to_request_dict())  # should not raise

    def test_inventory_record_to_disclosure_dict(self) -> None:
        rec = CCPADataInventoryRecord(
            data_category="identifiers",
            sources=["web_form"],
            business_purpose="enrollment",
            third_party_recipients=[],
            sold_or_shared=False,
        )
        d = rec.to_disclosure_dict()
        assert d["regulation"] == "CCPA"
        assert d["sold_or_shared"] is False
        json.dumps(d)  # should not raise


# ===========================================================================
# SOC 2
# ===========================================================================


class TestSOC2Policy:
    def test_authorised_action_permitted(self) -> None:
        policy = make_soc2_agent_policy()
        permitted, _ = policy.permits("read_authorised_data")
        assert permitted

    def test_disable_audit_logging_denied(self) -> None:
        policy = make_soc2_agent_policy()
        permitted, _ = policy.permits("disable_audit_logging")
        assert not permitted

    def test_escalation_for_audit_tampering(self) -> None:
        policy = make_soc2_agent_policy()
        rule = policy.escalation_for("disable_audit_trail")
        assert rule is not None


class TestSOC2ControlTestResult:
    def test_to_audit_evidence_dict_json_serialisable(self) -> None:
        result = SOC2ControlTestResult(
            control_id="CC6.1",
            trust_category=SOC2TrustCategory.SECURITY,
            action_tested="read_authorised_data",
            passed=True,
            finding="Control operating as designed",
            tested_by="automated-compliance-agent",
        )
        d = result.to_audit_evidence_dict()
        json.dumps(d)  # should not raise
        assert d["standard"] == "SOC2"
        assert d["trust_category"] == "Security"
        assert d["passed"] is True


# ===========================================================================
# AutoGen integration
# ===========================================================================


class _FakeAutoGenAgent:
    """Minimal stand-in for AutoGen ConversableAgent."""

    def __init__(self, name: str) -> None:
        self.name = name


class TestGovernedAutoGenAgent:
    def _policy(self) -> ActionPolicy:
        return ActionPolicy(allowed_actions={"fetch_record"}, require_all_allowed=True)

    def test_permitted_tool_executes(self) -> None:
        agent = GovernedAutoGenAgent.wrap(
            agent=_FakeAutoGenAgent("advisor"),
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        result = agent.guard_action("fetch_record", lambda: {"id": 1})
        assert result == {"id": 1}

    def test_denied_action_raises(self) -> None:
        agent = GovernedAutoGenAgent.wrap(
            agent=_FakeAutoGenAgent("advisor"),
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        with pytest.raises(PermissionError):
            agent.guard_action("export_records", lambda: None)

    def test_guarded_tool_wraps_callable(self) -> None:
        agent = GovernedAutoGenAgent.wrap(
            agent=_FakeAutoGenAgent("advisor"),
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )

        def fetch_record() -> dict:
            return {"data": "ok"}

        wrapped = agent.guarded_tool("fetch_record", fetch_record)
        assert wrapped() == {"data": "ok"}

    def test_underlying_agent_accessible(self) -> None:
        fake = _FakeAutoGenAgent("advisor")
        agent = GovernedAutoGenAgent.wrap(
            agent=fake,
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        assert agent.agent is fake


# ===========================================================================
# LlamaIndex integration
# ===========================================================================


class _FakeQueryEngine:
    """Minimal stand-in for LlamaIndex QueryEngine."""

    def query(self, query_str: str) -> dict:
        return {"response": f"answer to: {query_str}"}


class TestGovernedQueryEngine:
    def _policy(self) -> ActionPolicy:
        return ActionPolicy(allowed_actions={"llama_index_query"}, require_all_allowed=True)

    def test_permitted_query_executes(self) -> None:
        governed = GovernedQueryEngine.wrap(
            engine=_FakeQueryEngine(),
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        result = governed.query("enrollment status")
        assert "answer to" in result["response"]

    def test_denied_query_raises(self) -> None:
        policy = ActionPolicy(allowed_actions={"other_action"}, require_all_allowed=True)
        governed = GovernedQueryEngine.wrap(
            engine=_FakeQueryEngine(),
            policy=policy,
            regulation="FERPA",
            actor_id="stu-alice",
        )
        with pytest.raises(PermissionError):
            governed.query("any query")

    def test_audit_sink_called(self) -> None:
        from regulated_ai_governance.audit import GovernanceAuditRecord

        log: list[GovernanceAuditRecord] = []
        governed = GovernedQueryEngine.wrap(
            engine=_FakeQueryEngine(),
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
            audit_sink=log.append,
        )
        governed.query("test")
        assert len(log) == 1

    def test_underlying_engine_accessible(self) -> None:
        engine = _FakeQueryEngine()
        governed = GovernedQueryEngine.wrap(
            engine=engine,
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        assert governed.engine is engine


# ===========================================================================
# Semantic Kernel integration
# ===========================================================================


class _FakePlugin:
    def read_patient_data(self, patient_id: str) -> dict:
        return {"patient_id": patient_id}

    def write_note(self, note: str) -> str:
        return f"saved: {note}"


class TestGovernedKernelPlugin:
    def _policy_for(self, actions: set[str]) -> ActionPolicy:
        return ActionPolicy(allowed_actions=actions, require_all_allowed=True)

    def test_permitted_function_executes(self) -> None:
        plugin = GovernedKernelPlugin.from_object(
            plugin_name="PatientPlugin",
            target=_FakePlugin(),
            policy=self._policy_for({"read_patient_data"}),
            regulation="HIPAA",
            actor_id="nurse-101",
        )
        fn = plugin.get_governed_function("read_patient_data")
        result = fn(patient_id="P001")
        assert result == {"patient_id": "P001"}

    def test_denied_function_raises(self) -> None:
        plugin = GovernedKernelPlugin.from_object(
            plugin_name="PatientPlugin",
            target=_FakePlugin(),
            policy=self._policy_for({"read_patient_data"}),
            regulation="HIPAA",
            actor_id="nurse-101",
        )
        fn = plugin.get_governed_function("write_note")
        with pytest.raises(PermissionError):
            fn(note="some note")

    def test_function_names_lists_all(self) -> None:
        plugin = GovernedKernelPlugin.from_object(
            plugin_name="P",
            target=_FakePlugin(),
            policy=ActionPolicy(allowed_actions=set(), require_all_allowed=False),
            regulation="SOC2",
            actor_id="agent",
        )
        assert "read_patient_data" in plugin.function_names
        assert "write_note" in plugin.function_names

    def test_method_chaining(self) -> None:
        from regulated_ai_governance.agent_guard import GovernedActionGuard

        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"fn_a"}, require_all_allowed=True),
            regulation="GDPR",
            actor_id="user",
            audit_sink=lambda _: None,
        )
        plugin = (
            GovernedKernelPlugin(guard=guard, plugin_name="P")
            .add_function("fn_a", lambda: "a")
            .add_function("fn_b", lambda: "b")
        )
        assert isinstance(plugin, GovernedKernelPlugin)
        assert "fn_a" in plugin.function_names


# ===========================================================================
# Haystack integration
# ===========================================================================


class _FakeDoc:
    """Minimal stand-in for a Haystack Document."""

    def __init__(self, content: str) -> None:
        self.content = content


class TestGovernedHaystackComponent:
    def _policy(self) -> ActionPolicy:
        return ActionPolicy(
            allowed_actions={"retrieve_student_documents"},
            require_all_allowed=True,
        )

    def test_permitted_run_returns_documents(self) -> None:
        comp = GovernedHaystackComponent(
            action_name="retrieve_student_documents",
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        docs = [_FakeDoc("record 1"), _FakeDoc("record 2")]
        result = comp.run(documents=docs, query="enrollment")
        assert result["documents"] == docs

    def test_denied_action_raises(self) -> None:
        policy = ActionPolicy(allowed_actions={"other"}, require_all_allowed=True)
        comp = GovernedHaystackComponent(
            action_name="retrieve_student_documents",
            policy=policy,
            regulation="FERPA",
            actor_id="stu-alice",
        )
        with pytest.raises(PermissionError):
            comp.run(documents=[], query="test")

    def test_guard_callable_wraps_fn(self) -> None:
        comp = GovernedHaystackComponent(
            action_name="retrieve_student_documents",
            policy=self._policy(),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        result = comp.guard_callable(lambda: {"custom": True})
        assert result == {"custom": True}


# ===========================================================================
# PII Detector
# ===========================================================================


class TestPIIDetector:
    def test_detects_ssn(self) -> None:
        d = PIIDetector()
        result = d.scan("Patient SSN is 123-45-6789")
        assert result.has_pii
        assert PIICategory.SSN in result.detected_categories

    def test_detects_email(self) -> None:
        d = PIIDetector()
        result = d.scan("Contact me at alice@example.com")
        assert PIICategory.EMAIL in result.detected_categories

    def test_detects_phone(self) -> None:
        d = PIIDetector()
        result = d.scan("Call 415-555-1234")
        assert PIICategory.PHONE in result.detected_categories

    def test_clean_text_no_pii(self) -> None:
        d = PIIDetector()
        result = d.scan("The enrollment deadline is next Friday.")
        assert not result.has_pii

    def test_redact_replaces_pii(self) -> None:
        d = PIIDetector()
        redacted = d.redact("SSN: 123-45-6789 email: alice@example.com")
        assert "123-45-6789" not in redacted
        assert "REDACTED" in redacted

    def test_category_filter(self) -> None:
        d = PIIDetector(categories={PIICategory.SSN})
        result = d.scan("SSN: 123-45-6789 email: alice@example.com")
        assert PIICategory.SSN in result.detected_categories
        # Email should NOT be detected because we filtered to SSN only
        assert PIICategory.EMAIL not in result.detected_categories

    def test_contains_pii_convenience(self) -> None:
        d = PIIDetector()
        assert d.contains_pii("SSN 123-45-6789")
        assert not d.contains_pii("Hello world")

    def test_to_audit_dict_json_serialisable(self) -> None:
        d = PIIDetector()
        result = d.scan("SSN: 123-45-6789")
        json.dumps(result.to_audit_dict())  # should not raise


# ===========================================================================
# Consent
# ===========================================================================


class TestConsentRecord:
    def test_grant_factory(self) -> None:
        r = ConsentRecord.grant(
            subject_id="stu-alice",
            purpose="ai_tutoring",
            regulation="FERPA",
            granted_by="alice",
        )
        assert r.status == ConsentStatus.GRANTED
        assert r.is_active()

    def test_revoke_factory(self) -> None:
        r = ConsentRecord.revoke(
            subject_id="stu-alice",
            purpose="ai_tutoring",
            regulation="FERPA",
            revoked_by="alice",
        )
        assert r.status == ConsentStatus.REVOKED
        assert not r.is_active()

    def test_expired_consent_not_active(self) -> None:
        past = datetime.now(timezone.utc) - timedelta(days=1)
        r = ConsentRecord.grant(
            subject_id="stu-alice",
            purpose="ai_tutoring",
            regulation="GDPR",
            granted_by="alice",
            expires_at=past,
        )
        assert not r.is_active()

    def test_to_audit_dict_json_serialisable(self) -> None:
        r = ConsentRecord.grant("s1", "purpose", "GDPR", "s1")
        json.dumps(r.to_audit_dict())  # should not raise


class TestConsentStore:
    def test_is_consented_after_grant(self) -> None:
        store = ConsentStore()
        store.record(ConsentRecord.grant("stu-alice", "tutoring", "FERPA", "alice"))
        assert store.is_consented("stu-alice", "tutoring")

    def test_not_consented_after_revoke(self) -> None:
        store = ConsentStore()
        store.record(ConsentRecord.grant("stu-alice", "tutoring", "FERPA", "alice"))
        store.record(ConsentRecord.revoke("stu-alice", "tutoring", "FERPA", "alice"))
        assert not store.is_consented("stu-alice", "tutoring")

    def test_unknown_subject_not_consented(self) -> None:
        store = ConsentStore()
        assert not store.is_consented("unknown", "any_purpose")

    def test_history_chronological_order(self) -> None:
        store = ConsentStore()
        r1 = ConsentRecord.grant("stu-alice", "t", "GDPR", "alice")
        r2 = ConsentRecord.revoke("stu-alice", "t", "GDPR", "alice")
        store.record(r1)
        store.record(r2)
        history = store.history("stu-alice", "t")
        assert history[0].status == ConsentStatus.GRANTED
        assert history[1].status == ConsentStatus.REVOKED

    def test_load_fn_called_on_cache_miss(self) -> None:
        sentinel = ConsentRecord.grant("u1", "p1", "GDPR", "u1")
        load_fn_calls: list[tuple[str, str]] = []

        def _load(subject_id: str, purpose: str) -> ConsentRecord | None:
            load_fn_calls.append((subject_id, purpose))
            return sentinel

        store = ConsentStore(load_fn=_load)
        assert store.is_consented("u1", "p1")
        assert len(load_fn_calls) == 1


# ===========================================================================
# Data Lineage
# ===========================================================================


class TestDataLineageRecord:
    def test_to_audit_dict_json_serialisable(self) -> None:
        record = DataLineageRecord(
            pipeline_id="pipe-1",
            event_type=LineageEventType.RETRIEVAL,
            subject_id="stu-alice",
            source_system="vector_store",
            document_ids=["d1", "d2"],
            regulation="FERPA",
            actor_id="agent",
        )
        json.dumps(record.to_audit_dict())  # should not raise
        assert record.to_audit_dict()["document_count"] == 2


class TestLineageTracker:
    def test_record_retrieval(self) -> None:
        tracker = LineageTracker()
        record = tracker.record_retrieval(
            pipeline_id="p1",
            subject_id="stu-alice",
            source_system="vs",
            document_ids=["d1"],
            regulation="FERPA",
            actor_id="agent",
            query="enrollment",
        )
        assert record.event_type == LineageEventType.RETRIEVAL
        assert len(tracker.pipeline_records("p1")) == 1

    def test_record_compliance_filter(self) -> None:
        tracker = LineageTracker()
        tracker.record_compliance_filter(
            pipeline_id="p1",
            subject_id="stu-alice",
            before_ids=["d1", "d2", "d3"],
            after_ids=["d1"],
            regulation="FERPA",
            actor_id="filter",
        )
        records = tracker.pipeline_records("p1")
        assert records[0].metadata["removed_count"] == 2

    def test_pipeline_records_filters_by_id(self) -> None:
        tracker = LineageTracker()
        tracker.record_retrieval("pipe-A", "u1", "vs", ["d1"], "FERPA", "a")
        tracker.record_retrieval("pipe-B", "u2", "vs", ["d2"], "FERPA", "a")
        assert len(tracker.pipeline_records("pipe-A")) == 1
        assert len(tracker.pipeline_records("pipe-B")) == 1

    def test_to_audit_trail_json_serialisable(self) -> None:
        tracker = LineageTracker()
        tracker.record_retrieval("p1", "u1", "vs", ["d1"], "GDPR", "agent", query="test")
        trail = tracker.to_audit_trail("p1")
        json.dumps(trail)  # should not raise
        assert len(trail) == 1

    def test_sink_called_on_record(self) -> None:
        events: list[DataLineageRecord] = []
        tracker = LineageTracker(sink=events.append)
        tracker.record_retrieval("p1", "u1", "vs", [], "FERPA", "a")
        assert len(events) == 1
