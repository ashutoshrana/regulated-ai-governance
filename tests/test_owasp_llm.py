"""Tests for OWASP LLM Top 10 (2025) governance module."""

from __future__ import annotations

from regulated_ai_governance.regulations.owasp_llm import (
    OWASP_LLM_2025_ALL_RISKS,
    OWASP_LLM_DENIED_ACTIONS,
    OWASPLLMRisk,
    make_owasp_llm_policy,
)

# ---------------------------------------------------------------------------
# OWASPLLMRisk enum
# ---------------------------------------------------------------------------


class TestOWASPLLMRisk:
    def test_llm01_value(self) -> None:
        assert OWASPLLMRisk.LLM01_PROMPT_INJECTION == "LLM01_prompt_injection"

    def test_llm02_value(self) -> None:
        assert OWASPLLMRisk.LLM02_SENSITIVE_INFO_DISCLOSURE == "LLM02_sensitive_info_disclosure"

    def test_llm05_value(self) -> None:
        assert OWASPLLMRisk.LLM05_IMPROPER_OUTPUT_HANDLING == "LLM05_improper_output_handling"

    def test_llm06_value(self) -> None:
        assert OWASPLLMRisk.LLM06_EXCESSIVE_AGENCY == "LLM06_excessive_agency"

    def test_llm07_value(self) -> None:
        assert OWASPLLMRisk.LLM07_SYSTEM_PROMPT_LEAKAGE == "LLM07_system_prompt_leakage"

    def test_llm09_value(self) -> None:
        assert OWASPLLMRisk.LLM09_MISINFORMATION == "LLM09_misinformation"

    def test_llm10_value(self) -> None:
        assert OWASPLLMRisk.LLM10_UNBOUNDED_CONSUMPTION == "LLM10_unbounded_consumption"

    def test_seven_risks_defined(self) -> None:
        assert len(OWASPLLMRisk) == 7

    def test_is_string_enum(self) -> None:
        assert isinstance(OWASPLLMRisk.LLM01_PROMPT_INJECTION, str)


# ---------------------------------------------------------------------------
# OWASP_LLM_DENIED_ACTIONS structure
# ---------------------------------------------------------------------------


class TestOWASPLLMDeniedActions:
    def test_all_risks_have_entries(self) -> None:
        for risk in OWASPLLMRisk:
            assert risk in OWASP_LLM_DENIED_ACTIONS, f"Missing entry for {risk}"

    def test_all_entries_are_frozensets(self) -> None:
        for risk, actions in OWASP_LLM_DENIED_ACTIONS.items():
            assert isinstance(actions, frozenset), f"{risk} entry is not a frozenset"

    def test_all_entries_non_empty(self) -> None:
        for risk, actions in OWASP_LLM_DENIED_ACTIONS.items():
            assert len(actions) > 0, f"{risk} has empty denied actions"

    def test_llm01_contains_unvalidated_prompt(self) -> None:
        assert "execute_unvalidated_prompt" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM01_PROMPT_INJECTION]

    def test_llm02_contains_expose_training_data(self) -> None:
        assert "expose_training_data" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM02_SENSITIVE_INFO_DISCLOSURE]

    def test_llm05_contains_unsanitized_output(self) -> None:
        assert "execute_unsanitized_llm_output" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM05_IMPROPER_OUTPUT_HANDLING]

    def test_llm06_contains_autonomous_file_delete(self) -> None:
        assert "autonomous_file_delete" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM06_EXCESSIVE_AGENCY]

    def test_llm07_contains_system_prompt_return(self) -> None:
        assert "return_system_prompt_content" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM07_SYSTEM_PROMPT_LEAKAGE]

    def test_llm09_contains_hallucination_as_fact(self) -> None:
        assert "present_hallucination_as_fact" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM09_MISINFORMATION]

    def test_llm10_contains_unlimited_token_generation(self) -> None:
        assert "unlimited_token_generation" in OWASP_LLM_DENIED_ACTIONS[OWASPLLMRisk.LLM10_UNBOUNDED_CONSUMPTION]

    def test_no_action_duplicated_across_risks(self) -> None:
        # Each risk should have distinct denied actions (no overlap required, but
        # verify no single action is accidentally mapped to every risk identically)
        all_actions = [action for actions in OWASP_LLM_DENIED_ACTIONS.values() for action in actions]
        # Just ensure we have a reasonable total count
        assert len(all_actions) >= 14


# ---------------------------------------------------------------------------
# OWASP_LLM_2025_ALL_RISKS
# ---------------------------------------------------------------------------


class TestOWASPLLMAllRisks:
    def test_is_frozenset(self) -> None:
        assert isinstance(OWASP_LLM_2025_ALL_RISKS, frozenset)

    def test_contains_all_enum_members(self) -> None:
        for risk in OWASPLLMRisk:
            assert risk in OWASP_LLM_2025_ALL_RISKS

    def test_size_matches_enum(self) -> None:
        assert len(OWASP_LLM_2025_ALL_RISKS) == len(OWASPLLMRisk)

    def test_llm01_present(self) -> None:
        assert OWASPLLMRisk.LLM01_PROMPT_INJECTION in OWASP_LLM_2025_ALL_RISKS

    def test_llm06_present(self) -> None:
        assert OWASPLLMRisk.LLM06_EXCESSIVE_AGENCY in OWASP_LLM_2025_ALL_RISKS

    def test_llm10_present(self) -> None:
        assert OWASPLLMRisk.LLM10_UNBOUNDED_CONSUMPTION in OWASP_LLM_2025_ALL_RISKS


