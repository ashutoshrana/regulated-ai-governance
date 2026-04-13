"""
09_finra_sec_governance.py — SEC/FINRA broker-dealer AI governance combining
SEC Reg BI, FINRA Rule 3110 supervision, and SEC Model Risk guidance (SR 11-7).

Demonstrates multi-framework AI governance for an AI-driven investment
advisory assistant at a registered broker-dealer, where three compliance
obligations apply simultaneously:

    Framework 1 — SEC Regulation Best Interest (17 CFR Part 240 / Reg BI):
                  AI investment recommendations must be in the retail customer's
                  best interest, not the firm's. Requires: (a) disclosure of
                  conflicts of interest before recommendations, (b) care
                  obligation — reasonable basis for the recommendation based on
                  customer profile, (c) prohibition on recommendations driven
                  by firm inventory positions or compensation incentives.

    Framework 2 — FINRA Rule 3110 (Supervision):
                  Member firms must supervise AI investment recommendations.
                  Concentration risk recommendations (single security or sector
                  > 25% of portfolio) require registered principal review before
                  issuance. Customer suitability data (KYC, risk tolerance,
                  investment objectives) must be current before recommendations.

    Framework 3 — SEC Model Risk Guidance (SR 11-7 principles applied to AI):
                  AI investment models must be registered in the firm's model
                  inventory. Models not validated within 12 months must operate
                  in advisory-only mode with explicit disclosures. Model
                  limitations and uncertainty must be disclosed in output.

Scenarios
---------

  A. Standard diversified recommendation to verified retail customer:
     Reg BI: no conflict, care obligation met. FINRA 3110: no concentration,
     suitability current. Model Risk: model validated within 12 months. ALLOW.

  B. High-concentration recommendation (35% in single security):
     FINRA Rule 3110 requires registered principal review. ESCALATE_HUMAN.

  C. Conflicted product recommendation (firm holds inventory in security):
     Reg BI conflict-of-interest guard blocks recommendation. DENY.

  D. AI model past 12-month validation date:
     SEC Model Risk guard forces advisory-only mode — recommendation can be
     generated but must be presented as non-binding advisory output with
     explicit model limitation disclosure. ADVISORY_ONLY.

  E. Shadow audit mode — all 4 scenarios evaluated without blocking for
     FINRA exam and SEC model risk quarterly review preparation.

No external dependencies required.

Run:
    python examples/09_finra_sec_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------

class CustomerType(str, Enum):
    """SEC Reg BI customer classification."""
    RETAIL = "retail"               # Full Reg BI protections apply
    INSTITUTIONAL = "institutional" # Reg BI does not apply (non-retail)


class RecommendationAction(str, Enum):
    """AI investment recommendation actions."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REBALANCE = "rebalance"
    GENERATE_REPORT = "generate_report"
    GENERATE_SUITABILITY_ANALYSIS = "generate_suitability_analysis"
    SCREEN_SECURITIES = "screen_securities"


