"""
14_insurance_ai_governance.py — Four-layer AI governance framework for
insurance underwriting, claims adjudication, and credit-scored pricing.

Demonstrates a multi-layer governance orchestrator where four overlapping
regulatory frameworks each impose independent obligations on AI/ML models
used in insurance contexts:

    Layer 1  — NAIC Model AI Governance Bulletin 2023 (National Association
               of Insurance Commissioners):
               The NAIC bulletin establishes expectations for AI governance
               programs. For HIGH and MEDIUM risk models (models used in
               coverage decisions, claims adjudication, or pricing), insurers
               must document model purpose, validate performance, monitor for
               drift, and ensure explainability of decisions affecting
               policyholders. LOW risk models are subject to inventory
               requirements only.

    Layer 2  — FCRA (Fair Credit Reporting Act, 15 U.S.C. §1681 et seq.):
               When an insurer uses a credit-based insurance score (CBIS) —
               or any consumer report — as a factor in an adverse action
               (denial, cancellation, increased premium), the insurer must
               provide an adverse action notice identifying the specific
               principal reasons for the action (not generic "AI decision").
               Prohibited factors include medical information and certain
               protected characteristics.

    Layer 3  — NY DFS Circular Letter 2019-1 (New York Department of
               Financial Services):
               For AI/ML models used in insurance underwriting in New York,
               insurers must document that no external data sources or
               algorithms act as proxies for race, color, creed, national
               origin, or sex (prohibited bases). Insurers must also maintain
               documentation of all external data sources used in the ECDIS
               (External Consumer Data and Information Sources).

    Layer 4  — ECOA disparate impact (Equal Credit Opportunity Act,
               15 U.S.C. §1691; Regulation B):
               The 4/5 (80%) rule from EEOC Uniform Guidelines: if the
               adverse action rate for a protected class is less than 80%
               of the adverse action rate for the reference group, the model
               exhibits disparate impact and must be reviewed or rejected.
               Insufficient protected class testing data also blocks model
               deployment.

No external dependencies required.

Run:
    python examples/14_insurance_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class InsuranceAIUseCase(str, Enum):
    """Use cases for AI/ML models in the insurance domain."""

    UNDERWRITING_DECISION = "UNDERWRITING_DECISION"       # Coverage approval/denial
    CLAIMS_ADJUDICATION = "CLAIMS_ADJUDICATION"           # Claims approve/deny/amount
    CREDIT_SCORED_PRICING = "CREDIT_SCORED_PRICING"       # Premium based on CBIS
    FRAUD_DETECTION = "FRAUD_DETECTION"                    # Fraud scoring
    MARKETING_SEGMENTATION = "MARKETING_SEGMENTATION"     # Offer targeting
    OPERATIONAL_ANALYTICS = "OPERATIONAL_ANALYTICS"       # Internal ops, no consumer impact


class InsuranceModelRiskLevel(str, Enum):
    """
    NAIC Model AI Governance Bulletin 2023 risk classification.

    HIGH   — Models used in coverage decisions, claims adjudication, or
             pricing with direct policyholder impact.
    MEDIUM — Models with indirect policyholder impact (e.g., fraud scoring
             that triggers further review but does not deny directly).
    LOW    — Internal operational models with no policyholder impact.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FCRAAdverseActionStatus(str, Enum):
    """Whether this model triggers an FCRA adverse action notice requirement."""

    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
    USES_PROHIBITED_FACTOR = "USES_PROHIBITED_FACTOR"


class DisparateImpactStatus(str, Enum):
    """Result of 4/5 rule disparate impact analysis."""

    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class InsuranceGovernanceDecision(str, Enum):
    """Final governance decision for the AI model."""

    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DENIED = "DENIED"


