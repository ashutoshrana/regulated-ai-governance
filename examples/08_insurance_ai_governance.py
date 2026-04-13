"""
08_insurance_ai_governance.py — Insurance sector AI governance combining
NAIC Model Bulletin, state anti-discrimination requirements, and FCRA/GLBA.

Demonstrates multi-framework AI governance for an insurance underwriting and
claims triage assistant, where three compliance obligations apply simultaneously:

    Framework 1 — NAIC Model Bulletin on AI (2023): The National Association
                  of Insurance Commissioners Model Bulletin requires insurers
                  to maintain an AI Model Risk Management (MRM) framework.
                  AI systems must be listed in the MRM inventory. Adverse
                  underwriting decisions above a premium impact threshold
                  require human oversight and attestation.

    Framework 2 — State Anti-Discrimination Regulations: State insurance
                  commissioners prohibit the use of prohibited proxy variables
                  in underwriting and claims decisions. Detected prohibited
                  proxies (ZIP code in certain states, credit score in others)
                  trigger mandatory adverse action documentation. Disparate
                  impact testing is required for models used in rate-setting
                  and eligibility decisions.

    Framework 3 — FCRA / GLBA Safeguards Rule: The Fair Credit Reporting Act
                  requires written disclosure when a consumer credit report
                  contributes to an adverse decision. GLBA prohibits PII from
                  appearing in unprotected model audit logs. The GLBA Safeguards
                  Rule requires encryption of covered information in AI outputs.

Scenarios
---------

  A. Standard auto insurance quote — all frameworks permit.
     NAIC: model is in MRM inventory, no adverse threshold exceeded → ALLOW.
     Anti-discrimination: no prohibited proxies detected → ALLOW.
     FCRA/GLBA: no credit pull required for this product → ALLOW.

  B. Adverse underwriting decision (premium increase >25%) — NAIC triggers
     mandatory human oversight. AI cannot issue the decision alone.

  C. Prohibited proxy feature detected (credit score used in state where
     it is banned for auto underwriting) — state guard blocks the decision;
     escalates to compliance review.

  D. Claims denial scenario — NAIC + FCRA both require explanation artifact
     and human review attestation before AI issues denial.

  E. Audit-only shadow mode — all 4 actions evaluated without blocking;
     discrimination test results logged for quarterly model review (NAIC MRM
     reporting requirement).

No external dependencies required.

Run:
    python examples/08_insurance_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Insurance domain enumerations
# ---------------------------------------------------------------------------

class InsuranceLine(str, Enum):
    """Line of insurance business."""
    PERSONAL_AUTO = "personal_auto"
    HOMEOWNERS = "homeowners"
    COMMERCIAL_PROPERTY = "commercial_property"
    WORKERS_COMP = "workers_comp"
    LIFE = "life"
    HEALTH = "health"


class InsuranceAction(str, Enum):
    """Actions an insurance AI agent may take."""
    GENERATE_AUTO_QUOTE = "generate_auto_quote"
    UNDERWRITE_STANDARD_RISK = "underwrite_standard_risk"
    UNDERWRITE_ADVERSE_DECISION = "underwrite_adverse_decision"  # Premium ↑ or denial
    TRIAGE_CLAIM = "triage_claim"
    APPROVE_CLAIM = "approve_claim"
    DENY_CLAIM = "deny_claim"
    ISSUE_ADVERSE_ACTION_NOTICE = "issue_adverse_action_notice"
    GENERATE_EXPLANATION = "generate_explanation"


class DecisionOutcome(str, Enum):
    """Underwriting or claims decision outcome."""
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    ADVERSE = "adverse"       # Premium increase, coverage reduction, or denial
    DEFERRED_TO_HUMAN = "deferred_to_human"


# ---------------------------------------------------------------------------
# Request context
# ---------------------------------------------------------------------------

@dataclass
class InsuranceRequestContext:
    """Context for an insurance AI agent request."""
    request_id: str
    line_of_business: InsuranceLine
    action: InsuranceAction
    applicant_state: str              # US state — determines applicable anti-discrimination rules
    features_used: dict[str, Any]     # Model input features
    preliminary_outcome: DecisionOutcome
    premium_change_pct: float = 0.0   # Positive = increase, negative = decrease
    credit_report_used: bool = False
    mrm_inventory_id: str | None = None  # NAIC MRM inventory entry ID
    operator_role: str = "ai_agent"


# ---------------------------------------------------------------------------
# Framework 1 — NAIC Model Bulletin Guard
# ---------------------------------------------------------------------------

class NAICModelBulletinGuard:
    """
    Enforces NAIC Model Bulletin on the Use of Algorithms, Predictive Models,
    and Artificial Intelligence (2023).

    Key requirements:
    1. AI systems must be listed in the insurer's Model Risk Management inventory.
    2. Adverse underwriting decisions with significant premium impact require
       human oversight and an attestation record.
    3. Model outputs used in rate-setting or eligibility must be explainable.
    """

    _ADVERSE_HUMAN_OVERSIGHT_THRESHOLD_PCT = 15.0  # Premium increase requiring human review
    _ADVERSE_ACTIONS_REQUIRING_OVERSIGHT = frozenset({
        InsuranceAction.UNDERWRITE_ADVERSE_DECISION,
        InsuranceAction.DENY_CLAIM,
    })

    def __init__(
        self,
        registered_model_ids: frozenset[str],
        block_on_violation: bool = True,
        shadow_mode: bool = False,
    ) -> None:
        self._registered = registered_model_ids
        self._block = block_on_violation
        self._shadow = shadow_mode

    @property
    def name(self) -> str:
        return "NAIC_MODEL_BULLETIN_2023"

    def evaluate(self, context: InsuranceRequestContext) -> dict:
        violations: list[str] = []

        # Check 1: model must be in MRM inventory
        if context.mrm_inventory_id not in self._registered:
            violations.append(
                f"NAIC MRM: model '{context.mrm_inventory_id}' not in MRM inventory — "
                "all AI systems must be registered before use in underwriting/claims"
            )

        # Check 2: adverse decisions above threshold require human oversight
        if (
            context.action in self._ADVERSE_ACTIONS_REQUIRING_OVERSIGHT
            and context.preliminary_outcome == DecisionOutcome.ADVERSE
            and context.premium_change_pct >= self._ADVERSE_HUMAN_OVERSIGHT_THRESHOLD_PCT
        ):
            violations.append(
                f"NAIC MRM: adverse decision with premium impact "
                f"{context.premium_change_pct:.1f}% ≥ {self._ADVERSE_HUMAN_OVERSIGHT_THRESHOLD_PCT}% "
                "threshold — human oversight and attestation required before issuance"
            )

        # Check 3: adverse claims actions require human attestation
        if context.action == InsuranceAction.DENY_CLAIM:
            violations.append(
                "NAIC MRM: claims denial requires human underwriter attestation "
                "and explainability artifact under NAIC Model Bulletin §IV.B"
            )

        allowed = len(violations) == 0
        if self._shadow:
            allowed = True  # Shadow mode: log but do not block

        return {
            "framework": self.name,
            "allowed": allowed,
            "violations": violations,
            "shadow_mode": self._shadow,
        }


# ---------------------------------------------------------------------------
# Framework 2 — State Anti-Discrimination Guard
# ---------------------------------------------------------------------------

# State-level prohibited proxy variable registry
# Real implementations are maintained by compliance teams and updated as
# state insurance departments issue guidance
_STATE_PROHIBITED_PROXIES: dict[str, frozenset[str]] = {
    "CA": frozenset({"credit_score", "zip_code", "education_level", "occupation"}),
    "NY": frozenset({"credit_score", "education_level"}),
    "MI": frozenset({"credit_score"}),
    "WA": frozenset({"credit_score", "zip_code"}),
    "TX": frozenset(),  # Texas permits credit score for auto
    "FL": frozenset({"education_level"}),
    "DEFAULT": frozenset({"religion", "race", "national_origin", "sex"}),  # Federal baseline
}


class StateAntiDiscriminationGuard:
    """
    Enforces state insurance commissioner anti-discrimination requirements.

    Detects prohibited proxy variables in model feature sets and blocks
    underwriting/claims decisions that rely on prohibited inputs. Requires
    adverse action documentation when a decision is adverse and prohibited
    proxies were present (even if the model claims not to use them directly —
    disparate impact doctrine applies).
    """

    def __init__(
        self,
        block_on_violation: bool = True,
        shadow_mode: bool = False,
    ) -> None:
        self._block = block_on_violation
        self._shadow = shadow_mode

    @property
    def name(self) -> str:
        return "STATE_ANTI_DISCRIMINATION"

    def _get_prohibited_proxies(self, state: str) -> frozenset[str]:
        state_specific = _STATE_PROHIBITED_PROXIES.get(state.upper(), frozenset())
        federal_baseline = _STATE_PROHIBITED_PROXIES["DEFAULT"]
        return state_specific | federal_baseline

    def evaluate(self, context: InsuranceRequestContext) -> dict:
        prohibited = self._get_prohibited_proxies(context.applicant_state)
        detected = frozenset(context.features_used.keys()) & prohibited
        violations: list[str] = []

        if detected:
            violations.append(
                f"STATE ANTI-DISCRIMINATION ({context.applicant_state.upper()}): "
                f"prohibited proxy variable(s) detected in model features: {sorted(detected)}. "
                "Decision cannot proceed with these features; escalate to compliance review."
            )

        allowed = len(violations) == 0
        if self._shadow:
            allowed = True

        return {
            "framework": self.name,
            "allowed": allowed,
            "violations": violations,
            "prohibited_proxies_detected": sorted(detected),
            "state": context.applicant_state.upper(),
            "shadow_mode": self._shadow,
        }


# ---------------------------------------------------------------------------
# Framework 3 — FCRA / GLBA Safeguards Guard
# ---------------------------------------------------------------------------

class FCRAGLBAGuard:
    """
    Enforces FCRA and GLBA Safeguards Rule requirements for insurance AI.

    FCRA (15 U.S.C. § 1681):
    - When a consumer credit report contributes to an adverse action, the
      consumer must receive written disclosure of the adverse action, the
      CRA name/address/phone, and their right to dispute.
    - AI cannot issue an adverse action notice without this disclosure.

    GLBA Safeguards Rule (16 CFR Part 314):
    - Non-public personal information (NPI) must not appear unprotected
      in model audit logs or AI output payloads.
    - Covered information includes: SSN, account numbers, income, credit
      history, insurance claim history.
    """

    _ADVERSE_ACTIONS = frozenset({
        InsuranceAction.UNDERWRITE_ADVERSE_DECISION,
        InsuranceAction.DENY_CLAIM,
    })

    _GLBA_NPI_FEATURE_NAMES = frozenset({
        "ssn", "account_number", "income", "credit_history", "claim_history_detail",
        "full_dob", "bank_account",
    })

    def __init__(
        self,
        block_on_violation: bool = True,
        shadow_mode: bool = False,
    ) -> None:
        self._block = block_on_violation
        self._shadow = shadow_mode

    @property
    def name(self) -> str:
        return "FCRA_GLBA_SAFEGUARDS"

    def evaluate(self, context: InsuranceRequestContext) -> dict:
        violations: list[str] = []

        # FCRA check: adverse action with credit report requires disclosure
        if (
            context.action in self._ADVERSE_ACTIONS
            and context.preliminary_outcome == DecisionOutcome.ADVERSE
            and context.credit_report_used
        ):
            violations.append(
                "FCRA §615: adverse action based on credit report requires written "
                "disclosure to consumer (CRA name, address, right to dispute) — "
                "AI cannot issue adverse action notice without this disclosure artifact"
            )

        # GLBA check: NPI features in payload
        npi_features = frozenset(context.features_used.keys()) & self._GLBA_NPI_FEATURE_NAMES
        if npi_features:
            violations.append(
                f"GLBA Safeguards Rule: NPI features present in AI request payload "
                f"({sorted(npi_features)}) — must be encrypted or tokenized before "
                "appearing in model inputs or audit logs"
            )

        allowed = len(violations) == 0
        if self._shadow:
            allowed = True

        return {
            "framework": self.name,
            "allowed": allowed,
            "violations": violations,
            "shadow_mode": self._shadow,
        }


# ---------------------------------------------------------------------------
# Insurance Governance Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class InsuranceGovernanceAuditRecord:
    """
    NAIC-required model audit record for insurance AI decisions.

    Captures: request context, per-framework evaluation results, final
    governance outcome, prohibited proxy findings, and adverse action
    documentation status.
    """
    request_id: str
    action: str
    line_of_business: str
    applicant_state: str
    preliminary_outcome: str
    framework_results: list[dict]
    governance_outcome: str  # "ALLOW", "DENY", or "ESCALATE_HUMAN"
    prohibited_proxies_detected: list[str]
    human_oversight_required: bool
    adverse_action_disclosure_required: bool
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class InsuranceGovernanceOrchestrator:
    """
    Multi-framework governance orchestrator for insurance AI.

    Uses deny-all aggregation: any framework finding a violation blocks the
    action (unless shadow_mode=True for all frameworks). Returns a complete
    InsuranceGovernanceAuditRecord per evaluation.
    """

    def __init__(self, *guards: Any, shadow_mode: bool = False) -> None:
        self._guards = guards
        self._shadow = shadow_mode

    def evaluate(self, context: InsuranceRequestContext) -> InsuranceGovernanceAuditRecord:
        results: list[dict] = []
        all_allowed = True
        human_oversight_required = False
        adverse_action_disclosure = False
        all_prohibited_proxies: list[str] = []

        for guard in self._guards:
            result = guard.evaluate(context)
            results.append(result)

            if not result.get("allowed", True):
                all_allowed = False

            # Collect prohibited proxies from anti-discrimination results
            proxies = result.get("prohibited_proxies_detected", [])
            all_prohibited_proxies.extend(proxies)

            # Determine if human oversight is required (NAIC)
            if guard.name == "NAIC_MODEL_BULLETIN_2023" and not result["allowed"]:
                human_oversight_required = True

            # Determine if adverse action disclosure is required (FCRA)
            if guard.name == "FCRA_GLBA_SAFEGUARDS" and not result["allowed"]:
                adverse_action_disclosure = context.credit_report_used

        if self._shadow:
            governance_outcome = "SHADOW_ALLOW"
        elif not all_allowed:
            governance_outcome = (
                "ESCALATE_HUMAN" if human_oversight_required else "DENY"
            )
        else:
            governance_outcome = "ALLOW"

        return InsuranceGovernanceAuditRecord(
            request_id=context.request_id,
            action=context.action.value,
            line_of_business=context.line_of_business.value,
            applicant_state=context.applicant_state.upper(),
            preliminary_outcome=context.preliminary_outcome.value,
            framework_results=results,
            governance_outcome=governance_outcome,
            prohibited_proxies_detected=sorted(set(all_prohibited_proxies)),
            human_oversight_required=human_oversight_required,
            adverse_action_disclosure_required=adverse_action_disclosure,
        )


# ---------------------------------------------------------------------------
# Scenario helpers
# ---------------------------------------------------------------------------

REGISTERED_MODELS = frozenset({"NAIC-INV-2024-0047", "NAIC-INV-2024-0051"})

def _print_scenario(label: str, description: str) -> None:
    print(f"\n{'=' * 72}")
    print(f"Scenario {label}: {description}")
    print("=" * 72)


def _print_result(record: InsuranceGovernanceAuditRecord) -> None:
    print(f"Governance outcome: {record.governance_outcome}")
    print(f"Human oversight required: {record.human_oversight_required}")
    print(f"Adverse action disclosure required: {record.adverse_action_disclosure_required}")
    if record.prohibited_proxies_detected:
        print(f"Prohibited proxies detected: {record.prohibited_proxies_detected}")
    for result in record.framework_results:
        status = "PASS" if result["allowed"] else ("SHADOW" if result.get("shadow_mode") else "FAIL")
        print(f"  [{status}] {result['framework']}")
        for v in result.get("violations", []):
            print(f"    ! {v}")


# ---------------------------------------------------------------------------
# Main — five scenarios
# ---------------------------------------------------------------------------

def main() -> None:
    naic_guard = NAICModelBulletinGuard(registered_model_ids=REGISTERED_MODELS)
    state_guard = StateAntiDiscriminationGuard()
    fcra_guard = FCRAGLBAGuard()
    orchestrator = InsuranceGovernanceOrchestrator(naic_guard, state_guard, fcra_guard)

    # ------------------------------------------------------------------
    # Scenario A: Standard auto quote — all frameworks pass
    # ------------------------------------------------------------------
    _print_scenario(
        "A",
        "Standard auto quote (CA, no adverse outcome, no prohibited proxies). "
        "All three frameworks permit.",
    )
    ctx_a = InsuranceRequestContext(
        request_id="ins-a001",
        line_of_business=InsuranceLine.PERSONAL_AUTO,
        action=InsuranceAction.GENERATE_AUTO_QUOTE,
        applicant_state="CA",
        features_used={
            "driving_record_points": 0,
            "vehicle_age_years": 3,
            "annual_mileage": 12000,
            "prior_claims_count": 0,
        },
        preliminary_outcome=DecisionOutcome.APPROVED,
        premium_change_pct=0.0,
        credit_report_used=False,
        mrm_inventory_id="NAIC-INV-2024-0047",
    )
    record_a = orchestrator.evaluate(ctx_a)
    _print_result(record_a)

    # ------------------------------------------------------------------
    # Scenario B: Adverse underwriting — NAIC requires human oversight
    # ------------------------------------------------------------------
    _print_scenario(
        "B",
        "Adverse underwriting decision (premium +28%, CA). NAIC MRM: adverse "
        "threshold exceeded — human oversight and attestation required.",
    )
    ctx_b = InsuranceRequestContext(
        request_id="ins-b001",
        line_of_business=InsuranceLine.PERSONAL_AUTO,
        action=InsuranceAction.UNDERWRITE_ADVERSE_DECISION,
        applicant_state="CA",
        features_used={
            "driving_record_points": 8,
            "vehicle_age_years": 12,
            "annual_mileage": 28000,
            "prior_claims_count": 3,
        },
        preliminary_outcome=DecisionOutcome.ADVERSE,
        premium_change_pct=28.0,  # Above 15% threshold
        credit_report_used=False,
        mrm_inventory_id="NAIC-INV-2024-0047",
    )
    record_b = orchestrator.evaluate(ctx_b)
    _print_result(record_b)

    # ------------------------------------------------------------------
    # Scenario C: Prohibited proxy — credit score banned in CA
    # ------------------------------------------------------------------
    _print_scenario(
        "C",
        "Underwriting with credit_score feature (CA). State anti-discrimination "
        "guard detects prohibited proxy — decision blocked, escalate to compliance.",
    )
    ctx_c = InsuranceRequestContext(
        request_id="ins-c001",
        line_of_business=InsuranceLine.PERSONAL_AUTO,
        action=InsuranceAction.UNDERWRITE_STANDARD_RISK,
        applicant_state="CA",
        features_used={
            "driving_record_points": 1,
            "vehicle_age_years": 5,
            "credit_score": 680,       # PROHIBITED in California for auto underwriting
            "annual_mileage": 14000,
        },
        preliminary_outcome=DecisionOutcome.APPROVED,
        premium_change_pct=5.0,
        credit_report_used=True,
        mrm_inventory_id="NAIC-INV-2024-0047",
    )
    record_c = orchestrator.evaluate(ctx_c)
    _print_result(record_c)

    # ------------------------------------------------------------------
    # Scenario D: Claims denial — NAIC + FCRA both require human review
    # ------------------------------------------------------------------
    _print_scenario(
        "D",
        "Claims denial with credit report (NY). NAIC: claims denial requires "
        "human attestation. FCRA §615: adverse action disclosure required.",
    )
    ctx_d = InsuranceRequestContext(
        request_id="ins-d001",
        line_of_business=InsuranceLine.HOMEOWNERS,
        action=InsuranceAction.DENY_CLAIM,
        applicant_state="NY",
        features_used={
            "claim_type": "water_damage",
            "claim_amount_usd": 45000,
            "prior_claims_count": 4,
            "policy_age_days": 90,
        },
        preliminary_outcome=DecisionOutcome.ADVERSE,
        premium_change_pct=0.0,
        credit_report_used=True,
        mrm_inventory_id="NAIC-INV-2024-0047",
    )
    record_d = orchestrator.evaluate(ctx_d)
    _print_result(record_d)

    # ------------------------------------------------------------------
    # Scenario E: Shadow mode — all actions evaluated without blocking
    # ------------------------------------------------------------------
    _print_scenario(
        "E",
        "Audit-only shadow mode — all 4 actions evaluated without blocking. "
        "Full discrimination test results logged for NAIC quarterly MRM review.",
    )
    naic_shadow = NAICModelBulletinGuard(
        registered_model_ids=REGISTERED_MODELS, block_on_violation=False, shadow_mode=True
    )
    state_shadow = StateAntiDiscriminationGuard(block_on_violation=False, shadow_mode=True)
    fcra_shadow = FCRAGLBAGuard(block_on_violation=False, shadow_mode=True)
    shadow_orchestrator = InsuranceGovernanceOrchestrator(
        naic_shadow, state_shadow, fcra_shadow, shadow_mode=True
    )

    shadow_scenarios = [ctx_a, ctx_b, ctx_c, ctx_d]
    shadow_labels = ["A (standard quote)", "B (adverse decision)", "C (prohibited proxy)", "D (claims denial)"]

    for label, ctx in zip(shadow_labels, shadow_scenarios):
        record = shadow_orchestrator.evaluate(ctx)
        naic_viols = sum(
            1 for r in record.framework_results
            if r["framework"] == "NAIC_MODEL_BULLETIN_2023" and r.get("violations")
        )
        state_viols = sum(
            1 for r in record.framework_results
            if r["framework"] == "STATE_ANTI_DISCRIMINATION" and r.get("violations")
        )
        fcra_viols = sum(
            1 for r in record.framework_results
            if r["framework"] == "FCRA_GLBA_SAFEGUARDS" and r.get("violations")
        )
        print(
            f"  {label}: outcome={record.governance_outcome} | "
            f"NAIC_violations={naic_viols} | "
            f"state_violations={state_viols} | "
            f"fcra_violations={fcra_viols} | "
            f"prohibited_proxies={record.prohibited_proxies_detected}"
        )

    print("\nShadow mode: actions execute but violations are logged for MRM quarterly review.")
    print("NAIC Model Bulletin §IV.C requires quarterly model monitoring reports.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * 72}")
    print("INSURANCE GOVERNANCE DESIGN NOTES")
    print("=" * 72)
    print("NAIC Model Bulletin (2023):")
    print("  - All AI systems must be registered in MRM inventory before use")
    print("  - Adverse decisions ≥ 15% premium impact → mandatory human attestation")
    print("  - Claims denials always require human review under §IV.B")
    print("\nState Anti-Discrimination:")
    print("  - Prohibited proxy list is state-specific and changes with regulation")
    print("  - CA bans credit_score + zip_code for personal auto (Insurance Code §1861.02)")
    print("  - NY bans credit_score for auto underwriting (N.Y. Ins. Law §2611)")
    print("  - Disparate impact doctrine: proxy ban applies even if 'not directly used'")
    print("\nFCRA / GLBA:")
    print("  - Credit-based adverse action → written disclosure required (15 U.S.C. §1681m)")
    print("  - NPI in AI payload must be encrypted/tokenized (16 CFR Part 314)")
    print("  - AI cannot issue adverse action notice without FCRA disclosure artifact")


if __name__ == "__main__":
    main()
