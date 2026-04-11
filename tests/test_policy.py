"""Tests for ActionPolicy and EscalationRule."""

from __future__ import annotations

import pytest

from regulated_ai_governance.policy import ActionPolicy, EscalationRule, PolicyDecision


class TestEscalationRule:
    def test_matches_exact_action_name(self):
        rule = EscalationRule("export", "export_pdf", "compliance")
        assert rule.matches("export_pdf") is True

    def test_matches_substring_in_action_name(self):
        rule = EscalationRule("export", "export", "compliance")
        assert rule.matches("export_student_records") is True

    def test_no_match_unrelated_action(self):
        rule = EscalationRule("export", "export", "compliance")
        assert rule.matches("read_transcript") is False

    def test_empty_pattern_matches_all(self):
        rule = EscalationRule("catch_all", "", "compliance")
        assert rule.matches("anything") is True
        assert rule.matches("read_record") is True
        assert rule.matches("export_data") is True


class TestActionPolicy:
    def test_permits_action_in_allowed_set(self):
        policy = ActionPolicy(allowed_actions={"read_transcript", "read_enrollment"})
        permitted, reason = policy.permits("read_transcript")
        assert permitted is True
        assert reason == ""

    def test_denies_action_not_in_allowed_set(self):
        policy = ActionPolicy(allowed_actions={"read_transcript"})
        permitted, reason = policy.permits("export_records")
        assert permitted is False
        assert "export_records" in reason

    def test_empty_allowed_set_permits_all(self):
        policy = ActionPolicy(allowed_actions=set())
        permitted, _ = policy.permits("anything")
        assert permitted is True

    def test_require_all_allowed_false_permits_unlisted(self):
        policy = ActionPolicy(
            allowed_actions={"read_transcript"},
            require_all_allowed=False,
        )
        permitted, _ = policy.permits("export_records")
        assert permitted is True

    def test_denied_actions_take_precedence_over_allowed(self):
        policy = ActionPolicy(
            allowed_actions={"read_transcript"},
            denied_actions={"read_transcript"},
        )
        permitted, reason = policy.permits("read_transcript")
        assert permitted is False
        assert "explicitly denied" in reason

    def test_escalation_for_matching_pattern(self):
        rule = EscalationRule("export_attempt", "export", "compliance_officer")
        policy = ActionPolicy(escalation_rules=[rule])
        result = policy.escalation_for("export_student_records", {})
        assert result is not None
        assert result.escalate_to == "compliance_officer"

    def test_escalation_for_no_match_returns_none(self):
        rule = EscalationRule("export_attempt", "export", "compliance_officer")
        policy = ActionPolicy(escalation_rules=[rule])
        assert policy.escalation_for("read_transcript", {}) is None

    def test_first_matching_escalation_rule_is_returned(self):
        rules = [
            EscalationRule("rule_a", "export", "target_a"),
            EscalationRule("rule_b", "export", "target_b"),
        ]
        policy = ActionPolicy(escalation_rules=rules)
        result = policy.escalation_for("export_data", {})
        assert result.escalate_to == "target_a"


class TestPolicyDecision:
    def test_permitted_decision(self):
        decision = PolicyDecision(permitted=True)
        assert decision.permitted is True
        assert decision.denial_reason is None
        assert decision.escalation is None

    def test_denied_decision_with_reason(self):
        decision = PolicyDecision(permitted=False, denial_reason="Not allowed")
        assert decision.permitted is False
        assert decision.denial_reason == "Not allowed"

    def test_escalated_decision(self):
        rule = EscalationRule("e", "p", "target")
        decision = PolicyDecision(permitted=True, escalation=rule)
        assert decision.escalation.escalate_to == "target"