# ---------------------------------------------------------------------------
# Context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InsuranceModelContext:
    """
    Governance review context for an insurance AI/ML model.

    Attributes
    ----------
    model_id : str
        Unique model identifier.
    model_name : str
        Human-readable model name.
    use_case : InsuranceAIUseCase
        Business use case for this model.
    risk_level : InsuranceModelRiskLevel
        NAIC risk classification.
    intended_states : FrozenSet[str]
        US state(s) where the model will be used (e.g., frozenset({"NY", "CA"})).
    is_model_documented : bool
        True if model purpose, methodology, and training data are documented.
    is_model_validated : bool
        True if the model has been validated by an independent team.
    is_monitoring_active : bool
        True if model performance monitoring is deployed and active.
    is_explainability_available : bool
        True if the model can produce human-readable explanations for
        individual decisions (required for adverse action reasons).
    uses_consumer_report : bool
        True if the model uses any consumer report data (FCRA-covered).
    uses_credit_based_insurance_score : bool
        True if the model uses a CBIS (triggers FCRA adverse action rules).
    adverse_action_reasons_specific : bool
        True if the adverse action notice will provide specific reasons
        (e.g., "high outstanding balances") not generic ("AI decision").
    uses_prohibited_factor : bool
        True if the model incorporates medical information, race, color,
        sex, national origin, religion as direct factors (FCRA §604(g)/ECOA).
    ecdis_sources_documented : bool
        True if all external consumer data/information sources used by the
        model are inventoried per NY DFS Circular Letter 2019-1.
    non_discrimination_validated : bool
        True if the ECDIS sources have been validated to not act as proxies
        for protected characteristics (NY DFS requirement).
    disparate_impact_ratio : Optional[float]
        Adverse action rate for protected class / adverse action rate for
        reference group. None if testing data is insufficient.
    protected_class_sample_size : int
        Number of protected class observations in the disparate impact test.
    min_sample_size_for_di_test : int
        Minimum sample size required for a valid disparate impact test.
    """

    model_id: str
    model_name: str
    use_case: InsuranceAIUseCase
    risk_level: InsuranceModelRiskLevel
    intended_states: FrozenSet[str]
    is_model_documented: bool
    is_model_validated: bool
    is_monitoring_active: bool
    is_explainability_available: bool
    uses_consumer_report: bool
    uses_credit_based_insurance_score: bool
    adverse_action_reasons_specific: bool
    uses_prohibited_factor: bool
    ecdis_sources_documented: bool
    non_discrimination_validated: bool
    disparate_impact_ratio: Optional[float]
    protected_class_sample_size: int
    min_sample_size_for_di_test: int = 100


# ---------------------------------------------------------------------------
# Per-layer result
# ---------------------------------------------------------------------------


@dataclass
class InsuranceGovernanceResult:
    """Result of a single governance layer evaluation."""

    layer: str
    decision: InsuranceGovernanceDecision = InsuranceGovernanceDecision.APPROVED
    findings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        return self.decision == InsuranceGovernanceDecision.DENIED

    @property
    def has_conditions(self) -> bool:
        return self.decision == InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS


# ---------------------------------------------------------------------------
# Layer 1 — NAIC Model AI Governance Bulletin 2023
# ---------------------------------------------------------------------------

# Use cases that are HIGH risk under NAIC (direct policyholder impact)
_HIGH_IMPACT_USE_CASES: FrozenSet[InsuranceAIUseCase] = frozenset({
    InsuranceAIUseCase.UNDERWRITING_DECISION,
    InsuranceAIUseCase.CLAIMS_ADJUDICATION,
    InsuranceAIUseCase.CREDIT_SCORED_PRICING,
})


class NAICFilter:
    """
    Layer 1: NAIC Model AI Governance Bulletin 2023.

    HIGH and MEDIUM risk models must satisfy documentation, validation,
    monitoring, and explainability requirements. LOW risk models require
    inventory only (documentation).

    References
    ----------
    NAIC Model AI Governance Bulletin (December 2023)
    NAIC AI Principles (August 2020)
    """

    def evaluate(self, context: InsuranceModelContext) -> InsuranceGovernanceResult:
        result = InsuranceGovernanceResult(layer="NAIC_2023")
        violations: list[str] = []
        conditions: list[str] = []

        # All risk levels: documentation required
        if not context.is_model_documented:
            violations.append(
                "Model documentation missing — purpose, methodology, and training "
                "data must be documented [NAIC Bulletin §III.A]"
            )

        if context.risk_level in (InsuranceModelRiskLevel.HIGH, InsuranceModelRiskLevel.MEDIUM):
            if not context.is_model_validated:
                violations.append(
                    f"Independent model validation required for "
                    f"{context.risk_level.value} risk models [NAIC Bulletin §III.C]"
                )
            if not context.is_monitoring_active:
                violations.append(
                    f"Performance monitoring not active for "
                    f"{context.risk_level.value} risk model [NAIC Bulletin §III.D]"
                )
            if not context.is_explainability_available:
                violations.append(
                    f"Explainability required for {context.risk_level.value} risk model "
                    f"used in {context.use_case.value} [NAIC Bulletin §III.E]"
                )

        if context.risk_level == InsuranceModelRiskLevel.HIGH and context.is_model_validated:
            conditions.append(
                "HIGH risk model: annual model performance review required "
                "[NAIC Bulletin §III.C]"
            )

        if violations:
            result.decision = InsuranceGovernanceDecision.DENIED
            result.findings = violations
        elif conditions:
            result.decision = InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
        else:
            result.decision = InsuranceGovernanceDecision.APPROVED

        return result


