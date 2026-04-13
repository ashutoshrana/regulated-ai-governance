"""
owasp_llm.py — OWASP LLM Top 10 (2025) action-level governance guards.

The OWASP Top 10 for Large Language Model Applications (2025 edition) identifies
the ten most critical security and safety risks for LLM-based systems. This
module maps each risk to a concrete set of denied agent actions and provides
a composable ``ActionPolicy`` factory.

OWASP LLM Top 10 (2025)
------------------------

- **LLM01 — Prompt Injection**: Malicious prompts manipulate the LLM to
  perform unauthorized actions or bypass controls.
- **LLM02 — Sensitive Information Disclosure**: LLMs inadvertently reveal
  confidential data, PII, or system internals.
- **LLM03 — Supply Chain**: Vulnerabilities in third-party models, datasets,
  plugins, or deployment infrastructure.
- **LLM04 — Data and Model Poisoning**: Manipulation of training or fine-tuning
  data to introduce backdoors or biases.
- **LLM05 — Improper Output Handling**: Downstream consumption of LLM output
  without adequate sanitization or validation.
- **LLM06 — Excessive Agency**: LLM granted overly broad permissions or
  autonomy, leading to unintended real-world actions.
- **LLM07 — System Prompt Leakage**: Exposure of confidential system prompts
  through the model's output.
- **LLM08 — Vector and Embedding Weaknesses**: Adversarial manipulation of
  embeddings or vector stores in RAG pipelines.
- **LLM09 — Misinformation**: Generation of factually incorrect or misleading
  content presented as authoritative.
- **LLM10 — Unbounded Consumption**: Uncontrolled resource usage leading to
  denial-of-service or excessive cost.
"""

from __future__ import annotations

from enum import Enum

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# ---------------------------------------------------------------------------
# Risk enumeration
# ---------------------------------------------------------------------------


class OWASPLLMRisk(str, Enum):
    """OWASP LLM Top 10 (2025) risk identifiers."""

    LLM01_PROMPT_INJECTION = "LLM01_prompt_injection"
    LLM02_SENSITIVE_INFO_DISCLOSURE = "LLM02_sensitive_info_disclosure"
    LLM05_IMPROPER_OUTPUT_HANDLING = "LLM05_improper_output_handling"
    LLM06_EXCESSIVE_AGENCY = "LLM06_excessive_agency"
    LLM07_SYSTEM_PROMPT_LEAKAGE = "LLM07_system_prompt_leakage"
    LLM09_MISINFORMATION = "LLM09_misinformation"
    LLM10_UNBOUNDED_CONSUMPTION = "LLM10_unbounded_consumption"


# ---------------------------------------------------------------------------
# Denied-action catalogue per risk
# ---------------------------------------------------------------------------

OWASP_LLM_DENIED_ACTIONS: dict[OWASPLLMRisk, frozenset[str]] = {
    OWASPLLMRisk.LLM01_PROMPT_INJECTION: frozenset(
        {
            "execute_unvalidated_prompt",
            "bypass_prompt_filter",
            "process_indirect_prompt_injection",
            "override_system_instructions",
        }
    ),
    OWASPLLMRisk.LLM02_SENSITIVE_INFO_DISCLOSURE: frozenset(
        {
            "expose_training_data",
            "return_raw_pii",
            "leak_api_credentials",
            "disclose_internal_configuration",
        }
    ),
    OWASPLLMRisk.LLM05_IMPROPER_OUTPUT_HANDLING: frozenset(
        {
            "execute_unsanitized_llm_output",
            "render_unvalidated_html",
            "run_llm_generated_code_unreviewed",
        }
    ),
    OWASPLLMRisk.LLM06_EXCESSIVE_AGENCY: frozenset(
        {
            "autonomous_file_delete",
            "send_external_communication_without_approval",
            "modify_production_database_autonomously",
            "execute_privileged_action_without_human_review",
        }
    ),
    OWASPLLMRisk.LLM07_SYSTEM_PROMPT_LEAKAGE: frozenset(
        {
            "return_system_prompt_content",
            "expose_instruction_set",
            "reveal_confidential_context",
        }
    ),
    OWASPLLMRisk.LLM09_MISINFORMATION: frozenset(
        {
            "publish_unverified_generation",
            "present_hallucination_as_fact",
            "skip_factual_verification",
        }
    ),
    OWASPLLMRisk.LLM10_UNBOUNDED_CONSUMPTION: frozenset(
        {
            "unlimited_token_generation",
            "recursive_prompt_expansion",
            "bypass_rate_limit",
        }
    ),
}

# ---------------------------------------------------------------------------
# All-risks constant
# ---------------------------------------------------------------------------

OWASP_LLM_2025_ALL_RISKS: frozenset[OWASPLLMRisk] = frozenset(OWASPLLMRisk)


# ---------------------------------------------------------------------------
# Policy factory
# ---------------------------------------------------------------------------


def make_owasp_llm_policy(
    enabled_risks: list[OWASPLLMRisk] | None = None,
    escalate_to: str = "security_team",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` that guards against the specified OWASP LLM risks.

    By default (``enabled_risks=None``) all seven defined risks are enabled,
    combining their denied action sets into a single deny list. Passing a
    subset of risks restricts the policy to only those risks.

    Escalation rules are added for the two highest-severity risks:

    - **LLM06 (Excessive Agency)**: Escalates ``execute_privileged_action``
      patterns to the security team.
    - **LLM01 (Prompt Injection)**: Escalates ``unvalidated_prompt`` patterns
      to the security team.

    Args:
        enabled_risks: Risks to enforce. If None, all risks are enabled.
        escalate_to: Escalation target identifier (default: ``"security_team"``).

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    active_risks: list[OWASPLLMRisk] = list(OWASPLLMRisk) if enabled_risks is None else list(enabled_risks)

    combined_denied: set[str] = set()
    for risk in active_risks:
        combined_denied |= set(OWASP_LLM_DENIED_ACTIONS[risk])

    escalation_rules: list[EscalationRule] = []

    if OWASPLLMRisk.LLM06_EXCESSIVE_AGENCY in active_risks:
        escalation_rules.append(
            EscalationRule(
                condition="excessive_agency_action_detected",
                action_pattern="privileged_action",
                escalate_to=escalate_to,
            )
        )

    if OWASPLLMRisk.LLM01_PROMPT_INJECTION in active_risks:
        escalation_rules.append(
            EscalationRule(
                condition="prompt_injection_attempt_detected",
                action_pattern="unvalidated_prompt",
                escalate_to=escalate_to,
            )
        )

    return ActionPolicy(
        allowed_actions={
            "generate_with_validated_prompt",
            "retrieve_with_sanitized_query",
            "log_llm_interaction",
            "apply_output_filter",
            "request_human_review",
        },
        denied_actions=combined_denied,
        escalation_rules=escalation_rules,
        require_all_allowed=True,
    )
