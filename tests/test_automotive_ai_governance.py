"""
Tests for 11_automotive_ai_governance.py

Covers SafetyClassifier, R155CybersecFilter, R156SUMSFilter,
NHTSAAVFilter, and AutomotiveAIOrchestrator.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Module loading helper (frozen-dataclass fix for Python 3.14+)
# ---------------------------------------------------------------------------

_MODULE_NAME = "automotive_ai_governance"
_MODULE_PATH = (
    Path(__file__).parent.parent / "examples" / "11_automotive_ai_governance.py"
)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_mod = _load_module()

ASILLevel = _mod.ASILLevel
SAELevel = _mod.SAELevel
AISystemFunction = _mod.AISystemFunction
GovernanceOutcome = _mod.GovernanceOutcome
CybersecurityContext = _mod.CybersecurityContext
SoftwareUpdateContext = _mod.SoftwareUpdateContext
NHTSAAVContext = _mod.NHTSAAVContext
SafetyClassifier = _mod.SafetyClassifier
R155CybersecFilter = _mod.R155CybersecFilter
R156SUMSFilter = _mod.R156SUMSFilter
NHTSAAVFilter = _mod.NHTSAAVFilter
AutomotiveAIOrchestrator = _mod.AutomotiveAIOrchestrator


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def compliant_cybersec_ctx() -> CybersecurityContext:
    return CybersecurityContext(
        csms_certified=True,
        csms_certificate_id="CERT-TEST-001",
        threat_assessment_current=True,
        known_vulnerabilities_mitigated=True,
        intrusion_detection_active=True,
        incident_response_tested=True,
        security_logging_enabled=True,
    )


@pytest.fixture()
def compliant_sums_ctx() -> SoftwareUpdateContext:
    return SoftwareUpdateContext(
        sums_documented=True,
        update_cryptographically_signed=True,
        rollback_capability_present=True,
        over_the_air=False,
        driver_consent_obtained=True,
        installation_state_verified=True,
        asil_change_requires_reapproval=False,
    )


@pytest.fixture()
def compliant_nhtsa_ctx_l2() -> NHTSAAVContext:
    return NHTSAAVContext(
        sae_level=SAELevel.L2,
        odd_documented=True,
        safety_performance_tested=True,
        cybersecurity_compliance=True,
        crash_avoidance_validated=True,
        sgo_reporting_enabled=True,
        fallback_minimal_risk_condition=False,   # L2: driver in control
        human_machine_interface_tested=True,
        data_recording_capability=True,
    )


@pytest.fixture()
def compliant_nhtsa_ctx_l4() -> NHTSAAVContext:
    return NHTSAAVContext(
        sae_level=SAELevel.L4,
        odd_documented=True,
        safety_performance_tested=True,
        cybersecurity_compliance=True,
        crash_avoidance_validated=True,
        sgo_reporting_enabled=True,
        fallback_minimal_risk_condition=True,
        human_machine_interface_tested=True,
        data_recording_capability=True,
    )


# ---------------------------------------------------------------------------
# SafetyClassifier
# ---------------------------------------------------------------------------

class TestSafetyClassifier:

    def test_emergency_braking_is_asil_d(self) -> None:
        sc = SafetyClassifier()
        assert sc.classify(AISystemFunction.EMERGENCY_BRAKING) == ASILLevel.D

    def test_steering_control_is_asil_d(self) -> None:
        sc = SafetyClassifier()
        assert sc.classify(AISystemFunction.STEERING_CONTROL) == ASILLevel.D

    def test_lane_keep_is_asil_b(self) -> None:
        sc = SafetyClassifier()
        assert sc.classify(AISystemFunction.LANE_KEEP_ASSIST) == ASILLevel.B

    def test_infotainment_is_qm(self) -> None:
        sc = SafetyClassifier()
        assert sc.classify(AISystemFunction.INFOTAINMENT) == ASILLevel.QM

    def test_path_planning_is_asil_c(self) -> None:
        sc = SafetyClassifier()
        assert sc.classify(AISystemFunction.PATH_PLANNING) == ASILLevel.C

    def test_ota_update_is_asil_d(self) -> None:
        """OTA update execution is treated as ASIL D per ISO 26262-8 §7."""
        sc = SafetyClassifier()
        assert sc.classify(AISystemFunction.OTA_UPDATE_EXECUTION) == ASILLevel.D

    def test_asil_b_requirements_met_with_all_activities(self) -> None:
        sc = SafetyClassifier()
        activities = ["unit_testing", "code_review", "fmea_complete", "hara_complete"]
        met, missing = sc.verify_requirements_met(AISystemFunction.LANE_KEEP_ASSIST, activities)
        assert met
        assert missing == []

    def test_asil_b_fails_without_fmea(self) -> None:
        sc = SafetyClassifier()
        activities = ["unit_testing", "code_review"]
        met, missing = sc.verify_requirements_met(AISystemFunction.LANE_KEEP_ASSIST, activities)
        assert not met
        assert "fmea_complete" in missing
        assert "hara_complete" in missing

    def test_asil_d_requires_formal_verification(self) -> None:
        sc = SafetyClassifier()
        # Provide all but formal_verification
        activities = [
            "unit_testing", "code_review", "fmea_complete", "hara_complete",
            "independent_safety_assessment", "safety_case_documented",
            "safety_element_out_of_context",
        ]
        met, missing = sc.verify_requirements_met(AISystemFunction.EMERGENCY_BRAKING, activities)
        assert not met
        assert "formal_verification" in missing

    def test_qm_function_has_no_requirements(self) -> None:
        sc = SafetyClassifier()
        met, missing = sc.verify_requirements_met(AISystemFunction.INFOTAINMENT, [])
        assert met
        assert missing == []


# ---------------------------------------------------------------------------
# R155CybersecFilter
# ---------------------------------------------------------------------------

class TestR155CybersecFilter:

    def _filter(self) -> R155CybersecFilter:
        return R155CybersecFilter()

    def test_fully_compliant_returns_allow(
        self, compliant_cybersec_ctx: CybersecurityContext
    ) -> None:
        outcome, violations = self._filter().evaluate(compliant_cybersec_ctx)
        assert outcome == GovernanceOutcome.ALLOW
        assert violations == []

    def test_no_csms_cert_denies(self, compliant_cybersec_ctx: CybersecurityContext) -> None:
        ctx = CybersecurityContext(
            **{**compliant_cybersec_ctx.__dict__, "csms_certified": False}
        )
        outcome, violations = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.DENY
        assert any("§7.3.1" in v for v in violations)

    def test_unmitigated_vulnerabilities_denies(
        self, compliant_cybersec_ctx: CybersecurityContext
    ) -> None:
        ctx = CybersecurityContext(
            **{**compliant_cybersec_ctx.__dict__, "known_vulnerabilities_mitigated": False}
        )
        outcome, violations = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.DENY
        assert any("§7.3.3" in v for v in violations)

    def test_missing_ids_allows_with_conditions(
        self, compliant_cybersec_ctx: CybersecurityContext
    ) -> None:
        ctx = CybersecurityContext(
            **{**compliant_cybersec_ctx.__dict__, "intrusion_detection_active": False}
        )
        outcome, violations = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert any("§7.3.5" in v for v in violations)

    def test_missing_logging_allows_with_conditions(
        self, compliant_cybersec_ctx: CybersecurityContext
    ) -> None:
        ctx = CybersecurityContext(
            **{**compliant_cybersec_ctx.__dict__, "security_logging_enabled": False}
        )
        outcome, violations = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert any("§7.3.7" in v for v in violations)


# ---------------------------------------------------------------------------
# R156SUMSFilter
# ---------------------------------------------------------------------------

class TestR156SUMSFilter:

    def _filter(self) -> R156SUMSFilter:
        return R156SUMSFilter()

    def test_fully_compliant_returns_allow(
        self, compliant_sums_ctx: SoftwareUpdateContext
    ) -> None:
        outcome, violations = self._filter().evaluate(compliant_sums_ctx, ASILLevel.B)
        assert outcome == GovernanceOutcome.ALLOW
        assert violations == []

    def test_unsigned_update_denies(
        self, compliant_sums_ctx: SoftwareUpdateContext
    ) -> None:
        ctx = SoftwareUpdateContext(
            **{**compliant_sums_ctx.__dict__, "update_cryptographically_signed": False}
        )
        outcome, violations = self._filter().evaluate(ctx, ASILLevel.B)
        assert outcome == GovernanceOutcome.DENY
        assert any("§7.2.2" in v for v in violations)

    def test_no_rollback_denies(self, compliant_sums_ctx: SoftwareUpdateContext) -> None:
        ctx = SoftwareUpdateContext(
            **{**compliant_sums_ctx.__dict__, "rollback_capability_present": False}
        )
        outcome, violations = self._filter().evaluate(ctx, ASILLevel.B)
        assert outcome == GovernanceOutcome.DENY
        assert any("§7.2.4" in v for v in violations)

    def test_asil_d_any_violation_denies(
        self, compliant_sums_ctx: SoftwareUpdateContext
    ) -> None:
        """For ASIL D, even conditions become DENY."""
        ctx = SoftwareUpdateContext(
            **{**compliant_sums_ctx.__dict__,
               "over_the_air": True,
               "driver_consent_obtained": False}
        )
        outcome, violations = self._filter().evaluate(ctx, ASILLevel.D)
        assert outcome == GovernanceOutcome.DENY

    def test_ota_without_consent_allows_with_conditions_for_asil_b(
        self, compliant_sums_ctx: SoftwareUpdateContext
    ) -> None:
        ctx = SoftwareUpdateContext(
            **{**compliant_sums_ctx.__dict__,
               "over_the_air": True,
               "driver_consent_obtained": False}
        )
        outcome, violations = self._filter().evaluate(ctx, ASILLevel.B)
        assert outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert any("§7.2.6" in v for v in violations)

    def test_asil_change_requires_reapproval_flagged(
        self, compliant_sums_ctx: SoftwareUpdateContext
    ) -> None:
        ctx = SoftwareUpdateContext(
            **{**compliant_sums_ctx.__dict__, "asil_change_requires_reapproval": True}
        )
        outcome, violations = self._filter().evaluate(ctx, ASILLevel.B)
        assert outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert any("re-evaluation" in v for v in violations)

    def test_no_sums_documented_denies(
        self, compliant_sums_ctx: SoftwareUpdateContext
    ) -> None:
        ctx = SoftwareUpdateContext(
            **{**compliant_sums_ctx.__dict__, "sums_documented": False}
        )
        outcome, violations = self._filter().evaluate(ctx, ASILLevel.B)
        assert outcome == GovernanceOutcome.DENY
        assert any("§7.1.1" in v for v in violations)


# ---------------------------------------------------------------------------
# NHTSAAVFilter
# ---------------------------------------------------------------------------

class TestNHTSAAVFilter:

    def _filter(self) -> NHTSAAVFilter:
        return NHTSAAVFilter()

    def test_l2_fully_compliant_returns_allow(
        self, compliant_nhtsa_ctx_l2: NHTSAAVContext
    ) -> None:
        outcome, findings = self._filter().evaluate(compliant_nhtsa_ctx_l2)
        assert outcome == GovernanceOutcome.ALLOW
        assert findings == []

    def test_l4_fully_compliant_returns_allow(
        self, compliant_nhtsa_ctx_l4: NHTSAAVContext
    ) -> None:
        outcome, findings = self._filter().evaluate(compliant_nhtsa_ctx_l4)
        assert outcome == GovernanceOutcome.ALLOW
        assert findings == []

    def test_missing_odd_denies(self, compliant_nhtsa_ctx_l2: NHTSAAVContext) -> None:
        ctx = NHTSAAVContext(**{**compliant_nhtsa_ctx_l2.__dict__, "odd_documented": False})
        outcome, findings = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.DENY
        assert any("ODD" in f for f in findings)

    def test_l3_without_mrc_denies(self, compliant_nhtsa_ctx_l4: NHTSAAVContext) -> None:
        """L3 requires MRC; L4 also requires it."""
        ctx = NHTSAAVContext(
            **{**compliant_nhtsa_ctx_l4.__dict__,
               "sae_level": SAELevel.L3,
               "fallback_minimal_risk_condition": False}
        )
        outcome, findings = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.DENY
        assert any("MRC" in f or "Minimal Risk Condition" in f for f in findings)

    def test_l2_without_mrc_allowed(self, compliant_nhtsa_ctx_l2: NHTSAAVContext) -> None:
        """L2: driver still in control; MRC is not required."""
        ctx = NHTSAAVContext(
            **{**compliant_nhtsa_ctx_l2.__dict__, "fallback_minimal_risk_condition": False}
        )
        outcome, findings = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.ALLOW

    def test_l4_without_sgo_reporting_allows_with_conditions(
        self, compliant_nhtsa_ctx_l4: NHTSAAVContext
    ) -> None:
        ctx = NHTSAAVContext(
            **{**compliant_nhtsa_ctx_l4.__dict__, "sgo_reporting_enabled": False}
        )
        outcome, findings = self._filter().evaluate(ctx)
        assert outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert any("SGO" in f for f in findings)

    def test_l0_without_sgo_not_flagged(self) -> None:
        """L0 is not covered by SGO 2021-01."""
        ctx = NHTSAAVContext(
            sae_level=SAELevel.L0,
            odd_documented=True,
            safety_performance_tested=True,
            cybersecurity_compliance=True,
            crash_avoidance_validated=True,
            sgo_reporting_enabled=False,
            fallback_minimal_risk_condition=False,
            human_machine_interface_tested=True,
            data_recording_capability=True,
        )
        outcome, findings = NHTSAAVFilter().evaluate(ctx)
        assert outcome == GovernanceOutcome.ALLOW


# ---------------------------------------------------------------------------
# AutomotiveAIOrchestrator — integration tests
# ---------------------------------------------------------------------------

class TestAutomotiveAIOrchestrator:

    def _orch(self) -> AutomotiveAIOrchestrator:
        return AutomotiveAIOrchestrator()

    def _asil_b_activities(self) -> list[str]:
        return ["unit_testing", "code_review", "fmea_complete", "hara_complete"]

    def _asil_d_activities(self) -> list[str]:
        return [
            "unit_testing", "code_review", "fmea_complete", "hara_complete",
            "independent_safety_assessment", "safety_case_documented",
            "formal_verification", "safety_element_out_of_context",
        ]

    def test_scenario_a_adas_fully_compliant(
        self,
        compliant_cybersec_ctx: CybersecurityContext,
        compliant_sums_ctx: SoftwareUpdateContext,
        compliant_nhtsa_ctx_l2: NHTSAAVContext,
    ) -> None:
        audit = self._orch().evaluate(
            system_name="TestLKA",
            function=AISystemFunction.LANE_KEEP_ASSIST,
            sae_level=SAELevel.L2,
            completed_safety_activities=self._asil_b_activities(),
            cybersec_ctx=compliant_cybersec_ctx,
            sums_ctx=compliant_sums_ctx,
            nhtsa_ctx=compliant_nhtsa_ctx_l2,
        )
        assert audit.final_outcome == GovernanceOutcome.ALLOW
        assert audit.asil_requirements_met
        assert audit.denial_reasons == []
        assert audit.conditions == []

    def test_r155_deny_blocks_entire_deployment(
        self,
        compliant_sums_ctx: SoftwareUpdateContext,
        compliant_nhtsa_ctx_l2: NHTSAAVContext,
    ) -> None:
        bad_csms = CybersecurityContext(
            csms_certified=False,
            csms_certificate_id="",
            threat_assessment_current=True,
            known_vulnerabilities_mitigated=True,
            intrusion_detection_active=True,
            incident_response_tested=True,
            security_logging_enabled=True,
        )
        audit = self._orch().evaluate(
            system_name="TestSystem",
            function=AISystemFunction.LANE_KEEP_ASSIST,
            sae_level=SAELevel.L2,
            completed_safety_activities=self._asil_b_activities(),
            cybersec_ctx=bad_csms,
            sums_ctx=compliant_sums_ctx,
            nhtsa_ctx=compliant_nhtsa_ctx_l2,
        )
        assert audit.final_outcome == GovernanceOutcome.DENY
        assert any("§7.3.1" in r for r in audit.denial_reasons)

    def test_asil_gap_denies_deployment(
        self,
        compliant_cybersec_ctx: CybersecurityContext,
        compliant_sums_ctx: SoftwareUpdateContext,
        compliant_nhtsa_ctx_l2: NHTSAAVContext,
    ) -> None:
        audit = self._orch().evaluate(
            system_name="TestSystem",
            function=AISystemFunction.LANE_KEEP_ASSIST,
            sae_level=SAELevel.L2,
            completed_safety_activities=["unit_testing"],  # Missing fmea, hara, etc.
            cybersec_ctx=compliant_cybersec_ctx,
            sums_ctx=compliant_sums_ctx,
            nhtsa_ctx=compliant_nhtsa_ctx_l2,
        )
        assert audit.final_outcome == GovernanceOutcome.DENY
        assert not audit.asil_requirements_met
        assert len(audit.missing_asil_activities) > 0

    def test_r156_deny_blocks_ota_deployment(
        self,
        compliant_cybersec_ctx: CybersecurityContext,
        compliant_nhtsa_ctx_l2: NHTSAAVContext,
    ) -> None:
        bad_sums = SoftwareUpdateContext(
            sums_documented=True,
            update_cryptographically_signed=False,
            rollback_capability_present=False,
            over_the_air=True,
            driver_consent_obtained=True,
            installation_state_verified=True,
        )
        audit = self._orch().evaluate(
            system_name="TestOTA",
            function=AISystemFunction.OTA_UPDATE_EXECUTION,
            sae_level=SAELevel.L2,
            completed_safety_activities=self._asil_d_activities(),
            cybersec_ctx=compliant_cybersec_ctx,
            sums_ctx=bad_sums,
            nhtsa_ctx=compliant_nhtsa_ctx_l2,
        )
        assert audit.final_outcome == GovernanceOutcome.DENY

    def test_sgo_condition_surfaced_in_audit(
        self,
        compliant_cybersec_ctx: CybersecurityContext,
        compliant_sums_ctx: SoftwareUpdateContext,
    ) -> None:
        nhtsa_no_sgo = NHTSAAVContext(
            sae_level=SAELevel.L4,
            odd_documented=True,
            safety_performance_tested=True,
            cybersecurity_compliance=True,
            crash_avoidance_validated=True,
            sgo_reporting_enabled=False,
            fallback_minimal_risk_condition=True,
            human_machine_interface_tested=True,
            data_recording_capability=True,
        )
        audit = self._orch().evaluate(
            system_name="TestRobofleet",
            function=AISystemFunction.MOTION_CONTROL,
            sae_level=SAELevel.L4,
            completed_safety_activities=self._asil_d_activities(),
            cybersec_ctx=compliant_cybersec_ctx,
            sums_ctx=compliant_sums_ctx,
            nhtsa_ctx=nhtsa_no_sgo,
        )
        assert audit.final_outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert any("SGO" in c for c in audit.conditions)

    def test_audit_record_contains_system_metadata(
        self,
        compliant_cybersec_ctx: CybersecurityContext,
        compliant_sums_ctx: SoftwareUpdateContext,
        compliant_nhtsa_ctx_l2: NHTSAAVContext,
    ) -> None:
        audit = self._orch().evaluate(
            system_name="AuditMetaTest",
            function=AISystemFunction.LANE_KEEP_ASSIST,
            sae_level=SAELevel.L2,
            completed_safety_activities=self._asil_b_activities(),
            cybersec_ctx=compliant_cybersec_ctx,
            sums_ctx=compliant_sums_ctx,
            nhtsa_ctx=compliant_nhtsa_ctx_l2,
        )
        assert audit.system_name == "AuditMetaTest"
        assert audit.function == AISystemFunction.LANE_KEEP_ASSIST.value
        assert audit.asil_level == ASILLevel.B.value
        assert audit.audit_id  # non-empty UUID

    def test_multiple_violations_all_collected(
        self,
        compliant_sums_ctx: SoftwareUpdateContext,
    ) -> None:
        """ASIL gap + R155 DENY + NHTSA DENY should all be in denial_reasons."""
        bad_csms = CybersecurityContext(
            csms_certified=False,
            csms_certificate_id="",
            threat_assessment_current=False,
            known_vulnerabilities_mitigated=False,
            intrusion_detection_active=False,
            incident_response_tested=False,
            security_logging_enabled=False,
        )
        bad_nhtsa = NHTSAAVContext(
            sae_level=SAELevel.L4,
            odd_documented=False,
            safety_performance_tested=False,
            cybersecurity_compliance=False,
            crash_avoidance_validated=False,
            sgo_reporting_enabled=False,
            fallback_minimal_risk_condition=False,
            human_machine_interface_tested=False,
            data_recording_capability=False,
        )
        audit = self._orch().evaluate(
            system_name="MaxViolations",
            function=AISystemFunction.MOTION_CONTROL,
            sae_level=SAELevel.L4,
            completed_safety_activities=[],  # Missing all ASIL D activities
            cybersec_ctx=bad_csms,
            sums_ctx=compliant_sums_ctx,
            nhtsa_ctx=bad_nhtsa,
        )
        assert audit.final_outcome == GovernanceOutcome.DENY
        # All three layers should have contributed violations
        assert not audit.asil_requirements_met
        assert audit.r155_outcome == GovernanceOutcome.DENY.value
        assert audit.nhtsa_outcome == GovernanceOutcome.DENY.value
        assert len(audit.denial_reasons) >= 3