# ---------------------------------------------------------------------------
# Layer 2 — FCRA
# ---------------------------------------------------------------------------

# Use cases that trigger adverse action notice requirements when credit is used
_ADVERSE_ACTION_USE_CASES: FrozenSet[InsuranceAIUseCase] = frozenset({
    InsuranceAIUseCase.UNDERWRITING_DECISION,
    InsuranceAIUseCase.CLAIMS_ADJUDICATION,
    InsuranceAIUseCase.CREDIT_SCORED_PRICING,
})


class FCRAFilter:
    """
    Layer 2: FCRA adverse action notice requirements for credit-based
    insurance scoring (15 U.S.C. §1681m).

    When a CBIS or consumer report is used as a factor in an adverse action:
    - The adverse action notice must cite specific principal reasons
    - Generic "AI decision" or "score" alone is insufficient
    - Prohibited factors (medical info, protected characteristics under
      FCRA §604(g)) may not be used as model inputs

    References
    ----------
    15 U.S.C. §1681m — Requirements on users of consumer reports
    15 U.S.C. §1681b(g) — Medical information prohibition
    Reg. V (12 CFR Part 1022) — FCRA implementation
    """

    def evaluate(self, context: InsuranceModelContext) -> InsuranceGovernanceResult:
        result = InsuranceGovernanceResult(layer="FCRA")

        # Prohibited factor check (always applies)
        if context.uses_prohibited_factor:
            result.decision = InsuranceGovernanceDecision.DENIED
            result.findings = [
                "Model uses prohibited factor (medical information or protected "
                "characteristic as direct input) [FCRA §1681b(g); ECOA §1691]"
            ]
            return result

        # Consumer report / CBIS adverse action notice
        if (
            context.uses_consumer_report or context.uses_credit_based_insurance_score
        ) and context.use_case in _ADVERSE_ACTION_USE_CASES:
            if not context.adverse_action_reasons_specific:
                result.decision = InsuranceGovernanceDecision.DENIED
                result.findings = [
                    "Adverse action notice must identify specific principal reasons "
                    "(e.g., 'high outstanding balances') when CBIS is used; "
                    "generic 'AI decision' or 'score' is insufficient "
                    "[FCRA §1681m(a)(2); 12 CFR §1022.72(d)]"
                ]
                return result

            if not context.is_explainability_available:
                result.decision = InsuranceGovernanceDecision.DENIED
                result.findings = [
                    "Explainability capability required to generate specific "
                    "adverse action reasons for CBIS-based decisions "
                    "[FCRA §1681m(a)(2)]"
                ]
                return result

            result.decision = InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = [
                "FCRA adverse action notice required on denial/adverse action; "
                "must identify top specific reasons from model explanation "
                "[FCRA §1681m]"
            ]
            return result

        result.decision = InsuranceGovernanceDecision.APPROVED
        return result


# ---------------------------------------------------------------------------
# Layer 3 — NY DFS Circular Letter 2019-1
# ---------------------------------------------------------------------------


