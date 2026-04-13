"""
regulations/eu_ai_act.py — EU AI Act (Regulation 2024/1689) governance.

Provides governance-layer controls aligned with EU Regulation 2024/1689
(Artificial Intelligence Act), which entered into force on 2 August 2024
with enforcement phasing through 2026.

**Scope**: Risk classification, prohibited AI practice enforcement, high-risk
system compliance gates, fundamental rights impact assessment (FRIA), human
oversight enforcement, and logging requirements for AI systems operating in
the European Union.

Risk Classification (Articles 6–9)
-------------------------------------

The EU AI Act establishes a tiered risk framework:

  **UNACCEPTABLE** (Article 5 — Prohibited Practices):
    AI systems that pose unacceptable risks to fundamental rights. These are
    categorically banned, including biometric categorisation based on sensitive
    attributes, social scoring by public authorities, subliminal manipulation,
    exploitation of vulnerabilities, and real-time remote biometric identification
    in publicly accessible spaces.

  **HIGH_RISK** (Annex III):
    AI systems that must comply with a full set of obligations before being
    placed on the EU market or put into service. Annex III domains include
    biometric identification, critical infrastructure, education and vocational
    training, employment and workers management, access to essential private and
    public services, law enforcement, migration and border management, and
    administration of justice.

  **LIMITED_RISK** (Article 50 — Transparency):
    AI systems subject to transparency obligations only, such as chatbots and
    deepfakes. Operators must inform natural persons that they are interacting
    with an AI.

  **MINIMAL_RISK**:
    All other AI systems. No mandatory obligations; voluntary codes of conduct
    are encouraged.

Article 5 — Prohibited Practices
------------------------------------

The following practices are absolutely prohibited:

- Biometric categorisation inferring sensitive attributes (race, political
  opinions, religion, sexual orientation).
- Social scoring by public or private actors.
- Subliminal or manipulative techniques exploiting subconscious influences.
- Exploitation of age, disability, or social/economic vulnerabilities.
- Real-time remote biometric identification in publicly accessible spaces
  (with narrow law enforcement exceptions).
- Predictive policing based solely on profiling.
- Emotion recognition in workplaces or educational institutions.
- Facial recognition from the internet or CCTV for facial recognition databases.

High-Risk Obligations (Articles 9–15)
----------------------------------------

Systems classified as HIGH_RISK must satisfy:

  **Article 9** — Risk Management System:
    Continuous risk identification, analysis, and mitigation throughout the
    system lifecycle. Risk management records must be maintained and updated.

  **Article 10** — Data and Data Governance:
    Training, validation, and testing data must meet quality criteria for
    relevance, representativeness, and freedom from errors. Data provenance
    and processing operations must be documented.

  **Article 11** — Technical Documentation:
    Comprehensive technical documentation must be prepared before market
    placement. Documentation must demonstrate compliance with the Act.

  **Article 12** — Record-Keeping (Logging):
    High-risk AI systems must have automatic logging capabilities to record
    events throughout their operational lifetime. Logs must be retained for
    a period appropriate to the intended purpose.

  **Article 14** — Human Oversight:
    High-risk systems must be designed and developed to allow effective human
    oversight. Natural persons must be able to monitor, interrupt, or override
    system outputs. Oversight mechanisms must be assigned to specific roles.

  **Article 15** — Accuracy, Robustness, and Cybersecurity:
    Systems must achieve appropriate accuracy levels with documented
    performance metrics. Robustness against errors, faults, and adversarial
    manipulation must be ensured.

  **Article 43** — Conformity Assessment:
    High-risk systems must undergo conformity assessment before placement on
    the EU market. Certain categories require third-party assessment by a
    notified body.

Fundamental Rights Impact Assessment (Article 27)
---------------------------------------------------

Public sector deployers and certain private deployers of high-risk AI systems
must carry out a Fundamental Rights Impact Assessment (FRIA) before deployment.
The FRIA documents the impact on fundamental rights including dignity, privacy,
non-discrimination, and access to justice.

Defense-in-depth layer
------------------------
EU AI Act controls apply at multiple points in the AI system lifecycle:

    Prohibited check:   Art. 5   — absolute ban on unacceptable-risk actions
    Conformity gate:    Art. 43  — deployment blocked until assessment complete
    FRIA gate:          Art. 27  — FRIA required for HIGH_RISK + public sector
    Logging check:      Art. 12  — logging must be enabled for HIGH_RISK
    Oversight check:    Art. 14  — human oversight measures must be in place
    Use case scope:     Art. 9   — risk management system bounds permitted uses

Usage
------

.. code-block:: python

    from regulated_ai_governance.regulations.eu_ai_act import (
        EUAIActRiskCategory,
        EUAIActSystemProfile,
        EUAIActGovernancePolicy,
        EU_AI_ACT_PROHIBITED_PRACTICES,
        EU_AI_ACT_HIGH_RISK_DOMAINS,
        make_eu_ai_act_minimal_risk_policy,
        make_eu_ai_act_high_risk_policy,
    )

    profile = EUAIActSystemProfile(
        system_id="hr_screening_v2",
        risk_category=EUAIActRiskCategory.HIGH_RISK,
        deployment_approved=True,
        fria_completed=True,
        human_oversight_measures={"recruiter_review", "explainability_dashboard"},
        logging_enabled=True,
        permitted_use_cases={"rank_applications", "screen_qualifications"},
        prohibited_use_cases=set(EU_AI_ACT_PROHIBITED_PRACTICES),
        deployment_approver="cto_alice",
        conformity_assessment_complete=True,
    )

    policy = EUAIActGovernancePolicy(
        profile=profile,
        public_sector_deployer=False,
        audit_sink=my_log.append,
    )
    decision = policy.evaluate_action("rank_applications", actor_id="recruiter_01")
    print(decision.permitted)           # True
    print(decision.human_oversight_required)   # True (high-risk)
    print(policy.last_audit.to_log_entry())
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# ---------------------------------------------------------------------------
# Risk Category Enum
# ---------------------------------------------------------------------------


class EUAIActRiskCategory(str, Enum):
    """
    EU AI Act risk classification tiers (Articles 5–9).

    The four tiers reflect increasing regulatory obligations:

    - ``UNACCEPTABLE``: Absolutely prohibited (Art. 5).
    - ``HIGH_RISK``: Full compliance obligations (Arts. 9–15, Art. 43).
    - ``LIMITED_RISK``: Transparency obligations only (Art. 50).
    - ``MINIMAL_RISK``: No mandatory obligations.
    """

    UNACCEPTABLE = "unacceptable"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"


# ---------------------------------------------------------------------------
# Article 5 — Prohibited Practices
# ---------------------------------------------------------------------------

EU_AI_ACT_PROHIBITED_PRACTICES: frozenset[str] = frozenset(
    {
        # Biometric categorisation inferences (Art. 5(1)(b))
        "biometric_categorisation_sensitive_attributes",
        "infer_race_from_biometrics",
        "infer_political_opinion_from_biometrics",
        "infer_religion_from_biometrics",
        "infer_sexual_orientation_from_biometrics",
        # Social scoring (Art. 5(1)(c))
        "social_scoring",
        "social_credit_evaluation",
        "citizen_trustworthiness_scoring",
        # Subliminal manipulation (Art. 5(1)(a))
        "subliminal_manipulation",
        "subconscious_influence_deployment",
        "exploit_cognitive_bias",
        # Exploitation of vulnerabilities (Art. 5(1)(a))
        "exploit_age_vulnerability",
        "exploit_disability_vulnerability",
        "exploit_social_economic_vulnerability",
        # Real-time biometric ID in public spaces (Art. 5(1)(d))
        "realtime_biometric_identification_public",
        "live_facial_recognition_public_space",
        # Predictive policing (Art. 5(1)(e))
        "predictive_policing_profiling",
        "crime_prediction_individual_profiling",
        # Emotion recognition in sensitive contexts (Art. 5(1)(f))
        "emotion_recognition_workplace",
        "emotion_recognition_education",
        # Facial recognition scraping (Art. 5(1)(g))
        "facial_recognition_database_scraping",
        "internet_image_scraping_facial_recognition",
    }
)

# ---------------------------------------------------------------------------
# Annex III — High-Risk Domains
# ---------------------------------------------------------------------------

EU_AI_ACT_HIGH_RISK_DOMAINS: frozenset[str] = frozenset(
    {
        # Annex III 1 — Biometric identification and categorisation
        "biometric_identification",
        "remote_biometric_identification",
        # Annex III 2 — Critical infrastructure
        "critical_infrastructure_safety",
        "water_supply_management",
        "gas_supply_management",
        "electricity_supply_management",
        "transport_infrastructure_safety",
        # Annex III 3 — Education and vocational training
        "education_access_assessment",
        "student_learning_evaluation",
        "exam_monitoring",
        "educational_outcome_assessment",
        # Annex III 4 — Employment and workers management
        "recruitment_screening",
        "employment_decision",
        "performance_monitoring",
        "task_allocation_workers",
        "promotion_decision",
        "contract_termination_decision",
        # Annex III 5 — Essential private/public services
        "credit_scoring",
        "insurance_risk_assessment",
        "social_benefit_eligibility",
        "emergency_dispatch_prioritization",
        "healthcare_triage",
        # Annex III 6 — Law enforcement
        "crime_risk_assessment",
        "polygraph_testing",
        "deepfake_detection_law_enforcement",
        "evidence_reliability_assessment",
        # Annex III 7 — Migration and border management
        "asylum_application_assessment",
        "visa_application_screening",
        "border_crossing_risk_assessment",
        # Annex III 8 — Administration of justice
        "judicial_outcome_prediction",
        "case_prioritisation_judiciary",
        "legal_aid_eligibility",
        # General public sector administration
        "democratic_process_influence_detection",
        "election_integrity_monitoring",
    }
)

# ---------------------------------------------------------------------------
# System Profile
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class EUAIActSystemProfile:
    """
    Configuration profile for an AI system governed under the EU AI Act.

    Captures the system's risk classification, conformity assessment status,
    fundamental rights impact assessment completion, human oversight measures,
    and operational use case boundaries.

    Attributes:
        system_id: Unique identifier for the AI system (written into every
            audit record).
        risk_category: EU AI Act risk tier (Art. 5–9).
        deployment_approved: True if formal deployment approval has been
            granted. For HIGH_RISK systems, this requires conformity assessment
            completion (Art. 43).
        fria_completed: True if a Fundamental Rights Impact Assessment has
            been carried out (Art. 27). Required for HIGH_RISK systems
            deployed by public sector entities.
        human_oversight_measures: Set of named oversight measures in place
            (Art. 14). Examples: ``"explainability_dashboard"``,
            ``"human_in_the_loop_approval"``. HIGH_RISK systems must have at
            least one measure.
        logging_enabled: True if automatic logging is active (Art. 12).
            Required for HIGH_RISK systems.
        permitted_use_cases: Set of action/use-case names explicitly within
            scope under the risk management system (Art. 9). Any action not
            in this set is blocked (deny-all default).
        prohibited_use_cases: Set of action names explicitly prohibited,
            typically including Art. 5 banned practices. Takes precedence
            over ``permitted_use_cases``.
        deployment_approver: Identifier of the person or process that granted
            deployment approval.
        conformity_assessment_complete: True if conformity assessment has been
            completed under Art. 43. Required for HIGH_RISK before deployment.
    """

    system_id: str
    risk_category: EUAIActRiskCategory
    deployment_approved: bool
    fria_completed: bool
    human_oversight_measures: set[str]
    logging_enabled: bool
    permitted_use_cases: set[str]
    prohibited_use_cases: set[str]
    deployment_approver: str | None = None
    conformity_assessment_complete: bool = False


# ---------------------------------------------------------------------------
# Policy Decision
# ---------------------------------------------------------------------------


@dataclass
class EUAIActPolicyDecision:
    """
    Result of an EU AI Act governance evaluation.

    Attributes:
        permitted: Whether the action is permitted under the applicable
            EU AI Act requirements.
        denial_reason: Human-readable reason if ``permitted`` is False.
        human_oversight_required: True if Art. 14 requires routing to a
            human oversight measure for this action.
        risk_category: The risk tier of the system under evaluation.
    """

    permitted: bool
    denial_reason: str | None
    human_oversight_required: bool
    risk_category: EUAIActRiskCategory


# ---------------------------------------------------------------------------
# Audit Record
# ---------------------------------------------------------------------------


@dataclass
class EUAIActAuditRecord:
    """
    Structured audit record for an EU AI Act governance evaluation.

    Logged to satisfy Art. 12 (record-keeping) and Art. 17 (technical
    documentation) obligations for HIGH_RISK AI systems. Immutable once
    created; use ``content_hash()`` for tamper-evidence.

    Attributes:
        system_id: AI system identifier.
        actor_id: Authenticated principal identifier.
        action_name: The action or use case that was evaluated.
        permitted: Whether the action was permitted.
        risk_category: EU AI Act risk tier of the system.
        denial_reason: Reason for denial if ``permitted`` is False.
        human_oversight_required: Whether Art. 14 oversight was flagged.
        eu_ai_act_articles: EU AI Act articles applied during this evaluation.
        timestamp_utc: ISO 8601 UTC timestamp.
        session_id: Correlation ID for the session.
    """

    system_id: str
    actor_id: str
    action_name: str
    permitted: bool
    risk_category: str
    denial_reason: str | None = None
    human_oversight_required: bool = False
    eu_ai_act_articles: list[str] = field(
        default_factory=lambda: [
            "Art.5",
            "Art.9",
            "Art.12",
            "Art.14",
            "Art.43",
        ]
    )
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = ""

    def to_log_entry(self) -> str:
        """
        Serialize to a structured JSON log line for compliance audit trails.

        The ``framework`` key is set to ``"EU_AI_ACT_2024_1689"`` to allow
        downstream log aggregators to route records to the correct compliance
        pipeline.
        """
        return json.dumps(
            {
                "framework": "EU_AI_ACT_2024_1689",
                "eu_ai_act_articles": sorted(self.eu_ai_act_articles),
                "event": "eu_ai_act_governance_evaluation",
                "system_id": self.system_id,
                "actor_id": self.actor_id,
                "action_name": self.action_name,
                "permitted": self.permitted,
                "risk_category": self.risk_category,
                "denial_reason": self.denial_reason,
                "human_oversight_required": self.human_oversight_required,
                "timestamp_utc": self.timestamp_utc,
                "session_id": self.session_id,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """SHA-256 hash over the JSON log entry for tamper-evidence."""
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()


# ---------------------------------------------------------------------------
# Governance Policy
# ---------------------------------------------------------------------------


class EUAIActGovernancePolicy:
    """
    EU AI Act (Regulation 2024/1689) AI system governance policy.

    Evaluates AI agent actions against the EU AI Act's layered obligations.
    The evaluation order mirrors the regulatory priority: absolute prohibitions
    first, then deployment gates, then operational scope checks.

    Evaluation order
    -----------------
    1. **UNACCEPTABLE risk → deny (Art. 5)**
       If the system's risk category is ``UNACCEPTABLE`` or the action name
       appears in the system's ``prohibited_use_cases``, the action is
       categorically denied. No further checks are performed.

    2. **Deployment approval gate (Art. 43)**
       For HIGH_RISK systems, ``deployment_approved`` must be True and
       ``conformity_assessment_complete`` must be True. Both gates are
       required — partial approval is insufficient.

    3. **FRIA completion check (Art. 27)**
       For HIGH_RISK systems deployed by a public sector entity
       (``public_sector_deployer=True``), the FRIA must be completed before
       any action is permitted.

    4. **Logging requirement check (Art. 12)**
       For HIGH_RISK systems, ``logging_enabled`` must be True. If logging
       is disabled, the action is denied to prevent non-compliant operation.

    5. **Human oversight check (Art. 14)**
       For HIGH_RISK systems, at least one human oversight measure must be
       recorded in ``human_oversight_measures``. An empty set indicates that
       the Art. 14 requirement is not satisfied.

    6. **Permitted/prohibited use case check (Art. 9)**
       The action must be in ``permitted_use_cases`` and must not appear in
       ``prohibited_use_cases``. Unlisted actions are denied (deny-all default).

    Human oversight flag
    ---------------------
    For HIGH_RISK systems that pass all gates, ``human_oversight_required``
    is set to True in the decision and audit record, signalling that the
    caller should route the output through a human oversight measure before
    it is acted upon.

    Args:
        profile: ``EUAIActSystemProfile`` describing the AI system.
        public_sector_deployer: True if the deployer is a public sector
            entity subject to Art. 27 FRIA obligations.
        audit_sink: Optional callable receiving each ``EUAIActAuditRecord``.
        session_id: Correlation ID included in all audit records.
        eu_ai_act_articles: Override the default article IDs in audit records.
    """

    _DEFAULT_ARTICLES = [
        "Art.5",
        "Art.9",
        "Art.12",
        "Art.14",
        "Art.43",
    ]

    def __init__(
        self,
        profile: EUAIActSystemProfile,
        public_sector_deployer: bool = False,
        audit_sink: Any | None = None,
        session_id: str = "",
        eu_ai_act_articles: list[str] | None = None,
    ) -> None:
        self._profile = profile
        self._public_sector_deployer = public_sector_deployer
        self._audit_sink = audit_sink
        self._session_id = session_id
        self._eu_ai_act_articles = eu_ai_act_articles or list(self._DEFAULT_ARTICLES)
        self._last_audit: EUAIActAuditRecord | None = None

    @property
    def last_audit(self) -> EUAIActAuditRecord | None:
        """The ``EUAIActAuditRecord`` produced by the most recent evaluation."""
        return self._last_audit

    @property
    def system_id(self) -> str:
        """The AI system ID from the system profile."""
        return self._profile.system_id

    def evaluate_action(
        self,
        action_name: str,
        actor_id: str = "",
        context: dict[str, Any] | None = None,
    ) -> EUAIActPolicyDecision:
        """
        Evaluate *action_name* against the EU AI Act governance requirements.

        Args:
            action_name: The action or use case to evaluate.
            actor_id: Authenticated principal identifier.
            context: Optional context dict (reserved for future enrichment).

        Returns:
            An ``EUAIActPolicyDecision`` with permit/deny, oversight flag, and
            the applicable risk category.
        """
        _ = context  # reserved for future enrichment

        profile = self._profile

        # -------------------------------------------------------------------
        # Step 1: UNACCEPTABLE risk or prohibited practice (Art. 5)
        # -------------------------------------------------------------------
        if profile.risk_category is EUAIActRiskCategory.UNACCEPTABLE:
            return self._emit_and_return(
                action_name=action_name,
                actor_id=actor_id,
                permitted=False,
                denial_reason=(
                    f"AI system '{profile.system_id}' is classified as UNACCEPTABLE "
                    "risk under EU AI Act Article 5. All actions are categorically "
                    "prohibited. The system must not be deployed."
                ),
                human_oversight=False,
            )

        if action_name in profile.prohibited_use_cases:
            return self._emit_and_return(
                action_name=action_name,
                actor_id=actor_id,
                permitted=False,
                denial_reason=(
                    f"Action '{action_name}' is a prohibited practice under EU AI Act "
                    f"Article 5 for system '{profile.system_id}'. "
                    "Prohibited practices are categorically banned."
                ),
                human_oversight=False,
            )

        # -------------------------------------------------------------------
        # Step 2: Deployment approval gate (Art. 43) — HIGH_RISK only
        # -------------------------------------------------------------------
        if profile.risk_category is EUAIActRiskCategory.HIGH_RISK:
            if not profile.deployment_approved:
                return self._emit_and_return(
                    action_name=action_name,
                    actor_id=actor_id,
                    permitted=False,
                    denial_reason=(
                        f"HIGH_RISK AI system '{profile.system_id}' has not received "
                        "deployment approval (EU AI Act Art. 43). Action blocked until "
                        "conformity assessment and deployment sign-off are complete."
                    ),
                    human_oversight=False,
                )

            if not profile.conformity_assessment_complete:
                return self._emit_and_return(
                    action_name=action_name,
                    actor_id=actor_id,
                    permitted=False,
                    denial_reason=(
                        f"HIGH_RISK AI system '{profile.system_id}' has not completed "
                        "conformity assessment (EU AI Act Art. 43). Deployment approval "
                        "alone is insufficient — conformity assessment must be finalised."
                    ),
                    human_oversight=False,
                )

            # ---------------------------------------------------------------
            # Step 3: FRIA completion check (Art. 27) — public sector
            # ---------------------------------------------------------------
            if self._public_sector_deployer and not profile.fria_completed:
                return self._emit_and_return(
                    action_name=action_name,
                    actor_id=actor_id,
                    permitted=False,
                    denial_reason=(
                        f"HIGH_RISK AI system '{profile.system_id}' is deployed by a "
                        "public sector entity but Fundamental Rights Impact Assessment "
                        "(FRIA) has not been completed (EU AI Act Art. 27). Action "
                        "blocked until FRIA is documented and approved."
                    ),
                    human_oversight=False,
                )

            # ---------------------------------------------------------------
            # Step 4: Logging requirement (Art. 12)
            # ---------------------------------------------------------------
            if not profile.logging_enabled:
                return self._emit_and_return(
                    action_name=action_name,
                    actor_id=actor_id,
                    permitted=False,
                    denial_reason=(
                        f"HIGH_RISK AI system '{profile.system_id}' does not have "
                        "logging enabled (EU AI Act Art. 12). Automatic logging is "
                        "mandatory for high-risk systems. Action blocked."
                    ),
                    human_oversight=False,
                )

            # ---------------------------------------------------------------
            # Step 5: Human oversight measures (Art. 14)
            # ---------------------------------------------------------------
            if not profile.human_oversight_measures:
                return self._emit_and_return(
                    action_name=action_name,
                    actor_id=actor_id,
                    permitted=False,
                    denial_reason=(
                        f"HIGH_RISK AI system '{profile.system_id}' has no human "
                        "oversight measures configured (EU AI Act Art. 14). At least "
                        "one oversight measure is required. Action blocked."
                    ),
                    human_oversight=False,
                )

        # -------------------------------------------------------------------
        # Step 6: Permitted/prohibited use case scope (Art. 9)
        # -------------------------------------------------------------------
        if action_name not in profile.permitted_use_cases:
            return self._emit_and_return(
                action_name=action_name,
                actor_id=actor_id,
                permitted=False,
                denial_reason=(
                    f"Action '{action_name}' is outside the permitted use case scope "
                    f"for system '{profile.system_id}' (EU AI Act Art. 9 risk "
                    "management system). Only documented use cases may be executed."
                ),
                human_oversight=False,
            )

        # -------------------------------------------------------------------
        # Permitted — flag human oversight for HIGH_RISK (Art. 14)
        # -------------------------------------------------------------------
        human_oversight = profile.risk_category is EUAIActRiskCategory.HIGH_RISK

        return self._emit_and_return(
            action_name=action_name,
            actor_id=actor_id,
            permitted=True,
            denial_reason=None,
            human_oversight=human_oversight,
        )

    def _emit_and_return(
        self,
        action_name: str,
        actor_id: str,
        permitted: bool,
        denial_reason: str | None,
        human_oversight: bool,
    ) -> EUAIActPolicyDecision:
        record = EUAIActAuditRecord(
            system_id=self._profile.system_id,
            actor_id=actor_id,
            action_name=action_name,
            permitted=permitted,
            risk_category=self._profile.risk_category.value,
            denial_reason=denial_reason,
            human_oversight_required=human_oversight,
            eu_ai_act_articles=self._eu_ai_act_articles,
            session_id=self._session_id,
        )
        self._last_audit = record
        if self._audit_sink is not None:
            self._audit_sink(record)

        return EUAIActPolicyDecision(
            permitted=permitted,
            denial_reason=denial_reason,
            human_oversight_required=human_oversight,
            risk_category=self._profile.risk_category,
        )


# ---------------------------------------------------------------------------
# ActionPolicy Factory Functions
# ---------------------------------------------------------------------------


def make_eu_ai_act_minimal_risk_policy(
    allowed_actions: set[str] | None = None,
    denied_actions: set[str] | None = None,
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for a MINIMAL_RISK EU AI Act system.

    Minimal-risk systems have no mandatory EU AI Act obligations. This factory
    produces a permissive policy that allows all specified actions and denies
    Art. 5 prohibited practices by default.

    Args:
        allowed_actions: Set of permitted action names. If None, defaults to
            an empty set (allow-all when ``require_all_allowed=False``).
        denied_actions: Set of denied action names. If None, defaults to
            ``EU_AI_ACT_PROHIBITED_PRACTICES`` to prevent accidental invocation
            of banned practices from minimal-risk systems.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_denied = denied_actions if denied_actions is not None else set(EU_AI_ACT_PROHIBITED_PRACTICES)
    effective_allowed = allowed_actions if allowed_actions is not None else set()
    require_all = bool(effective_allowed)
    return ActionPolicy(
        allowed_actions=effective_allowed,
        denied_actions=effective_denied,
        require_all_allowed=require_all,
    )


def make_eu_ai_act_high_risk_policy(
    allowed_actions: set[str] | None = None,
    escalate_to: str = "eu_ai_act_compliance_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for a HIGH_RISK EU AI Act system.

    High-risk systems require strict action scope enforcement and escalation
    routing for any actions that require human oversight (Art. 14). All Art. 5
    prohibited practices are denied.

    Args:
        allowed_actions: Set of documented permitted actions from the risk
            management system (Art. 9). If None, defaults to an empty set
            (``ActionPolicy`` treats an empty allowed set as allow-all except
            for denied_actions; provide an explicit set to enforce strict scope).
        escalate_to: Escalation target for human oversight routing (Art. 14).
            Defaults to ``"eu_ai_act_compliance_officer"``.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_allowed = allowed_actions if allowed_actions is not None else set()
    return ActionPolicy(
        allowed_actions=effective_allowed,
        denied_actions=set(EU_AI_ACT_PROHIBITED_PRACTICES),
        escalation_rules=[
            EscalationRule(
                condition="eu_ai_act_art14_human_oversight",
                action_pattern="",  # matches all actions — human oversight for everything
                escalate_to=escalate_to,
            ),
        ],
        require_all_allowed=True,
    )
