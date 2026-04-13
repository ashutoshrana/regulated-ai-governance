"""Tests for ISO/IEC 42001:2023 AI Management System governance module."""

from __future__ import annotations

import json

from regulated_ai_governance.regulations.iso42001 import (
    ISO42001AuditRecord,
    ISO42001DataProvenanceRecord,
    ISO42001DeploymentRecord,
    ISO42001GovernancePolicy,
    ISO42001OperatingScope,
    ISO42001PolicyDecision,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_scope(
    permitted: set[str] | None = None,
    prohibited: set[str] | None = None,
    deployment_approved: bool = True,
    human_oversight: set[str] | None = None,
) -> ISO42001OperatingScope:
    # generate_recommendation_letter is in BOTH permitted_use_cases AND
    # human_oversight_required_for — it's allowed but requires human review (A.9.5)
    return ISO42001OperatingScope(
        system_id="test_ai_v1",
        permitted_use_cases=permitted or {
            "read_transcript",
            "summarize_document",
            "answer_question",
            "generate_recommendation_letter",
        },
        prohibited_use_cases=prohibited or {"generate_legal_advice", "make_admissions_decision"},
        deployment_approved=deployment_approved,
        deployment_approver="cto_alice" if deployment_approved else None,
        human_oversight_required_for=human_oversight or {"generate_recommendation_letter"},
    )


def _make_policy(scope: ISO42001OperatingScope | None = None) -> ISO42001GovernancePolicy:
    return ISO42001GovernancePolicy(
        scope=scope or _make_scope(),
        session_id="sess_test_001",
    )


# ---------------------------------------------------------------------------
# ISO42001OperatingScope
# ---------------------------------------------------------------------------


class TestISO42001OperatingScope:
    def test_fields_accessible(self):
        scope = _make_scope()
        assert scope.system_id == "test_ai_v1"
        assert "read_transcript" in scope.permitted_use_cases
        assert "generate_legal_advice" in scope.prohibited_use_cases
        assert "generate_recommendation_letter" in scope.human_oversight_required_for

    def test_deployment_approved_false(self):
        scope = _make_scope(deployment_approved=False)
        assert scope.deployment_approved is False
        assert scope.deployment_approver is None


# ---------------------------------------------------------------------------
# ISO42001GovernancePolicy — evaluate_action
# ---------------------------------------------------------------------------


class TestISO42001GovernancePolicyEvaluate:
    def test_permitted_action_allowed(self):
        policy = _make_policy()
        decision = policy.evaluate_action("read_transcript")
        assert decision.permitted is True
        assert decision.denial_reason is None
        assert decision.human_oversight_required is False

    def test_prohibited_action_denied(self):
        policy = _make_policy()
        decision = policy.evaluate_action("generate_legal_advice")
        assert decision.permitted is False
        assert decision.denial_reason is not None
        assert "prohibited" in decision.denial_reason.lower() or "A.6.2.10" in decision.denial_reason

    def test_action_not_in_permitted_set_denied(self):
        """Action that is neither permitted nor prohibited should be denied (default-deny)."""
        policy = _make_policy()
        decision = policy.evaluate_action("unknown_action_xyz")
        assert decision.permitted is False

    def test_human_oversight_required_action_permitted_with_flag(self):
        policy = _make_policy()
        decision = policy.evaluate_action("generate_recommendation_letter")
        assert decision.permitted is True
        assert decision.human_oversight_required is True

    def test_deployment_gate_blocks_when_not_approved(self):
        """A.6.2.5: Deployment must be approved before any action is allowed."""
        scope = _make_scope(deployment_approved=False)
        policy = _make_policy(scope=scope)
        decision = policy.evaluate_action("read_transcript")  # even permitted actions blocked
        assert decision.permitted is False
        assert "deployment" in decision.denial_reason.lower() or "A.6.2.5" in decision.denial_reason

    def test_evaluate_with_context(self):
        """Context dict should not crash evaluation."""
        policy = _make_policy()
        decision = policy.evaluate_action("read_transcript", context={"session": "abc"})
        assert decision.permitted is True


# ---------------------------------------------------------------------------
# ISO42001PolicyDecision
# ---------------------------------------------------------------------------


class TestISO42001PolicyDecision:
    def test_permitted_decision_attributes(self):
        decision = ISO42001PolicyDecision(
            permitted=True,
            denial_reason=None,
            human_oversight_required=False,
        )
        assert decision.permitted is True
        assert decision.denial_reason is None
        assert decision.human_oversight_required is False

    def test_denied_decision_attributes(self):
        decision = ISO42001PolicyDecision(
            permitted=False,
            denial_reason="Prohibited use case",
            human_oversight_required=False,
        )
        assert decision.permitted is False
        assert "Prohibited" in decision.denial_reason


# ---------------------------------------------------------------------------
# ISO42001DataProvenanceRecord
# ---------------------------------------------------------------------------


class TestISO42001DataProvenanceRecord:
    def test_basic_creation(self):
        record = ISO42001DataProvenanceRecord(
            source_id="src_001",
            source_type="internal_docs",
            lawful_basis="legitimate_interests",
            data_quality_validated=True,
        )
        assert record.source_id == "src_001"
        assert record.source_type == "internal_docs"
        assert record.lawful_basis == "legitimate_interests"
        assert record.data_quality_validated is True

    def test_default_quality_false(self):
        record = ISO42001DataProvenanceRecord(
            source_id="src_002",
            source_type="web_crawl",
            lawful_basis="consent",
        )
        assert record.data_quality_validated is False


# ---------------------------------------------------------------------------
# ISO42001DeploymentRecord
# ---------------------------------------------------------------------------


class TestISO42001DeploymentRecord:
    def test_basic_creation(self):
        record = ISO42001DeploymentRecord(
            system_id="ai_v1",
            system_version="1.0.0",
            approver_id="cto_alice",
            risk_level="high",
            impact_assessment_completed=True,
        )
        assert record.system_id == "ai_v1"
        assert record.system_version == "1.0.0"
        assert record.approver_id == "cto_alice"
        assert record.risk_level == "high"
        assert record.impact_assessment_completed is True

    def test_default_third_party_empty(self):
        record = ISO42001DeploymentRecord(
            system_id="ai_v2",
            system_version="2.0.0",
            approver_id="cto_bob",
            risk_level="low",
            impact_assessment_completed=False,
        )
        assert record.third_party_components == []


# ---------------------------------------------------------------------------
# ISO42001AuditRecord
# ---------------------------------------------------------------------------


class TestISO42001AuditRecord:
    def _make_record(self, permitted: bool = True) -> ISO42001AuditRecord:
        # Directly construct an audit record (as the policy produces internally)
        return ISO42001AuditRecord(
            system_id="test_ai_v1",
            action_name="read_transcript",
            actor_id="advisor_001",
            permitted=permitted,
            denial_reason=None if permitted else "blocked",
            human_oversight_required=False,
            session_id="sess_001",
        )

    def test_to_log_entry_is_valid_json(self):
        record = self._make_record()
        entry = record.to_log_entry()
        parsed = json.loads(entry)
        assert parsed["framework"] == "ISO_IEC_42001_2023"

    def test_to_log_entry_contains_fields(self):
        record = self._make_record()
        parsed = json.loads(record.to_log_entry())
        for key in ("system_id", "action_name", "actor_id", "permitted", "timestamp_utc"):
            assert key in parsed, f"Missing field: {key}"

    def test_content_hash_is_64_hex_chars(self):
        record = self._make_record()
        h = record.content_hash()
        assert len(h) == 64
        int(h, 16)

    def test_content_hash_is_stable(self):
        """Same record produces same hash on repeated calls."""
        record = self._make_record()
        assert record.content_hash() == record.content_hash()

    def test_denied_record_has_reason(self):
        record = self._make_record(permitted=False)
        parsed = json.loads(record.to_log_entry())
        assert parsed["denial_reason"] == "blocked"


# ---------------------------------------------------------------------------
# Integration: ISO42001 as FrameworkGuard in orchestrator
# ---------------------------------------------------------------------------


class TestISO42001OrchestratorIntegration:
    def test_iso42001_guard_plugs_into_orchestrator(self):
        """ISO42001GovernancePolicy can be wrapped as a GovernedActionGuard."""
        from regulated_ai_governance import (
            ActionPolicy,
            FrameworkGuard,
            GovernanceOrchestrator,
            GovernedActionGuard,
        )
        from regulated_ai_governance.policy import PolicyDecision

        class ISO42001Guard(GovernedActionGuard):
            def __init__(self, iso_policy: ISO42001GovernancePolicy) -> None:
                super().__init__(
                    policy=ActionPolicy(allowed_actions=set()),
                    regulation="ISO_42001",
                    actor_id="test_actor",
                )
                self._iso = iso_policy

            def evaluate(self, action_name, context=None):  # type: ignore[override]
                decision = self._iso.evaluate_action(action_name, context=context)
                return PolicyDecision(
                    permitted=decision.permitted,
                    denial_reason=decision.denial_reason,
                )

        scope = _make_scope()
        policy = _make_policy(scope)
        guard = ISO42001Guard(iso_policy=policy)

        orch = GovernanceOrchestrator(
            framework_guards=[FrameworkGuard(regulation="ISO_42001", guard=guard)]
        )

        # Permitted action
        result = orch.guard("read_transcript", execute_fn=lambda: "DATA")
        assert result == "DATA"

        # Prohibited action
        result = orch.guard("generate_legal_advice", execute_fn=lambda: "ADVICE")
        assert "BLOCKED" in result
        assert "ISO_42001" in result