class NYDFSFilter:
    """
    Layer 3: NY DFS Circular Letter 2019-1 — External Consumer Data and
    Information Sources (ECDIS) in insurance underwriting.

    Applies only when "NY" is in context.intended_states.

    Requires:
    - Documentation of all ECDIS sources used in the model
    - Validation that no ECDIS source acts as a proxy for race, color,
      creed, national origin, or sex

    References
    ----------
    NY DFS Circular Letter No. 1 (2019) — Use of External Consumer Data and
    Information Sources in Underwriting for Life Insurance
    NY Insurance Law §2606 — Unfair discrimination
    """

    def evaluate(self, context: InsuranceModelContext) -> InsuranceGovernanceResult:
        result = InsuranceGovernanceResult(layer="NY_DFS_2019")

        # NY DFS only applies to NY operations
        if "NY" not in context.intended_states:
            result.decision = InsuranceGovernanceDecision.APPROVED
            result.findings = ["NY DFS Circular Letter 2019-1 does not apply (no NY operations)"]
            return result

        violations: list[str] = []
        conditions: list[str] = []

        if not context.ecdis_sources_documented:
            violations.append(
                "All external consumer data and information sources (ECDIS) must be "
                "inventoried and documented for NY DFS review "
                "[NY DFS Circular Letter 2019-1 §II.A]"
            )

        if not context.non_discrimination_validated:
            violations.append(
                "ECDIS sources have not been validated to confirm they do not act "
                "as proxies for race, color, creed, national origin, or sex "
                "[NY DFS Circular Letter 2019-1 §II.B; NY Insurance Law §2606]"
            )

        if context.ecdis_sources_documented and context.non_discrimination_validated:
            conditions.append(
                "NY operations: ECDIS documentation and non-discrimination validation "
                "must be maintained and available for DFS examination "
                "[NY DFS Circular Letter 2019-1]"
            )

        if violations:
            result.decision = InsuranceGovernanceDecision.DENIED
            result.findings = violations
        elif conditions:
            result.decision = InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
            result.conditions = conditions
        else:
            result.decision = InsuranceGovernanceDecision.APPROVED

        return result


# ---------------------------------------------------------------------------
# Layer 4 — ECOA Disparate Impact (4/5 Rule)
# ---------------------------------------------------------------------------


class ECOADisparateImpactFilter:
    """
    Layer 4: ECOA disparate impact analysis using the 4/5 (80%) rule.

    From EEOC Uniform Guidelines on Employee Selection (adopted for credit
    and insurance by Regulation B): if the adverse action (denial/surcharge)
    rate for a protected class is less than 80% of the adverse action rate
    for the reference group, the model exhibits disparate impact and must be
    remediated or rejected.

    Insufficient protected class test data (below min_sample_size) blocks
    deployment until adequate testing is conducted.

    References
    ----------
    15 U.S.C. §1691 — ECOA
    12 CFR Part 202 (Regulation B) — ECOA implementation
    CFPB Supervisory Guidance on Model Risk (April 2024)
    EEOC Uniform Guidelines §60-3.4(D) — the 4/5 rule
    """

    _FOUR_FIFTHS_THRESHOLD: float = 0.80

    def evaluate(self, context: InsuranceModelContext) -> InsuranceGovernanceResult:
        result = InsuranceGovernanceResult(layer="ECOA_DISPARATE_IMPACT")

        # Only apply to models with consumer adverse action potential
        if context.use_case not in _ADVERSE_ACTION_USE_CASES:
            result.decision = InsuranceGovernanceDecision.APPROVED
            result.findings = [
                f"ECOA disparate impact analysis not required for "
                f"{context.use_case.value}"
            ]
            return result

        # Insufficient data check
        if context.protected_class_sample_size < context.min_sample_size_for_di_test:
            result.decision = InsuranceGovernanceDecision.DENIED
            result.findings = [
                f"Disparate impact test data insufficient: "
                f"{context.protected_class_sample_size} observations "
                f"(minimum {context.min_sample_size_for_di_test} required). "
                f"Model cannot be deployed until adequate protected class "
                f"testing is conducted [CFPB Model Risk Guidance 2024]"
            ]
            return result

        # No ratio provided but sufficient sample — cannot evaluate
        if context.disparate_impact_ratio is None:
            result.decision = InsuranceGovernanceDecision.DENIED
            result.findings = [
                "Disparate impact ratio not calculated. Protected class adverse "
                "action rate analysis required before deployment [Reg. B §202.6]"
            ]
            return result

        # 4/5 rule
        if context.disparate_impact_ratio < self._FOUR_FIFTHS_THRESHOLD:
            result.decision = InsuranceGovernanceDecision.DENIED
            result.findings = [
                f"Model exhibits disparate impact: protected class adverse action "
                f"rate is {context.disparate_impact_ratio:.1%} of reference group "
                f"rate ({self._FOUR_FIFTHS_THRESHOLD:.0%} threshold). "
                f"Model must be remediated and re-tested [EEOC 4/5 rule; ECOA §1691]"
            ]
            return result

        result.decision = InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
        result.conditions = [
            f"Disparate impact ratio: {context.disparate_impact_ratio:.2f} "
            f"(above 0.80 threshold). Annual re-testing required. "
            f"Document monitoring cadence [Reg. B §202.6]"
        ]
        return result


