"""Tests for EU AI Act (Regulation 2024/1689) governance module."""

from __future__ import annotations

import json

from regulated_ai_governance.regulations.eu_ai_act import (
    EU_AI_ACT_HIGH_RISK_DOMAINS,
    EU_AI_ACT_PROHIBITED_PRACTICES,
    EUAIActAuditRecord,
    EUAIActGovernancePolicy,
    EUAIActPolicyDecision,
    EUAIActRiskCategory,
    EUAIActSystemProfile,
    make_eu_ai_act_high_risk_policy,
    make_eu_ai_act_minimal_risk_policy,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_high_risk_profile(
    system_id: str = "hr_screening_v1",
    deployment_approved: bool = True,
    conformity_assessment_complete: bool = True,
    fria_completed: bool = True,
    logging_enabled: bool = True,
    human_oversight_measures: set[str] | None = None,
    permitted_use_cases: set[str] | None = None,
    prohibited_use_cases: set[str] | None = None,
) -> EUAIActSystemProfile:
    return EUAIActSystemProfile(
        system_id=system_id,
        risk_category=EUAIActRiskCategory.HIGH_RISK,
        deployment_approved=deployment_approved,
        fria_completed=fria_completed,
        human_oversight_measures=human_oversight_measures
        if human_oversight_measures is not None
        else {"human_in_the_loop_review", "explainability_dashboard"},
        logging_enabled=logging_enabled,
        permitted_use_cases=permitted_use_cases
        if permitted_use_cases is not None
        else {"rank_applications", "screen_qualifications", "summarize_cv"},
        prohibited_use_cases=prohibited_use_cases
        if prohibited_use_cases is not None
        else set(EU_AI_ACT_PROHIBITED_PRACTICES),
        deployment_approver="compliance_lead_bob",
        conformity_assessment_complete=conformity_assessment_complete,
    )


def _make_minimal_risk_profile(
    permitted_use_cases: set[str] | None = None,
) -> EUAIActSystemProfile:
    return EUAIActSystemProfile(
        system_id="faq_bot_v1",
        risk_category=EUAIActRiskCategory.MINIMAL_RISK,
        deployment_approved=True,
        fria_completed=False,
        human_oversight_measures=set(),
        logging_enabled=False,
        permitted_use_cases=permitted_use_cases if permitted_use_cases is not None else {"answer_faq", "search_kb"},
        prohibited_use_cases=set(EU_AI_ACT_PROHIBITED_PRACTICES),
        deployment_approver=None,
        conformity_assessment_complete=False,
    )


def _make_high_risk_policy(
    profile: EUAIActSystemProfile | None = None,
    public_sector_deployer: bool = False,
    session_id: str = "sess_test_001",
) -> EUAIActGovernancePolicy:
    return EUAIActGovernancePolicy(
        profile=profile or _make_high_risk_profile(),
        public_sector_deployer=public_sector_deployer,
        session_id=session_id,
    )


def _make_minimal_risk_policy(
    profile: EUAIActSystemProfile | None = None,
) -> EUAIActGovernancePolicy:
    return EUAIActGovernancePolicy(
        profile=profile or _make_minimal_risk_profile(),
        session_id="sess_min_001",
    )


# ---------------------------------------------------------------------------
# EUAIActRiskCategory
# ---------------------------------------------------------------------------


class TestEUAIActRiskCategory:
    def test_all_four_values_exist(self):
        cats = {c.value for c in EUAIActRiskCategory}
        assert cats == {"unacceptable", "high_risk", "limited_risk", "minimal_risk"}

    def test_is_str_enum(self):
        assert EUAIActRiskCategory.HIGH_RISK == "high_risk"
        assert EUAIActRiskCategory.UNACCEPTABLE == "unacceptable"
        assert EUAIActRiskCategory.LIMITED_RISK == "limited_risk"
        assert EUAIActRiskCategory.MINIMAL_RISK == "minimal_risk"

    def test_string_comparison(self):
        assert EUAIActRiskCategory.HIGH_RISK.value == "high_risk"


# ---------------------------------------------------------------------------
# EU_AI_ACT_PROHIBITED_PRACTICES
# ---------------------------------------------------------------------------


class TestEUAIActProhibitedPractices:
    def test_is_frozenset(self):
        assert isinstance(EU_AI_ACT_PROHIBITED_PRACTICES, frozenset)

    def test_contains_key_art5_practices(self):
        assert "social_scoring" in EU_AI_ACT_PROHIBITED_PRACTICES
        assert "subliminal_manipulation" in EU_AI_ACT_PROHIBITED_PRACTICES
        assert "realtime_biometric_identification_public" in EU_AI_ACT_PROHIBITED_PRACTICES
        assert "emotion_recognition_workplace" in EU_AI_ACT_PROHIBITED_PRACTICES
        assert "predictive_policing_profiling" in EU_AI_ACT_PROHIBITED_PRACTICES
        assert "facial_recognition_database_scraping" in EU_AI_ACT_PROHIBITED_PRACTICES

    def test_non_empty(self):
        assert len(EU_AI_ACT_PROHIBITED_PRACTICES) > 0


# ---------------------------------------------------------------------------
# EU_AI_ACT_HIGH_RISK_DOMAINS
# ---------------------------------------------------------------------------


class TestEUAIActHighRiskDomains:
    def test_is_frozenset(self):
        assert isinstance(EU_AI_ACT_HIGH_RISK_DOMAINS, frozenset)

    def test_contains_annex_iii_sectors(self):
        assert "biometric_identification" in EU_AI_ACT_HIGH_RISK_DOMAINS
        assert "recruitment_screening" in EU_AI_ACT_HIGH_RISK_DOMAINS
        assert "credit_scoring" in EU_AI_ACT_HIGH_RISK_DOMAINS
        assert "healthcare_triage" in EU_AI_ACT_HIGH_RISK_DOMAINS
        assert "crime_risk_assessment" in EU_AI_ACT_HIGH_RISK_DOMAINS
        assert "asylum_application_assessment" in EU_AI_ACT_HIGH_RISK_DOMAINS
        assert "judicial_outcome_prediction" in EU_AI_ACT_HIGH_RISK_DOMAINS

    def test_non_empty(self):
        assert len(EU_AI_ACT_HIGH_RISK_DOMAINS) > 0


# ---------------------------------------------------------------------------
# EUAIActSystemProfile
# ---------------------------------------------------------------------------


class TestEUAIActSystemProfile:
    def test_high_risk_profile_attributes(self):
        profile = _make_high_risk_profile()
        assert profile.system_id == "hr_screening_v1"
        assert profile.risk_category is EUAIActRiskCategory.HIGH_RISK
        assert profile.deployment_approved is True
        assert profile.conformity_assessment_complete is True
        assert profile.fria_completed is True
        assert profile.logging_enabled is True
        assert "human_in_the_loop_review" in profile.human_oversight_measures
        assert "rank_applications" in profile.permitted_use_cases
        assert profile.deployment_approver == "compliance_lead_bob"

    def test_minimal_risk_profile_defaults(self):
        profile = _make_minimal_risk_profile()
        assert profile.risk_category is EUAIActRiskCategory.MINIMAL_RISK
        assert profile.conformity_assessment_complete is False
        assert profile.fria_completed is False
        assert profile.deployment_approver is None
        assert len(profile.human_oversight_measures) == 0


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — evaluate_action: UNACCEPTABLE risk
# ---------------------------------------------------------------------------


class TestEUAIActUnacceptableRisk:
    def test_unacceptable_system_always_denied(self):
        profile = EUAIActSystemProfile(
            system_id="banned_scorer_v1",
            risk_category=EUAIActRiskCategory.UNACCEPTABLE,
            deployment_approved=True,
            fria_completed=True,
            human_oversight_measures={"oversight"},
            logging_enabled=True,
            permitted_use_cases={"social_scoring"},
            prohibited_use_cases=set(),
            conformity_assessment_complete=True,
        )
        policy = EUAIActGovernancePolicy(profile=profile)
        decision = policy.evaluate_action("social_scoring")
        assert decision.permitted is False
        assert decision.risk_category is EUAIActRiskCategory.UNACCEPTABLE
        assert decision.denial_reason is not None
        reason = decision.denial_reason
        assert "UNACCEPTABLE" in reason or "Article 5" in reason or "Art" in reason

    def test_prohibited_practice_denied_for_high_risk_system(self):
        profile = _make_high_risk_profile()
        policy = _make_high_risk_policy(profile=profile)
        # social_scoring is in EU_AI_ACT_PROHIBITED_PRACTICES, which is in prohibited_use_cases
        decision = policy.evaluate_action("social_scoring")
        assert decision.permitted is False
        assert "prohibited" in decision.denial_reason.lower() or "Article 5" in decision.denial_reason

    def test_prohibited_practice_no_human_oversight(self):
        """Prohibited practices must not return human_oversight_required=True."""
        profile = _make_high_risk_profile()
        policy = _make_high_risk_policy(profile=profile)
        decision = policy.evaluate_action("emotion_recognition_workplace")
        assert decision.permitted is False
        assert decision.human_oversight_required is False


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — evaluate_action: deployment gate (Art. 43)
# ---------------------------------------------------------------------------


class TestEUAIActDeploymentGate:
    def test_high_risk_blocked_if_not_deployment_approved(self):
        profile = _make_high_risk_profile(deployment_approved=False)
        policy = _make_high_risk_policy(profile=profile)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is False
        assert "deployment" in decision.denial_reason.lower() or "Art. 43" in decision.denial_reason

    def test_high_risk_blocked_if_conformity_assessment_incomplete(self):
        profile = _make_high_risk_profile(
            deployment_approved=True,
            conformity_assessment_complete=False,
        )
        policy = _make_high_risk_policy(profile=profile)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is False
        assert "conformity" in decision.denial_reason.lower() or "Art. 43" in decision.denial_reason

    def test_minimal_risk_not_subject_to_conformity_gate(self):
        """MINIMAL_RISK systems skip the conformity assessment check."""
        profile = _make_minimal_risk_profile()
        policy = _make_minimal_risk_policy(profile=profile)
        decision = policy.evaluate_action("answer_faq")
        assert decision.permitted is True


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — evaluate_action: FRIA check (Art. 27)
# ---------------------------------------------------------------------------


class TestEUAIActFRIACheck:
    def test_high_risk_public_sector_blocked_without_fria(self):
        profile = _make_high_risk_profile(fria_completed=False)
        policy = _make_high_risk_policy(profile=profile, public_sector_deployer=True)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is False
        reason = decision.denial_reason
        assert "FRIA" in reason or "Fundamental Rights" in reason or "Art. 27" in reason

    def test_high_risk_private_sector_permitted_without_fria(self):
        """Private sector deployers are not required to complete FRIA."""
        profile = _make_high_risk_profile(fria_completed=False)
        policy = _make_high_risk_policy(profile=profile, public_sector_deployer=False)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is True

    def test_high_risk_public_sector_with_fria_permitted(self):
        profile = _make_high_risk_profile(fria_completed=True)
        policy = _make_high_risk_policy(profile=profile, public_sector_deployer=True)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is True


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — evaluate_action: logging check (Art. 12)
# ---------------------------------------------------------------------------


class TestEUAIActLoggingCheck:
    def test_high_risk_blocked_if_logging_disabled(self):
        profile = _make_high_risk_profile(logging_enabled=False)
        policy = _make_high_risk_policy(profile=profile)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is False
        assert "logging" in decision.denial_reason.lower() or "Art. 12" in decision.denial_reason

    def test_minimal_risk_logging_not_required(self):
        """MINIMAL_RISK systems do not require logging to be enabled."""
        profile = _make_minimal_risk_profile()
        policy = _make_minimal_risk_policy(profile=profile)
        decision = policy.evaluate_action("answer_faq")
        assert decision.permitted is True


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — evaluate_action: human oversight (Art. 14)
# ---------------------------------------------------------------------------


class TestEUAIActHumanOversightCheck:
    def test_high_risk_blocked_without_oversight_measures(self):
        profile = _make_high_risk_profile(human_oversight_measures=set())
        policy = _make_high_risk_policy(profile=profile)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is False
        assert "oversight" in decision.denial_reason.lower() or "Art. 14" in decision.denial_reason

    def test_high_risk_permitted_action_flags_human_oversight(self):
        """Permitted HIGH_RISK actions always require human oversight (Art. 14)."""
        profile = _make_high_risk_profile()
        policy = _make_high_risk_policy(profile=profile)
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is True
        assert decision.human_oversight_required is True

    def test_minimal_risk_permitted_action_no_human_oversight(self):
        """MINIMAL_RISK permitted actions do not require human oversight."""
        policy = _make_minimal_risk_policy()
        decision = policy.evaluate_action("answer_faq")
        assert decision.permitted is True
        assert decision.human_oversight_required is False


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — evaluate_action: use case scope (Art. 9)
# ---------------------------------------------------------------------------


class TestEUAIActUseCaseScope:
    def test_permitted_action_allowed(self):
        policy = _make_high_risk_policy()
        decision = policy.evaluate_action("rank_applications")
        assert decision.permitted is True
        assert decision.denial_reason is None

    def test_unlisted_action_denied(self):
        policy = _make_high_risk_policy()
        decision = policy.evaluate_action("generate_reference_letter")
        assert decision.permitted is False
        assert "permitted" in decision.denial_reason.lower() or "Art. 9" in decision.denial_reason

    def test_evaluate_with_context_dict(self):
        """Context dict must not raise."""
        policy = _make_high_risk_policy()
        decision = policy.evaluate_action("rank_applications", context={"session": "abc"})
        assert decision.permitted is True

    def test_evaluate_with_actor_id(self):
        policy = _make_high_risk_policy()
        decision = policy.evaluate_action("rank_applications", actor_id="recruiter_99")
        assert decision.permitted is True
        assert policy.last_audit is not None
        assert policy.last_audit.actor_id == "recruiter_99"

    def test_limited_risk_permitted_action(self):
        profile = EUAIActSystemProfile(
            system_id="chatbot_v1",
            risk_category=EUAIActRiskCategory.LIMITED_RISK,
            deployment_approved=True,
            fria_completed=False,
            human_oversight_measures=set(),
            logging_enabled=False,
            permitted_use_cases={"answer_question", "provide_information"},
            prohibited_use_cases=set(EU_AI_ACT_PROHIBITED_PRACTICES),
            conformity_assessment_complete=False,
        )
        policy = EUAIActGovernancePolicy(profile=profile)
        decision = policy.evaluate_action("answer_question")
        assert decision.permitted is True
        assert decision.human_oversight_required is False


# ---------------------------------------------------------------------------
# EUAIActGovernancePolicy — last_audit property
# ---------------------------------------------------------------------------


class TestEUAIActLastAudit:
    def test_last_audit_none_before_evaluation(self):
        policy = _make_high_risk_policy()
        assert policy.last_audit is None

    def test_last_audit_set_after_evaluation(self):
        policy = _make_high_risk_policy()
        policy.evaluate_action("rank_applications")
        assert policy.last_audit is not None

    def test_last_audit_updated_each_call(self):
        policy = _make_high_risk_policy()
        policy.evaluate_action("rank_applications")
        first = policy.last_audit
        policy.evaluate_action("screen_qualifications")
        second = policy.last_audit
        assert second is not first
        assert second.action_name == "screen_qualifications"

    def test_audit_sink_called(self):
        sink_records: list[EUAIActAuditRecord] = []
        policy = EUAIActGovernancePolicy(
            profile=_make_high_risk_profile(),
            audit_sink=sink_records.append,
        )
        policy.evaluate_action("rank_applications")
        assert len(sink_records) == 1
        assert sink_records[0].action_name == "rank_applications"


# ---------------------------------------------------------------------------
# EUAIActPolicyDecision
# ---------------------------------------------------------------------------


class TestEUAIActPolicyDecision:
    def test_permitted_decision_attributes(self):
        decision = EUAIActPolicyDecision(
            permitted=True,
            denial_reason=None,
            human_oversight_required=True,
            risk_category=EUAIActRiskCategory.HIGH_RISK,
        )
        assert decision.permitted is True
        assert decision.denial_reason is None
        assert decision.human_oversight_required is True
        assert decision.risk_category is EUAIActRiskCategory.HIGH_RISK

    def test_denied_decision_attributes(self):
        decision = EUAIActPolicyDecision(
            permitted=False,
            denial_reason="Art. 5 prohibited practice",
            human_oversight_required=False,
            risk_category=EUAIActRiskCategory.UNACCEPTABLE,
        )
        assert decision.permitted is False
        assert "Art. 5" in decision.denial_reason
        assert decision.human_oversight_required is False


# ---------------------------------------------------------------------------
# EUAIActAuditRecord
# ---------------------------------------------------------------------------


class TestEUAIActAuditRecord:
    def _make_record(self, permitted: bool = True) -> EUAIActAuditRecord:
        return EUAIActAuditRecord(
            system_id="hr_screening_v1",
            actor_id="recruiter_001",
            action_name="rank_applications",
            permitted=permitted,
            risk_category=EUAIActRiskCategory.HIGH_RISK.value,
            denial_reason=None if permitted else "blocked_by_policy",
            human_oversight_required=permitted,
            session_id="sess_001",
        )

    def test_to_log_entry_is_valid_json(self):
        record = self._make_record()
        entry = record.to_log_entry()
        parsed = json.loads(entry)
        assert parsed["framework"] == "EU_AI_ACT_2024_1689"

    def test_to_log_entry_contains_required_fields(self):
        record = self._make_record()
        parsed = json.loads(record.to_log_entry())
        for key in (
            "system_id",
            "actor_id",
            "action_name",
            "permitted",
            "risk_category",
            "denial_reason",
            "human_oversight_required",
            "timestamp_utc",
            "session_id",
            "eu_ai_act_articles",
        ):
            assert key in parsed, f"Missing field: {key}"

    def test_to_log_entry_framework_identifier(self):
        record = self._make_record()
        parsed = json.loads(record.to_log_entry())
        assert parsed["framework"] == "EU_AI_ACT_2024_1689"

    def test_to_log_entry_denied_record(self):
        record = self._make_record(permitted=False)
        parsed = json.loads(record.to_log_entry())
        assert parsed["permitted"] is False
        assert parsed["denial_reason"] == "blocked_by_policy"

    def test_content_hash_is_64_hex_chars(self):
        record = self._make_record()
        h = record.content_hash()
        assert len(h) == 64
        int(h, 16)  # raises ValueError if not valid hex

    def test_content_hash_is_stable(self):
        """Same record content produces the same hash on repeated calls."""
        record = self._make_record()
        assert record.content_hash() == record.content_hash()

    def test_content_hash_differs_for_different_records(self):
        r1 = self._make_record(permitted=True)
        r2 = self._make_record(permitted=False)
        # Hashes differ because permitted field and denial_reason differ
        assert r1.content_hash() != r2.content_hash()

    def test_default_articles_list(self):
        record = self._make_record()
        assert "Art.5" in record.eu_ai_act_articles
        assert "Art.12" in record.eu_ai_act_articles
        assert "Art.14" in record.eu_ai_act_articles
        assert "Art.43" in record.eu_ai_act_articles

    def test_eu_ai_act_articles_sorted_in_log(self):
        record = self._make_record()
        parsed = json.loads(record.to_log_entry())
        articles = parsed["eu_ai_act_articles"]
        assert articles == sorted(articles)


# ---------------------------------------------------------------------------
# Factory: make_eu_ai_act_minimal_risk_policy
# ---------------------------------------------------------------------------


class TestMakeEUAIActMinimalRiskPolicy:
    def test_returns_action_policy(self):
        from regulated_ai_governance.policy import ActionPolicy

        policy = make_eu_ai_act_minimal_risk_policy(
            allowed_actions={"answer_faq", "search_catalog"},
        )
        assert isinstance(policy, ActionPolicy)

    def test_permits_allowed_action(self):
        policy = make_eu_ai_act_minimal_risk_policy(
            allowed_actions={"answer_faq", "search_catalog"},
        )
        permitted, _ = policy.permits("answer_faq")
        assert permitted is True

    def test_denies_prohibited_practice(self):
        policy = make_eu_ai_act_minimal_risk_policy(
            allowed_actions={"answer_faq"},
        )
        permitted, reason = policy.permits("social_scoring")
        assert permitted is False
        assert "explicitly denied" in reason.lower() or "denied" in reason.lower()

    def test_default_denied_actions_include_prohibited_practices(self):
        policy = make_eu_ai_act_minimal_risk_policy()
        for practice in ("subliminal_manipulation", "social_scoring", "emotion_recognition_workplace"):
            permitted, _ = policy.permits(practice)
            assert permitted is False, f"{practice} should be denied"

    def test_custom_denied_actions_override(self):
        policy = make_eu_ai_act_minimal_risk_policy(
            allowed_actions={"do_something"},
            denied_actions={"custom_bad_action"},
        )
        # social_scoring is not in the custom denied_actions set, but it IS not
        # in the allowed_actions set either; since require_all_allowed=True
        # (allowed_actions is non-empty), it is denied as unlisted.
        permitted, reason = policy.permits("social_scoring")
        assert permitted is False
        assert "not in the allowed actions" in reason

    def test_empty_allowed_allow_all_behavior(self):
        """No allowed_actions means allow-all (except denied)."""
        policy = make_eu_ai_act_minimal_risk_policy(allowed_actions=set())
        permitted, _ = policy.permits("anything_not_prohibited")
        assert permitted is True


# ---------------------------------------------------------------------------
# Factory: make_eu_ai_act_high_risk_policy
# ---------------------------------------------------------------------------


class TestMakeEUAIActHighRiskPolicy:
    def test_returns_action_policy(self):
        from regulated_ai_governance.policy import ActionPolicy

        policy = make_eu_ai_act_high_risk_policy(
            allowed_actions={"screen_cv", "rank_candidates"},
        )
        assert isinstance(policy, ActionPolicy)

    def test_permits_allowed_action(self):
        policy = make_eu_ai_act_high_risk_policy(
            allowed_actions={"screen_cv", "rank_candidates"},
        )
        permitted, _ = policy.permits("screen_cv")
        assert permitted is True

    def test_denies_unlisted_action(self):
        policy = make_eu_ai_act_high_risk_policy(
            allowed_actions={"screen_cv"},
        )
        permitted, reason = policy.permits("generate_reference_letter")
        assert permitted is False

    def test_denies_prohibited_practice(self):
        policy = make_eu_ai_act_high_risk_policy(
            allowed_actions={"screen_cv"},
        )
        permitted, _ = policy.permits("emotion_recognition_workplace")
        assert permitted is False

    def test_escalation_rule_present(self):
        policy = make_eu_ai_act_high_risk_policy(
            allowed_actions={"screen_cv"},
            escalate_to="eu_compliance_team",
        )
        rule = policy.escalation_for("screen_cv")
        assert rule is not None
        assert rule.escalate_to == "eu_compliance_team"

    def test_default_escalation_target(self):
        policy = make_eu_ai_act_high_risk_policy(allowed_actions={"screen_cv"})
        rule = policy.escalation_for("screen_cv")
        assert rule is not None
        assert rule.escalate_to == "eu_ai_act_compliance_officer"

    def test_empty_allowed_permits_non_prohibited(self):
        """No allowed_actions: ActionPolicy treats empty set as allow-all (except denied)."""
        policy = make_eu_ai_act_high_risk_policy()
        # Empty allowed_actions → require_all_allowed=True but ActionPolicy skips
        # the allowed-set check when allowed_actions is empty, so non-prohibited
        # actions pass through. Prohibited practices are still denied.
        permitted, _ = policy.permits("any_non_prohibited_action")
        assert permitted is True
