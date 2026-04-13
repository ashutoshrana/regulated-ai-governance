"""
nist_ai_rmf.py — NIST AI Risk Management Framework 1.0 + AI 600-1 GenAI Profile.

Published by the National Institute of Standards and Technology (NIST):

- **AI RMF 1.0** (January 2023): Voluntary framework for managing risks
  associated with the design, development, deployment, and use of AI systems.
  Organized around four core functions: GOVERN, MAP, MEASURE, MANAGE.
- **NIST AI 600-1** (July 2024): GenAI Profile — extends the AI RMF with
  profiles specific to generative AI risks including confabulation (hallucination),
  data bias, human-AI configuration (overreliance), information integrity,
  and harmful bias in output.

Framework Functions
-------------------

- **GOVERN (GV)**: Organizational practices, accountability, culture, and
  policy to manage AI risks throughout the lifecycle.
- **MAP (MP)**: Context establishment and risk identification — classifying
  the AI system, its intended use, and risk categories.
- **MEASURE (MS)**: Risk analysis and assessment — quantifying and qualifying
  identified AI risks using metrics and evaluation methods.
- **MANAGE (MG)**: Risk treatment — mitigating, transferring, avoiding, or
  accepting identified risks with documented rationale.

GenAI-Specific Risk Categories (AI 600-1)
------------------------------------------

- **Confabulation** (hallucination): AI generates plausible but false information.
- **Data Bias**: Training data biases propagated into outputs.
- **Human-AI Configuration** (overreliance): Undue reliance on AI outputs
  without appropriate human oversight.
- **Information Integrity**: Accuracy and truthfulness of AI-generated content.
- **Data Privacy**: Risk of generating outputs that expose personal data.
- **Explainability**: Inability to explain AI reasoning or outputs.
- **Harmful Bias**: Discriminatory or harmful outputs from bias in the model.
- **Security**: Adversarial attacks, prompt injection, and model abuse.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class NISTAIRMFFunction(str, Enum):
    """The four core functions of the NIST AI Risk Management Framework 1.0."""

    GOVERN = "GOVERN"
    MAP = "MAP"
    MEASURE = "MEASURE"
    MANAGE = "MANAGE"


class NISTAIRMFRiskCategory(str, Enum):
    """
    AI risk categories from NIST AI RMF 1.0 and NIST AI 600-1 GenAI Profile.

    Attribute names follow the AI 600-1 terminology.
    """

    CONFABULATION = "confabulation"
    DATA_BIAS = "data_bias"
    HUMAN_AI_CONFIGURATION = "human_ai_configuration"
    INFORMATION_INTEGRITY = "information_integrity"
    DATA_PRIVACY = "data_privacy"
    EXPLAINABILITY = "explainability"
    HARMFUL_BIAS = "harmful_bias"
    SECURITY = "security"


# ---------------------------------------------------------------------------
# High-risk GenAI action catalogue
# ---------------------------------------------------------------------------

NIST_GENAI_HIGH_RISK_ACTIONS: frozenset[str] = frozenset(
    {
        "unverified_generation",
        "autonomous_decision_without_oversight",
        "share_pii_without_consent",
        "cross_purpose_data_use",
        "automated_decision",
        "override_human_review",
        "generate_without_bias_check",
        "deploy_without_impact_assessment",
        "disable_explainability_logging",
        "bypass_content_filter",
        "generate_without_fact_check",
        "expose_training_data",
    }
)


# ---------------------------------------------------------------------------
# Risk assessment record
# ---------------------------------------------------------------------------


@dataclass
class NISTAIRMFRiskAssessment:
    """
    A structured risk assessment record aligned with the NIST AI RMF.

    Captures the four-function risk posture (GOVERN/MAP/MEASURE/MANAGE)
    for a given AI system, together with the identified risk categories and
    overall risk level.

    Attributes:
        system_id: Identifier for the AI system being assessed.
        risk_categories: List of applicable NIST AI RMF / AI 600-1 risk categories.
        risk_level: Overall assessed risk level: ``"critical"``, ``"high"``,
            ``"medium"``, or ``"low"``.
        gov_measures: List of GOVERN-function controls applied.
        map_measures: List of MAP-function activities completed.
        measure_measures: List of MEASURE-function evaluations performed.
        manage_measures: List of MANAGE-function mitigations in place.
        timestamp_utc: ISO-8601 UTC timestamp of this assessment.
        assessor_id: Optional identifier for the assessor.
    """

    system_id: str
    risk_categories: list[NISTAIRMFRiskCategory]
    risk_level: str  # "critical" | "high" | "medium" | "low"
    gov_measures: list[str]
    map_measures: list[str]
    measure_measures: list[str]
    manage_measures: list[str]
    timestamp_utc: str
    assessor_id: str = ""

    def to_log_entry(self) -> str:
        """Serialize to a structured JSON log entry for NIST AI RMF audit purposes."""
        return json.dumps(
            {
                "framework": "NIST_AI_RMF_1_0",
                "record_type": "risk_assessment",
                "system_id": self.system_id,
                "risk_categories": sorted(c.value for c in self.risk_categories),
                "risk_level": self.risk_level,
                "gov_measures": sorted(self.gov_measures),
                "map_measures": sorted(self.map_measures),
                "measure_measures": sorted(self.measure_measures),
                "manage_measures": sorted(self.manage_measures),
                "timestamp_utc": self.timestamp_utc,
                "assessor_id": self.assessor_id,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """SHA-256 hash for tamper-evidence in the AI risk assessment audit trail."""
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()


# ---------------------------------------------------------------------------
# Policy factory
# ---------------------------------------------------------------------------

from regulated_ai_governance.policy import ActionPolicy, EscalationRule  # noqa: E402


def make_nist_ai_rmf_policy(
    risk_categories: list[NISTAIRMFRiskCategory] | None = None,
    escalate_high_risk_to: str = "ai_risk_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` tailored to the identified NIST AI RMF risk categories.

    The policy applies risk-category-specific denied actions and escalation rules:

    - **CONFABULATION**: Denies ``unverified_generation`` and
      ``autonomous_decision_without_oversight``.
    - **DATA_PRIVACY**: Denies ``share_pii_without_consent`` and
      ``cross_purpose_data_use``.
    - **HUMAN_AI_CONFIGURATION** (overreliance): Escalates ``automated_decision``
      actions to human review.
    - **HARMFUL_BIAS**: Denies ``generate_without_bias_check``.
    - **SECURITY**: Denies ``bypass_content_filter``.

    Args:
        risk_categories: List of applicable risk categories. If None or empty,
            a broad default set of GenAI risks is applied.
        escalate_high_risk_to: Escalation target for high-risk actions.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_categories: list[NISTAIRMFRiskCategory] = (
        risk_categories if risk_categories is not None else list(NISTAIRMFRiskCategory)
    )

    denied: set[str] = set()
    escalation_rules: list[EscalationRule] = []

    if NISTAIRMFRiskCategory.CONFABULATION in effective_categories:
        denied |= {"unverified_generation", "autonomous_decision_without_oversight"}
        escalation_rules.append(
            EscalationRule(
                condition="confabulation_risk_action_detected",
                action_pattern="unverified_generation",
                escalate_to=escalate_high_risk_to,
            )
        )

    if NISTAIRMFRiskCategory.DATA_PRIVACY in effective_categories:
        denied |= {"share_pii_without_consent", "cross_purpose_data_use"}
        escalation_rules.append(
            EscalationRule(
                condition="data_privacy_risk_action_detected",
                action_pattern="pii",
                escalate_to=escalate_high_risk_to,
            )
        )

    if NISTAIRMFRiskCategory.HUMAN_AI_CONFIGURATION in effective_categories:
        escalation_rules.append(
            EscalationRule(
                condition="overreliance_risk_detected",
                action_pattern="automated_decision",
                escalate_to=escalate_high_risk_to,
            )
        )

    if NISTAIRMFRiskCategory.HARMFUL_BIAS in effective_categories:
        denied.add("generate_without_bias_check")

    if NISTAIRMFRiskCategory.SECURITY in effective_categories:
        denied.add("bypass_content_filter")

    if NISTAIRMFRiskCategory.INFORMATION_INTEGRITY in effective_categories:
        denied.add("generate_without_fact_check")

    if NISTAIRMFRiskCategory.EXPLAINABILITY in effective_categories:
        denied.add("disable_explainability_logging")

    return ActionPolicy(
        allowed_actions={
            "read_ai_system_profile",
            "log_risk_assessment",
            "generate_rmf_report",
            "run_bias_evaluation",
            "request_human_review",
            "record_governance_measure",
        },
        denied_actions=denied,
        escalation_rules=escalation_rules,
        require_all_allowed=True,
    )
