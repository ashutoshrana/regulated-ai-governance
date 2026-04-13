"""
12_medtech_ai_governance.py — FDA Software as a Medical Device (SaMD) +
IEC 62304 Software Lifecycle + ISO 14971 Risk Management + EU MDR/MDCG 2021-1
governance for AI systems used in medical device contexts.

Demonstrates a layered governance framework for AI models embedded in or used
alongside medical devices, where four overlapping regulatory frameworks each
impose independent safety and lifecycle obligations:

    Layer 1  — IEC 62304:2006+AMD1:2015 (Software Lifecycle):
               The international standard for medical device software lifecycle.
               Assigns each software item to Safety Class A (no injury possible),
               B (serious injury possible but not death), or C (death or serious
               injury possible). Class C software requires comprehensive testing,
               formal change management, and verified requirement traceability.
               Class B requires documented design verification. Class A permits
               lighter-weight lifecycle processes.

    Layer 2  — ISO 14971:2019 (Risk Management):
               The foundational medical device risk management standard. Requires
               hazard identification, risk estimation (probability × severity),
               risk evaluation against acceptability criteria, and risk control
               measures. Residual risk after controls must be demonstrated ALARP
               (As Low As Reasonably Practicable). Unacceptable residual risk
               blocks deployment.

    Layer 3  — FDA SaMD Guidance (2019) + 21 CFR Part 820 (QSR):
               The FDA classifies SaMD by its intended function and patient
               contact level. Class I (lowest risk) devices require general
               controls only. Class II requires 510(k) premarket notification
               and special controls. Class III requires PMA (Premarket Approval)
               with clinical evidence. AI/ML-based SaMD must follow FDA's
               Predetermined Change Control Plan (PCCP) for adaptive algorithms.

    Layer 4  — EU MDR 2017/745 + MDCG 2021-1 (AI in Medical Devices):
               The European Medical Device Regulation classifies devices into
               Class I, IIa, IIb, and III. The MDCG 2021-1 guidance specifically
               addresses AI/ML qualification as a medical device accessory or
               standalone device. Class III EU devices require Notified Body
               certification. The EU AI Act (Annex I, §5) designates medical
               device AI as high-risk.

Scenarios
---------

  A. AI-powered diagnostic imaging assistant (Class IIb / Safety Class C):
     IEC 62304: Class C requires full lifecycle compliance + change control.
     ISO 14971: All identified hazards must have residual risk = ACCEPTABLE.
     FDA: Class II → 510(k) cleared + special controls enforced.
     EU MDR: Class IIb → Notified Body required.
     Result: APPROVED with conditions (PCCP required).

  B. Administrative AI (scheduling optimizer) — minimal risk:
     IEC 62304: Safety Class A — lightweight lifecycle permitted.
     ISO 14971: No patient hazard pathway → ACCEPTABLE residual risk.
     FDA: Not a SaMD (no clinical decision support) → exempt from 510(k).
     EU MDR: Class I → self-certification only.
     Result: APPROVED.

  C. High-risk autonomous treatment recommendation (Class III):
     IEC 62304: Class C + formal verification required.
     ISO 14971: Unacceptable residual risk detected → BLOCK.
     FDA: Class III → PMA required (no 510(k) eligibility).
     EU MDR: Class III → Notified Body + clinical evaluation.
     Result: DENIED — unacceptable residual risk.

  D. Monitoring AI with pending validation study:
     FDA: 510(k) pathway but study incomplete → DENY.
     ISO 14971: Risk ALARP but pending validation.
     Result: DENIED — clearance pathway not completed.

No external dependencies required.

Run:
    python examples/12_medtech_ai_governance.py
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class IEC62304SafetyClass(str, Enum):
    """
    IEC 62304 Software Safety Classification.

    Determines the rigor of required software lifecycle activities.
    """
    CLASS_A = "CLASS_A"   # No injury or damage to health possible
    CLASS_B = "CLASS_B"   # Non-serious injury possible
    CLASS_C = "CLASS_C"   # Death or serious injury possible


class FDASaMDClass(str, Enum):
    """
    FDA Device Classification (21 CFR Parts 862–892).

    Drives the applicable pre-market pathway.
    """
    CLASS_I = "CLASS_I"    # General controls only; most exempt from 510(k)
    CLASS_II = "CLASS_II"  # 510(k) premarket notification + special controls
    CLASS_III = "CLASS_III"  # PMA (Premarket Approval) required


class FDAClearancePathway(str, Enum):
    """FDA clearance/approval pathway for SaMD."""
    EXEMPT = "EXEMPT"             # 510(k) exempt — general controls only
    K510_CLEARED = "K510_CLEARED" # 510(k) cleared
    PMA_APPROVED = "PMA_APPROVED" # Premarket Approval granted
    DE_NOVO = "DE_NOVO"           # De Novo granted (novel low-to-moderate risk)
    NOT_CLEARED = "NOT_CLEARED"   # No clearance/approval obtained


class EUMDRClass(str, Enum):
    """EU MDR 2017/745 Device Classification."""
    CLASS_I = "CLASS_I"    # Low risk; self-certification
    CLASS_IIA = "CLASS_IIA"  # Medium risk; Notified Body for QMS
    CLASS_IIB = "CLASS_IIB"  # Medium-high risk; Notified Body for technical file
    CLASS_III = "CLASS_III"  # High risk; Notified Body + clinical evaluation


class ISO14971RiskLevel(str, Enum):
    """ISO 14971 residual risk after risk controls applied."""
    ACCEPTABLE = "ACCEPTABLE"             # Risk acceptable; no further action
    ALARP = "ALARP"                       # As Low As Reasonably Practicable; acceptable
    UNACCEPTABLE = "UNACCEPTABLE"         # Risk exceeds acceptability criteria; block


class SaMDChangeType(str, Enum):
    """
    Types of AI/ML algorithm changes per FDA PCCP guidance.

    Predetermined Change Control Plan (PCCP) allows post-market modifications
    within pre-specified bounds without requiring new 510(k) submission.
    """
    PERFORMANCE_IMPROVEMENT = "PERFORMANCE_IMPROVEMENT"  # Within PCCP bounds
    INTENDED_USE_CHANGE = "INTENDED_USE_CHANGE"          # New 510(k) required
    OUTPUT_TYPE_CHANGE = "OUTPUT_TYPE_CHANGE"            # New 510(k) required
    MINOR_BUG_FIX = "MINOR_BUG_FIX"                    # No PCCP required


class DeploymentDecision(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DENIED = "DENIED"


# ---------------------------------------------------------------------------
# Request context and AI system descriptor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MedicalAIRequestContext:
    """
    Full description of an AI system seeking deployment approval.

    Attributes
    ----------
    system_id : str
        Unique identifier for the AI system.
    system_name : str
        Human-readable name.
    iec62304_safety_class : IEC62304SafetyClass
        Assigned safety class per IEC 62304 §4.3.
    fda_device_class : FDASaMDClass
        FDA classification per 21 CFR Parts 862–892.
    fda_clearance_pathway : FDAClearancePathway
        Clearance/approval status.
    eu_mdr_class : EUMDRClass
        EU MDR classification.
    iso14971_residual_risk : ISO14971RiskLevel
        Residual risk level after all risk controls applied.
    intended_use : str
        Plain-language description of clinical intended use.
    has_notified_body_certificate : bool
        True if EU Notified Body certificate issued.
    has_pccp : bool
        True if a Predetermined Change Control Plan is filed with FDA.
    lifecycle_documentation_complete : bool
        True if IEC 62304 software lifecycle documentation is complete.
    formal_verification_complete : bool
        True if formal mathematical verification performed (required for
        some Class C functions).
    risk_management_file_complete : bool
        True if ISO 14971 risk management file is complete.
    clinical_validation_study_complete : bool
        True if clinical validation/performance study is complete.
    change_type : SaMDChangeType | None
        If this is a change request, the type of change.
    intended_markets : tuple[str, ...]
        Markets where the device will be placed ('US', 'EU', 'UK', etc.).
    """
    system_id: str
    system_name: str
    iec62304_safety_class: IEC62304SafetyClass
    fda_device_class: FDASaMDClass
    fda_clearance_pathway: FDAClearancePathway
    eu_mdr_class: EUMDRClass
    iso14971_residual_risk: ISO14971RiskLevel
    intended_use: str
    has_notified_body_certificate: bool = False
    has_pccp: bool = False
    lifecycle_documentation_complete: bool = True
    formal_verification_complete: bool = False
    risk_management_file_complete: bool = True
    clinical_validation_study_complete: bool = True
    change_type: Optional[SaMDChangeType] = None
    intended_markets: tuple[str, ...] = ("US",)


# ---------------------------------------------------------------------------
# Filter outputs
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Output from a single governance filter layer."""
    layer: str
    decision: DeploymentDecision
    violations: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_denied(self) -> bool:
        return self.decision == DeploymentDecision.DENIED


