"""
Tests for 40_governance_framework_auditor.py

Covers GovernanceFrameworkConfig, AuditFinding, GovernanceAuditReport, and
GovernanceFrameworkAuditor across all six framework domains (37 controls total).

~40 test cases using pytest and importlib loading pattern.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

# ---------------------------------------------------------------------------
# Load the example module via importlib
# ---------------------------------------------------------------------------

_MOD_NAME = "governance_framework_auditor_40"
_EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "examples", "40_governance_framework_auditor.py")

spec = importlib.util.spec_from_file_location(_MOD_NAME, _EXAMPLE_PATH)
mod = types.ModuleType(_MOD_NAME)
sys.modules[_MOD_NAME] = mod
spec.loader.exec_module(mod)  # type: ignore[union-attr]

GovernanceFrameworkConfig = mod.GovernanceFrameworkConfig
AuditFinding = mod.AuditFinding
GovernanceAuditReport = mod.GovernanceAuditReport
GovernanceFrameworkAuditor = mod.GovernanceFrameworkAuditor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _all_off_config(**overrides) -> GovernanceFrameworkConfig:
    """Return a fully-default (all-False) GovernanceFrameworkConfig with optional overrides."""
    return GovernanceFrameworkConfig(**overrides)


def _all_on_config() -> GovernanceFrameworkConfig:
    """Return a GovernanceFrameworkConfig with every control enabled."""
    return GovernanceFrameworkConfig(
        system_id="fully-governed",
        owasp_llm_prompt_injection_controls=True,
        owasp_llm_insecure_output_handling=True,
        owasp_llm_supply_chain_controls=True,
        owasp_llm_data_poisoning_controls=True,
        owasp_llm_sensitive_info_controls=True,
        owasp_llm_vector_weakness_controls=True,
        owasp_llm_misinformation_controls=True,
        owasp_llm_unlimited_consumption_controls=True,
        owasp_asi_goal_hijack_controls=True,
        owasp_asi_tool_misuse_controls=True,
        owasp_asi_memory_poisoning_controls=True,
        owasp_asi_trust_boundary_controls=True,
        nist_map_function_implemented=True,
        nist_measure_function_implemented=True,
        nist_manage_function_implemented=True,
        nist_govern_function_implemented=True,
        nist_genai_testing_implemented=True,
        iso_ai_policy_defined=True,
        iso_ai_risk_assessment=True,
        iso_ai_objectives_set=True,
        iso_ai_competence_managed=True,
        iso_ai_documented_info=True,
        iso_ai_operational_controls=True,
        iso_ai_monitoring=True,
        iso_ai_internal_audit=True,
        iso_ai_management_review=True,
        mitre_recon_detection=True,
        mitre_poisoning_detection=True,
        mitre_extraction_controls=True,
        mitre_prompt_injection_detection=True,
        mitre_tool_invocation_controls=True,
        mitre_rag_db_controls=True,
        csa_atf_sandbox_controls=True,
        csa_atf_controlled_controls=True,
        csa_atf_trusted_controls=True,
        csa_atf_autonomous_controls=True,
        csa_atf_continuous_assessment=True,
    )


def _audit(config: GovernanceFrameworkConfig) -> GovernanceAuditReport:
    return GovernanceFrameworkAuditor().audit(config)


def _find(report: GovernanceAuditReport, control_id: str) -> AuditFinding:
    for f in report.findings:
        if f.control_id == control_id:
            return f
    raise AssertionError(f"Control {control_id!r} not found in findings")


# ---------------------------------------------------------------------------
# GovernanceFrameworkConfig defaults
# ---------------------------------------------------------------------------


class TestGovernanceFrameworkConfigDefaults:
    def test_system_id_default(self):
        assert GovernanceFrameworkConfig().system_id == "ai-governance-system"

    def test_all_bool_fields_default_false(self):
        cfg = GovernanceFrameworkConfig()
        bool_fields = [
            "owasp_llm_prompt_injection_controls",
            "owasp_llm_insecure_output_handling",
            "owasp_llm_supply_chain_controls",
            "owasp_llm_data_poisoning_controls",
            "owasp_llm_sensitive_info_controls",
            "owasp_llm_vector_weakness_controls",
            "owasp_llm_misinformation_controls",
            "owasp_llm_unlimited_consumption_controls",
            "owasp_asi_goal_hijack_controls",
            "owasp_asi_tool_misuse_controls",
            "owasp_asi_memory_poisoning_controls",
            "owasp_asi_trust_boundary_controls",
            "nist_map_function_implemented",
            "nist_measure_function_implemented",
            "nist_manage_function_implemented",
            "nist_govern_function_implemented",
            "nist_genai_testing_implemented",
            "iso_ai_policy_defined",
            "iso_ai_risk_assessment",
            "iso_ai_objectives_set",
            "iso_ai_competence_managed",
            "iso_ai_documented_info",
            "iso_ai_operational_controls",
            "iso_ai_monitoring",
            "iso_ai_internal_audit",
            "iso_ai_management_review",
            "mitre_recon_detection",
            "mitre_poisoning_detection",
            "mitre_extraction_controls",
            "mitre_prompt_injection_detection",
            "mitre_tool_invocation_controls",
            "mitre_rag_db_controls",
            "csa_atf_sandbox_controls",
            "csa_atf_controlled_controls",
            "csa_atf_trusted_controls",
            "csa_atf_autonomous_controls",
            "csa_atf_continuous_assessment",
        ]
        for field in bool_fields:
            assert getattr(cfg, field) is False, f"{field} should default to False"


# ---------------------------------------------------------------------------
# All-defaults audit: score == 0, maturity == "INITIAL", 37 controls all FAIL
# ---------------------------------------------------------------------------


class TestAllDefaultsAudit:
    def setup_method(self):
        self.report = _audit(_all_off_config())

    def test_score_is_zero(self):
        assert self.report.score == 0

    def test_maturity_is_initial(self):
        assert self.report.maturity_level == "INITIAL"

    def test_total_controls_is_37(self):
        assert self.report.total_controls == 37

    def test_all_controls_fail(self):
        assert self.report.failed == 37

    def test_passed_is_zero(self):
        assert self.report.passed == 0

    def test_findings_has_37_items(self):
        assert len(self.report.findings) == 37

    def test_system_id_preserved(self):
        report = _audit(GovernanceFrameworkConfig(system_id="test-system"))
        assert report.system_id == "test-system"


# ---------------------------------------------------------------------------
# All-enabled audit: score == 100, maturity == "OPTIMIZING"
# ---------------------------------------------------------------------------


class TestAllEnabledAudit:
    def setup_method(self):
        self.report = _audit(_all_on_config())

    def test_score_is_100(self):
        assert self.report.score == 100

    def test_maturity_is_optimizing(self):
        assert self.report.maturity_level == "OPTIMIZING"

    def test_zero_failures(self):
        assert self.report.failed == 0

    def test_all_37_pass(self):
        assert self.report.passed == 37

    def test_critical_failures_empty(self):
        assert self.report.critical_failures() == []

    def test_high_failures_empty(self):
        assert self.report.high_failures() == []


# ---------------------------------------------------------------------------
# OWASP LLM controls
# ---------------------------------------------------------------------------


class TestOWASPLLMControls:
    def test_gov_ollm_001_pass_when_prompt_injection_controls_true(self):
        report = _audit(_all_off_config(owasp_llm_prompt_injection_controls=True))
        finding = _find(report, "GOV-OLLM-001")
        assert finding.status == "PASS"

    def test_gov_ollm_001_fail_critical_when_prompt_injection_controls_false(self):
        report = _audit(_all_off_config(owasp_llm_prompt_injection_controls=False))
        finding = _find(report, "GOV-OLLM-001")
        assert finding.status == "FAIL"
        assert finding.severity == "CRITICAL"


# ---------------------------------------------------------------------------
# NIST controls
# ---------------------------------------------------------------------------


class TestNISTControls:
    def test_gov_nist_004_pass_when_govern_function_implemented(self):
        report = _audit(_all_off_config(nist_govern_function_implemented=True))
        finding = _find(report, "GOV-NIST-004")
        assert finding.status == "PASS"

    def test_gov_nist_004_fail_when_govern_function_not_implemented(self):
        report = _audit(_all_off_config(nist_govern_function_implemented=False))
        finding = _find(report, "GOV-NIST-004")
        assert finding.status == "FAIL"


# ---------------------------------------------------------------------------
# ISO controls
# ---------------------------------------------------------------------------


class TestISOControls:
    def test_gov_iso_001_pass_when_ai_policy_defined(self):
        report = _audit(_all_off_config(iso_ai_policy_defined=True))
        finding = _find(report, "GOV-ISO-001")
        assert finding.status == "PASS"

    def test_gov_iso_001_fail_when_ai_policy_not_defined(self):
        report = _audit(_all_off_config(iso_ai_policy_defined=False))
        finding = _find(report, "GOV-ISO-001")
        assert finding.status == "FAIL"


# ---------------------------------------------------------------------------
# MITRE ATLAS controls
# ---------------------------------------------------------------------------


class TestMITREATLASControls:
    def test_gov_atlas_002_fail_critical_when_poisoning_detection_false(self):
        report = _audit(_all_off_config(mitre_poisoning_detection=False))
        finding = _find(report, "GOV-ATLAS-002")
        assert finding.status == "FAIL"
        assert finding.severity == "CRITICAL"

    def test_gov_atlas_002_pass_when_poisoning_detection_true(self):
        report = _audit(_all_off_config(mitre_poisoning_detection=True))
        finding = _find(report, "GOV-ATLAS-002")
        assert finding.status == "PASS"


# ---------------------------------------------------------------------------
# CSA controls
# ---------------------------------------------------------------------------


class TestCSAControls:
    def test_gov_csa_005_pass_when_continuous_assessment_true(self):
        report = _audit(_all_off_config(csa_atf_continuous_assessment=True))
        finding = _find(report, "GOV-CSA-005")
        assert finding.status == "PASS"

    def test_gov_csa_005_fail_when_continuous_assessment_false(self):
        report = _audit(_all_off_config(csa_atf_continuous_assessment=False))
        finding = _find(report, "GOV-CSA-005")
        assert finding.status == "FAIL"


# ---------------------------------------------------------------------------
# Domain coverage
# ---------------------------------------------------------------------------


class TestDomainCoverage:
    _EXPECTED_DOMAINS = {
        "OWASP LLM Top 10 2025",
        "OWASP Agentic AI Top 10 2026",
        "NIST AI RMF",
        "ISO/IEC 42001:2023",
        "MITRE ATLAS v5.1",
        "CSA Agentic Trust Framework",
    }

    def test_all_six_domains_covered(self):
        report = _audit(_all_off_config())
        actual_domains = {f.domain for f in report.findings}
        assert self._EXPECTED_DOMAINS == actual_domains

    def test_domain_summary_has_six_entries(self):
        report = _audit(_all_off_config())
        assert len(report.domain_summary) == 6

    def test_domain_summary_totals_sum_to_37(self):
        report = _audit(_all_off_config())
        total = sum(d["total"] for d in report.domain_summary.values())
        assert total == 37

    def test_findings_by_domain_helper(self):
        report = _audit(_all_off_config())
        owasp_llm = report.findings_by_domain("OWASP LLM Top 10 2025")
        assert len(owasp_llm) == 8

    def test_owasp_agentic_domain_has_4_findings(self):
        report = _audit(_all_off_config())
        agentic = report.findings_by_domain("OWASP Agentic AI Top 10 2026")
        assert len(agentic) == 4

    def test_nist_domain_has_5_findings(self):
        report = _audit(_all_off_config())
        nist = report.findings_by_domain("NIST AI RMF")
        assert len(nist) == 5

    def test_iso_domain_has_9_findings(self):
        report = _audit(_all_off_config())
        iso = report.findings_by_domain("ISO/IEC 42001:2023")
        assert len(iso) == 9

    def test_mitre_domain_has_6_findings(self):
        report = _audit(_all_off_config())
        mitre = report.findings_by_domain("MITRE ATLAS v5.1")
        assert len(mitre) == 6

    def test_csa_domain_has_5_findings(self):
        report = _audit(_all_off_config())
        csa = report.findings_by_domain("CSA Agentic Trust Framework")
        assert len(csa) == 5


# ---------------------------------------------------------------------------
# Framework refs
# ---------------------------------------------------------------------------


class TestFrameworkRefs:
    def test_framework_refs_nonempty_for_all_findings(self):
        report = _audit(_all_off_config())
        for f in report.findings:
            assert isinstance(f.framework_refs, list), f"{f.control_id}: framework_refs must be a list"
            assert len(f.framework_refs) > 0, f"{f.control_id}: framework_refs must not be empty"
            for ref in f.framework_refs:
                assert isinstance(ref, str) and len(ref) > 0, (
                    f"{f.control_id}: framework ref must be a non-empty string, got {ref!r}"
                )


# ---------------------------------------------------------------------------
# Score and count consistency
# ---------------------------------------------------------------------------


class TestScoreAndCountConsistency:
    def test_score_not_negative(self):
        assert _audit(_all_off_config()).score >= 0

    def test_score_not_above_100(self):
        assert _audit(_all_on_config()).score <= 100

    def test_passed_plus_failed_equals_total_controls(self):
        report = _audit(_all_off_config())
        assert report.passed + report.failed + report.warned == report.total_controls

    def test_score_deduction_property_zero_for_pass(self):
        """AuditFinding.score_deduction returns 0 for PASS findings."""
        report = _audit(_all_on_config())
        for f in report.findings:
            assert f.score_deduction == 0

    def test_score_deduction_property_nonzero_for_fail(self):
        """AuditFinding.score_deduction returns > 0 for FAIL findings."""
        report = _audit(_all_off_config())
        for f in report.findings:
            if f.status == "FAIL":
                assert f.score_deduction > 0, f"{f.control_id}: FAIL finding should have positive score_deduction"