# ---------------------------------------------------------------------------
# Four-layer orchestrator
# ---------------------------------------------------------------------------


@dataclass
class InsuranceGovernanceReport:
    """Aggregated governance report from all four layers."""

    model_id: str
    model_name: str
    use_case: str
    final_decision: InsuranceGovernanceDecision
    layer_results: List[InsuranceGovernanceResult] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "use_case": self.use_case,
            "final_decision": self.final_decision.value,
            "layers": [
                {
                    "layer": lr.layer,
                    "decision": lr.decision.value,
                    "findings": lr.findings,
                    "conditions": lr.conditions,
                }
                for lr in self.layer_results
            ],
        }


class InsuranceGovernanceOrchestrator:
    """
    Four-layer insurance AI governance orchestrator.

    Evaluation order:
        NAIC 2023  →  FCRA  →  NY DFS  →  ECOA Disparate Impact

    Decision aggregation:
    - Any DENIED layer → final decision is DENIED
    - No DENIED + any APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS
    - All APPROVED → APPROVED

    All layers are evaluated regardless of earlier failures to produce a
    complete audit record.
    """

    def __init__(self) -> None:
        self._naic = NAICFilter()
        self._fcra = FCRAFilter()
        self._ny_dfs = NYDFSFilter()
        self._ecoa = ECOADisparateImpactFilter()

    def evaluate(self, context: InsuranceModelContext) -> InsuranceGovernanceReport:
        layer_results = [
            self._naic.evaluate(context),
            self._fcra.evaluate(context),
            self._ny_dfs.evaluate(context),
            self._ecoa.evaluate(context),
        ]

        # Aggregate decision
        if any(lr.is_denied for lr in layer_results):
            final = InsuranceGovernanceDecision.DENIED
        elif any(lr.has_conditions for lr in layer_results):
            final = InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
        else:
            final = InsuranceGovernanceDecision.APPROVED

        return InsuranceGovernanceReport(
            model_id=context.model_id,
            model_name=context.model_name,
            use_case=context.use_case.value,
            final_decision=final,
            layer_results=layer_results,
        )


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def scenario_a_compliant_underwriting_model() -> None:
    """Fully compliant HIGH risk underwriting model — APPROVED_WITH_CONDITIONS."""
    print("\n--- Scenario A: Compliant Underwriting Model (HIGH risk, NY) ---")
    orchestrator = InsuranceGovernanceOrchestrator()
    ctx = InsuranceModelContext(
        model_id="UW-001",
        model_name="Auto Policy Underwriting Classifier v3",
        use_case=InsuranceAIUseCase.UNDERWRITING_DECISION,
        risk_level=InsuranceModelRiskLevel.HIGH,
        intended_states=frozenset({"NY", "CA", "TX"}),
        is_model_documented=True,
        is_model_validated=True,
        is_monitoring_active=True,
        is_explainability_available=True,
        uses_consumer_report=True,
        uses_credit_based_insurance_score=True,
        adverse_action_reasons_specific=True,
        uses_prohibited_factor=False,
        ecdis_sources_documented=True,
        non_discrimination_validated=True,
        disparate_impact_ratio=0.87,
        protected_class_sample_size=450,
    )
    report = orchestrator.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")
        for c in lr.conditions:
            print(f"    Condition: {c[:80]}...")


def scenario_b_missing_validation() -> None:
    """HIGH risk model without independent validation — DENIED."""
    print("\n--- Scenario B: Missing Independent Validation — DENIED ---")
    orchestrator = InsuranceGovernanceOrchestrator()
    ctx = InsuranceModelContext(
        model_id="CLM-002",
        model_name="Claims Fraud Scoring Model",
        use_case=InsuranceAIUseCase.CLAIMS_ADJUDICATION,
        risk_level=InsuranceModelRiskLevel.HIGH,
        intended_states=frozenset({"TX", "FL"}),
        is_model_documented=True,
        is_model_validated=False,     # Missing
        is_monitoring_active=True,
        is_explainability_available=True,
        uses_consumer_report=False,
        uses_credit_based_insurance_score=False,
        adverse_action_reasons_specific=True,
        uses_prohibited_factor=False,
        ecdis_sources_documented=True,
        non_discrimination_validated=True,
        disparate_impact_ratio=0.91,
        protected_class_sample_size=200,
    )
    report = orchestrator.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    naic = next(lr for lr in report.layer_results if lr.layer == "NAIC_2023")
    for f in naic.findings:
        print(f"  NAIC finding: {f[:90]}...")