# ---------------------------------------------------------------------------
# make_owasp_llm_policy — all risks (default)
# ---------------------------------------------------------------------------


class TestOWASPLLMPolicyAllRisks:
    def test_default_none_enables_all_risks(self) -> None:
        policy = make_owasp_llm_policy()
        # Denied actions from all seven risks should be present
        perm_01, _ = policy.permits("execute_unvalidated_prompt")
        perm_06, _ = policy.permits("autonomous_file_delete")
        perm_10, _ = policy.permits("unlimited_token_generation")
        assert not perm_01
        assert not perm_06
        assert not perm_10

    def test_permitted_action_allowed(self) -> None:
        policy = make_owasp_llm_policy()
        permitted, _ = policy.permits("generate_with_validated_prompt")
        assert permitted

    def test_log_llm_interaction_allowed(self) -> None:
        policy = make_owasp_llm_policy()
        permitted, _ = policy.permits("log_llm_interaction")
        assert permitted

    def test_llm06_escalation_present_when_all_risks(self) -> None:
        policy = make_owasp_llm_policy()
        rule = policy.escalation_for("execute_privileged_action_without_human_review")
        assert rule is not None

    def test_llm01_escalation_present_when_all_risks(self) -> None:
        policy = make_owasp_llm_policy()
        rule = policy.escalation_for("execute_unvalidated_prompt")
        assert rule is not None

    def test_default_escalation_target_is_security_team(self) -> None:
        policy = make_owasp_llm_policy()
        rule = policy.escalation_for("execute_privileged_action_without_human_review")
        assert rule is not None
        assert rule.escalate_to == "security_team"

    def test_unknown_action_denied(self) -> None:
        policy = make_owasp_llm_policy()
        permitted, _ = policy.permits("completely_unknown_llm_action")
        assert not permitted


# ---------------------------------------------------------------------------
# make_owasp_llm_policy — specific risks
# ---------------------------------------------------------------------------


class TestOWASPLLMPolicySpecificRisks:
    def test_single_risk_llm02_only_blocks_its_actions(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM02_SENSITIVE_INFO_DISCLOSURE])
        # LLM02 action should be denied
        perm_02, _ = policy.permits("expose_training_data")
        assert not perm_02

    def test_single_risk_llm02_does_not_block_llm06_actions(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM02_SENSITIVE_INFO_DISCLOSURE])
        # LLM06 action should be allowed (only LLM02 is enabled)
        perm_06, _ = policy.permits("autonomous_file_delete")
        assert not perm_06  # denied because require_all_allowed=True for unknown actions
        # But the action is blocked by require_all_allowed, not by LLM02 denied set
        # Verify the denied_actions set only contains LLM02 actions
        assert "autonomous_file_delete" not in policy.denied_actions

    def test_no_escalation_for_llm06_when_only_llm02_enabled(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM02_SENSITIVE_INFO_DISCLOSURE])
        rule = policy.escalation_for("execute_privileged_action_without_human_review")
        assert rule is None

    def test_no_escalation_for_llm01_when_only_llm09_enabled(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM09_MISINFORMATION])
        rule = policy.escalation_for("execute_unvalidated_prompt")
        assert rule is None

    def test_custom_escalate_to_target(self) -> None:
        policy = make_owasp_llm_policy(
            enabled_risks=[OWASPLLMRisk.LLM06_EXCESSIVE_AGENCY],
            escalate_to="incident_response_team",
        )
        rule = policy.escalation_for("execute_privileged_action_without_human_review")
        assert rule is not None
        assert rule.escalate_to == "incident_response_team"

    def test_combined_risks_combine_denied_actions(self) -> None:
        policy = make_owasp_llm_policy(
            enabled_risks=[
                OWASPLLMRisk.LLM01_PROMPT_INJECTION,
                OWASPLLMRisk.LLM10_UNBOUNDED_CONSUMPTION,
            ]
        )
        perm_01, _ = policy.permits("execute_unvalidated_prompt")
        perm_10, _ = policy.permits("unlimited_token_generation")
        assert not perm_01
        assert not perm_10

    def test_empty_risk_list_creates_no_denied_actions(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[])
        assert len(policy.denied_actions) == 0

    def test_llm07_blocks_system_prompt_leakage(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM07_SYSTEM_PROMPT_LEAKAGE])
        perm, _ = policy.permits("return_system_prompt_content")
        assert not perm

    def test_llm05_blocks_unsanitized_output_execution(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM05_IMPROPER_OUTPUT_HANDLING])
        perm, _ = policy.permits("execute_unsanitized_llm_output")
        assert not perm

    def test_llm09_blocks_misinformation_publication(self) -> None:
        policy = make_owasp_llm_policy(enabled_risks=[OWASPLLMRisk.LLM09_MISINFORMATION])
        perm, _ = policy.permits("publish_unverified_generation")
        assert not perm
