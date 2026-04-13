"""
Tests for 10_eu_ai_act_governance.py

Covers Article5ProhibitionGuard, Article6ClassificationGuard,
Article13TransparencyGuard, Article14OversightGuard, Article15RobustnessGuard,
GPAIGuard, and EUAIActGovernanceOrchestrator.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "eu_ai_act_governance",
    os.path.join(os.path.dirname(__file__), "..", "examples", "10_eu_ai_act_governance.py"),
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["eu_ai_act_governance"] = _mod  # required for frozen dataclasses on Python 3.14
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

AIRiskLevel = _mod.AIRiskLevel
AnnexIIICategory = _mod.AnnexIIICategory
ProhibitedAIType = _mod.ProhibitedAIType
GovernanceOutcome = _mod.GovernanceOutcome
EUAIActRequestContext = _mod.EUAIActRequestContext
Article5ProhibitionGuard = _mod.Article5ProhibitionGuard
Article6ClassificationGuard = _mod.Article6ClassificationGuard
Article13TransparencyGuard = _mod.Article13TransparencyGuard
Article14OversightGuard = _mod.Article14OversightGuard
Article15RobustnessGuard = _mod.Article15RobustnessGuard
GPAIGuard = _mod.GPAIGuard
EUAIActGovernanceOrchestrator = _mod.EUAIActGovernanceOrchestrator
_GPAI_SYSTEMIC_RISK_FLOPS_THRESHOLD = _mod._GPAI_SYSTEMIC_RISK_FLOPS_THRESHOLD


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _ctx(
    name: str = "Test AI",
    *,
    annex: AnnexIIICategory | None = None,
    prohibited: ProhibitedAIType | None = None,
    is_gpai: bool = False,
    flops: float | None = None,
    transparency_ok: bool = True,
    oversight_ok: bool = True,
    accuracy_ok: bool = True,
    robustness_ok: bool = True,
    model_card: bool = False,
    adversarial: bool = False,
    incident_reporting: bool = True,
    conformity: bool = False,
    public_authority: bool = False,
    public_space: bool = False,
) -> EUAIActRequestContext:
    return EUAIActRequestContext(
        system_name=name,
        annex_iii_category=annex,
        prohibited_ai_type=prohibited,
        is_gpai=is_gpai,
        gpai_flops_training=flops,
        transparency_documentation_complete=transparency_ok,
        human_oversight_mechanism_in_place=oversight_ok,
        accuracy_level_validated=accuracy_ok,
        robustness_measures_in_place=robustness_ok,
        model_card_published=model_card,
        adversarial_testing_completed=adversarial,
        incident_reporting_capability=incident_reporting,
        conformity_assessment_done=conformity,
        deployer_is_public_authority=public_authority,
        deployment_in_public_space=public_space,
    )


# ---------------------------------------------------------------------------
# Article 5 tests
# ---------------------------------------------------------------------------

class TestArticle5ProhibitionGuard:
    def setup_method(self):
        self.g = Article5ProhibitionGuard()

    def test_social_scoring_is_prohibited(self):
        result = self.g.evaluate(_ctx(prohibited=ProhibitedAIType.SOCIAL_SCORING_PUBLIC))
        assert result["allowed"] is False
        assert any("Article 5" in v for v in result["violations"])

    def test_subliminal_manipulation_is_prohibited(self):
        result = self.g.evaluate(_ctx(prohibited=ProhibitedAIType.SUBLIMINAL_MANIPULATION))
        assert result["allowed"] is False

    def test_vulnerability_exploitation_is_prohibited(self):
        result = self.g.evaluate(_ctx(prohibited=ProhibitedAIType.VULNERABILITY_EXPLOITATION))
        assert result["allowed"] is False

    def test_predictive_policing_is_prohibited(self):
        result = self.g.evaluate(_ctx(prohibited=ProhibitedAIType.PREDICTIVE_POLICING_INDIVIDUAL))
        assert result["allowed"] is False

    def test_emotion_recognition_workplace_is_prohibited(self):
        result = self.g.evaluate(_ctx(prohibited=ProhibitedAIType.EMOTION_RECOGNITION_WORK_SCHOOL))
        assert result["allowed"] is False

    def test_untargeted_face_scraping_is_prohibited(self):
        result = self.g.evaluate(_ctx(prohibited=ProhibitedAIType.UNTARGETED_FACE_SCRAPING))
        assert result["allowed"] is False

    def test_real_time_biometric_in_public_space_is_prohibited(self):
        result = self.g.evaluate(_ctx(
            prohibited=ProhibitedAIType.REAL_TIME_BIOMETRIC_PUBLIC,
            public_space=True,
        ))
        assert result["allowed"] is False
        assert any("5(1)(a)" in v for v in result["violations"])

    def test_real_time_biometric_not_in_public_space_is_allowed(self):
        result = self.g.evaluate(_ctx(
            prohibited=ProhibitedAIType.REAL_TIME_BIOMETRIC_PUBLIC,
            public_space=False,  # e.g. controlled environment
        ))
        assert result["allowed"] is True

    def test_no_prohibited_type_is_allowed(self):
        result = self.g.evaluate(_ctx())
        assert result["allowed"] is True
        assert result["violations"] == []


# ---------------------------------------------------------------------------
# Article 6 tests
# ---------------------------------------------------------------------------

class TestArticle6ClassificationGuard:
    def setup_method(self):
        self.g = Article6ClassificationGuard()

    def test_no_annex_iii_is_not_high_risk(self):
        result = self.g.evaluate(_ctx())
        assert result["is_high_risk"] is False
        assert result["risk_level"] == AIRiskLevel.MINIMAL_RISK

    def test_employment_category_is_high_risk(self):
        result = self.g.evaluate(_ctx(annex=AnnexIIICategory.EMPLOYMENT))
        assert result["is_high_risk"] is True
        assert result["risk_level"] == AIRiskLevel.HIGH_RISK

    def test_all_annex_iii_categories_are_high_risk(self):
        for cat in AnnexIIICategory:
            result = self.g.evaluate(_ctx(annex=cat))
            assert result["is_high_risk"] is True, f"{cat} should be HIGH_RISK"

    def test_conformity_assessment_missing_is_violation(self):
        result = self.g.evaluate(_ctx(annex=AnnexIIICategory.EDUCATION, conformity=False))
        assert not result["allowed"]
        assert any("Article 43" in v for v in result["violations"])

    def test_conformity_assessment_done_no_violation(self):
        result = self.g.evaluate(_ctx(annex=AnnexIIICategory.EDUCATION, conformity=True))
        assert result["allowed"] is True
        assert result["violations"] == []


# ---------------------------------------------------------------------------
# Article 13 transparency tests
# ---------------------------------------------------------------------------

class TestArticle13TransparencyGuard:
    def setup_method(self):
        self.g = Article13TransparencyGuard()

    def test_non_high_risk_skips_transparency(self):
        result = self.g.evaluate(_ctx(transparency_ok=False), is_high_risk=False)
        assert result["allowed"] is True

    def test_high_risk_requires_transparency_documentation(self):
        result = self.g.evaluate(_ctx(transparency_ok=False), is_high_risk=True)
        assert result["allowed"] is False
        assert any("Article 13" in v for v in result["violations"])

    def test_high_risk_with_documentation_is_allowed(self):
        result = self.g.evaluate(_ctx(transparency_ok=True), is_high_risk=True)
        assert result["allowed"] is True


# ---------------------------------------------------------------------------
# Article 14 oversight tests
# ---------------------------------------------------------------------------

class TestArticle14OversightGuard:
    def setup_method(self):
        self.g = Article14OversightGuard()

    def test_non_high_risk_skips_oversight(self):
        result = self.g.evaluate(_ctx(oversight_ok=False), is_high_risk=False)
        assert result["allowed"] is True

    def test_high_risk_requires_human_oversight(self):
        result = self.g.evaluate(_ctx(oversight_ok=False), is_high_risk=True)
        assert result["allowed"] is False
        assert any("Article 14" in v for v in result["violations"])

    def test_high_risk_with_oversight_is_allowed(self):
        result = self.g.evaluate(_ctx(oversight_ok=True), is_high_risk=True)
        assert result["allowed"] is True


# ---------------------------------------------------------------------------
# Article 15 robustness tests
# ---------------------------------------------------------------------------

class TestArticle15RobustnessGuard:
    def setup_method(self):
        self.g = Article15RobustnessGuard()

    def test_non_high_risk_skips_robustness(self):
        result = self.g.evaluate(_ctx(accuracy_ok=False, robustness_ok=False), is_high_risk=False)
        assert result["allowed"] is True

    def test_high_risk_requires_accuracy_validation(self):
        result = self.g.evaluate(_ctx(accuracy_ok=False, robustness_ok=True), is_high_risk=True)
        assert result["allowed"] is False
        assert any("15(1)" in v for v in result["violations"])

    def test_high_risk_requires_robustness_measures(self):
        result = self.g.evaluate(_ctx(accuracy_ok=True, robustness_ok=False), is_high_risk=True)
        assert result["allowed"] is False
        assert any("15(2)" in v for v in result["violations"])

    def test_high_risk_with_both_validated_is_allowed(self):
        result = self.g.evaluate(_ctx(accuracy_ok=True, robustness_ok=True), is_high_risk=True)
        assert result["allowed"] is True


# ---------------------------------------------------------------------------
# GPAI tests
# ---------------------------------------------------------------------------

class TestGPAIGuard:
    def setup_method(self):
        self.g = GPAIGuard()

    def test_non_gpai_is_allowed(self):
        result = self.g.evaluate(_ctx(is_gpai=False))
        assert result["allowed"] is True
        assert result["has_systemic_risk"] is False

    def test_gpai_without_model_card_is_violation(self):
        result = self.g.evaluate(_ctx(is_gpai=True, model_card=False))
        assert result["allowed"] is False
        assert any("53(1)(d)" in v for v in result["violations"])

    def test_gpai_with_model_card_below_threshold_is_allowed(self):
        result = self.g.evaluate(_ctx(
            is_gpai=True,
            flops=1e24,   # below 10^25 threshold
            model_card=True,
        ))
        assert result["allowed"] is True
        assert result["has_systemic_risk"] is False

    def test_gpai_above_threshold_is_systemic_risk(self):
        result = self.g.evaluate(_ctx(
            is_gpai=True,
            flops=2e25,   # above 10^25 threshold
            model_card=True,
            adversarial=True,
            incident_reporting=True,
        ))
        assert result["has_systemic_risk"] is True
        assert result["allowed"] is True

    def test_gpai_systemic_risk_requires_adversarial_testing(self):
        result = self.g.evaluate(_ctx(
            is_gpai=True,
            flops=2e25,
            model_card=True,
            adversarial=False,  # missing
            incident_reporting=True,
        ))
        assert result["allowed"] is False
        assert any("55(1)(a)" in v for v in result["violations"])

    def test_gpai_systemic_risk_requires_incident_reporting(self):
        result = self.g.evaluate(_ctx(
            is_gpai=True,
            flops=2e25,
            model_card=True,
            adversarial=True,
            incident_reporting=False,  # missing
        ))
        assert result["allowed"] is False
        assert any("55(1)(c)" in v for v in result["violations"])

    def test_flops_threshold_value(self):
        assert _GPAI_SYSTEMIC_RISK_FLOPS_THRESHOLD == 1e25


# ---------------------------------------------------------------------------
# Orchestrator integration tests
# ---------------------------------------------------------------------------

class TestEUAIActGovernanceOrchestrator:
    def setup_method(self):
        self.orch = EUAIActGovernanceOrchestrator()

    def test_prohibited_ai_is_denied(self):
        ctx = _ctx(prohibited=ProhibitedAIType.SOCIAL_SCORING_PUBLIC)
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.DENY

    def test_prohibited_ai_denied_even_with_all_safeguards(self):
        ctx = _ctx(
            prohibited=ProhibitedAIType.SUBLIMINAL_MANIPULATION,
            transparency_ok=True,
            oversight_ok=True,
            accuracy_ok=True,
            robustness_ok=True,
            conformity=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.DENY

    def test_high_risk_compliant_is_allow_with_conditions(self):
        ctx = _ctx(
            annex=AnnexIIICategory.EMPLOYMENT,
            transparency_ok=True,
            oversight_ok=True,
            accuracy_ok=True,
            robustness_ok=True,
            conformity=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert audit.is_high_risk is True

    def test_high_risk_missing_conformity_escalates(self):
        ctx = _ctx(
            annex=AnnexIIICategory.EDUCATION,
            transparency_ok=True,
            oversight_ok=True,
            accuracy_ok=True,
            robustness_ok=True,
            conformity=False,  # not done
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.ESCALATE_HUMAN

    def test_high_risk_missing_transparency_is_denied(self):
        ctx = _ctx(
            annex=AnnexIIICategory.EMPLOYMENT,
            transparency_ok=False,   # violation
            oversight_ok=True,
            accuracy_ok=True,
            robustness_ok=True,
            conformity=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.DENY

    def test_minimal_risk_is_allowed(self):
        ctx = _ctx()
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.ALLOW
        assert audit.is_high_risk is False

    def test_gpai_systemic_risk_compliant_is_allow_with_conditions(self):
        ctx = _ctx(
            is_gpai=True,
            flops=5e25,
            model_card=True,
            adversarial=True,
            incident_reporting=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert audit.has_systemic_risk is True

    def test_gpai_without_model_card_is_denied(self):
        ctx = _ctx(is_gpai=True, flops=5e25, model_card=False)
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.DENY

    def test_audit_record_applicable_articles_for_high_risk(self):
        ctx = _ctx(
            annex=AnnexIIICategory.EMPLOYMENT,
            transparency_ok=True,
            oversight_ok=True,
            accuracy_ok=True,
            robustness_ok=True,
            conformity=True,
        )
        audit = self.orch.evaluate(ctx)
        assert any("Annex III" in a for a in audit.applicable_articles)

    def test_conformity_assessment_required_for_high_risk(self):
        ctx = _ctx(annex=AnnexIIICategory.EMPLOYMENT, conformity=True)
        audit = self.orch.evaluate(ctx)
        assert audit.conformity_assessment_required is True

    def test_notified_body_required_for_biometric_id(self):
        ctx = _ctx(annex=AnnexIIICategory.BIOMETRIC_ID, conformity=True,
                   transparency_ok=True, oversight_ok=True,
                   accuracy_ok=True, robustness_ok=True)
        audit = self.orch.evaluate(ctx)
        assert audit.notified_body_required is True

    def test_notified_body_not_required_for_employment(self):
        ctx = _ctx(annex=AnnexIIICategory.EMPLOYMENT, conformity=True,
                   transparency_ok=True, oversight_ok=True,
                   accuracy_ok=True, robustness_ok=True)
        audit = self.orch.evaluate(ctx)
        assert audit.notified_body_required is False

    def test_audit_includes_system_name(self):
        ctx = _ctx(name="My Test System")
        audit = self.orch.evaluate(ctx)
        assert audit.system_name == "My Test System"

    def test_prohibited_type_recorded_in_audit(self):
        ctx = _ctx(prohibited=ProhibitedAIType.SOCIAL_SCORING_PUBLIC)
        audit = self.orch.evaluate(ctx)
        assert audit.prohibited_ai_type == ProhibitedAIType.SOCIAL_SCORING_PUBLIC.value

    def test_annex_iii_recorded_in_audit(self):
        ctx = _ctx(annex=AnnexIIICategory.EDUCATION, conformity=True,
                   transparency_ok=True, oversight_ok=True,
                   accuracy_ok=True, robustness_ok=True)
        audit = self.orch.evaluate(ctx)
        assert audit.annex_iii_category == AnnexIIICategory.EDUCATION.value

    def test_scenario_a_employment_screening_compliant(self):
        """Full Scenario A: employment screening with all obligations met."""
        ctx = _ctx(
            name="CV Ranking & Candidate Screening AI",
            annex=AnnexIIICategory.EMPLOYMENT,
            conformity=True,
            transparency_ok=True,
            oversight_ok=True,
            accuracy_ok=True,
            robustness_ok=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
        assert len(audit.violations) == 0

    def test_scenario_b_social_scoring_denied(self):
        """Full Scenario B: social scoring by public authority is prohibited."""
        ctx = _ctx(
            prohibited=ProhibitedAIType.SOCIAL_SCORING_PUBLIC,
            public_authority=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.DENY

    def test_scenario_c_gpai_missing_model_card_denied(self):
        """Full Scenario C: GPAI systemic risk without model card is denied."""
        ctx = _ctx(
            is_gpai=True,
            flops=3e25,
            model_card=False,
            adversarial=False,
            incident_reporting=True,
        )
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.DENY
        assert audit.has_systemic_risk is True

    def test_scenario_d_minimal_risk_chatbot_allowed(self):
        """Full Scenario D: minimal-risk chatbot with no obligations violated."""
        ctx = _ctx(name="Customer Support Chatbot")
        audit = self.orch.evaluate(ctx)
        assert audit.outcome == GovernanceOutcome.ALLOW
        assert len(audit.violations) == 0
