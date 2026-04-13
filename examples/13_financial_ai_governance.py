"""
13_financial_ai_governance.py — FRB SR 11-7 Model Risk Management +
Basel III/IV (BCBS 239 + FRTB) + EU DORA (Regulation 2022/2554) +
OCC Bulletin 2011-12 governance for AI models in financial risk management.

Demonstrates a layered governance framework for AI/ML models used in financial
risk management contexts (credit risk, market risk, AML, capital calculation),
where four overlapping regulatory frameworks each impose independent model
governance obligations:

    Layer 1  — FRB SR 11-7 (Model Risk Management, April 2011):
               The Federal Reserve and OCC joint guidance defines a model as "a
               quantitative method, system, or approach that applies statistical,
               economic, financial, or mathematical theories, techniques, and
               assumptions to process input data into quantitative estimates."
               SR 11-7 requires: model inventory with tier classification,
               independent model validation (developer ≠ validator), ongoing
               monitoring with performance thresholds, and challenge mechanisms.
               Tier 1 models (capital, trading, AML) face the highest scrutiny.

    Layer 2  — Basel III/IV (BCBS 239 + CRR III):
               BCBS 239 "Principles for Effective Risk Data Aggregation and
               Risk Reporting" (2013): requires that risk data be accurate,
               complete, timely, and have verified data lineage. For IRB
               (Internal Ratings-Based) credit models and FRTB (Fundamental
               Review of the Trading Book) IMA models, regulatory approval
               from the prudential supervisor is required before use in
               regulatory capital calculation. Backtesting P&L attribution
               is mandatory for FRTB IMA models.

    Layer 3  — EU DORA (Digital Operational Resilience Act, Regulation 2022/2554,
               effective January 2025):
               Applies to all EU financial entities. Classifies ICT systems
               by criticality. Critical ICT systems require documented resilience
               requirements, operational resilience testing (including TLPT),
               incident reporting within 4 hours for major ICT incidents, and
               DORA-compliant contracts with third-party ICT providers. AI models
               embedded in critical ICT functions fall under DORA Art. 11/28.

    Layer 4  — OCC Bulletin 2011-12 (Third-Party Risk Management, 2013/2023):
               Banks must perform due diligence on third-party service providers
               supplying models or AI systems. Critical third-party AI providers
               require contractual access rights for audit, data ownership
               clauses, business continuity requirements, and annual performance
               reassessment.

Scenarios
---------

  A. Tier 1 credit IRB model — fully validated, Basel regulatory approval:
     SR 11-7: Tier 1 + independent validation + resolved findings → approved.
     Basel: IRB + regulatory approval + BCBS 239 lineage → approved.
     DORA: Important ICT + resilience docs present → approved.
     OCC: Third-party standard risk + due diligence done → approved.
     Result: APPROVED_WITH_CONDITIONS (monitoring + PMS conditions).

  B. Tier 1 trading VaR model — validation findings unresolved:
     SR 11-7: Tier 1 + independent validation but UNRESOLVED findings → DENIED.

  C. Third-party AML screening AI — DORA Critical ICT, no resilience docs:
     DORA: Critical ICT third-party without resilience documentation → DENIED.

  D. Tier 3 internal operational model — minimal governance:
     SR 11-7: Tier 3 + no independent validation needed → APPROVED.
     Basel: Not a capital model → no Basel approval needed.
     DORA: Non-critical ICT → no DORA requirements.
     OCC: Low third-party risk → standard due diligence only.
     Result: APPROVED.

No external dependencies required.

Run:
    python examples/13_financial_ai_governance.py
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class ModelTier(str, Enum):
    """
    SR 11-7 model tier classification.

    Tier 1 — highest risk: capital models, trading desk models, AML/BSA models,
             enterprise stress testing (DFAST/CCAR), counterparty credit models.
    Tier 2 — medium risk: credit scoring, pricing models, PPNR projections.
    Tier 3 — lower risk: operational/analytical models, internal reporting.
    """
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"


class ModelApprovalStatus(str, Enum):
    """
    Regulatory approval status for capital/trading models (Basel III/IV).
    """
    APPROVED = "APPROVED"            # Supervisor approval granted
    CONDITIONAL_APPROVAL = "CONDITIONAL_APPROVAL"  # Approved with remediation items
    PENDING_REVIEW = "PENDING_REVIEW"  # Under supervisor review
    REJECTED = "REJECTED"            # Supervisor rejected; cannot use for capital
    NOT_REQUIRED = "NOT_REQUIRED"    # Not a capital/regulatory model


class DORAClassification(str, Enum):
    """
    DORA ICT system criticality classification (Art. 3(22), 3(23)).

    CRITICAL_ICT — supports functions essential for financial stability;
                   full DORA resilience requirements apply
    IMPORTANT_ICT — supports important business processes; DORA applies
                    with lighter oversight
    NON_CRITICAL — standard ICT risk management; DORA Chapter II basic
                   requirements only
    """
    CRITICAL_ICT = "CRITICAL_ICT"
    IMPORTANT_ICT = "IMPORTANT_ICT"
    NON_CRITICAL = "NON_CRITICAL"


class ThirdPartyRiskLevel(str, Enum):
    """
    OCC 2011-12 third-party risk classification.

    CRITICAL — directly supports critical activities; highest due diligence
    HIGH — supports important activities; enhanced due diligence
    MODERATE — standard due diligence
    LOW — limited due diligence required
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class FinancialGovernanceDecision(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DENIED = "DENIED"


# ---------------------------------------------------------------------------
# Model context
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FinancialModelContext:
    """
    Complete description of a financial AI/ML model seeking deployment approval.

    Attributes
    ----------
    model_id : str
    model_name : str
    tier : ModelTier
        SR 11-7 tier classification.
    is_validated_independently : bool
        True if an independent model validation team (developer ≠ validator)
        has completed the validation.
    validation_findings_resolved : bool
        True if all material validation findings have been remediated.
        Irrelevant if is_validated_independently=False.
    ongoing_monitoring_active : bool
        True if the model has active ongoing performance monitoring with
        defined alert thresholds (SR 11-7 §III.C).
    last_performance_review_days_ago : int
        Days since the last formal model performance review.
        SR 11-7 requires annual review for Tier 1/2.
    model_approval_status : ModelApprovalStatus
        Regulatory supervisor approval status (Basel IRB/FRTB).
    is_capital_model : bool
        True if the model output feeds into regulatory capital calculation.
    bcbs239_lineage_verified : bool
        True if BCBS 239 data lineage has been documented and verified.
    frtb_backtesting_passed : bool
        True if FRTB IMA P&L attribution backtesting has passed (Basel IV).
    dora_classification : DORAClassification
        DORA ICT criticality classification.
    dora_resilience_documented : bool
        True if operational resilience requirements (Art. 11) are documented.
    dora_incident_reporting_active : bool
        True if incident reporting mechanism (Art. 19) is in place.
    is_third_party : bool
        True if the model is sourced from a third-party provider.
    third_party_risk_level : ThirdPartyRiskLevel
        OCC 2011-12 risk classification for the third-party provider.
    third_party_due_diligence_complete : bool
        True if vendor due diligence assessment has been completed.
    third_party_contract_has_audit_rights : bool
        True if the vendor contract includes audit access rights.
    intended_jurisdiction : tuple[str, ...]
        Jurisdictions where the model will be used ('US', 'EU', 'UK').
    model_inventory_registered : bool
        True if the model is registered in the model inventory/MRM system.
    """
    model_id: str
    model_name: str
    tier: ModelTier
    is_validated_independently: bool
    validation_findings_resolved: bool
    ongoing_monitoring_active: bool
    last_performance_review_days_ago: int
    model_approval_status: ModelApprovalStatus
    is_capital_model: bool
    bcbs239_lineage_verified: bool
    frtb_backtesting_passed: bool
    dora_classification: DORAClassification
    dora_resilience_documented: bool
    dora_incident_reporting_active: bool
    is_third_party: bool
    third_party_risk_level: ThirdPartyRiskLevel
    third_party_due_diligence_complete: bool
    third_party_contract_has_audit_rights: bool
    intended_jurisdiction: tuple[str, ...]
    model_inventory_registered: bool = True


# ---------------------------------------------------------------------------
# Filter output
# ---------------------------------------------------------------------------


@dataclass
class FinancialFilterResult:
    """Output of a single governance layer."""
    layer: str
    decision: FinancialGovernanceDecision
    violations: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        return self.decision == FinancialGovernanceDecision.DENIED


# ---------------------------------------------------------------------------
# Layer 1 — FRB SR 11-7 Model Risk Management
# ---------------------------------------------------------------------------


class SR117Filter:
    """
    Layer 1: FRB SR 11-7 (April 2011) — Model Risk Management.

    Mandatory requirements by tier:

        Tier 1 (capital, trading, AML, DFAST/CCAR):
            - Independent validation REQUIRED (developer ≠ validator)
            - All material validation findings must be resolved before deployment
            - Ongoing monitoring with defined thresholds REQUIRED
            - Annual performance review REQUIRED (>365 days → DENY)
            - Model inventory registration REQUIRED

        Tier 2 (credit scoring, pricing, PPNR):
            - Independent validation REQUIRED
            - Validation findings resolution REQUIRED
            - Ongoing monitoring REQUIRED
            - Biennial performance review (>730 days → DENY)

        Tier 3 (operational, analytical):
            - Independent validation: recommended, not required
            - Ongoing monitoring: recommended
            - Triennial performance review (>1095 days → DENY)

    All tiers require model inventory registration.
    """

    # Maximum days since performance review by tier
    _MAX_REVIEW_AGE: dict[ModelTier, int] = {
        ModelTier.TIER_1: 365,
        ModelTier.TIER_2: 730,
        ModelTier.TIER_3: 1095,
    }

    def evaluate(self, context: FinancialModelContext) -> FinancialFilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        if not context.model_inventory_registered:
            violations.append(
                "SR 11-7 §III.A — model must be registered in the model inventory "
                "before deployment; unregistered models cannot be validated or monitored"
            )

        tier = context.tier
        max_review_age = self._MAX_REVIEW_AGE[tier]

        if tier in (ModelTier.TIER_1, ModelTier.TIER_2):
            if not context.is_validated_independently:
                violations.append(
                    f"SR 11-7 §III.B — {tier.value} model requires independent "
                    f"validation; model developer cannot be the sole validator "
                    f"(developer ≠ validator principle)"
                )
            elif not context.validation_findings_resolved:
                violations.append(
                    f"SR 11-7 §III.B — {tier.value} model has unresolved material "
                    f"validation findings; deployment blocked until all findings are "
                    f"remediated and validation team signs off"
                )

            if not context.ongoing_monitoring_active:
                violations.append(
                    f"SR 11-7 §III.C — {tier.value} model requires active ongoing "
                    f"performance monitoring with defined alert thresholds and escalation "
                    f"procedures before deployment"
                )

        if context.last_performance_review_days_ago > max_review_age:
            violations.append(
                f"SR 11-7 §III.C — last performance review was "
                f"{context.last_performance_review_days_ago} days ago; "
                f"{tier.value} maximum is {max_review_age} days; "
                f"annual/periodic review overdue"
            )

        if tier == ModelTier.TIER_3:
            notes.append(
                "SR 11-7 Tier 3: independent validation recommended but not required; "
                "simplified validation acceptable for operational/analytical models"
            )

        if not violations:
            if tier == ModelTier.TIER_1:
                conditions.append(
                    "SR 11-7 Tier 1: quarterly performance monitoring reports required; "
                    "material model changes trigger re-validation"
                )
            elif tier == ModelTier.TIER_2:
                conditions.append(
                    "SR 11-7 Tier 2: semi-annual monitoring reports required"
                )

        if violations:
            return FinancialFilterResult(
                layer="SR 11-7",
                decision=FinancialGovernanceDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )
        return FinancialFilterResult(
            layer="SR 11-7",
            decision=FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS if conditions else FinancialGovernanceDecision.APPROVED,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Layer 2 — Basel III/IV (BCBS 239 + FRTB)
# ---------------------------------------------------------------------------


class Basel3Filter:
    """
    Layer 2: Basel III/IV — BCBS 239 + CRR III (Capital Requirements Regulation).

    Rules:
        Capital models (is_capital_model=True):
            - IRB / FRTB IMA: regulatory supervisor approval REQUIRED before
              use in capital calculation (CRR III Art. 143 / FRTB §325az)
            - BCBS 239 data lineage verification REQUIRED for all capital models
              (Principle 2: Accuracy; Principle 3: Completeness)

        FRTB IMA models:
            - P&L attribution backtesting REQUIRED; failed backtesting
              triggers fallback to Standardised Approach (Basel FRTB §325bc)

        Non-capital models:
            - No Basel regulatory approval required
            - BCBS 239 lineage: recommended but not blocking
    """

    def evaluate(self, context: FinancialModelContext) -> FinancialFilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        if not context.is_capital_model:
            notes.append(
                "Basel III/IV: not a capital model — no regulatory supervisor "
                "approval required; standard model governance applies"
            )
            return FinancialFilterResult(
                layer="Basel III/IV",
                decision=FinancialGovernanceDecision.APPROVED,
                notes=notes,
            )

        # Capital model: regulatory approval required
        if context.model_approval_status not in (
            ModelApprovalStatus.APPROVED,
            ModelApprovalStatus.CONDITIONAL_APPROVAL,
        ):
            violations.append(
                f"CRR III Art. 143 / Basel IV FRTB §325az — capital model "
                f"requires regulatory supervisor approval before use in Pillar 1 "
                f"capital calculation; current status: {context.model_approval_status.value}; "
                f"use Standardised Approach until approval granted"
            )

        # BCBS 239 data lineage
        if not context.bcbs239_lineage_verified:
            violations.append(
                "BCBS 239 Principle 2/3 — capital model risk data must have "
                "verified, documented lineage demonstrating accuracy and completeness; "
                "data lineage verification has not been completed"
            )

        # FRTB IMA backtesting (only if this is an IMA market risk model)
        # We identify IMA models as Tier 1 capital models with FRTB scope
        if context.tier == ModelTier.TIER_1 and context.is_capital_model:
            if not context.frtb_backtesting_passed:
                violations.append(
                    "Basel IV FRTB §325bc — FRTB IMA trading model requires P&L "
                    "attribution backtesting to pass; backtesting failure triggers "
                    "mandatory fallback to Standardised Approach for that trading desk"
                )

        if context.model_approval_status == ModelApprovalStatus.CONDITIONAL_APPROVAL:
            conditions.append(
                "CRR III Art. 143 — conditional approval: supervisor remediation items "
                "must be completed within agreed timeline; model output subject to "
                "add-ons until conditions are resolved"
            )

        if violations:
            return FinancialFilterResult(
                layer="Basel III/IV",
                decision=FinancialGovernanceDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )
        return FinancialFilterResult(
            layer="Basel III/IV",
            decision=FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS if conditions else FinancialGovernanceDecision.APPROVED,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Layer 3 — EU DORA
# ---------------------------------------------------------------------------


class DORAFilter:
    """
    Layer 3: EU DORA (Regulation 2022/2554, Art. 11, 19, 28) — Digital
    Operational Resilience Act (effective January 17, 2025).

    Applies to EU financial entities. Rules by ICT classification:

        CRITICAL_ICT:
            - Operational resilience documentation REQUIRED (Art. 11)
            - Incident reporting mechanism REQUIRED (Art. 19 — report within
              4 hours of classification)
            - Third-party DORA-compliant contracts REQUIRED (Art. 28) if
              third-party sourced
            - TLPT (Threat-Led Penetration Testing) required every 3 years
              (Art. 26) — not modeled as a blocking condition here

        IMPORTANT_ICT:
            - Resilience documentation REQUIRED
            - Incident reporting: REQUIRED (24-hour classification, 3 hours report)

        NON_CRITICAL:
            - Basic ICT risk management (Art. 5–10)
            - No DORA resilience documentation or incident reporting required

    Only applies to EU jurisdiction.
    """

    def evaluate(self, context: FinancialModelContext) -> FinancialFilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        # DORA only applies to EU
        if "EU" not in context.intended_jurisdiction:
            notes.append("DORA: EU not in intended_jurisdiction — DORA not applicable")
            return FinancialFilterResult(
                layer="DORA",
                decision=FinancialGovernanceDecision.APPROVED,
                notes=notes,
            )

        dc = context.dora_classification

        if dc == DORAClassification.NON_CRITICAL:
            notes.append(
                "DORA Art. 5–10: NON_CRITICAL ICT — basic ICT risk management "
                "requirements apply; no TLPT or advanced resilience testing required"
            )
            return FinancialFilterResult(
                layer="DORA",
                decision=FinancialGovernanceDecision.APPROVED,
                notes=notes,
            )

        # IMPORTANT_ICT and CRITICAL_ICT
        if not context.dora_resilience_documented:
            violations.append(
                f"DORA Art. 11 — {dc.value} ICT system requires documented "
                f"operational resilience requirements including RTO/RPO targets, "
                f"redundancy architecture, and recovery procedures; not documented"
            )

        if not context.dora_incident_reporting_active:
            violations.append(
                f"DORA Art. 19 — {dc.value} ICT system requires active major "
                f"incident reporting mechanism; initial report due within 4 hours "
                f"(CRITICAL) or 24 hours (IMPORTANT) of classification; not in place"
            )

        # Critical ICT third-party requires DORA-compliant contracts
        if (
            dc == DORAClassification.CRITICAL_ICT
            and context.is_third_party
            and not context.third_party_contract_has_audit_rights
        ):
            violations.append(
                "DORA Art. 28 — CRITICAL ICT third-party provider contract must "
                "include: access/audit rights, data ownership, business continuity "
                "requirements, and sub-outsourcing controls; contract does not meet "
                "DORA Art. 28(2) requirements"
            )

        if dc == DORAClassification.CRITICAL_ICT and not violations:
            conditions.append(
                "DORA Art. 26 — Critical ICT: Threat-Led Penetration Testing (TLPT) "
                "required every 3 years; must be conducted with NCA (national competent "
                "authority) oversight; first TLPT due within 3 years of DORA applicability"
            )

        if violations:
            return FinancialFilterResult(
                layer="DORA",
                decision=FinancialGovernanceDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )
        return FinancialFilterResult(
            layer="DORA",
            decision=FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS if conditions else FinancialGovernanceDecision.APPROVED,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Layer 4 — OCC Bulletin 2011-12 / 2023-17 Third-Party Risk Management
# ---------------------------------------------------------------------------


class OCC2011Filter:
    """
    Layer 4: OCC Bulletin 2011-12 (updated 2023-17) — Third-Party Risk Management.

    Only applies to third-party sourced models (is_third_party=True).
    For internally developed models, this filter is a pass-through.

    Due diligence requirements by risk level:
        CRITICAL: Full due diligence + contractual protections required.
                  Annual reassessment required.
        HIGH:     Enhanced due diligence + key contractual protections.
                  Annual reassessment required.
        MODERATE: Standard due diligence. Periodic (biennial) reassessment.
        LOW:      Simplified due diligence. No audit rights required.
    """

    _DD_REQUIRED_LEVELS: frozenset[ThirdPartyRiskLevel] = frozenset({
        ThirdPartyRiskLevel.CRITICAL,
        ThirdPartyRiskLevel.HIGH,
        ThirdPartyRiskLevel.MODERATE,
    })

    _AUDIT_RIGHTS_REQUIRED_LEVELS: frozenset[ThirdPartyRiskLevel] = frozenset({
        ThirdPartyRiskLevel.CRITICAL,
        ThirdPartyRiskLevel.HIGH,
    })

    def evaluate(self, context: FinancialModelContext) -> FinancialFilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        if not context.is_third_party:
            notes.append(
                "OCC 2011-12: internally developed model — third-party risk "
                "management requirements not applicable"
            )
            return FinancialFilterResult(
                layer="OCC 2011-12",
                decision=FinancialGovernanceDecision.APPROVED,
                notes=notes,
            )

        risk_level = context.third_party_risk_level

        if (
            risk_level in self._DD_REQUIRED_LEVELS
            and not context.third_party_due_diligence_complete
        ):
            violations.append(
                f"OCC 2011-12 §III.A — {risk_level.value} third-party AI provider "
                f"requires completed vendor due diligence assessment covering: "
                f"financial condition, business resumption capabilities, information "
                f"security controls, model governance practices, and regulatory compliance"
            )

        if (
            risk_level in self._AUDIT_RIGHTS_REQUIRED_LEVELS
            and not context.third_party_contract_has_audit_rights
        ):
            violations.append(
                f"OCC 2011-12 §III.B — {risk_level.value} third-party AI provider "
                f"contract must include: bank's right to audit, data ownership clause, "
                f"confidentiality protections, and business continuity requirements; "
                f"contract does not include required provisions"
            )

        if not violations:
            if risk_level in (ThirdPartyRiskLevel.CRITICAL, ThirdPartyRiskLevel.HIGH):
                conditions.append(
                    f"OCC 2011-12 §III.C — {risk_level.value} third-party: annual "
                    f"performance reassessment required; document evidence of ongoing "
                    f"monitoring and any changes to provider's risk profile"
                )

        if violations:
            return FinancialFilterResult(
                layer="OCC 2011-12",
                decision=FinancialGovernanceDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )
        return FinancialFilterResult(
            layer="OCC 2011-12",
            decision=FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS if conditions else FinancialGovernanceDecision.APPROVED,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Governance result + orchestrator
# ---------------------------------------------------------------------------


@dataclass
class FinancialGovernanceResult:
    """Aggregated governance decision across all four layers."""
    model_id: str
    model_name: str
    final_decision: FinancialGovernanceDecision
    layer_results: list[FinancialFilterResult]
    all_violations: list[str]
    all_conditions: list[str]
    all_notes: list[str]
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def summary(self) -> str:
        lines = [
            f"Model: {self.model_name} ({self.model_id})",
            f"Decision: {self.final_decision.value}",
            f"Violations: {len(self.all_violations)} | Conditions: {len(self.all_conditions)}",
        ]
        for v in self.all_violations:
            lines.append(f"  BLOCK: {v}")
        for c in self.all_conditions:
            lines.append(f"  COND:  {c}")
        return "\n".join(lines)


class FinancialModelGovernanceOrchestrator:
    """
    Four-layer financial model risk governance orchestrator.

    Evaluation order:
        1. SR117Filter     — model inventory, validation, monitoring
        2. Basel3Filter    — capital model regulatory approval + BCBS 239
        3. DORAFilter      — EU operational resilience (EU jurisdiction only)
        4. OCC2011Filter   — third-party due diligence (third-party only)

    Final decision:
        - Any DENIED → overall DENIED
        - All APPROVED → overall APPROVED
        - Mix with APPROVED_WITH_CONDITIONS → overall APPROVED_WITH_CONDITIONS
    """

    def __init__(self) -> None:
        self._sr117 = SR117Filter()
        self._basel = Basel3Filter()
        self._dora = DORAFilter()
        self._occ = OCC2011Filter()

    def evaluate(self, context: FinancialModelContext) -> FinancialGovernanceResult:
        layer_results = [
            self._sr117.evaluate(context),
            self._basel.evaluate(context),
            self._dora.evaluate(context),
            self._occ.evaluate(context),
        ]

        all_violations = [v for lr in layer_results for v in lr.violations]
        all_conditions = [c for lr in layer_results for c in lr.conditions]
        all_notes = [n for lr in layer_results for n in lr.notes]

        if any(lr.is_denied for lr in layer_results):
            final = FinancialGovernanceDecision.DENIED
        elif any(lr.decision == FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS for lr in layer_results):
            final = FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS
        else:
            final = FinancialGovernanceDecision.APPROVED

        return FinancialGovernanceResult(
            model_id=context.model_id,
            model_name=context.model_name,
            final_decision=final,
            layer_results=layer_results,
            all_violations=all_violations,
            all_conditions=all_conditions,
            all_notes=all_notes,
        )


# ---------------------------------------------------------------------------
# Demo scenarios
# ---------------------------------------------------------------------------


def _print_result(result: FinancialGovernanceResult) -> None:
    icon = {"APPROVED": "✓", "APPROVED_WITH_CONDITIONS": "⚠", "DENIED": "✗"}[result.final_decision.value]
    print(f"\n  [{icon}] {result.model_name} → {result.final_decision.value}")
    for lr in result.layer_results:
        layer_icon = {"APPROVED": "✓", "APPROVED_WITH_CONDITIONS": "⚠", "DENIED": "✗"}[lr.decision.value]
        print(f"    [{layer_icon}] {lr.layer}")
        for v in lr.violations:
            print(f"         BLOCK: {v[:80]}...")
        for c in lr.conditions:
            print(f"         COND:  {c[:80]}...")


def scenario_a_tier1_irb_model() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO A: Tier 1 Credit IRB Model — Fully Validated, Basel Approved")
    print("=" * 70)

    ctx = FinancialModelContext(
        model_id="MDL-IRB-0441",
        model_name="Probability of Default — Corporate IRB Model",
        tier=ModelTier.TIER_1,
        is_validated_independently=True,
        validation_findings_resolved=True,
        ongoing_monitoring_active=True,
        last_performance_review_days_ago=180,
        model_approval_status=ModelApprovalStatus.APPROVED,
        is_capital_model=True,
        bcbs239_lineage_verified=True,
        frtb_backtesting_passed=True,
        dora_classification=DORAClassification.IMPORTANT_ICT,
        dora_resilience_documented=True,
        dora_incident_reporting_active=True,
        is_third_party=True,
        third_party_risk_level=ThirdPartyRiskLevel.HIGH,
        third_party_due_diligence_complete=True,
        third_party_contract_has_audit_rights=True,
        intended_jurisdiction=("US", "EU"),
        model_inventory_registered=True,
    )

    orch = FinancialModelGovernanceOrchestrator()
    result = orch.evaluate(ctx)
    _print_result(result)


def scenario_b_tier1_trading_unresolved_findings() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO B: Tier 1 Trading VaR Model — Unresolved Validation Findings")
    print("=" * 70)

    ctx = FinancialModelContext(
        model_id="MDL-VAR-0881",
        model_name="Value-at-Risk FRTB IMA Model — Rates Desk",
        tier=ModelTier.TIER_1,
        is_validated_independently=True,
        validation_findings_resolved=False,  # UNRESOLVED!
        ongoing_monitoring_active=True,
        last_performance_review_days_ago=90,
        model_approval_status=ModelApprovalStatus.APPROVED,
        is_capital_model=True,
        bcbs239_lineage_verified=True,
        frtb_backtesting_passed=True,
        dora_classification=DORAClassification.CRITICAL_ICT,
        dora_resilience_documented=True,
        dora_incident_reporting_active=True,
        is_third_party=False,
        third_party_risk_level=ThirdPartyRiskLevel.LOW,
        third_party_due_diligence_complete=True,
        third_party_contract_has_audit_rights=False,
        intended_jurisdiction=("US", "EU"),
        model_inventory_registered=True,
    )

    orch = FinancialModelGovernanceOrchestrator()
    result = orch.evaluate(ctx)
    _print_result(result)


def scenario_c_third_party_aml_no_dora() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO C: Third-Party AML Screening AI — DORA Critical ICT, No Resilience Docs")
    print("=" * 70)

    ctx = FinancialModelContext(
        model_id="MDL-AML-3301",
        model_name="AML Transaction Screening AI (Vendor)",
        tier=ModelTier.TIER_1,
        is_validated_independently=True,
        validation_findings_resolved=True,
        ongoing_monitoring_active=True,
        last_performance_review_days_ago=45,
        model_approval_status=ModelApprovalStatus.NOT_REQUIRED,
        is_capital_model=False,
        bcbs239_lineage_verified=True,
        frtb_backtesting_passed=False,
        dora_classification=DORAClassification.CRITICAL_ICT,
        dora_resilience_documented=False,     # NOT DOCUMENTED
        dora_incident_reporting_active=False, # NOT IN PLACE
        is_third_party=True,
        third_party_risk_level=ThirdPartyRiskLevel.CRITICAL,
        third_party_due_diligence_complete=True,
        third_party_contract_has_audit_rights=False,  # MISSING
        intended_jurisdiction=("EU",),
        model_inventory_registered=True,
    )

    orch = FinancialModelGovernanceOrchestrator()
    result = orch.evaluate(ctx)
    _print_result(result)


def scenario_d_tier3_internal_model() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO D: Tier 3 Internal Operational Model — Minimal Governance Overhead")
    print("=" * 70)

    ctx = FinancialModelContext(
        model_id="MDL-OPS-0012",
        model_name="Branch Staffing Optimization Model",
        tier=ModelTier.TIER_3,
        is_validated_independently=False,  # Not required for Tier 3
        validation_findings_resolved=True,
        ongoing_monitoring_active=False,   # Recommended, not required
        last_performance_review_days_ago=300,
        model_approval_status=ModelApprovalStatus.NOT_REQUIRED,
        is_capital_model=False,
        bcbs239_lineage_verified=False,    # Not required for operational model
        frtb_backtesting_passed=False,
        dora_classification=DORAClassification.NON_CRITICAL,
        dora_resilience_documented=False,
        dora_incident_reporting_active=False,
        is_third_party=False,
        third_party_risk_level=ThirdPartyRiskLevel.LOW,
        third_party_due_diligence_complete=True,
        third_party_contract_has_audit_rights=False,
        intended_jurisdiction=("US",),
        model_inventory_registered=True,
    )

    orch = FinancialModelGovernanceOrchestrator()
    result = orch.evaluate(ctx)
    _print_result(result)


if __name__ == "__main__":
    print("Financial Model Risk Governance")
    print("FRB SR 11-7 + Basel III/IV (BCBS 239 + FRTB) + EU DORA + OCC 2011-12")

    scenario_a_tier1_irb_model()
    scenario_b_tier1_trading_unresolved_findings()
    scenario_c_third_party_aml_no_dora()
    scenario_d_tier3_internal_model()

    print("\n" + "=" * 70)
    print("All scenarios complete.")
    print("=" * 70)
