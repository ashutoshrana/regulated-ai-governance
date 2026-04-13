"""Tests for DORA (EU Digital Operational Resilience Act) governance module."""

from __future__ import annotations

import json

from regulated_ai_governance.regulations.dora import (
    DORA_HIGH_RISK_ICT_ACTIONS,
    DORAICTCapabilityArea,
    DORAICTIncidentRecord,
    DORAICTRiskLevel,
    DORAThirdPartyRecord,
    make_dora_ict_management_policy,
    make_dora_third_party_policy,
)

# ---------------------------------------------------------------------------
# DORAICTRiskLevel
# ---------------------------------------------------------------------------


class TestDORAICTRiskLevel:
    def test_critical_value(self) -> None:
        assert DORAICTRiskLevel.CRITICAL == "critical"

    def test_high_value(self) -> None:
        assert DORAICTRiskLevel.HIGH == "high"

    def test_medium_value(self) -> None:
        assert DORAICTRiskLevel.MEDIUM == "medium"

    def test_low_value(self) -> None:
        assert DORAICTRiskLevel.LOW == "low"

    def test_all_four_levels_defined(self) -> None:
        levels = {r.value for r in DORAICTRiskLevel}
        assert levels == {"critical", "high", "medium", "low"}

    def test_is_string_enum(self) -> None:
        assert isinstance(DORAICTRiskLevel.HIGH, str)


# ---------------------------------------------------------------------------
# DORAICTCapabilityArea
# ---------------------------------------------------------------------------


class TestDORAICTCapabilityArea:
    def test_identify_value(self) -> None:
        assert DORAICTCapabilityArea.IDENTIFY == "identify"

    def test_protect_value(self) -> None:
        assert DORAICTCapabilityArea.PROTECT == "protect"

    def test_detect_value(self) -> None:
        assert DORAICTCapabilityArea.DETECT == "detect"

    def test_respond_value(self) -> None:
        assert DORAICTCapabilityArea.RESPOND == "respond"

    def test_recover_value(self) -> None:
        assert DORAICTCapabilityArea.RECOVER == "recover"

    def test_five_areas_defined(self) -> None:
        areas = {a.value for a in DORAICTCapabilityArea}
        assert areas == {"identify", "protect", "detect", "respond", "recover"}


# ---------------------------------------------------------------------------
# DORAThirdPartyRecord
# ---------------------------------------------------------------------------


class TestDORAThirdPartyRecord:
    def _make_record(self) -> DORAThirdPartyRecord:
        return DORAThirdPartyRecord(
            provider_id="prov-001",
            provider_name="CloudInfra Ltd",
            risk_level=DORAICTRiskLevel.HIGH,
            assessed=True,
            contract_id="CTR-2025-001",
            assessment_date="2025-03-15",
        )

    def test_provider_id_stored(self) -> None:
        rec = self._make_record()
        assert rec.provider_id == "prov-001"

    def test_provider_name_stored(self) -> None:
        rec = self._make_record()
        assert rec.provider_name == "CloudInfra Ltd"

    def test_risk_level_stored(self) -> None:
        rec = self._make_record()
        assert rec.risk_level == DORAICTRiskLevel.HIGH

    def test_assessed_flag(self) -> None:
        rec = self._make_record()
        assert rec.assessed is True

    def test_contract_id_default_empty(self) -> None:
        rec = DORAThirdPartyRecord(provider_id="p", provider_name="P", risk_level=DORAICTRiskLevel.LOW, assessed=False)
        assert rec.contract_id == ""

    def test_assessment_date_default_empty(self) -> None:
        rec = DORAThirdPartyRecord(provider_id="p", provider_name="P", risk_level=DORAICTRiskLevel.LOW, assessed=False)
        assert rec.assessment_date == ""

    def test_contract_id_and_date_stored(self) -> None:
        rec = self._make_record()
        assert rec.contract_id == "CTR-2025-001"
        assert rec.assessment_date == "2025-03-15"


# ---------------------------------------------------------------------------
# DORAICTIncidentRecord
# ---------------------------------------------------------------------------


class TestDORAICTIncidentRecord:
    def _make_incident(self) -> DORAICTIncidentRecord:
        return DORAICTIncidentRecord(
            incident_id="INC-2025-042",
            classification="major",
            affected_services=["payment_processing", "customer_portal"],
            reported_to_authority=True,
            timestamp_utc="2025-06-01T10:30:00Z",
        )

    def test_to_log_entry_is_json(self) -> None:
        inc = self._make_incident()
        entry = inc.to_log_entry()
        parsed = json.loads(entry)
        assert isinstance(parsed, dict)

    def test_framework_field(self) -> None:
        inc = self._make_incident()
        parsed = json.loads(inc.to_log_entry())
        assert parsed["framework"] == "DORA_EU_2022_2554"

    def test_record_type_field(self) -> None:
        inc = self._make_incident()
        parsed = json.loads(inc.to_log_entry())
        assert parsed["record_type"] == "ict_incident"

    def test_incident_id_in_log(self) -> None:
        inc = self._make_incident()
        parsed = json.loads(inc.to_log_entry())
        assert parsed["incident_id"] == "INC-2025-042"

    def test_classification_in_log(self) -> None:
        inc = self._make_incident()
        parsed = json.loads(inc.to_log_entry())
        assert parsed["classification"] == "major"

    def test_affected_services_sorted(self) -> None:
        inc = self._make_incident()
        parsed = json.loads(inc.to_log_entry())
        assert parsed["affected_services"] == sorted(["payment_processing", "customer_portal"])

    def test_reported_to_authority_in_log(self) -> None:
        inc = self._make_incident()
        parsed = json.loads(inc.to_log_entry())
        assert parsed["reported_to_authority"] is True

    def test_content_hash_is_hex_string(self) -> None:
        inc = self._make_incident()
        h = inc.content_hash()
        assert len(h) == 64
        int(h, 16)  # should not raise — valid hex

    def test_content_hash_stability(self) -> None:
        inc = self._make_incident()
        assert inc.content_hash() == inc.content_hash()

    def test_content_hash_changes_with_data(self) -> None:
        inc1 = self._make_incident()
        inc2 = DORAICTIncidentRecord(
            incident_id="INC-2025-043",
            classification="standard",
            affected_services=["login_service"],
            reported_to_authority=False,
            timestamp_utc="2025-06-02T09:00:00Z",
        )
        assert inc1.content_hash() != inc2.content_hash()


