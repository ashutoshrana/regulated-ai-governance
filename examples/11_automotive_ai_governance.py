"""
11_automotive_ai_governance.py — AI governance for automotive and
mobility systems under UNECE WP.29, ISO 26262, and NHTSA AV guidance.

Autonomous vehicles and advanced driver-assistance systems (ADAS) sit at
the intersection of software, safety engineering, and public safety regulation.
Three distinct regulatory frameworks govern AI deployed in this domain:

    UNECE WP.29 — Regulation R155 (cybersecurity management system, CSMS)
                  Regulation R156 (software update management system, SUMS)
                  Mandatory in EU, Japan, South Korea for type approval
                  (effective July 2022 for new models; July 2024 expanded)

    ISO 26262  — Functional safety standard for road vehicles.
                  Assigns Automotive Safety Integrity Levels (ASIL) A/B/C/D
                  based on severity × exposure × controllability. AI components
                  deployed in safety-relevant systems must comply with ASIL
                  requirements for their assigned level.

    NHTSA AV  — "A Vision for Safety" (2017) and subsequent guidance;
                  SAE J3016 automation levels (L0–L5); federal reporting
                  requirements for Standing General Order (SGO) 2021-01;
                  AV TEST Initiative voluntary safety principles.

This module demonstrates a layered governance framework that:

    1. Classifies AI components by ASIL level (Part 1 — SafetyClassifier)
    2. Validates cybersecurity management compliance (Part 2 — R155CybersecFilter)
    3. Validates software update management compliance (Part 3 — R156SUMSFilter)
    4. Applies NHTSA reporting and safety-principle checks (Part 4 — NHTSAAVFilter)
    5. Orchestrates all checks and produces an OEM-grade audit record
       (Part 5 — AutomotiveAIOrchestrator)

Scenarios
---------

  A. ADAS lane-keep assist (ASIL B):
     System has valid CSMS, SUMS, ODD documentation, and operational safety
     record. All checks pass; outcome = ALLOW.

  B. Level 3 automated driving (ASIL C) — cybersecurity gap:
     No active CSMS certificate and vulnerability not mitigated. R155 blocks
     deployment; outcome = DENY with audit trail.

  C. OTA software update (ASIL D) — SUMS non-compliant:
     Over-the-air update lacks cryptographic signature verification and rollback
     capability. R156 blocks the update; outcome = DENY.

  D. Level 4 robotaxi (ASIL D) — SGO reporting required:
     System exceeds SAE Level 3, triggering NHTSA SGO 2021-01 mandatory
     reporting obligation. Incident data must be submitted within 24 hours.
     Outcome = ALLOW_WITH_CONDITIONS (reporting obligation flagged).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# ASIL Classification
# ---------------------------------------------------------------------------

class ASILLevel(str, Enum):
    """
    Automotive Safety Integrity Level (ISO 26262-1:2018 §3.6).

    QM  — Quality Managed: no specific ISO 26262 requirement.
    A   — Lowest ASIL; some safety relevance.
    B   — Moderate safety relevance; higher fault detection requirements.
    C   — High safety relevance; redundancy and monitoring required.
    D   — Highest ASIL; strict independence, formal verification required.
    """
    QM = "QM"
    A = "ASIL_A"
    B = "ASIL_B"
    C = "ASIL_C"
    D = "ASIL_D"


class SAELevel(str, Enum):
    """SAE J3016 automation taxonomy."""
    L0 = "L0_NO_AUTOMATION"
    L1 = "L1_DRIVER_ASSISTANCE"
    L2 = "L2_PARTIAL_AUTOMATION"
    L3 = "L3_CONDITIONAL_AUTOMATION"
    L4 = "L4_HIGH_AUTOMATION"
    L5 = "L5_FULL_AUTOMATION"


class AISystemFunction(str, Enum):
    """Automotive AI function classification for ASIL assignment."""
    LANE_KEEP_ASSIST = "LANE_KEEP_ASSIST"
    ADAPTIVE_CRUISE_CONTROL = "ADAPTIVE_CRUISE_CONTROL"
    EMERGENCY_BRAKING = "EMERGENCY_BRAKING"
    STEERING_CONTROL = "STEERING_CONTROL"
    TRAFFIC_SIGN_RECOGNITION = "TRAFFIC_SIGN_RECOGNITION"
    OBJECT_DETECTION = "OBJECT_DETECTION"
    PATH_PLANNING = "PATH_PLANNING"
    MOTION_CONTROL = "MOTION_CONTROL"
    PERCEPTION_FUSION = "PERCEPTION_FUSION"
    DRIVER_MONITORING = "DRIVER_MONITORING"
    OTA_UPDATE_EXECUTION = "OTA_UPDATE_EXECUTION"
    CYBERSECURITY_MONITOR = "CYBERSECURITY_MONITOR"
    TELEMETRY_LOGGING = "TELEMETRY_LOGGING"
    INFOTAINMENT = "INFOTAINMENT"


class GovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_CONDITIONS = "ALLOW_WITH_CONDITIONS"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"
    DENY = "DENY"


# ---------------------------------------------------------------------------
# Part 1 — Safety Classifier (ISO 26262 ASIL Assignment)
# ---------------------------------------------------------------------------

# ASIL assignment table (simplified; based on ISO 26262 HARA severity×exposure×controllability)
_FUNCTION_ASIL_TABLE: dict[AISystemFunction, ASILLevel] = {
    AISystemFunction.EMERGENCY_BRAKING:         ASILLevel.D,
    AISystemFunction.STEERING_CONTROL:           ASILLevel.D,
    AISystemFunction.MOTION_CONTROL:             ASILLevel.D,
    AISystemFunction.PATH_PLANNING:              ASILLevel.C,
    AISystemFunction.PERCEPTION_FUSION:          ASILLevel.C,
    AISystemFunction.OBJECT_DETECTION:           ASILLevel.C,
    AISystemFunction.LANE_KEEP_ASSIST:           ASILLevel.B,
    AISystemFunction.ADAPTIVE_CRUISE_CONTROL:    ASILLevel.B,
    AISystemFunction.TRAFFIC_SIGN_RECOGNITION:   ASILLevel.B,
    AISystemFunction.DRIVER_MONITORING:          ASILLevel.A,
    AISystemFunction.OTA_UPDATE_EXECUTION:       ASILLevel.D,   # ISO 26262-8 §7
    AISystemFunction.CYBERSECURITY_MONITOR:      ASILLevel.A,
    AISystemFunction.TELEMETRY_LOGGING:          ASILLevel.QM,
    AISystemFunction.INFOTAINMENT:               ASILLevel.QM,
}

# Minimum verification requirements per ASIL level
_ASIL_VERIFICATION_REQUIREMENTS: dict[ASILLevel, list[str]] = {
    ASILLevel.QM:  [],
    ASILLevel.A:   ["unit_testing", "code_review"],
    ASILLevel.B:   ["unit_testing", "code_review", "fmea_complete", "hara_complete"],
    ASILLevel.C:   ["unit_testing", "code_review", "fmea_complete", "hara_complete",
                    "independent_safety_assessment", "safety_case_documented"],
    ASILLevel.D:   ["unit_testing", "code_review", "fmea_complete", "hara_complete",
                    "independent_safety_assessment", "safety_case_documented",
                    "formal_verification", "safety_element_out_of_context"],
}


class SafetyClassifier:
    """
    Assigns ISO 26262 ASIL level to AI components and validates that
    required verification activities have been completed.

    ISO 26262-4 requires that every item (system) and element (component)
    implementing a safety function carries a documented ASIL. The level
    determines which development process rigor is required.
    """

    def classify(self, function: AISystemFunction) -> ASILLevel:
        """Return the ASIL level for the given function."""
        return _FUNCTION_ASIL_TABLE.get(function, ASILLevel.QM)

    def verify_requirements_met(
        self,
        function: AISystemFunction,
        completed_activities: list[str],
    ) -> tuple[bool, list[str]]:
        """
        Check that all required verification activities for the ASIL level
        have been completed.

        Returns (all_met, missing_activities).
        """
        asil = self.classify(function)
        required = set(_ASIL_VERIFICATION_REQUIREMENTS[asil])
        completed = set(completed_activities)
        missing = sorted(required - completed)
        return len(missing) == 0, missing


# ---------------------------------------------------------------------------
# Part 2 — UNECE WP.29 R155 Cybersecurity Management System Filter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CybersecurityContext:
    """
    R155 cybersecurity management context for a vehicle model or fleet.

    csms_certified: bool — OEM holds a valid CSMS type-approval certificate
                           (required per R155 §7.3.1).
    csms_certificate_id: str — Certificate reference number.
    threat_assessment_current: bool — TARA (Threat Analysis and Risk Assessment)
                                       completed and documented for this component
                                       (R155 §7.3.2).
    known_vulnerabilities_mitigated: bool — All CVEs / TARA findings at HIGH or
                                             CRITICAL severity have accepted
                                             mitigations (R155 §7.3.3).
    intrusion_detection_active: bool — IDS/IPS monitoring active on relevant ECUs
                                        (R155 §7.3.5).
    incident_response_tested: bool — IR plan exercised within the last 12 months
                                      (R155 §7.3.6).
    security_logging_enabled: bool — Audit trail for security events (R155 §7.3.7).
    """
    csms_certified: bool
    csms_certificate_id: str
    threat_assessment_current: bool
    known_vulnerabilities_mitigated: bool
    intrusion_detection_active: bool
    incident_response_tested: bool
    security_logging_enabled: bool


class R155CybersecFilter:
    """
    Validates compliance with UNECE WP.29 Regulation 155 — Cybersecurity
    Management System (CSMS).

    R155 is mandatory for type approval in the EU, Japan, and South Korea
    for new vehicle models (July 2022) and all new vehicles (July 2024).
    Non-compliant vehicles cannot be type-approved or sold in regulated markets.

    This filter blocks deployment of AI systems on vehicles without a valid CSMS.
    """

    def evaluate(
        self, ctx: CybersecurityContext
    ) -> tuple[GovernanceOutcome, list[str]]:
        violations: list[str] = []

        if not ctx.csms_certified:
            violations.append(
                "R155 §7.3.1: OEM does not hold a valid CSMS type-approval certificate; "
                "vehicle cannot be type-approved in R155 markets"
            )
        if not ctx.threat_assessment_current:
            violations.append(
                "R155 §7.3.2: TARA (Threat Analysis and Risk Assessment) not completed "
                "or not current for this component"
            )
        if not ctx.known_vulnerabilities_mitigated:
            violations.append(
                "R155 §7.3.3: HIGH/CRITICAL severity vulnerabilities identified in TARA "
                "have no accepted mitigation; deployment blocked"
            )
        if not ctx.intrusion_detection_active:
            violations.append(
                "R155 §7.3.5: Intrusion detection/prevention system not active "
                "on safety-relevant ECUs"
            )
        if not ctx.security_logging_enabled:
            violations.append(
                "R155 §7.3.7: Security event audit logging not enabled"
            )

        if any("§7.3.1" in v or "§7.3.3" in v for v in violations):
            return GovernanceOutcome.DENY, violations
        if violations:
            return GovernanceOutcome.ALLOW_WITH_CONDITIONS, violations
        return GovernanceOutcome.ALLOW, violations


# ---------------------------------------------------------------------------
# Part 3 — UNECE WP.29 R156 Software Update Management System Filter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SoftwareUpdateContext:
    """
    R156 software update management context.

    sums_documented: bool — OEM has a documented Software Update Management
                             System (R156 §7.1.1).
    update_cryptographically_signed: bool — Each update package carries a valid
                                              cryptographic signature from the OEM's
                                              root of trust (R156 §7.2.2).
    rollback_capability_present: bool — ECU can restore previous software version
                                         if update fails (R156 §7.2.4).
    over_the_air: bool — Update is delivered over-the-air (increases scope of
                          R156 §7.2.5–7.2.7 requirements).
    driver_consent_obtained: bool — Driver has been notified and consented
                                     to the update (R156 §7.2.6 for OTA).
    installation_state_verified: bool — Post-update integrity check confirms
                                         the installed software matches the
                                         expected version hash (R156 §7.2.3).
    asil_change_requires_reapproval: bool — Set True if update changes the ASIL
                                              scope of any safety function; triggers
                                              type-approval re-evaluation.
    """
    sums_documented: bool
    update_cryptographically_signed: bool
    rollback_capability_present: bool
    over_the_air: bool
    driver_consent_obtained: bool
    installation_state_verified: bool
    asil_change_requires_reapproval: bool = False


class R156SUMSFilter:
    """
    Validates compliance with UNECE WP.29 Regulation 156 — Software Update
    Management System (SUMS).

    R156 requires that every software update to a type-approved vehicle follows
    a documented, auditable process. Updates to safety-critical ECUs without a
    valid SUMS are prohibited.

    OTA updates have additional requirements (driver consent, secure channel)
    compared to workshop updates. An OTA update to an ASIL D component is the
    highest-risk scenario and requires the strictest validation.
    """

    def evaluate(
        self, ctx: SoftwareUpdateContext, asil_level: ASILLevel
    ) -> tuple[GovernanceOutcome, list[str]]:
        violations: list[str] = []

        if not ctx.sums_documented:
            violations.append(
                "R156 §7.1.1: No documented Software Update Management System; "
                "all software updates to type-approved vehicles are prohibited"
            )
        if not ctx.update_cryptographically_signed:
            violations.append(
                "R156 §7.2.2: Update package lacks cryptographic signature from OEM "
                "root-of-trust; unsigned software must not be installed"
            )
        if not ctx.rollback_capability_present:
            violations.append(
                "R156 §7.2.4: ECU does not support rollback to previous version; "
                "update cannot proceed without recovery capability"
            )
        if not ctx.installation_state_verified:
            violations.append(
                "R156 §7.2.3: Post-installation integrity verification not configured; "
                "software version hash must be confirmed after installation"
            )
        if ctx.over_the_air and not ctx.driver_consent_obtained:
            violations.append(
                "R156 §7.2.6: OTA update requires driver notification and consent "
                "before installation; consent not on record"
            )
        if ctx.asil_change_requires_reapproval:
            violations.append(
                "R156 §7.3 / ISO 26262-8: Update changes ASIL scope of safety function; "
                "type-approval re-evaluation required before market deployment"
            )

        # Unsigned updates and missing SUMS are hard blocks regardless of ASIL
        hard_block = any(
            "§7.1.1" in v or "§7.2.2" in v or "§7.2.4" in v
            for v in violations
        )

        # ASIL D requires zero violations
        if asil_level == ASILLevel.D and violations:
            return GovernanceOutcome.DENY, violations
        if hard_block:
            return GovernanceOutcome.DENY, violations
        if violations:
            return GovernanceOutcome.ALLOW_WITH_CONDITIONS, violations
        return GovernanceOutcome.ALLOW, violations


# ---------------------------------------------------------------------------
# Part 4 — NHTSA AV Safety Filter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NHTSAAVContext:
    """
    NHTSA AV context for a deployed autonomous or semi-autonomous system.

    sae_level: SAELevel — SAE J3016 automation level.
    odd_documented: bool — Operational Design Domain (ODD) specification
                            exists and is current (NHTSA Principles #5).
    safety_performance_tested: bool — System has been validated against ODD
                                        (NHTSA AV Safety 2.0 Principle #3).
    cybersecurity_compliance: bool — References NHTSA cybersecurity best
                                      practices (AV Safety 2.0 Principle #9).
    crash_avoidance_validated: bool — System demonstrates improved crash
                                       avoidance vs. baseline (SGO obligation).
    sgo_reporting_enabled: bool — Telemetry and incident reporting pipeline
                                   active to comply with SGO 2021-01 (L2+
                                   systems, ≥100k miles/year or incident
                                   threshold).
    fallback_minimal_risk_condition: bool — MRC (minimal risk condition) is
                                             implemented: system can safely
                                             bring vehicle to a stop if
                                             automation fails (SAE L3+).
    human_machine_interface_tested: bool — HMI for takeover requests tested
                                            (required for L2/L3 systems).
    data_recording_capability: bool — EDR/DSSAD equivalent captures pre/post
                                       incident data (NHTSA EDR requirements).
    """
    sae_level: SAELevel
    odd_documented: bool
    safety_performance_tested: bool
    cybersecurity_compliance: bool
    crash_avoidance_validated: bool
    sgo_reporting_enabled: bool
    fallback_minimal_risk_condition: bool
    human_machine_interface_tested: bool
    data_recording_capability: bool


# SAE levels that require SGO reporting (L2 and above when thresholds are met)
_SGO_REQUIRED_LEVELS: frozenset[SAELevel] = frozenset({
    SAELevel.L2, SAELevel.L3, SAELevel.L4, SAELevel.L5
})

# L3+ requires fallback MRC (no human driver available on demand)
_MRC_REQUIRED_LEVELS: frozenset[SAELevel] = frozenset({
    SAELevel.L3, SAELevel.L4, SAELevel.L5
})


class NHTSAAVFilter:
    """
    Validates compliance with NHTSA AV safety guidance.

    Key references:
    - "Ensuring Complete and Consistent Rulemaking for Automated Vehicles" (AV Safety 2.0, 2020)
    - Standing General Order 2021-01 (incident reporting for L2+ systems)
    - NHTSA preliminary statement on AV policy (2021)
    - Federal Motor Vehicle Safety Standards (FMVSS) applicability
    """

    def evaluate(
        self, ctx: NHTSAAVContext
    ) -> tuple[GovernanceOutcome, list[str]]:
        violations: list[str] = []
        conditions: list[str] = []

        if not ctx.odd_documented:
            violations.append(
                "NHTSA AV Safety Principle #5: Operational Design Domain (ODD) must be "
                "documented before deployment; defines conditions under which automation "
                "is engaged"
            )
        if not ctx.safety_performance_tested:
            violations.append(
                "NHTSA AV Safety Principle #3: System must demonstrate validation "
                "against the ODD before public road deployment"
            )
        if not ctx.crash_avoidance_validated:
            violations.append(
                "NHTSA AV Safety: Crash avoidance capability must be validated; "
                "system cannot demonstrate improvement over baseline"
            )

        # MRC required for L3+
        if ctx.sae_level in _MRC_REQUIRED_LEVELS and not ctx.fallback_minimal_risk_condition:
            violations.append(
                f"SAE J3016 / NHTSA: {ctx.sae_level.value} system requires Minimal Risk "
                "Condition (MRC) implementation; system must safely stop if automation "
                "disengages without driver takeover"
            )

        # SGO reporting — mandatory for L2+ deployments above reporting thresholds
        if ctx.sae_level in _SGO_REQUIRED_LEVELS and not ctx.sgo_reporting_enabled:
            conditions.append(
                f"NHTSA SGO 2021-01: {ctx.sae_level.value} deployment requires Standing "
                "General Order incident reporting; crashes and AV disengagements must be "
                "reported within 24 hours of OEM/operator awareness"
            )

        # HMI tested for L2/L3 (driver still in the loop)
        if ctx.sae_level in {SAELevel.L2, SAELevel.L3} and not ctx.human_machine_interface_tested:
            conditions.append(
                "NHTSA AV Safety Principle #7: Human-Machine Interface for takeover "
                "requests not tested; L2/L3 systems require validated HMI before deployment"
            )

        if not ctx.data_recording_capability:
            conditions.append(
                "NHTSA EDR / DSSAD: Data recording capability (pre/post incident) not "
                "confirmed; recommended for all AV deployments"
            )

        if violations:
            return GovernanceOutcome.DENY, violations + conditions
        if conditions:
            return GovernanceOutcome.ALLOW_WITH_CONDITIONS, conditions
        return GovernanceOutcome.ALLOW, []


# ---------------------------------------------------------------------------
# Part 5 — Automotive AI Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class AutomotiveGovernanceAuditRecord:
    """
    OEM-grade audit record for an automotive AI deployment decision.

    Captures all regulatory check outcomes, the final governance decision,
    and the rationale for traceability in type-approval documentation.
    """
    audit_id: str
    system_name: str
    function: str
    sae_level: str
    asil_level: str
    asil_requirements_met: bool
    missing_asil_activities: list[str]
    r155_outcome: str
    r155_violations: list[str]
    r156_outcome: str
    r156_violations: list[str]
    nhtsa_outcome: str
    nhtsa_findings: list[str]
    final_outcome: GovernanceOutcome
    denial_reasons: list[str]
    conditions: list[str]


class AutomotiveAIOrchestrator:
    """
    Orchestrates all regulatory checks and produces a final governance decision.

    Priority: DENY > ESCALATE_HUMAN > ALLOW_WITH_CONDITIONS > ALLOW

    A single DENY from any layer (ASIL gap, R155, R156, NHTSA safety) blocks
    the deployment. Conditions from ALLOW_WITH_CONDITIONS checks are surfaced
    in the audit record even when the final outcome is ALLOW.
    """

    def __init__(self) -> None:
        self._safety_classifier = SafetyClassifier()
        self._r155 = R155CybersecFilter()
        self._r156 = R156SUMSFilter()
        self._nhtsa = NHTSAAVFilter()

    def evaluate(
        self,
        system_name: str,
        function: AISystemFunction,
        sae_level: SAELevel,
        completed_safety_activities: list[str],
        cybersec_ctx: CybersecurityContext,
        sums_ctx: SoftwareUpdateContext,
        nhtsa_ctx: NHTSAAVContext,
    ) -> AutomotiveGovernanceAuditRecord:
        asil_level = self._safety_classifier.classify(function)
        asil_met, missing_activities = self._safety_classifier.verify_requirements_met(
            function, completed_safety_activities
        )

        r155_outcome, r155_violations = self._r155.evaluate(cybersec_ctx)
        r156_outcome, r156_violations = self._r156.evaluate(sums_ctx, asil_level)
        nhtsa_outcome, nhtsa_findings = self._nhtsa.evaluate(nhtsa_ctx)

        # Determine final outcome
        denial_reasons: list[str] = []
        conditions: list[str] = []

        if not asil_met:
            denial_reasons.append(
                f"ISO 26262 ASIL {asil_level.value}: incomplete verification activities: "
                + ", ".join(missing_activities)
            )
        if r155_outcome == GovernanceOutcome.DENY:
            denial_reasons.extend(r155_violations)
        if r156_outcome == GovernanceOutcome.DENY:
            denial_reasons.extend(r156_violations)
        if nhtsa_outcome == GovernanceOutcome.DENY:
            denial_reasons.extend(nhtsa_findings)

        if r155_outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS:
            conditions.extend(r155_violations)
        if r156_outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS:
            conditions.extend(r156_violations)
        if nhtsa_outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS:
            conditions.extend(nhtsa_findings)

        if denial_reasons:
            final_outcome = GovernanceOutcome.DENY
        elif conditions:
            final_outcome = GovernanceOutcome.ALLOW_WITH_CONDITIONS
        else:
            final_outcome = GovernanceOutcome.ALLOW

        return AutomotiveGovernanceAuditRecord(
            audit_id=str(uuid.uuid4()),
            system_name=system_name,
            function=function.value,
            sae_level=sae_level.value,
            asil_level=asil_level.value,
            asil_requirements_met=asil_met,
            missing_asil_activities=missing_activities,
            r155_outcome=r155_outcome.value,
            r155_violations=r155_violations,
            r156_outcome=r156_outcome.value,
            r156_violations=r156_violations,
            nhtsa_outcome=nhtsa_outcome.value,
            nhtsa_findings=nhtsa_findings,
            final_outcome=final_outcome,
            denial_reasons=denial_reasons,
            conditions=conditions,
        )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _print_audit(label: str, audit: AutomotiveGovernanceAuditRecord) -> None:
    OUTCOME_SYMBOLS = {
        GovernanceOutcome.ALLOW: "✅ ALLOW",
        GovernanceOutcome.ALLOW_WITH_CONDITIONS: "⚠️  ALLOW_WITH_CONDITIONS",
        GovernanceOutcome.ESCALATE_HUMAN: "🔶 ESCALATE_HUMAN",
        GovernanceOutcome.DENY: "🚫 DENY",
    }
    print(f"\n{'='*72}")
    print(f"  {label}")
    print(f"{'='*72}")
    print(f"  System       : {audit.system_name}")
    print(f"  Function     : {audit.function}")
    print(f"  SAE Level    : {audit.sae_level}")
    print(f"  ASIL Level   : {audit.asil_level}")
    print(f"  ASIL met     : {'✓' if audit.asil_requirements_met else '✗ MISSING: ' + ', '.join(audit.missing_asil_activities)}")
    print(f"  R155 (CSMS)  : {audit.r155_outcome}")
    print(f"  R156 (SUMS)  : {audit.r156_outcome}")
    print(f"  NHTSA        : {audit.nhtsa_outcome}")
    print(f"  OUTCOME      : {OUTCOME_SYMBOLS[audit.final_outcome]}")
    if audit.denial_reasons:
        print("\n  Denial reasons:")
        for r in audit.denial_reasons:
            print(f"    ✗ {r[:100]}...")
    if audit.conditions:
        print("\n  Conditions (must comply before/during operation):")
        for c in audit.conditions:
            print(f"    ⚠ {c[:100]}...")


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_a_adas_lane_keep() -> None:
    """
    Scenario A — ADAS Lane-Keep Assist (ASIL B): fully compliant.

    ASIL B requires FMEA, HARA, code review, and unit testing.
    All cybersecurity, SUMS, and NHTSA checks pass.
    """
    orch = AutomotiveAIOrchestrator()
    audit = orch.evaluate(
        system_name="VehicleCo LKA-3000",
        function=AISystemFunction.LANE_KEEP_ASSIST,
        sae_level=SAELevel.L2,
        completed_safety_activities=[
            "unit_testing", "code_review", "fmea_complete", "hara_complete"
        ],
        cybersec_ctx=CybersecurityContext(
            csms_certified=True,
            csms_certificate_id="CERT-EU-2024-0891",
            threat_assessment_current=True,
            known_vulnerabilities_mitigated=True,
            intrusion_detection_active=True,
            incident_response_tested=True,
            security_logging_enabled=True,
        ),
        sums_ctx=SoftwareUpdateContext(
            sums_documented=True,
            update_cryptographically_signed=True,
            rollback_capability_present=True,
            over_the_air=False,
            driver_consent_obtained=True,
            installation_state_verified=True,
            asil_change_requires_reapproval=False,
        ),
        nhtsa_ctx=NHTSAAVContext(
            sae_level=SAELevel.L2,
            odd_documented=True,
            safety_performance_tested=True,
            cybersecurity_compliance=True,
            crash_avoidance_validated=True,
            sgo_reporting_enabled=True,
            fallback_minimal_risk_condition=False,  # L2: driver still in control
            human_machine_interface_tested=True,
            data_recording_capability=True,
        ),
    )
    _print_audit("Scenario A — ADAS Lane-Keep Assist (ASIL B): compliant", audit)
    assert audit.final_outcome == GovernanceOutcome.ALLOW, (
        f"Expected ALLOW, got {audit.final_outcome}: {audit.denial_reasons}"
    )


def scenario_b_l3_cybersec_gap() -> None:
    """
    Scenario B — L3 Conditional Automation (ASIL C): R155 CSMS gap.

    No valid CSMS certificate. R155 denies deployment for EU market.
    """
    orch = AutomotiveAIOrchestrator()
    audit = orch.evaluate(
        system_name="VehicleCo AutoDrive-L3",
        function=AISystemFunction.PATH_PLANNING,
        sae_level=SAELevel.L3,
        completed_safety_activities=[
            "unit_testing", "code_review", "fmea_complete", "hara_complete",
            "independent_safety_assessment", "safety_case_documented",
        ],
        cybersec_ctx=CybersecurityContext(
            csms_certified=False,           # No CSMS certificate
            csms_certificate_id="",
            threat_assessment_current=True,
            known_vulnerabilities_mitigated=False,  # Unmitigated CVEs
            intrusion_detection_active=True,
            incident_response_tested=True,
            security_logging_enabled=True,
        ),
        sums_ctx=SoftwareUpdateContext(
            sums_documented=True,
            update_cryptographically_signed=True,
            rollback_capability_present=True,
            over_the_air=False,
            driver_consent_obtained=True,
            installation_state_verified=True,
        ),
        nhtsa_ctx=NHTSAAVContext(
            sae_level=SAELevel.L3,
            odd_documented=True,
            safety_performance_tested=True,
            cybersecurity_compliance=True,
            crash_avoidance_validated=True,
            sgo_reporting_enabled=True,
            fallback_minimal_risk_condition=True,
            human_machine_interface_tested=True,
            data_recording_capability=True,
        ),
    )
    _print_audit("Scenario B — L3 Conditional Automation: R155 CSMS denied", audit)
    assert audit.final_outcome == GovernanceOutcome.DENY
    assert any("§7.3.1" in r for r in audit.denial_reasons)


def scenario_c_ota_sums_noncompliant() -> None:
    """
    Scenario C — OTA Update to ASIL D Emergency Braking: R156 SUMS gap.

    Unsigned update package + no rollback = DENY regardless of ASIL.
    """
    orch = AutomotiveAIOrchestrator()
    audit = orch.evaluate(
        system_name="VehicleCo AEB-ECU OTA v4.1.2",
        function=AISystemFunction.OTA_UPDATE_EXECUTION,
        sae_level=SAELevel.L2,
        completed_safety_activities=[
            "unit_testing", "code_review", "fmea_complete", "hara_complete",
            "independent_safety_assessment", "safety_case_documented",
            "formal_verification", "safety_element_out_of_context",
        ],
        cybersec_ctx=CybersecurityContext(
            csms_certified=True,
            csms_certificate_id="CERT-EU-2024-0891",
            threat_assessment_current=True,
            known_vulnerabilities_mitigated=True,
            intrusion_detection_active=True,
            incident_response_tested=True,
            security_logging_enabled=True,
        ),
        sums_ctx=SoftwareUpdateContext(
            sums_documented=True,
            update_cryptographically_signed=False,  # No cryptographic signature
            rollback_capability_present=False,       # No rollback
            over_the_air=True,
            driver_consent_obtained=True,
            installation_state_verified=True,
        ),
        nhtsa_ctx=NHTSAAVContext(
            sae_level=SAELevel.L2,
            odd_documented=True,
            safety_performance_tested=True,
            cybersecurity_compliance=True,
            crash_avoidance_validated=True,
            sgo_reporting_enabled=True,
            fallback_minimal_risk_condition=False,
            human_machine_interface_tested=True,
            data_recording_capability=True,
        ),
    )
    _print_audit("Scenario C — OTA Update ASIL D: R156 SUMS non-compliant", audit)
    assert audit.final_outcome == GovernanceOutcome.DENY
    assert any("§7.2.2" in r for r in audit.denial_reasons)
    assert any("§7.2.4" in r for r in audit.denial_reasons)


def scenario_d_l4_robotaxi_sgo_reporting() -> None:
    """
    Scenario D — L4 High Automation Robotaxi: SGO reporting required.

    All safety/cybersecurity checks pass but SGO 2021-01 reporting
    obligation is triggered. Outcome = ALLOW_WITH_CONDITIONS.
    """
    orch = AutomotiveAIOrchestrator()
    audit = orch.evaluate(
        system_name="MobilityCo RoboFleet-L4",
        function=AISystemFunction.MOTION_CONTROL,
        sae_level=SAELevel.L4,
        completed_safety_activities=[
            "unit_testing", "code_review", "fmea_complete", "hara_complete",
            "independent_safety_assessment", "safety_case_documented",
            "formal_verification", "safety_element_out_of_context",
        ],
        cybersec_ctx=CybersecurityContext(
            csms_certified=True,
            csms_certificate_id="CERT-EU-2024-1104",
            threat_assessment_current=True,
            known_vulnerabilities_mitigated=True,
            intrusion_detection_active=True,
            incident_response_tested=True,
            security_logging_enabled=True,
        ),
        sums_ctx=SoftwareUpdateContext(
            sums_documented=True,
            update_cryptographically_signed=True,
            rollback_capability_present=True,
            over_the_air=True,
            driver_consent_obtained=True,
            installation_state_verified=True,
        ),
        nhtsa_ctx=NHTSAAVContext(
            sae_level=SAELevel.L4,
            odd_documented=True,
            safety_performance_tested=True,
            cybersecurity_compliance=True,
            crash_avoidance_validated=True,
            sgo_reporting_enabled=False,    # SGO not yet wired up
            fallback_minimal_risk_condition=True,
            human_machine_interface_tested=True,
            data_recording_capability=True,
        ),
    )
    _print_audit("Scenario D — L4 Robotaxi: ALLOW with SGO reporting condition", audit)
    assert audit.final_outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
    assert any("SGO" in c for c in audit.conditions)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Automotive AI Governance Framework")
    print("UNECE WP.29 R155/R156 · ISO 26262 ASIL · NHTSA AV Safety")
    print("All checks are independent; DENY from any layer blocks deployment.")

    scenario_a_adas_lane_keep()
    scenario_b_l3_cybersec_gap()
    scenario_c_ota_sums_noncompliant()
    scenario_d_l4_robotaxi_sgo_reporting()

    print(f"\n{'='*72}")
    print("  All four scenarios complete.")
    print("  Key invariants verified:")
    print("    • ASIL B: unit_testing + code_review + fmea + hara required")
    print("    • R155: no valid CSMS → DENY (cannot type-approve)")
    print("    • R156: unsigned OTA + no rollback → DENY (ASIL D absolute)")
    print("    • NHTSA L4: SGO 2021-01 reporting obligation flagged as condition")
    print(f"{'='*72}")