# ---------------------------------------------------------------------------
# Layer 1 — IEC 62304 Software Lifecycle Filter
# ---------------------------------------------------------------------------


class IEC62304SafetyFilter:
    """
    Layer 1: IEC 62304:2006+AMD1:2015 — Medical Device Software Lifecycle.

    Enforcement rules by safety class:

        Class A — No injury pathway:
            Lifecycle documentation: recommended but not blocking.
            Formal verification: not required.

        Class B — Non-serious injury pathway:
            Lifecycle documentation: REQUIRED (blocks deployment if incomplete).
            Formal verification: not required but recommended.

        Class C — Death or serious injury pathway:
            Lifecycle documentation: REQUIRED.
            Formal verification: REQUIRED for functions that can cause death/
            serious injury (IEC 62304 §5.5.3, §5.7.5, §8.2.4).
            Change management: all modifications must go through full SOUP
            (Software of Unknown Provenance) evaluation.
    """

    def evaluate(self, context: MedicalAIRequestContext) -> FilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        sc = context.iec62304_safety_class

        if sc == IEC62304SafetyClass.CLASS_A:
            notes.append(
                "IEC 62304 Class A: lightweight lifecycle process permitted; "
                "no injury pathway identified"
            )
            return FilterResult(
                layer="IEC 62304",
                decision=DeploymentDecision.APPROVED,
                notes=notes,
            )

        if sc == IEC62304SafetyClass.CLASS_B:
            if not context.lifecycle_documentation_complete:
                violations.append(
                    "IEC 62304 §5.1 — Class B requires complete software lifecycle "
                    "documentation (requirements, architecture, detailed design, "
                    "unit tests, integration tests)"
                )
            else:
                conditions.append(
                    "IEC 62304 Class B: lifecycle documentation verified; "
                    "periodic re-verification required on each software release"
                )

        if sc == IEC62304SafetyClass.CLASS_C:
            if not context.lifecycle_documentation_complete:
                violations.append(
                    "IEC 62304 §5.1/§8.2.4 — Class C requires complete lifecycle "
                    "documentation including hazard-traced requirements"
                )
            if not context.formal_verification_complete:
                violations.append(
                    "IEC 62304 §5.5.3 — Class C software items that can cause death "
                    "or serious injury require formal verification (static analysis, "
                    "model checking, or formal proof of correctness)"
                )
            if not violations:
                conditions.append(
                    "IEC 62304 Class C: full lifecycle compliance verified; "
                    "all future changes must go through Class C change management "
                    "(§8.2.1 problem resolution, §8.2.3 impact analysis)"
                )

        if violations:
            return FilterResult(
                layer="IEC 62304",
                decision=DeploymentDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )
        return FilterResult(
            layer="IEC 62304",
            decision=DeploymentDecision.APPROVED_WITH_CONDITIONS if conditions else DeploymentDecision.APPROVED,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Layer 2 — ISO 14971 Risk Management Filter
# ---------------------------------------------------------------------------


class ISO14971RiskFilter:
    """
    Layer 2: ISO 14971:2019 — Application of Risk Management to Medical Devices.

    ISO 14971 requires:
        §4: Risk management plan
        §5: Hazard identification
        §6: Risk estimation and evaluation
        §7: Risk controls
        §8: Evaluation of overall residual risk
        §9: Risk management review

    Deployment criteria per residual risk level:
        ACCEPTABLE   → deploy without additional constraints
        ALARP        → deploy with risk control monitoring; documented benefit/risk
        UNACCEPTABLE → block deployment; risk controls insufficient

    For ALARP, ISO 14971 §8 requires demonstration that overall residual risk
    is acceptable in light of clinical benefit. A complete risk management file
    is required.
    """

    def evaluate(self, context: MedicalAIRequestContext) -> FilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        rr = context.iso14971_residual_risk

        if rr == ISO14971RiskLevel.UNACCEPTABLE:
            violations.append(
                "ISO 14971 §8 — overall residual risk is UNACCEPTABLE after "
                "application of risk control measures; deployment blocked until "
                "additional risk controls reduce residual risk to ALARP or ACCEPTABLE"
            )
            return FilterResult(
                layer="ISO 14971",
                decision=DeploymentDecision.DENIED,
                violations=violations,
            )

        if not context.risk_management_file_complete:
            violations.append(
                "ISO 14971 §9 — risk management file is incomplete; all required "
                "elements (hazard log, FMEA, risk control evidence, §8 summary) "
                "must be present before deployment"
            )
            return FilterResult(
                layer="ISO 14971",
                decision=DeploymentDecision.DENIED,
                violations=violations,
            )

        if rr == ISO14971RiskLevel.ALARP:
            conditions.append(
                "ISO 14971 §8 — residual risk is ALARP; clinical benefit must "
                "demonstrably outweigh residual risk; post-market surveillance "
                "required per §10 to confirm benefit/risk balance in real-world use"
            )
            notes.append(
                "ISO 14971 §10 (PMS) — periodic risk management review required; "
                "serious incidents trigger risk management file update per MDR §87/88"
            )
        else:
            notes.append(
                "ISO 14971 — residual risk ACCEPTABLE; risk management file complete"
            )

        return FilterResult(
            layer="ISO 14971",
            decision=DeploymentDecision.APPROVED_WITH_CONDITIONS if conditions else DeploymentDecision.APPROVED,
            violations=violations,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Layer 3 — FDA SaMD Governance Filter
# ---------------------------------------------------------------------------


class FDASaMDFilter:
    """
    Layer 3: FDA SaMD Guidance (2019) + 21 CFR Part 820 (Quality System Regulation).

    Clearance pathway rules:
        Class I Exempt    → deploy; general controls apply
        Class I (non-exempt) → 510(k) not required; general controls apply
        Class II          → 510(k) K510_CLEARED required; special controls
        Class III         → PMA_APPROVED required

    AI/ML-specific rules:
        - Locked algorithms: standard 510(k)/PMA pathway.
        - Adaptive algorithms (continuous learning): FDA PCCP required.
          Without PCCP, adaptive changes trigger new 510(k)/PMA.
        - Intended use changes always require new 510(k)/PMA regardless of
          PCCP (FDA AI/ML Action Plan, 2021).

    Change control:
        - INTENDED_USE_CHANGE or OUTPUT_TYPE_CHANGE → new clearance required
          even if device is currently cleared (FDA SaMD guidance §5.1).
        - PERFORMANCE_IMPROVEMENT within PCCP bounds → no new submission required.
    """

    def evaluate(self, context: MedicalAIRequestContext) -> FilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        # Only apply FDA rules for US market
        if "US" not in context.intended_markets:
            notes.append("FDA filter: US not in intended_markets — FDA rules not applicable")
            return FilterResult(
                layer="FDA SaMD",
                decision=DeploymentDecision.APPROVED,
                notes=notes,
            )

        dc = context.fda_device_class
        cp = context.fda_clearance_pathway
        ct = context.change_type

        # Class I: generally exempt from 510(k)
        if dc == FDASaMDClass.CLASS_I:
            if cp not in (FDAClearancePathway.EXEMPT, FDAClearancePathway.K510_CLEARED):
                notes.append(
                    "21 CFR §880.9: Class I device — 510(k) generally not required; "
                    "general controls (21 CFR Part 820 QSR) apply"
                )
            conditions.append(
                "FDA Class I: general controls required — 21 CFR Part 820 QSR, "
                "labeling (21 CFR Part 801), registration and listing (21 CFR Part 807)"
            )
            return FilterResult(
                layer="FDA SaMD",
                decision=DeploymentDecision.APPROVED_WITH_CONDITIONS,
                conditions=conditions,
                notes=notes,
            )

        # Class II: 510(k) required
        if dc == FDASaMDClass.CLASS_II:
            if cp != FDAClearancePathway.K510_CLEARED and cp != FDAClearancePathway.DE_NOVO:
                violations.append(
                    f"21 CFR §807.81 — Class II SaMD requires 510(k) clearance "
                    f"before commercial distribution; current status: {cp.value}"
                )

            # Clinical validation study required for Class II
            if not context.clinical_validation_study_complete:
                violations.append(
                    "FDA 510(k) guidance — Class II AI SaMD requires clinical "
                    "performance validation study; study not complete"
                )

            # Adaptive algorithm without PCCP
            if not context.has_pccp:
                conditions.append(
                    "FDA AI/ML Action Plan (2021) — adaptive AI/ML algorithms "
                    "require a Predetermined Change Control Plan (PCCP); without PCCP, "
                    "any performance improvement change requires new 510(k) submission"
                )

            # Change type requiring new submission
            if ct in (SaMDChangeType.INTENDED_USE_CHANGE, SaMDChangeType.OUTPUT_TYPE_CHANGE):
                violations.append(
                    f"FDA SaMD Guidance §5.1 — {ct.value} requires new 510(k) "
                    f"submission; existing clearance does not cover this change"
                )

        # Class III: PMA required
        if dc == FDASaMDClass.CLASS_III:
            if cp != FDAClearancePathway.PMA_APPROVED:
                violations.append(
                    f"21 CFR §814.1 — Class III SaMD requires PMA (Premarket Approval); "
                    f"510(k) or De Novo is not an eligible pathway; "
                    f"current status: {cp.value}"
                )
            if not context.clinical_validation_study_complete:
                violations.append(
                    "21 CFR §814.20(b)(6) — PMA requires valid clinical investigation "
                    "data; clinical validation study not complete"
                )

        if violations:
            return FilterResult(
                layer="FDA SaMD",
                decision=DeploymentDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )

        return FilterResult(
            layer="FDA SaMD",
            decision=DeploymentDecision.APPROVED_WITH_CONDITIONS if conditions else DeploymentDecision.APPROVED,
            violations=violations,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Layer 4 — EU MDR / MDCG 2021-1 Filter
# ---------------------------------------------------------------------------


class MDCGEUFilter:
    """
    Layer 4: EU MDR 2017/745 + MDCG 2021-1 (Guidance on AI/ML Medical Devices).

    Classification rules:
        Class I   → self-certification; Declaration of Conformity + CE marking
        Class IIa → Notified Body involvement for QMS certification
        Class IIb → Notified Body certification of technical documentation
        Class III → Notified Body certification + clinical evaluation (MDR Annex IX/X)

    MDCG 2021-1 specific requirements for AI/ML medical devices:
        - Transparency: AI/ML model must have explainable decision logic documented
          in the Instructions for Use (IFU).
        - Validation: performance validation on representative population required
          (including underserved subgroups per MDCG equity guidance).
        - Post-Market Surveillance: periodic performance monitoring; serious
          deterioration of AI performance triggers MDR §87/88 incident reporting.
        - EU AI Act Annex I §5: AI used as safety component of medical devices
          is automatically high-risk under the EU AI Act.
    """

    def evaluate(self, context: MedicalAIRequestContext) -> FilterResult:
        violations: list[str] = []
        conditions: list[str] = []
        notes: list[str] = []

        # Only apply EU rules for EU market
        if "EU" not in context.intended_markets:
            notes.append("EU MDR filter: EU not in intended_markets — EU rules not applicable")
            return FilterResult(
                layer="EU MDR",
                decision=DeploymentDecision.APPROVED,
                notes=notes,
            )

        eu_class = context.eu_mdr_class

        if eu_class == EUMDRClass.CLASS_I:
            conditions.append(
                "EU MDR Annex IX §2.2 — Class I: Declaration of Conformity + "
                "CE marking; self-certification; MDCG 2021-1 IFU transparency "
                "requirements apply"
            )
            return FilterResult(
                layer="EU MDR",
                decision=DeploymentDecision.APPROVED_WITH_CONDITIONS,
                conditions=conditions,
                notes=notes,
            )

        # Class IIa, IIb, III: Notified Body required
        if not context.has_notified_body_certificate:
            violations.append(
                f"EU MDR Art. 52 — {eu_class.value} devices require Notified Body "
                f"involvement; CE marking cannot be self-declared for this class"
            )

        # Class IIb and III: clinical validation
        if eu_class in (EUMDRClass.CLASS_IIB, EUMDRClass.CLASS_III):
            if not context.clinical_validation_study_complete:
                violations.append(
                    "EU MDR Annex XIV + MDCG 2020-13 — clinical performance "
                    "validation study required for Class IIb/III; study not complete"
                )

        # Class III: highest scrutiny
        if eu_class == EUMDRClass.CLASS_III:
            if not context.formal_verification_complete:
                violations.append(
                    "EU MDR Annex IX §4.5 + MDCG 2021-1 §4 — Class III AI/ML "
                    "requires verified algorithmic performance with documented "
                    "confidence intervals; formal validation required"
                )
            notes.append(
                "EU AI Act Annex I §5 — Class III medical device AI is automatically "
                "high-risk under EU AI Act; registration in EU AI Act database required"
            )

        if not violations:
            conditions.extend([
                f"EU MDR {eu_class.value}: MDCG 2021-1 transparency requirements apply — "
                f"IFU must describe AI model logic, limitations, and performance metrics",
                "EU MDR Art. 83/84 — Post-Market Surveillance plan required; "
                "periodic PSUR (periodic safety update report) for Class IIa+",
            ])

        if violations:
            return FilterResult(
                layer="EU MDR",
                decision=DeploymentDecision.DENIED,
                violations=violations,
                conditions=conditions,
                notes=notes,
            )

        return FilterResult(
            layer="EU MDR",
            decision=DeploymentDecision.APPROVED_WITH_CONDITIONS if conditions else DeploymentDecision.APPROVED,
            violations=violations,
            conditions=conditions,
            notes=notes,
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


@dataclass
class MedicalDeviceGovernanceResult:
    """Final governance decision with per-layer detail."""
    system_id: str
    system_name: str
    final_decision: DeploymentDecision
    layer_results: list[FilterResult]
    all_violations: list[str]
    all_conditions: list[str]
    all_notes: list[str]
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def summary(self) -> str:
        lines = [
            f"System: {self.system_name} ({self.system_id})",
            f"Final Decision: {self.final_decision.value}",
            f"Violations: {len(self.all_violations)}",
            f"Conditions: {len(self.all_conditions)}",
        ]
        if self.all_violations:
            lines.append("Blocking violations:")
            for v in self.all_violations:
                lines.append(f"  • {v}")
        if self.all_conditions:
            lines.append("Deployment conditions:")
            for c in self.all_conditions:
                lines.append(f"  ○ {c}")
        return "\n".join(lines)


class MedicalDeviceAIOrchestrator:
    """
    Four-layer governance orchestrator for medical device AI systems.

    Evaluation order:
        1. IEC62304SafetyFilter  — software lifecycle and safety class
        2. ISO14971RiskFilter    — residual risk acceptability
        3. FDASaMDFilter         — FDA clearance pathway (US market)
        4. MDCGEUFilter          — EU MDR/MDCG certification (EU market)

    Final decision logic:
        - Any DENIED result from any layer → overall DENIED.
        - All APPROVED → overall APPROVED.
        - Mix of APPROVED and APPROVED_WITH_CONDITIONS → APPROVED_WITH_CONDITIONS.
        - Conditions and notes from all layers are aggregated.
    """

    def __init__(self) -> None:
        self._iec62304 = IEC62304SafetyFilter()
        self._iso14971 = ISO14971RiskFilter()
        self._fda = FDASaMDFilter()
        self._mdcg = MDCGEUFilter()

    def evaluate(
        self,
        context: MedicalAIRequestContext,
    ) -> MedicalDeviceGovernanceResult:
        layer_results = [
            self._iec62304.evaluate(context),
            self._iso14971.evaluate(context),
            self._fda.evaluate(context),
            self._mdcg.evaluate(context),
        ]

        all_violations = [v for lr in layer_results for v in lr.violations]
        all_conditions = [c for lr in layer_results for c in lr.conditions]
        all_notes = [n for lr in layer_results for n in lr.notes]

        # Compute final decision
        if any(lr.is_denied for lr in layer_results):
            final = DeploymentDecision.DENIED
        elif any(lr.decision == DeploymentDecision.APPROVED_WITH_CONDITIONS for lr in layer_results):
            final = DeploymentDecision.APPROVED_WITH_CONDITIONS
        else:
            final = DeploymentDecision.APPROVED

        return MedicalDeviceGovernanceResult(
            system_id=context.system_id,
            system_name=context.system_name,
            final_decision=final,
            layer_results=layer_results,
            all_violations=all_violations,
            all_conditions=all_conditions,
            all_notes=all_notes,
        )


# ---------------------------------------------------------------------------
# Demo scenarios
# ---------------------------------------------------------------------------


def _print_result(result: MedicalDeviceGovernanceResult) -> None:
    print(f"\n{'─' * 60}")
    print(result.summary())
    print(f"\nPer-layer results:")
    for lr in result.layer_results:
        icon = {"APPROVED": "✓", "APPROVED_WITH_CONDITIONS": "⚠", "DENIED": "✗"}[lr.decision.value]
        print(f"  [{icon}] {lr.layer}: {lr.decision.value}")
        for v in lr.violations:
            print(f"       BLOCK: {v}")
        for c in lr.conditions:
            print(f"       COND:  {c}")
    print(f"{'─' * 60}")


def scenario_a_diagnostic_imaging_assistant() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO A: AI Diagnostic Imaging Assistant (Class IIb / Safety Class C)")
    print("=" * 70)

    context = MedicalAIRequestContext(
        system_id="SYS-IMG-2001",
        system_name="RetinalScan AI — Diabetic Retinopathy Detection",
        iec62304_safety_class=IEC62304SafetyClass.CLASS_C,
        fda_device_class=FDASaMDClass.CLASS_II,
        fda_clearance_pathway=FDAClearancePathway.K510_CLEARED,
        eu_mdr_class=EUMDRClass.CLASS_IIB,
        iso14971_residual_risk=ISO14971RiskLevel.ALARP,
        intended_use=(
            "AI-assisted detection of diabetic retinopathy in fundus images; "
            "provides grading recommendation to ophthalmologist"
        ),
        has_notified_body_certificate=True,
        has_pccp=True,
        lifecycle_documentation_complete=True,
        formal_verification_complete=True,
        risk_management_file_complete=True,
        clinical_validation_study_complete=True,
        intended_markets=("US", "EU"),
    )

    orchestrator = MedicalDeviceAIOrchestrator()
    result = orchestrator.evaluate(context)
    _print_result(result)


def scenario_b_administrative_scheduler() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO B: Administrative AI Scheduling Optimizer (Class I / Safety Class A)")
    print("=" * 70)

    context = MedicalAIRequestContext(
        system_id="SYS-SCHED-0501",
        system_name="OR Schedule Optimizer",
        iec62304_safety_class=IEC62304SafetyClass.CLASS_A,
        fda_device_class=FDASaMDClass.CLASS_I,
        fda_clearance_pathway=FDAClearancePathway.EXEMPT,
        eu_mdr_class=EUMDRClass.CLASS_I,
        iso14971_residual_risk=ISO14971RiskLevel.ACCEPTABLE,
        intended_use=(
            "Optimizes operating room scheduling based on staff availability, "
            "equipment maintenance windows, and historical case durations; "
            "no clinical decision support function"
        ),
        has_notified_body_certificate=False,
        has_pccp=False,
        lifecycle_documentation_complete=True,
        formal_verification_complete=False,
        risk_management_file_complete=True,
        clinical_validation_study_complete=True,
        intended_markets=("US", "EU"),
    )

    orchestrator = MedicalDeviceAIOrchestrator()
    result = orchestrator.evaluate(context)
    _print_result(result)


def scenario_c_autonomous_treatment_recommendation() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO C: High-Risk Autonomous Treatment AI (Class III) — Unacceptable Residual Risk")
    print("=" * 70)

    context = MedicalAIRequestContext(
        system_id="SYS-TX-9001",
        system_name="AutoOncology — Autonomous Chemotherapy Dosing",
        iec62304_safety_class=IEC62304SafetyClass.CLASS_C,
        fda_device_class=FDASaMDClass.CLASS_III,
        fda_clearance_pathway=FDAClearancePathway.NOT_CLEARED,
        eu_mdr_class=EUMDRClass.CLASS_III,
        iso14971_residual_risk=ISO14971RiskLevel.UNACCEPTABLE,
        intended_use=(
            "Autonomous chemotherapy protocol selection and dosing without "
            "required physician oversight for each treatment cycle"
        ),
        has_notified_body_certificate=False,
        has_pccp=False,
        lifecycle_documentation_complete=True,
        formal_verification_complete=False,
        risk_management_file_complete=True,
        clinical_validation_study_complete=False,
        intended_markets=("US", "EU"),
    )

    orchestrator = MedicalDeviceAIOrchestrator()
    result = orchestrator.evaluate(context)
    _print_result(result)


def scenario_d_monitoring_pending_study() -> None:
    print("\n" + "=" * 70)
    print("SCENARIO D: Patient Monitoring AI — 510(k) Filed, Study Pending")
    print("=" * 70)

    context = MedicalAIRequestContext(
        system_id="SYS-MON-3301",
        system_name="ContinuousSepsis Sentinel",
        iec62304_safety_class=IEC62304SafetyClass.CLASS_B,
        fda_device_class=FDASaMDClass.CLASS_II,
        fda_clearance_pathway=FDAClearancePathway.NOT_CLEARED,
        eu_mdr_class=EUMDRClass.CLASS_IIA,
        iso14971_residual_risk=ISO14971RiskLevel.ALARP,
        intended_use=(
            "Continuous monitoring of ICU patient vital signs to predict sepsis "
            "onset; alerts clinicians 6 hours before predicted onset"
        ),
        has_notified_body_certificate=True,
        has_pccp=False,
        lifecycle_documentation_complete=True,
        formal_verification_complete=False,
        risk_management_file_complete=True,
        clinical_validation_study_complete=False,   # Study still running
        intended_markets=("US", "EU"),
    )

    orchestrator = MedicalDeviceAIOrchestrator()
    result = orchestrator.evaluate(context)
    _print_result(result)


if __name__ == "__main__":
    print("Medical Device AI Governance")
    print("IEC 62304 + ISO 14971 + FDA SaMD + EU MDR/MDCG 2021-1")

    scenario_a_diagnostic_imaging_assistant()
    scenario_b_administrative_scheduler()
    scenario_c_autonomous_treatment_recommendation()
    scenario_d_monitoring_pending_study()

    print("\n" + "=" * 70)
    print("All scenarios complete.")
    print("=" * 70)