# ---------------------------------------------------------------------------
# DORA_HIGH_RISK_ICT_ACTIONS
# ---------------------------------------------------------------------------


class TestDORAHighRiskActions:
    def test_is_frozenset(self) -> None:
        assert isinstance(DORA_HIGH_RISK_ICT_ACTIONS, frozenset)

    def test_bypass_ict_controls_present(self) -> None:
        assert "bypass_ict_controls" in DORA_HIGH_RISK_ICT_ACTIONS

    def test_skip_backup_present(self) -> None:
        assert "skip_backup_procedure" in DORA_HIGH_RISK_ICT_ACTIONS

    def test_disable_monitoring_present(self) -> None:
        assert "disable_monitoring" in DORA_HIGH_RISK_ICT_ACTIONS

    def test_at_least_ten_actions(self) -> None:
        assert len(DORA_HIGH_RISK_ICT_ACTIONS) >= 10


# ---------------------------------------------------------------------------
# make_dora_ict_management_policy
# ---------------------------------------------------------------------------


class TestDORAICTManagementPolicy:
    def test_permitted_action_allowed(self) -> None:
        policy = make_dora_ict_management_policy()
        permitted, _ = policy.permits("log_ict_event")
        assert permitted

    def test_bypass_ict_controls_denied(self) -> None:
        policy = make_dora_ict_management_policy()
        permitted, reason = policy.permits("bypass_ict_controls")
        assert not permitted
        assert "bypass_ict_controls" in reason

    def test_skip_backup_denied(self) -> None:
        policy = make_dora_ict_management_policy()
        permitted, _ = policy.permits("skip_backup_procedure")
        assert not permitted

    def test_disable_monitoring_denied(self) -> None:
        policy = make_dora_ict_management_policy()
        permitted, _ = policy.permits("disable_monitoring")
        assert not permitted

    def test_unvalidated_third_party_access_denied(self) -> None:
        policy = make_dora_ict_management_policy()
        permitted, _ = policy.permits("unvalidated_third_party_access")
        assert not permitted

    def test_incident_escalation_rule_present(self) -> None:
        policy = make_dora_ict_management_policy()
        rule = policy.escalation_for("trigger_incident_response")
        assert rule is not None

    def test_escalation_target_default(self) -> None:
        policy = make_dora_ict_management_policy()
        rule = policy.escalation_for("trigger_incident_response")
        assert rule is not None
        assert "ict_risk" in rule.escalate_to or "team" in rule.escalate_to

    def test_custom_escalation_target(self) -> None:
        policy = make_dora_ict_management_policy(escalate_incidents_to="ciso_team")
        rule = policy.escalation_for("trigger_incident_response")
        assert rule is not None
        assert rule.escalate_to == "ciso_team"

    def test_unknown_action_denied(self) -> None:
        policy = make_dora_ict_management_policy()
        permitted, _ = policy.permits("unregistered_ict_action")
        assert not permitted

    def test_custom_allowed_actions(self) -> None:
        policy = make_dora_ict_management_policy(allowed_actions={"custom_ict_read"})
        permitted, _ = policy.permits("custom_ict_read")
        assert permitted


# ---------------------------------------------------------------------------
# make_dora_third_party_policy
# ---------------------------------------------------------------------------


class TestDORAThirdPartyPolicy:
    def test_read_provider_register_allowed(self) -> None:
        policy = make_dora_third_party_policy()
        permitted, _ = policy.permits("read_provider_register")
        assert permitted

    def test_unassessed_provider_access_denied(self) -> None:
        policy = make_dora_third_party_policy()
        permitted, reason = policy.permits("access_via_unassessed_provider")
        assert not permitted
        assert "access_via_unassessed_provider" in reason

    def test_unauthorized_provider_integration_denied(self) -> None:
        policy = make_dora_third_party_policy()
        permitted, _ = policy.permits("unauthorized_provider_integration")
        assert not permitted

    def test_escalation_rule_present(self) -> None:
        policy = make_dora_third_party_policy()
        rule = policy.escalation_for("read_provider_register")
        assert rule is not None

    def test_custom_escalation_target(self) -> None:
        policy = make_dora_third_party_policy(escalate_to="vendor_risk_committee")
        rule = policy.escalation_for("update_provider_assessment")
        assert rule is not None
        assert rule.escalate_to == "vendor_risk_committee"

    def test_default_escalation_target(self) -> None:
        policy = make_dora_third_party_policy()
        rule = policy.escalation_for("read_provider_register")
        assert rule is not None
        assert "third_party" in rule.escalate_to or "risk" in rule.escalate_to

    def test_unknown_action_denied(self) -> None:
        policy = make_dora_third_party_policy()
        permitted, _ = policy.permits("unregistered_provider_action")
        assert not permitted