class GovernanceOutcome(str, Enum):
    """Investment governance decision outcomes."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"
    ADVISORY_ONLY = "ADVISORY_ONLY"   # For model risk: proceed with limitations disclosed
    SHADOW_ALLOW = "SHADOW_ALLOW"


# ---------------------------------------------------------------------------
# Request context
# ---------------------------------------------------------------------------

@dataclass
class BrokerDealerRequestContext:
    """Context for an AI investment advisory action."""
    request_id: str
    customer_type: CustomerType
    action: RecommendationAction
    securities: list[str]                           # Securities involved in recommendation
    customer_portfolio_value: float                 # USD
    position_concentration_pct: float              # Proposed position as % of portfolio
    firm_inventory_positions: frozenset[str]        # Securities where firm holds inventory
    customer_suitability_days_old: int              # Days since last KYC/suitability update
    model_id: str
    model_last_validated_days_ago: int              # Days since last model validation
    conflicts_disclosed: bool = False               # Whether conflicts were disclosed to customer
    operator_role: str = "ai_agent"


# ---------------------------------------------------------------------------
# Framework 1 — SEC Regulation Best Interest Guard
# ---------------------------------------------------------------------------

class RegBIGuard:
    """
    Enforces SEC Regulation Best Interest (17 CFR Part 240.15l-1).

    Best Interest obligation applies to recommendations to retail customers.
    Key requirements enforced:
    1. Conflict of Interest: AI must not recommend securities where the firm
       holds principal inventory positions unless conflicts are disclosed.
    2. Care Obligation: AI must have a reasonable basis for recommendations
       based on the customer's investment profile.
    3. Disclosure Obligation: Material conflicts must be disclosed before
       the recommendation is made.
    """

    def __init__(self, block_on_violation: bool = True, shadow_mode: bool = False) -> None:
        self._block = block_on_violation
        self._shadow = shadow_mode

    @property
    def name(self) -> str:
        return "SEC_REG_BI"

    def evaluate(self, context: BrokerDealerRequestContext) -> dict:
        violations: list[str] = []

        # Only applies to retail customers
        if context.customer_type != CustomerType.RETAIL:
            return {"framework": self.name, "allowed": True, "violations": [], "shadow_mode": self._shadow}

        # Check 1: Conflict of interest — firm inventory
        conflicted_securities = frozenset(context.securities) & context.firm_inventory_positions
        if conflicted_securities and not context.conflicts_disclosed:
            violations.append(
                f"SEC Reg BI §240.15l-1(a)(2)(iv): firm holds principal inventory position "
                f"in {sorted(conflicted_securities)} — material conflict must be disclosed "
                "to retail customer before recommendation is made"
            )

        # Check 2: Conflicted recommendation even with disclosure — recommendation
        # cannot be driven primarily by firm's interest in liquidating inventory
        if conflicted_securities and context.action in (RecommendationAction.BUY,):
            violations.append(
                f"SEC Reg BI §240.15l-1(a)(2)(ii): BUY recommendation for securities "
                f"in firm inventory ({sorted(conflicted_securities)}) must demonstrate "
                "that recommendation is in customer best interest, not firm's inventory "
                "reduction interest — additional care obligation review required"
            )

        allowed = len(violations) == 0
        if self._shadow:
            allowed = True

        return {
            "framework": self.name,
            "allowed": allowed,
            "violations": violations,
            "conflicted_securities": sorted(conflicted_securities),
            "shadow_mode": self._shadow,
        }


# ---------------------------------------------------------------------------
# Framework 2 — FINRA Rule 3110 Supervision Guard
# ---------------------------------------------------------------------------

class FINRA3110Guard:
    """
    Enforces FINRA Rule 3110 (Supervision) for AI investment recommendations.

    Key requirements:
    1. Concentration Risk: Recommendations placing > 25% of portfolio in a
       single security or sector require registered principal review.
    2. Suitability Freshness: KYC/suitability data must be current. Stale
       suitability data (> 365 days old) requires refresh before recommendations.
    3. Supervisory Review Threshold: Large transactions (> 10% portfolio in
       a single order) require supervisory review regardless of concentration.
    """

    _CONCENTRATION_THRESHOLD_PCT = 25.0    # FINRA guidance threshold
    _SUITABILITY_MAX_DAYS = 365            # Maximum days before suitability refresh required
    _LARGE_TRANSACTION_PCT = 10.0          # Single-order supervisory threshold

    def __init__(self, block_on_violation: bool = True, shadow_mode: bool = False) -> None:
        self._block = block_on_violation
        self._shadow = shadow_mode

    @property
    def name(self) -> str:
        return "FINRA_RULE_3110"

    def evaluate(self, context: BrokerDealerRequestContext) -> dict:
        violations: list[str] = []
        requires_principal_review = False

        # Check 1: Concentration risk
        if context.position_concentration_pct > self._CONCENTRATION_THRESHOLD_PCT:
            requires_principal_review = True
            violations.append(
                f"FINRA Rule 3110: proposed concentration {context.position_concentration_pct:.1f}% "
                f"exceeds {self._CONCENTRATION_THRESHOLD_PCT}% threshold — "
                "registered principal review required before recommendation issuance"
            )

        # Check 2: Suitability data freshness
        if context.customer_suitability_days_old > self._SUITABILITY_MAX_DAYS:
            violations.append(
                f"FINRA Rule 3110 / FINRA Rule 2111: customer suitability data is "
                f"{context.customer_suitability_days_old} days old "
                f"(max: {self._SUITABILITY_MAX_DAYS} days) — "
                "KYC/suitability refresh required before recommendations"
            )

        # Check 3: Large transaction supervisory review
        if (
            context.position_concentration_pct > self._LARGE_TRANSACTION_PCT
            and context.action in (RecommendationAction.BUY, RecommendationAction.REBALANCE)
        ):
            requires_principal_review = True

        allowed = len(violations) == 0
        if self._shadow:
            allowed = True

        return {
            "framework": self.name,
            "allowed": allowed,
            "violations": violations,
            "requires_principal_review": requires_principal_review,
            "shadow_mode": self._shadow,
        }


# ---------------------------------------------------------------------------
# Framework 3 — SEC Model Risk Guard (SR 11-7 principles)
# ---------------------------------------------------------------------------

class SECModelRiskGuard:
    """
    Enforces SEC model risk governance principles (SR 11-7 applied to AI).

    The SEC's 2011 Supervisory Guidance on Model Risk Management (SR 11-7)
    requires financial institutions to maintain model inventories and conduct
    periodic model validations. Applied to AI investment models:

    1. Model Registry: AI models must be registered in the firm's model
       inventory with documentation of methodology, limitations, and use cases.
    2. Validation Cadence: Models must be validated at least annually. Models
       past the validation deadline operate in advisory-only mode.
    3. Limitation Disclosure: Model limitations and uncertainty estimates must
       be disclosed in recommendation outputs.
    """

    _VALIDATION_MAX_DAYS = 365             # Annual validation requirement
    _REGISTERED_MODELS: frozenset[str] = frozenset({
        "INVEST-AI-v3.2", "PORTFOLIO-OPT-v1.8", "RISK-SCORE-v2.1"
    })

    def __init__(
        self,
        registered_models: frozenset[str] | None = None,
        block_on_violation: bool = True,
        shadow_mode: bool = False,
    ) -> None:
        self._registered = registered_models or self._REGISTERED_MODELS
        self._block = block_on_violation
        self._shadow = shadow_mode

    @property
    def name(self) -> str:
        return "SEC_MODEL_RISK_SR11_7"

    def evaluate(self, context: BrokerDealerRequestContext) -> dict:
        violations: list[str] = []
        advisory_only = False

        # Check 1: Model must be in inventory
        if context.model_id not in self._registered:
            violations.append(
                f"SR 11-7 Model Risk: model '{context.model_id}' not in firm model "
                "inventory — all AI models used in customer-facing recommendations "
                "must be registered and documented"
            )

        # Check 2: Validation freshness — advisory-only if stale
        if context.model_last_validated_days_ago > self._VALIDATION_MAX_DAYS:
            advisory_only = True
            violations.append(
                f"SR 11-7 Model Risk: model '{context.model_id}' last validated "
                f"{context.model_last_validated_days_ago} days ago "
                f"(max: {self._VALIDATION_MAX_DAYS} days) — model operates in "
                "advisory-only mode; recommendations must include explicit limitation "
                "disclosure and may not be presented as definitive guidance"
            )

        allowed = not advisory_only and len(violations) == 0
        if self._shadow:
            allowed = True

        return {
            "framework": self.name,
            "allowed": allowed,
            "violations": violations,
            "advisory_only": advisory_only,
            "shadow_mode": self._shadow,
        }


# ---------------------------------------------------------------------------
# Broker-Dealer Governance Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class BrokerDealerAuditRecord:
    """
    SEC/FINRA-compliant audit record for AI investment advisory actions.

    Fields required by FINRA Rule 4511 (books and records) and SEC
    Regulation S-P for AI-driven recommendations:
    - request_id, action, customer_type, securities
    - per-framework evaluation results
    - governance outcome
    - conflicts of interest detected
    - human supervision required flag
    - model risk status
    """
    request_id: str
    action: str
    customer_type: str
    securities: list[str]
    framework_results: list[dict]
    governance_outcome: GovernanceOutcome
    conflicts_detected: list[str]
    principal_review_required: bool
    advisory_only_mode: bool
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BrokerDealerGovernanceOrchestrator:
    """
    Multi-framework governance orchestrator for SEC/FINRA broker-dealer AI.

    Outcome logic:
    - Any Reg BI violation (conflict undisclosed) → DENY
    - FINRA 3110 concentration/supervision → ESCALATE_HUMAN
    - Model Risk (stale validation) → ADVISORY_ONLY (not blocking, but disclosed)
    - All pass → ALLOW
    - Shadow mode → SHADOW_ALLOW regardless
    """

    def __init__(self, *guards: Any, shadow_mode: bool = False) -> None:
        self._guards = guards
        self._shadow = shadow_mode

    def evaluate(self, context: BrokerDealerRequestContext) -> BrokerDealerAuditRecord:
        results: list[dict] = []
        all_allowed = True
        principal_review = False
        advisory_only = False
        deny_outcome = False
        escalate_outcome = False
        all_conflicts: list[str] = []

        for guard in self._guards:
            result = guard.evaluate(context)
            results.append(result)

            if not result.get("allowed", True):
                all_allowed = False

            # Determine outcome type by framework
            if guard.name == "SEC_REG_BI" and not result["allowed"]:
                deny_outcome = True  # Reg BI conflict → hard DENY

            if guard.name == "FINRA_RULE_3110":
                if result.get("requires_principal_review"):
                    escalate_outcome = True
                    principal_review = True

            if guard.name == "SEC_MODEL_RISK_SR11_7" and result.get("advisory_only"):
                advisory_only = True

            conflicts = result.get("conflicted_securities", [])
            all_conflicts.extend(conflicts)

        if self._shadow:
            outcome = GovernanceOutcome.SHADOW_ALLOW
        elif deny_outcome:
            outcome = GovernanceOutcome.DENY
        elif escalate_outcome:
            outcome = GovernanceOutcome.ESCALATE_HUMAN
        elif advisory_only:
            outcome = GovernanceOutcome.ADVISORY_ONLY
        else:
            outcome = GovernanceOutcome.ALLOW

        return BrokerDealerAuditRecord(
            request_id=context.request_id,
            action=context.action.value,
            customer_type=context.customer_type.value,
            securities=context.securities,
            framework_results=results,
            governance_outcome=outcome,
            conflicts_detected=sorted(set(all_conflicts)),
            principal_review_required=principal_review,
            advisory_only_mode=advisory_only,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_scenario(label: str, description: str) -> None:
    print(f"\n{'=' * 72}")
    print(f"Scenario {label}: {description}")
    print("=" * 72)


def _print_result(record: BrokerDealerAuditRecord) -> None:
    print(f"Governance outcome: {record.governance_outcome.value}")
    print(f"Principal review required: {record.principal_review_required}")
    print(f"Advisory-only mode: {record.advisory_only_mode}")
    if record.conflicts_detected:
        print(f"Conflicts of interest detected: {record.conflicts_detected}")
    for result in record.framework_results:
        status = "PASS" if result["allowed"] else ("SHADOW" if result.get("shadow_mode") else "FAIL")
        print(f"  [{status}] {result['framework']}")
        for v in result.get("violations", []):
            print(f"    ! {v}")


# ---------------------------------------------------------------------------
# Main — five scenarios
# ---------------------------------------------------------------------------

def main() -> None:
    reg_bi = RegBIGuard()
    finra_3110 = FINRA3110Guard()
    model_risk = SECModelRiskGuard()
    orchestrator = BrokerDealerGovernanceOrchestrator(reg_bi, finra_3110, model_risk)

    # ------------------------------------------------------------------
    # Scenario A: Standard diversified BUY — all frameworks pass
    # ------------------------------------------------------------------
    _print_scenario(
        "A",
        "Standard diversified BUY recommendation (5% concentration, no conflicts, "
        "model validated 180 days ago). All three frameworks permit.",
    )
    ctx_a = BrokerDealerRequestContext(
        request_id="bd-a001",
        customer_type=CustomerType.RETAIL,
        action=RecommendationAction.BUY,
        securities=["MSFT", "AAPL", "VTI"],
        customer_portfolio_value=250_000.0,
        position_concentration_pct=5.0,
        firm_inventory_positions=frozenset({"GS_BOND_2027", "FIRM_NOTE_A"}),
        customer_suitability_days_old=120,
        model_id="INVEST-AI-v3.2",
        model_last_validated_days_ago=180,
        conflicts_disclosed=False,
    )
    record_a = orchestrator.evaluate(ctx_a)
    _print_result(record_a)

    # ------------------------------------------------------------------
    # Scenario B: High concentration — FINRA 3110 principal review
    # ------------------------------------------------------------------
    _print_scenario(
        "B",
        "High-concentration BUY (35% in single security, retail customer). "
        "FINRA Rule 3110 requires registered principal review → ESCALATE_HUMAN.",
    )
    ctx_b = BrokerDealerRequestContext(
        request_id="bd-b001",
        customer_type=CustomerType.RETAIL,
        action=RecommendationAction.BUY,
        securities=["NVDA"],
        customer_portfolio_value=180_000.0,
        position_concentration_pct=35.0,  # Exceeds 25% threshold
        firm_inventory_positions=frozenset(),
        customer_suitability_days_old=90,
        model_id="INVEST-AI-v3.2",
        model_last_validated_days_ago=90,
        conflicts_disclosed=False,
    )
    record_b = orchestrator.evaluate(ctx_b)
    _print_result(record_b)

    # ------------------------------------------------------------------
    # Scenario C: Conflicted product — firm holds inventory, not disclosed
    # ------------------------------------------------------------------
    _print_scenario(
        "C",
        "BUY recommendation for security in firm's principal inventory "
        "(conflicts not disclosed to retail customer). "
        "SEC Reg BI §240.15l-1(a)(2)(iv) → DENY.",
    )
    ctx_c = BrokerDealerRequestContext(
        request_id="bd-c001",
        customer_type=CustomerType.RETAIL,
        action=RecommendationAction.BUY,
        securities=["GS_BOND_2027"],       # In firm's inventory
        customer_portfolio_value=500_000.0,
        position_concentration_pct=8.0,
        firm_inventory_positions=frozenset({"GS_BOND_2027", "FIRM_NOTE_A"}),
        customer_suitability_days_old=60,
        model_id="INVEST-AI-v3.2",
        model_last_validated_days_ago=200,
        conflicts_disclosed=False,         # Conflict NOT disclosed
    )
    record_c = orchestrator.evaluate(ctx_c)
    _print_result(record_c)

    # ------------------------------------------------------------------
    # Scenario D: Model past validation date — advisory-only mode
    # ------------------------------------------------------------------
    _print_scenario(
        "D",
        "Model last validated 420 days ago (>365 day limit). SR 11-7 model risk: "
        "advisory-only mode — recommendation permitted but must include explicit "
        "limitation disclosure.",
    )
    ctx_d = BrokerDealerRequestContext(
        request_id="bd-d001",
        customer_type=CustomerType.RETAIL,
        action=RecommendationAction.REBALANCE,
        securities=["SPY", "BND", "GLD"],
        customer_portfolio_value=350_000.0,
        position_concentration_pct=12.0,
        firm_inventory_positions=frozenset(),
        customer_suitability_days_old=200,
        model_id="INVEST-AI-v3.2",
        model_last_validated_days_ago=420,  # Past 365-day limit
        conflicts_disclosed=False,
    )
    record_d = orchestrator.evaluate(ctx_d)
    _print_result(record_d)

    # ------------------------------------------------------------------
    # Scenario E: Shadow audit mode — FINRA exam preparation
    # ------------------------------------------------------------------
    _print_scenario(
        "E",
        "Shadow audit mode — all 4 scenarios evaluated without blocking. "
        "Full violation log for FINRA exam and SEC model risk quarterly review.",
    )
    shadow_orchestrator = BrokerDealerGovernanceOrchestrator(
        RegBIGuard(shadow_mode=True),
        FINRA3110Guard(shadow_mode=True),
        SECModelRiskGuard(shadow_mode=True),
        shadow_mode=True,
    )
    shadow_scenarios = [ctx_a, ctx_b, ctx_c, ctx_d]
    shadow_labels = ["A (standard)", "B (concentration)", "C (conflict)", "D (model stale)"]

    for label, ctx in zip(shadow_labels, shadow_scenarios):
        record = shadow_orchestrator.evaluate(ctx)
        violations_by_framework = {
            r["framework"]: len(r.get("violations", []))
            for r in record.framework_results
        }
        print(
            f"  {label}: outcome={record.governance_outcome.value} | "
            f"reg_bi_violations={violations_by_framework.get('SEC_REG_BI', 0)} | "
            f"finra_violations={violations_by_framework.get('FINRA_RULE_3110', 0)} | "
            f"model_risk_violations={violations_by_framework.get('SEC_MODEL_RISK_SR11_7', 0)} | "
            f"conflicts={record.conflicts_detected}"
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * 72}")
    print("GOVERNANCE DESIGN NOTES")
    print("=" * 72)
    print("SEC Reg BI (Retail):")
    print("  - Best interest obligation applies only to retail customers (not institutional)")
    print("  - Firm inventory conflict + undisclosed = DENY (not ESCALATE)")
    print("  - Disclosed conflict + BUY recommendation still requires care obligation review")
    print("\nFINRA Rule 3110:")
    print("  - Concentration threshold (25%) triggers principal review, not denial")
    print("  - Suitability data > 365 days requires refresh, not just review")
    print("  - Large transaction (>10% portfolio) also triggers supervisory review")
    print("\nSEC Model Risk (SR 11-7):")
    print("  - Stale model = ADVISORY_ONLY, not DENY — recommendation is useful")
    print("    but cannot be presented as definitive; limitation must be disclosed")
    print("  - Unregistered model = DENY (no audit trail, no methodology documentation)")
    print("\nOutcome priority: DENY > ESCALATE_HUMAN > ADVISORY_ONLY > ALLOW")


if __name__ == "__main__":
    main()
