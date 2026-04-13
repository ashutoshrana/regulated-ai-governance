"""
10_eu_ai_act_governance.py — EU AI Act (Regulation 2024/1689) standalone
governance framework for AI systems deployed in the European Union.

Demonstrates a complete implementation of the EU AI Act risk-based approach:
prohibited AI practices (Article 5), high-risk AI classification (Article 6 /
Annex III), transparency obligations (Article 13), human oversight requirements
(Article 14), accuracy and robustness standards (Article 15), and General
Purpose AI model obligations (Articles 51–53).

    Layer 1  — Article 5 Guard (Prohibited Practices):
               Certain AI applications are absolutely prohibited regardless of
               safeguards: real-time remote biometric identification in public
               spaces (with narrow law enforcement exceptions), social scoring
               by public authorities, subliminal manipulation, exploitation of
               vulnerable groups, predictive policing, and emotion recognition
               in workplaces/schools.

    Layer 2  — Article 6 / Annex III Classification Guard:
               High-risk AI systems covering 8 Annex III domains receive
               elevated obligations: biometric identification and categorisation,
               critical infrastructure management, education and vocational
               training, employment and worker management, access to essential
               services, law enforcement, migration and border control,
               administration of justice.

    Layer 3  — Article 13 Transparency Guard:
               High-risk AI systems must provide clear capability documentation,
               intended purpose, accuracy/performance ranges, known limitations,
               and human oversight specifications. Systems without compliant
               transparency documentation cannot operate.

    Layer 4  — Article 14 Human Oversight Guard:
               High-risk AI systems must be deployable under effective human
               oversight: meaningful review capability, override mechanism,
               and active monitoring duty. Automated-only deployment of
               high-risk systems is not permitted.

    Layer 5  — Article 15 Accuracy/Robustness Guard:
               Appropriate accuracy levels for the intended purpose, resilience
               against errors, faults, and inconsistencies; and cybersecurity
               measures commensurate with the risk.

    Layer 6  — GPAI Guard (Articles 51–53):
               General Purpose AI models with systemic risk (training compute
               ≥ 10^25 FLOPs) have additional obligations: adversarial testing,
               incident reporting to the Commission, model evaluation, and
               cybersecurity measures. All GPAI models require model cards.

Scenarios
---------

  A. High-risk employment screening AI — Article 6 Annex III (employment/worker
     management). Transparency, human oversight, and accuracy obligations apply.
     System is compliant; governance ALLOWS with compliance record.

  B. Prohibited social scoring system — Article 5(1)(c): AI by public authority
     for social scoring that leads to detrimental treatment. Absolute prohibition;
     governance DENIES with no mitigation path.

  C. GPAI model deployment — Article 51 systemic risk threshold exceeded (training
     compute > 10^25 FLOPs). Requires model card, adversarial testing, incident
     reporting capability. Non-compliant model card → DENY.

  D. Minimal-risk AI chatbot — below Annex III; no transparency/oversight
     mandate. Voluntary transparency code recommended. Governance ALLOWS
     without conditions.

No external dependencies required.

Run:
    python examples/10_eu_ai_act_governance.py
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------

class AIRiskLevel(str, Enum):
    """
    EU AI Act risk classification tiers.
    Article 5 = UNACCEPTABLE; Annex III = HIGH; voluntary code = LIMITED/MINIMAL.
    """
    UNACCEPTABLE_RISK = "UNACCEPTABLE_RISK"  # Article 5 — absolute prohibition
    HIGH_RISK = "HIGH_RISK"                  # Article 6 + Annex III — elevated obligations
    LIMITED_RISK = "LIMITED_RISK"            # Article 50 — transparency obligations only
    MINIMAL_RISK = "MINIMAL_RISK"            # No mandatory obligations; voluntary code


class AnnexIIICategory(str, Enum):
    """
    Annex III categories of high-risk AI systems under Article 6(2).
    Systems falling under any of these categories are HIGH_RISK.
    """
    BIOMETRIC_ID = "ANNEX_III_1"             # Biometric identification and categorisation
    CRITICAL_INFRASTRUCTURE = "ANNEX_III_2"  # Critical infrastructure management/operation
    EDUCATION = "ANNEX_III_3"               # Education and vocational training
    EMPLOYMENT = "ANNEX_III_4"              # Employment, workers management, self-employment
    ESSENTIAL_SERVICES = "ANNEX_III_5"      # Access to essential private/public services
    LAW_ENFORCEMENT = "ANNEX_III_6"         # Law enforcement
    MIGRATION_BORDER = "ANNEX_III_7"        # Migration, asylum, border control
    JUSTICE = "ANNEX_III_8"                 # Administration of justice and democratic processes


class ProhibitedAIType(str, Enum):
    """
    Article 5(1) prohibited AI practices. Deployment of any of these is
    unconditionally denied regardless of safeguards or operator intent.
    """
    REAL_TIME_BIOMETRIC_PUBLIC = "ART5_1A"      # Real-time remote biometric ID in public spaces
    SOCIAL_SCORING_PUBLIC = "ART5_1C"           # Social scoring by public authorities
    SUBLIMINAL_MANIPULATION = "ART5_1B"         # Subliminal/manipulative AI
    VULNERABILITY_EXPLOITATION = "ART5_1B_VUL"  # Exploitation of vulnerable groups
    PREDICTIVE_POLICING_INDIVIDUAL = "ART5_1D"  # Predictive policing targeting individuals
    EMOTION_RECOGNITION_WORK_SCHOOL = "ART5_1F" # Emotion recognition in workplace/education
    UNTARGETED_FACE_SCRAPING = "ART5_1E"        # Untargeted facial image scraping


class GovernanceOutcome(str, Enum):
    """Governance decision outcomes, in priority order DENY > ESCALATE > ALLOW."""
    ALLOW = "ALLOW"                           # System may operate
    ALLOW_WITH_CONDITIONS = "ALLOW_WITH_CONDITIONS"  # Operates with mandatory disclosures
    ESCALATE_HUMAN = "ESCALATE_HUMAN"         # Requires notified body or national authority review
    DENY = "DENY"                             # System must not operate; deployment blocked


# ---------------------------------------------------------------------------
# Request context
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EUAIActRequestContext:
    """
    Governance evaluation context for an AI system deployment.

    Attributes
    ----------
    system_name:
        Human-readable name for logging and audit purposes.
    annex_iii_category:
        Annex III category, if applicable. None = not Annex III classified.
    prohibited_ai_type:
        Article 5 prohibited practice, if applicable. None = not prohibited.
    is_gpai:
        True if this is a General Purpose AI model (Article 3(63)).
    gpai_flops_training:
        Training compute in FLOPs. Required when is_gpai=True.
        Systemic risk threshold: 10^25 FLOPs (Article 51).
    transparency_documentation_complete:
        Article 13 documentation is complete (capability statement, intended
        purpose, accuracy ranges, limitations, oversight specifications).
    human_oversight_mechanism_in_place:
        Article 14 human oversight implemented (meaningful review capability,
        override mechanism, monitoring duty).
    accuracy_level_validated:
        Article 15: accuracy validated for intended purpose.
    robustness_measures_in_place:
        Article 15: resilience against errors, adversarial inputs.
    model_card_published:
        GPAI model card published per Article 53(1)(d).
    adversarial_testing_completed:
        GPAI systemic risk: adversarial testing per Article 55(1)(a).
    incident_reporting_capability:
        GPAI systemic risk: capability to report incidents per Article 55(1)(c).
    conformity_assessment_done:
        Article 43: conformity assessment performed (required for high-risk
        Annex III systems except those self-assessed under Annex VI).
    deployer_is_public_authority:
        True if the deployer is a public authority (affects social scoring
        and law enforcement prohibition thresholds).
    deployment_in_public_space:
        True if the system operates in publicly accessible physical space
        (relevant for real-time biometric prohibition).
    """
    system_name: str
    annex_iii_category: Optional[AnnexIIICategory] = None
    prohibited_ai_type: Optional[ProhibitedAIType] = None
    is_gpai: bool = False
    gpai_flops_training: Optional[float] = None   # e.g. 1e25
    transparency_documentation_complete: bool = False
    human_oversight_mechanism_in_place: bool = False
    accuracy_level_validated: bool = False
    robustness_measures_in_place: bool = False
    model_card_published: bool = False
    adversarial_testing_completed: bool = False
    incident_reporting_capability: bool = False
    conformity_assessment_done: bool = False
    deployer_is_public_authority: bool = False
    deployment_in_public_space: bool = False
    system_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Guard implementations
# ---------------------------------------------------------------------------

class Article5ProhibitionGuard:
    """
    Enforces Article 5(1) prohibited AI practices.

    Article 5 prohibitions are absolute — there is no safeguard, transparency
    measure, or oversight mechanism that can lawfully permit a prohibited
    application. DENY with no escalation path.

    Note: Article 5(1)(a) includes a narrow exception for law enforcement
    use of real-time biometric identification in public spaces; this
    implementation applies the default prohibition for non-law-enforcement
    deployers.
    """

    _ALWAYS_PROHIBITED: frozenset[ProhibitedAIType] = frozenset({
        ProhibitedAIType.SOCIAL_SCORING_PUBLIC,
        ProhibitedAIType.SUBLIMINAL_MANIPULATION,
        ProhibitedAIType.VULNERABILITY_EXPLOITATION,
        ProhibitedAIType.PREDICTIVE_POLICING_INDIVIDUAL,
        ProhibitedAIType.EMOTION_RECOGNITION_WORK_SCHOOL,
        ProhibitedAIType.UNTARGETED_FACE_SCRAPING,
    })

    def evaluate(self, ctx: EUAIActRequestContext) -> dict[str, Any]:
        if ctx.prohibited_ai_type is None:
            return {"allowed": True, "violations": []}

        violations: list[str] = []

        if ctx.prohibited_ai_type in self._ALWAYS_PROHIBITED:
            violations.append(
                f"Article 5(1) — prohibited AI practice: "
                f"{ctx.prohibited_ai_type.value} is unconditionally prohibited"
            )

        elif ctx.prohibited_ai_type == ProhibitedAIType.REAL_TIME_BIOMETRIC_PUBLIC:
            if ctx.deployment_in_public_space:
                violations.append(
                    "Article 5(1)(a) — real-time remote biometric identification "
                    "in publicly accessible spaces is prohibited (non-law-enforcement deployer)"
                )

        return {"allowed": len(violations) == 0, "violations": violations}


class Article6ClassificationGuard:
    """
    Evaluates whether the AI system is HIGH_RISK under Article 6 + Annex III
    and whether required conformity assessment has been performed.

    Article 6(2) lists 8 Annex III domains. A system falling under any
    domain is high-risk and requires conformity assessment (Article 43)
    before deployment.
    """

    def evaluate(self, ctx: EUAIActRequestContext) -> dict[str, Any]:
        if ctx.annex_iii_category is None:
            return {
                "allowed": True,
                "risk_level": AIRiskLevel.MINIMAL_RISK,
                "violations": [],
                "is_high_risk": False,
            }

        violations: list[str] = []
        if not ctx.conformity_assessment_done:
            violations.append(
                f"Article 43 — conformity assessment required before deployment "
                f"of high-risk AI system ({ctx.annex_iii_category.value})"
            )

        return {
            "allowed": len(violations) == 0,
            "risk_level": AIRiskLevel.HIGH_RISK,
            "violations": violations,
            "is_high_risk": True,
        }


class Article13TransparencyGuard:
    """
    Enforces Article 13 transparency and provision of information obligations
    for high-risk AI systems.

    High-risk AI systems must be accompanied by instructions for use that
    include: capabilities and limitations, accuracy/performance ranges,
    intended purpose, foreseeable risks, human oversight specifications,
    and technical infrastructure requirements.
    """

    def evaluate(self, ctx: EUAIActRequestContext, is_high_risk: bool) -> dict[str, Any]:
        if not is_high_risk:
            return {"allowed": True, "violations": []}

        violations: list[str] = []
        if not ctx.transparency_documentation_complete:
            violations.append(
                "Article 13 — high-risk AI system must be accompanied by complete "
                "transparency documentation: capabilities, limitations, accuracy ranges, "
                "intended purpose, and human oversight specifications"
            )

        return {"allowed": len(violations) == 0, "violations": violations}


class Article14OversightGuard:
    """
    Enforces Article 14 human oversight obligations for high-risk AI systems.

    Article 14 requires that high-risk AI systems are designed and developed
    such that natural persons can effectively oversee them during the period
    of use. This includes:
    - Meaningful review capability (not rubber-stamp)
    - Override/stop functionality
    - Active monitoring duty with ability to intervene
    """

    def evaluate(self, ctx: EUAIActRequestContext, is_high_risk: bool) -> dict[str, Any]:
        if not is_high_risk:
            return {"allowed": True, "violations": []}

        violations: list[str] = []
        if not ctx.human_oversight_mechanism_in_place:
            violations.append(
                "Article 14 — high-risk AI system must have effective human oversight: "
                "meaningful review capability, override mechanism, and active "
                "monitoring duty are mandatory"
            )

        return {"allowed": len(violations) == 0, "violations": violations}


class Article15RobustnessGuard:
    """
    Enforces Article 15 accuracy, robustness, and cybersecurity requirements
    for high-risk AI systems.

    High-risk AI systems must achieve appropriate accuracy levels for their
    intended purpose and be resilient against errors, faults, inconsistencies,
    and adversarial manipulation.
    """

    def evaluate(self, ctx: EUAIActRequestContext, is_high_risk: bool) -> dict[str, Any]:
        if not is_high_risk:
            return {"allowed": True, "violations": []}

        violations: list[str] = []
        if not ctx.accuracy_level_validated:
            violations.append(
                "Article 15(1) — appropriate accuracy levels for intended purpose "
                "must be validated before high-risk AI system deployment"
            )
        if not ctx.robustness_measures_in_place:
            violations.append(
                "Article 15(2) — resilience against errors, faults, inconsistencies, "
                "and adversarial inputs must be demonstrated"
            )

        return {"allowed": len(violations) == 0, "violations": violations}


_GPAI_SYSTEMIC_RISK_FLOPS_THRESHOLD = 1e25  # Article 51(1): 10^25 FLOPs


class GPAIGuard:
    """
    Enforces General Purpose AI model obligations under Articles 51–53.

    All GPAI models must publish model cards (Article 53(1)(d)).

    GPAI models with systemic risk (training compute ≥ 10^25 FLOPs under
    Article 51(1)) have additional obligations:
    - Adversarial testing (Article 55(1)(a))
    - Incident reporting capability to the Commission (Article 55(1)(c))
    - Enhanced cybersecurity measures
    """

    def evaluate(self, ctx: EUAIActRequestContext) -> dict[str, Any]:
        if not ctx.is_gpai:
            return {"allowed": True, "violations": [], "has_systemic_risk": False}

        violations: list[str] = []

        # All GPAI models: model card required
        if not ctx.model_card_published:
            violations.append(
                "Article 53(1)(d) — all GPAI models must publish a model card "
                "disclosing training data, capabilities, and limitations"
            )

        # Determine systemic risk
        flops = ctx.gpai_flops_training or 0.0
        has_systemic_risk = flops >= _GPAI_SYSTEMIC_RISK_FLOPS_THRESHOLD

        if has_systemic_risk:
            if not ctx.adversarial_testing_completed:
                violations.append(
                    f"Article 55(1)(a) — GPAI model with systemic risk "
                    f"(training compute {flops:.2e} FLOPs ≥ 10^25 threshold) "
                    f"must complete adversarial testing before deployment"
                )
            if not ctx.incident_reporting_capability:
                violations.append(
                    "Article 55(1)(c) — GPAI model with systemic risk must have "
                    "capability to report incidents to the AI Office / Commission"
                )

        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "has_systemic_risk": has_systemic_risk,
        }


# ---------------------------------------------------------------------------
# Audit record
# ---------------------------------------------------------------------------

@dataclass
class EUAIActAuditRecord:
    """
    Governance decision record for EU AI Act compliance review.

    Captures the risk classification, applicable articles, all violations
    detected, and conformity assessment status for regulatory submission.
    """
    request_id: str
    system_id: str
    system_name: str
    outcome: GovernanceOutcome
    risk_level: AIRiskLevel
    is_high_risk: bool
    is_gpai: bool
    has_systemic_risk: bool
    applicable_articles: list[str]
    violations: list[str]
    conformity_assessment_required: bool
    notified_body_required: bool
    annex_iii_category: Optional[str]
    prohibited_ai_type: Optional[str]


# ---------------------------------------------------------------------------
# Governance Orchestrator
# ---------------------------------------------------------------------------

class EUAIActGovernanceOrchestrator:
    """
    EU AI Act governance orchestrator applying all six guard layers.

    Decision priority:
        DENY        — Article 5 prohibited practice, or unresolved high-risk
                      compliance violations
        ESCALATE    — Conformity assessment not completed; referred to
                      notified body / national authority
        ALLOW_CONDITIONS — GPAI or high-risk with all compliance met
        ALLOW       — Minimal/limited risk; no mandatory obligations violated
    """

    def __init__(self) -> None:
        self._art5 = Article5ProhibitionGuard()
        self._art6 = Article6ClassificationGuard()
        self._art13 = Article13TransparencyGuard()
        self._art14 = Article14OversightGuard()
        self._art15 = Article15RobustnessGuard()
        self._gpai = GPAIGuard()

    def evaluate(self, ctx: EUAIActRequestContext) -> EUAIActAuditRecord:
        all_violations: list[str] = []
        applicable_articles: list[str] = []

        # Layer 1: Article 5 — absolute prohibition
        art5_result = self._art5.evaluate(ctx)
        if art5_result["violations"]:
            all_violations.extend(art5_result["violations"])
            applicable_articles.append("Article 5 (Prohibited Practices)")

        # Layer 2: Article 6 — Annex III classification
        art6_result = self._art6.evaluate(ctx)
        is_high_risk = art6_result.get("is_high_risk", False)
        risk_level: AIRiskLevel = art6_result.get("risk_level", AIRiskLevel.MINIMAL_RISK)
        if is_high_risk:
            applicable_articles.append("Article 6 / Annex III (High-Risk Classification)")
        if art6_result["violations"]:
            all_violations.extend(art6_result["violations"])

        # Layers 3–5: High-risk obligations (only if Annex III)
        if is_high_risk:
            art13_result = self._art13.evaluate(ctx, is_high_risk)
            art14_result = self._art14.evaluate(ctx, is_high_risk)
            art15_result = self._art15.evaluate(ctx, is_high_risk)

            if art13_result["violations"]:
                all_violations.extend(art13_result["violations"])
                applicable_articles.append("Article 13 (Transparency)")
            if art14_result["violations"]:
                all_violations.extend(art14_result["violations"])
                applicable_articles.append("Article 14 (Human Oversight)")
            if art15_result["violations"]:
                all_violations.extend(art15_result["violations"])
                applicable_articles.append("Article 15 (Accuracy/Robustness)")

        # Layer 6: GPAI
        gpai_result = self._gpai.evaluate(ctx)
        has_systemic_risk = gpai_result.get("has_systemic_risk", False)
        if ctx.is_gpai:
            if has_systemic_risk:
                applicable_articles.append("Articles 51–55 (GPAI with Systemic Risk)")
            else:
                applicable_articles.append("Articles 51–53 (GPAI)")
        if gpai_result["violations"]:
            all_violations.extend(gpai_result["violations"])

        # Determine outcome
        if not art5_result["allowed"]:
            # Article 5 prohibition = absolute DENY
            outcome = GovernanceOutcome.DENY
        elif all_violations:
            # Non-Article-5 violations on a high-risk system:
            # if conformity assessment is missing → ESCALATE to notified body
            # otherwise DENY (compliance violations not resolved)
            if is_high_risk and not ctx.conformity_assessment_done:
                outcome = GovernanceOutcome.ESCALATE_HUMAN
            else:
                outcome = GovernanceOutcome.DENY
        elif is_high_risk or (ctx.is_gpai and has_systemic_risk):
            outcome = GovernanceOutcome.ALLOW_WITH_CONDITIONS
        else:
            outcome = GovernanceOutcome.ALLOW

        # Conformity assessment requirements
        conformity_required = is_high_risk
        notified_body_required = (
            is_high_risk
            and ctx.annex_iii_category in {
                AnnexIIICategory.BIOMETRIC_ID,
                AnnexIIICategory.LAW_ENFORCEMENT,
                AnnexIIICategory.MIGRATION_BORDER,
                AnnexIIICategory.JUSTICE,
            }
        )

        return EUAIActAuditRecord(
            request_id=str(uuid.uuid4()),
            system_id=ctx.system_id,
            system_name=ctx.system_name,
            outcome=outcome,
            risk_level=risk_level,
            is_high_risk=is_high_risk,
            is_gpai=ctx.is_gpai,
            has_systemic_risk=has_systemic_risk,
            applicable_articles=applicable_articles,
            violations=all_violations,
            conformity_assessment_required=conformity_required,
            notified_body_required=notified_body_required,
            annex_iii_category=ctx.annex_iii_category.value if ctx.annex_iii_category else None,
            prohibited_ai_type=ctx.prohibited_ai_type.value if ctx.prohibited_ai_type else None,
        )


# ---------------------------------------------------------------------------
# Scenario helpers
# ---------------------------------------------------------------------------

def _print_result(label: str, audit: EUAIActAuditRecord) -> None:
    outcome_icons = {
        GovernanceOutcome.ALLOW: "✓  ALLOW",
        GovernanceOutcome.ALLOW_WITH_CONDITIONS: "✓⚠  ALLOW WITH CONDITIONS",
        GovernanceOutcome.ESCALATE_HUMAN: "↑  ESCALATE TO NOTIFIED BODY / AUTHORITY",
        GovernanceOutcome.DENY: "✗  DENY",
    }
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    print(f"  System       : {audit.system_name}")
    print(f"  Risk Level   : {audit.risk_level.value}")
    print(f"  Outcome      : {outcome_icons[audit.outcome]}")
    print(f"  High-Risk    : {audit.is_high_risk}")
    print(f"  GPAI         : {audit.is_gpai}  (systemic risk: {audit.has_systemic_risk})")
    if audit.annex_iii_category:
        print(f"  Annex III    : {audit.annex_iii_category}")
    if audit.prohibited_ai_type:
        print(f"  Prohibited   : {audit.prohibited_ai_type}")
    print(f"  Conformity   : required={audit.conformity_assessment_required}  notified_body={audit.notified_body_required}")
    print()
    if audit.applicable_articles:
        print(f"  Applicable articles: {', '.join(audit.applicable_articles)}")
    print()
    if audit.violations:
        print(f"  Violations ({len(audit.violations)}):")
        for v in audit.violations:
            print(f"    ✗  {v}")
    else:
        print("  Violations: none — all applicable article requirements satisfied")


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_a_high_risk_employment_screening() -> None:
    """
    Annex III category 4 (employment / worker management).
    Fully compliant: conformity assessment done, transparency complete,
    human oversight in place, accuracy validated, robustness measures active.
    """
    ctx = EUAIActRequestContext(
        system_name="CV Ranking & Candidate Screening AI",
        annex_iii_category=AnnexIIICategory.EMPLOYMENT,
        prohibited_ai_type=None,
        is_gpai=False,
        transparency_documentation_complete=True,
        human_oversight_mechanism_in_place=True,
        accuracy_level_validated=True,
        robustness_measures_in_place=True,
        conformity_assessment_done=True,
        deployer_is_public_authority=False,
    )
    orchestrator = EUAIActGovernanceOrchestrator()
    audit = orchestrator.evaluate(ctx)
    _print_result(
        "Scenario A — High-risk Annex III (employment screening): compliant deployment",
        audit,
    )
    assert audit.outcome == GovernanceOutcome.ALLOW_WITH_CONDITIONS
    assert audit.is_high_risk
    assert len(audit.violations) == 0


def scenario_b_prohibited_social_scoring() -> None:
    """
    Article 5(1)(c): AI system by a public authority for social scoring that
    leads to detrimental treatment. Absolute prohibition; no compliance path.
    """
    ctx = EUAIActRequestContext(
        system_name="Citizen Trust Score System",
        annex_iii_category=None,
        prohibited_ai_type=ProhibitedAIType.SOCIAL_SCORING_PUBLIC,
        is_gpai=False,
        transparency_documentation_complete=True,  # Compliance is irrelevant for Art. 5
        human_oversight_mechanism_in_place=True,
        accuracy_level_validated=True,
        robustness_measures_in_place=True,
        conformity_assessment_done=True,
        deployer_is_public_authority=True,  # Public authority deployer
    )
    orchestrator = EUAIActGovernanceOrchestrator()
    audit = orchestrator.evaluate(ctx)
    _print_result(
        "Scenario B — Article 5 prohibited: social scoring by public authority",
        audit,
    )
    assert audit.outcome == GovernanceOutcome.DENY
    assert len(audit.violations) >= 1
    assert any("Article 5" in v for v in audit.violations)


def scenario_c_gpai_systemic_risk_non_compliant() -> None:
    """
    GPAI model with training compute 3×10^25 FLOPs (above systemic risk threshold).
    Model card NOT published. Adversarial testing NOT completed.
    """
    ctx = EUAIActRequestContext(
        system_name="Enterprise Foundation Model v3",
        annex_iii_category=None,
        prohibited_ai_type=None,
        is_gpai=True,
        gpai_flops_training=3e25,              # > 10^25 threshold → systemic risk
        transparency_documentation_complete=True,
        human_oversight_mechanism_in_place=True,
        accuracy_level_validated=True,
        robustness_measures_in_place=True,
        conformity_assessment_done=False,
        model_card_published=False,            # Article 53(1)(d) — missing
        adversarial_testing_completed=False,   # Article 55(1)(a) — missing
        incident_reporting_capability=True,    # Article 55(1)(c) — present
    )
    orchestrator = EUAIActGovernanceOrchestrator()
    audit = orchestrator.evaluate(ctx)
    _print_result(
        "Scenario C — GPAI systemic risk: model card missing + adversarial testing incomplete",
        audit,
    )
    assert audit.outcome == GovernanceOutcome.DENY
    assert audit.has_systemic_risk
    assert any("model card" in v.lower() or "53" in v for v in audit.violations)
    assert any("adversarial" in v.lower() or "55" in v for v in audit.violations)


def scenario_d_minimal_risk_chatbot() -> None:
    """
    Standard customer service chatbot. Not Annex III; not GPAI; not prohibited.
    No mandatory obligations apply. Voluntary transparency code recommended.
    Governance ALLOWS without conditions.
    """
    ctx = EUAIActRequestContext(
        system_name="Customer Support Chatbot",
        annex_iii_category=None,          # Not Annex III
        prohibited_ai_type=None,
        is_gpai=False,
        transparency_documentation_complete=True,
        human_oversight_mechanism_in_place=True,
        accuracy_level_validated=True,
        robustness_measures_in_place=True,
        conformity_assessment_done=False,  # Not required for minimal-risk
        model_card_published=False,        # Not required (not GPAI)
        deployer_is_public_authority=False,
    )
    orchestrator = EUAIActGovernanceOrchestrator()
    audit = orchestrator.evaluate(ctx)
    _print_result(
        "Scenario D — Minimal-risk chatbot: no mandatory obligations, ALLOW",
        audit,
    )
    assert audit.outcome == GovernanceOutcome.ALLOW
    assert not audit.is_high_risk
    assert not audit.has_systemic_risk
    assert len(audit.violations) == 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("EU AI Act Governance Framework (Regulation 2024/1689)")
    print("Art. 5 Prohibition · Art. 6/Annex III Risk Classification")
    print("Art. 13 Transparency · Art. 14 Oversight · Art. 15 Robustness · Art. 51-53 GPAI")

    scenario_a_high_risk_employment_screening()
    scenario_b_prohibited_social_scoring()
    scenario_c_gpai_systemic_risk_non_compliant()
    scenario_d_minimal_risk_chatbot()

    print("\n" + "="*70)
    print("  All four scenarios complete.")
    print("  Risk-based approach demonstrated:")
    print("    • Article 5 prohibition → DENY (no mitigation path)")
    print("    • Annex III high-risk + all obligations met → ALLOW WITH CONDITIONS")
    print("    • GPAI systemic risk + missing model card/testing → DENY")
    print("    • Minimal-risk → ALLOW (voluntary code only)")
    print("="*70)