def scenario_c_fcra_generic_reasons() -> None:
    """CBIS model without specific adverse action reasons — DENIED."""
    print("\n--- Scenario C: CBIS Without Specific Adverse Action Reasons — DENIED ---")
    orchestrator = InsuranceGovernanceOrchestrator()
    ctx = InsuranceModelContext(
        model_id="CBIS-003",
        model_name="Credit-Based Insurance Pricing Engine",
        use_case=InsuranceAIUseCase.CREDIT_SCORED_PRICING,
        risk_level=InsuranceModelRiskLevel.HIGH,
        intended_states=frozenset({"IL", "OH"}),
        is_model_documented=True,
        is_model_validated=True,
        is_monitoring_active=True,
        is_explainability_available=False,  # Cannot generate specific reasons
        uses_consumer_report=True,
        uses_credit_based_insurance_score=True,
        adverse_action_reasons_specific=False,  # Generic "score" only
        uses_prohibited_factor=False,
        ecdis_sources_documented=True,
        non_discrimination_validated=True,
        disparate_impact_ratio=0.85,
        protected_class_sample_size=300,
    )
    report = orchestrator.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    fcra = next(lr for lr in report.layer_results if lr.layer == "FCRA")
    for f in fcra.findings:
        print(f"  FCRA finding: {f[:90]}...")


def scenario_d_disparate_impact_failure() -> None:
    """Model with 4/5 rule violation — DENIED."""
    print("\n--- Scenario D: Disparate Impact Failure (4/5 rule) — DENIED ---")
    orchestrator = InsuranceGovernanceOrchestrator()
    ctx = InsuranceModelContext(
        model_id="UW-004",
        model_name="Homeowners Underwriting Model v2",
        use_case=InsuranceAIUseCase.UNDERWRITING_DECISION,
        risk_level=InsuranceModelRiskLevel.HIGH,
        intended_states=frozenset({"GA", "AL"}),
        is_model_documented=True,
        is_model_validated=True,
        is_monitoring_active=True,
        is_explainability_available=True,
        uses_consumer_report=False,
        uses_credit_based_insurance_score=False,
        adverse_action_reasons_specific=True,
        uses_prohibited_factor=False,
        ecdis_sources_documented=True,
        non_discrimination_validated=True,
        disparate_impact_ratio=0.72,   # Below 0.80 threshold
        protected_class_sample_size=250,
    )
    report = orchestrator.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    ecoa = next(lr for lr in report.layer_results if lr.layer == "ECOA_DISPARATE_IMPACT")
    for f in ecoa.findings:
        print(f"  ECOA finding: {f[:90]}...")


def scenario_e_low_risk_operational() -> None:
    """LOW risk operational analytics model — minimal requirements."""
    print("\n--- Scenario E: LOW Risk Operational Analytics Model ---")
    orchestrator = InsuranceGovernanceOrchestrator()
    ctx = InsuranceModelContext(
        model_id="OPS-005",
        model_name="Claims Processing Time Predictor",
        use_case=InsuranceAIUseCase.OPERATIONAL_ANALYTICS,
        risk_level=InsuranceModelRiskLevel.LOW,
        intended_states=frozenset({"WA", "OR"}),
        is_model_documented=True,
        is_model_validated=False,      # Not required for LOW risk
        is_monitoring_active=False,    # Not required for LOW risk
        is_explainability_available=False,
        uses_consumer_report=False,
        uses_credit_based_insurance_score=False,
        adverse_action_reasons_specific=True,
        uses_prohibited_factor=False,
        ecdis_sources_documented=True,
        non_discrimination_validated=True,
        disparate_impact_ratio=None,   # ECOA not applicable
        protected_class_sample_size=0,
    )
    report = orchestrator.evaluate(ctx)
    print(f"  Decision: {report.final_decision.value}")
    for lr in report.layer_results:
        print(f"  [{lr.layer}] {lr.decision.value}")


if __name__ == "__main__":
    scenario_a_compliant_underwriting_model()
    scenario_b_missing_validation()
    scenario_c_fcra_generic_reasons()
    scenario_d_disparate_impact_failure()
    scenario_e_low_risk_operational()
    print("\nAll scenarios complete.")
