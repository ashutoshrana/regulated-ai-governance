"""
20_singapore_ai_governance.py — Four-layer AI governance framework for AI systems
subject to Singapore law, covering the overlapping national and sector-level
obligations that apply to AI-driven data processing in Singapore.

Demonstrates a multi-layer governance orchestrator where four Singapore
regulatory frameworks each impose independent requirements on AI systems
deployed in Singapore:

    Layer 1  — PDPC Model AI Governance Framework v2 (2020):
               The Personal Data Protection Commission (PDPC) published
               Singapore's Model AI Governance Framework in 2019 (updated
               to version 2.0 in 2020), establishing detailed guidance for
               the responsible development and deployment of AI. The framework
               focuses on four areas of internal governance:
               (1) Internal Governance Structures and Measures — organisations
                   must establish clear ownership and accountability for AI
                   outcomes, including defined roles for humans in the AI
                   decision pipeline;
               (2) Determining the Level of Human Involvement in AI-Augmented
                   Decision-Making — the degree of human oversight must be
                   commensurate with the risk level of the AI decision; high-
                   risk automated decisions require human review pathways;
               (3) Operations Management — AI systems must be monitored for
                   performance, safety, and correctness throughout their
                   operational lifecycle; audit trails should be maintained for
                   medium- and high-risk systems;
               (4) Stakeholder Interaction and Communication — individuals
                   affected by AI-driven decisions must be able to obtain an
                   explanation of how the decision was made; explainability is
                   mandatory for automated decisions affecting individuals; and
                   organisations should conduct an AI Impact Assessment (AIIA)
                   before deploying high-risk AI systems.

    Layer 2  — PDPA (Personal Data Protection Act 2012):
               The Personal Data Protection Act 2012 (Act 26 of 2012, as
               amended by the Personal Data Protection (Amendment) Act 2020)
               constitutes Singapore's primary data protection legislation,
               applicable to all organisations collecting, using, or disclosing
               personal data of individuals in Singapore. Key obligations for
               AI systems include:
               Section 13 — Consent Obligation: Organisations must obtain the
                   individual's consent (or rely on a prescribed exception)
                   before or at the time of collecting, using, or disclosing
                   personal data; deemed consent (Section 15) and contractual
                   necessity (Section 17) are recognised exceptions but must
                   be documented;
               Section 18 — Purpose Limitation Obligation: Organisations must
                   collect, use, and disclose personal data only for purposes
                   that a reasonable person would consider appropriate in the
                   circumstances and for which the individual has been notified
                   (via a Data Protection Notice);
               Section 24 — Protection Obligation: Organisations must protect
                   personal data in their possession or under their control by
                   making reasonable security arrangements to prevent
                   unauthorised access, collection, use, disclosure, copying,
                   modification, disposal, or similar risks;
               Section 26 — Transfer Limitation Obligation: Organisations must
                   not transfer personal data to a country or territory outside
                   Singapore except in accordance with the requirements
                   prescribed by the PDPC — the receiving jurisdiction must
                   appear on the PDPC Third Schedule (white-listed countries)
                   or the organisation must have contractual clauses providing
                   a comparable level of protection;
               Data Protection Officers: Large and medium organisations and
                   organisations processing sensitive personal data are
                   recommended to appoint a Data Protection Officer (DPO) to
                   oversee PDPA compliance.

    Layer 3  — MAS FEAT Principles (Fairness, Ethics, Accountability,
               Transparency — Financial Services AI):
               The Monetary Authority of Singapore (MAS) published its FEAT
               Principles in November 2018 as guidance for financial
               institutions using AI and data analytics in consequential
               decisions. The four FEAT principles establish specific
               obligations for MAS-regulated financial institutions:
               Fairness (F.1) — AI models used in consequential decisions
                   must be tested for biased or discriminatory outcomes;
                   ongoing monitoring for demographic parity, equalized odds,
                   and other fairness metrics is required; bias testing must
                   be documented;
               Ethics (E.1) — AI system design and operation must be aligned
                   with MAS ethical expectations; AI must not facilitate market
                   manipulation, customer deception, or regulatory arbitrage;
               Accountability (A.2) — For high-risk AI used in material
                   financial decisions, the AI model and its risk framework
                   should be reviewed by MAS-authorised supervisors; model
                   risk management frameworks must be maintained;
               Transparency (T.1) — Financial institutions must be able to
                   explain individual AI-driven decisions on request to
                   customers and regulators; black-box models require
                   compensating explainability mechanisms (SHAP, LIME, etc.)
                   for medium- and high-risk decisions.
               Institutions that are not MAS-regulated financial institutions
               are outside the scope of FEAT; they receive an acknowledgment
               that FEAT does not apply and no adverse decision.

    Layer 4  — IMDA AI Testing Framework:
               The Infocomm Media Development Authority (IMDA) developed the
               AI Verify testing framework (2022, updated 2023) in partnership
               with the PDPC to provide a methodology for organisations to
               verify that their AI systems meet internationally accepted
               principles of responsible AI. The framework covers eleven
               principles aligned with major international AI governance
               frameworks (EU AI Act, NIST AI RMF, OECD AI Principles) and
               establishes two key procedural requirements:
               Model Registration — high-risk AI models deployed in Singapore
                   should be registered and tested using AI Verify; unregistered
                   high-risk models require human review before deployment;
               Bias and Fairness Testing — non-low-risk AI systems must be
                   tested for bias and fairness; AI Verify provides standardised
                   test kits for demographic parity, equalized odds, and
                   disparate impact metrics; and
               Human Decision Pathway — where a document or use case flags a
                   human decision requirement, fully automated systems without
                   a human review pathway must be denied.

No external dependencies required.

Run:
    python examples/20_singapore_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class SingaporeAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under the PDPC Model AI Governance
    Framework v2 (2020).

    HIGH    — Significant potential to affect individual rights, safety, or
              welfare; substantial human oversight required; AI Impact
              Assessment (AIIA) recommended; MAS model approval required for
              high-risk financial AI.
    MEDIUM  — Meaningful but bounded risk; moderate human oversight required;
              audit trails and bias testing required; explainability expected
              for automated decisions.
    LOW     — Limited potential for harm; minimal oversight; lighter
              procedural requirements; some checks do not apply.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SingaporeAIDecision(str, Enum):
    """Final governance decision for a Singapore AI system evaluation."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    REDACTED = "REDACTED"


class SingaporeSector(str, Enum):
    """
    Deployment sector for the AI system.

    FINANCIAL_SERVICES — MAS-regulated entity; MAS FEAT Principles apply in
                         Layer 3.
    HEALTHCARE         — Healthcare institution; heightened privacy and safety
                         obligations apply.
    GOVERNMENT         — Singapore government agency or statutory board under
                         the Smart Nation initiative; GovTech guidelines apply.
    GENERAL            — General private-sector organisation; MAS FEAT and
                         healthcare-specific rules do not apply.
    """

    FINANCIAL_SERVICES = "FINANCIAL_SERVICES"
    HEALTHCARE = "HEALTHCARE"
    GOVERNMENT = "GOVERNMENT"
    GENERAL = "GENERAL"


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SingaporeAIContext:
    """
    Governance review context for a Singapore AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    sector : SingaporeSector
        The sector in which the AI system is deployed. A value of
        ``SingaporeSector.FINANCIAL_SERVICES`` triggers MAS FEAT checks in
        Layer 3.

    — Risk classification —

    ai_risk_level : SingaporeAIRiskLevel
        Risk level under the PDPC Model AI Governance Framework v2.

    — PDPC Model AI Governance Framework v2 —

    is_automated_decision : bool
        True if the AI system makes a material decision about an individual
        with no human review in the decision loop. Per PDPC Section 2.3, high-
        risk automated decisions require an available human review pathway;
        per Section 2.4, all automated decisions affecting individuals require
        explainability.
    has_ai_impact_assessment : bool
        True if an AI Impact Assessment (AIIA) has been completed before
        deployment. PDPC recommends an AIIA for all high-risk AI systems.
    explainability_available : bool
        True if the system can provide an explanation of any individual
        automated decision on request (PDPC Section 2.4).
    audit_trail_enabled : bool
        True if a comprehensive audit trail of AI decisions is maintained.
        Required for medium- and high-risk AI systems (PDPC Section 2.5).
    human_review_available : bool
        True if an escalation path to a human reviewer exists for decisions
        made or influenced by the AI system.

    — PDPA (Personal Data Protection Act 2012) —

    involves_personal_data : bool
        True if the AI system collects, uses, or discloses personal data of
        individuals in Singapore.
    has_pdpa_consent : bool
        True if a valid Data Protection Notice has been provided and consent
        obtained (or a prescribed PDPA exception applies) — PDPA Section 13.
    has_data_protection_officer : bool
        True if a Data Protection Officer (DPO) has been appointed. Recommended
        by PDPA for medium/large organisations and those processing sensitive
        personal data (other than GENERAL sector).
    is_cross_border_transfer : bool
        True if personal data is transferred to a country or territory outside
        Singapore — triggers PDPA Section 26 transfer limitation checks.
    transfer_adequate_protection : bool
        True if the cross-border transfer meets PDPA requirements: recipient
        jurisdiction is on the PDPC Third Schedule (white-listed) or
        contractual clauses providing comparable protection are in place
        (PDPA Section 26).

    — MAS FEAT Principles (financial institutions only) —

    is_financial_institution : bool
        True if the organisation is a MAS-regulated financial institution.
        Required for FEAT Principles to apply in Layer 3.
    has_mas_approval : bool
        True if the AI model has been reviewed under the MAS model risk
        management framework and received supervisory approval (MAS FEAT A.2).
    bias_testing_done : bool
        True if bias and fairness testing of the AI model has been completed
        and documented (MAS FEAT F.1; also used in IMDA Layer 4).

    — IMDA AI Testing Framework —

    model_registered : bool
        True if the AI model has been registered and tested under the IMDA
        AI Verify framework, as expected for high-risk AI deployments.

    — Smart Nation / Government —

    is_government_system : bool
        True if the system is deployed by a Singapore government agency or
        statutory board as part of the Smart Nation initiative.
    """

    user_id: str
    sector: SingaporeSector
    ai_risk_level: SingaporeAIRiskLevel

    # PDPC Model AI Governance Framework v2
    is_automated_decision: bool
    has_ai_impact_assessment: bool
    explainability_available: bool
    audit_trail_enabled: bool
    human_review_available: bool

    # PDPA
    involves_personal_data: bool
    has_pdpa_consent: bool
    has_data_protection_officer: bool
    is_cross_border_transfer: bool
    transfer_adequate_protection: bool

    # MAS FEAT
    is_financial_institution: bool
    has_mas_approval: bool
    bias_testing_done: bool

    # IMDA
    model_registered: bool

    # Smart Nation / Government
    is_government_system: bool


@dataclass(frozen=True)
class SingaporeAIDocument:
    """
    Document metadata submitted to the Singapore AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    contains_personal_data : bool
        True if the document contains personal data of Singapore individuals.
    data_classification : str
        Sensitivity classification: "PUBLIC", "INTERNAL", "CONFIDENTIAL", or
        "RESTRICTED".
    is_financial_data : bool
        True if the document contains financial account or transaction data.
    is_health_data : bool
        True if the document contains health or medical information.
    is_government_data : bool
        True if the document contains Singapore government or restricted
        official data.
    requires_human_decision : bool
        True if the document or its originating use case explicitly flags that
        a human decision is required before any AI-driven action is taken.
    """

    document_id: str
    contains_personal_data: bool
    data_classification: str
    is_financial_data: bool
    is_health_data: bool
    is_government_data: bool
    requires_human_decision: bool


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class SingaporeAIFilterResult:
    """Result of a single Singapore AI governance filter evaluation."""

    filter_name: str
    decision: SingaporeAIDecision = SingaporeAIDecision.APPROVED
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = False

    @property
    def is_denied(self) -> bool:
        """True if this filter produced a DENIED decision."""
        return self.decision == SingaporeAIDecision.DENIED


# ---------------------------------------------------------------------------
# Layer 1 — PDPC Model AI Governance Framework v2
# ---------------------------------------------------------------------------


class PDPCModelAIGovernanceFilter:
    """
    Layer 1: PDPC Model AI Governance Framework v2 (2020).

    The Personal Data Protection Commission (PDPC) Model AI Governance
    Framework v2 provides detailed, practical guidance on responsible AI
    deployment in Singapore. It focuses on four areas: internal governance
    structures, determining the appropriate level of human involvement,
    operations management including audit trails, and stakeholder interaction
    including explainability. This filter evaluates the four principal
    controls most relevant to automated decision-making:

    (a) Human oversight for high-risk automated decisions (Section 2.3) —
        organisations must ensure that the degree of human involvement in
        AI-augmented decision-making is commensurate with the risk level;
        high-risk automated decisions with no human review pathway are
        non-compliant;
    (b) Explainability for automated decisions (Section 2.4) — organisations
        must be able to explain, on request, how an automated decision
        affecting an individual was made; black-box outputs are not
        acceptable where the decision has material consequences;
    (c) Audit trails for non-low-risk AI (Section 2.5) — audit trails and
        logging are required to support accountability, incident investigation,
        and continuous monitoring of medium- and high-risk AI systems;
    (d) AI Impact Assessment for high-risk deployments — the PDPC recommends
        that organisations conduct a pre-deployment AIIA to identify and
        mitigate risks before releasing high-risk AI systems.

    References
    ----------
    PDPC — Model AI Governance Framework Version 2.0 (2020)
    PDPC — Implementation and Self-Assessment Guide for Organisations (ISAGO)
    PDPC — A Proposed Model AI Governance Framework — Second Edition (2020)
    """

    FILTER_NAME = "PDPC_MODEL_AI_GOVERNANCE"

    def evaluate(
        self, context: SingaporeAIContext, document: SingaporeAIDocument
    ) -> SingaporeAIFilterResult:
        # High-risk automated decision with no human review pathway
        if (
            context.is_automated_decision
            and context.ai_risk_level == SingaporeAIRiskLevel.HIGH
            and not context.human_review_available
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.DENIED,
                reason=(
                    "PDPC Model AI Framework v2 Section 2.3: High-risk automated "
                    "decisions require human oversight"
                ),
                regulation_citation=(
                    "PDPC Model AI Governance Framework v2 (2020), Section 2.3 — "
                    "Determining the Level of Human Involvement in AI-Augmented "
                    "Decision-Making"
                ),
                requires_logging=True,
            )

        # Automated decision without explainability
        if context.is_automated_decision and not context.explainability_available:
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "PDPC Section 2.4: Explainability required for automated "
                    "decisions affecting individuals"
                ),
                regulation_citation=(
                    "PDPC Model AI Governance Framework v2 (2020), Section 2.4 — "
                    "Stakeholder Interaction and Communication: Explainability"
                ),
                requires_logging=True,
            )

        # No audit trail for medium or high-risk AI
        if (
            not context.audit_trail_enabled
            and context.ai_risk_level != SingaporeAIRiskLevel.LOW
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "PDPC Section 2.5: Audit trails required for medium/high-risk AI"
                ),
                regulation_citation=(
                    "PDPC Model AI Governance Framework v2 (2020), Section 2.5 — "
                    "Operations Management: Logging and Monitoring"
                ),
                requires_logging=True,
            )

        # High-risk deployment without AI Impact Assessment
        if (
            not context.has_ai_impact_assessment
            and context.ai_risk_level == SingaporeAIRiskLevel.HIGH
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "PDPC AI Impact Assessment recommended for high-risk deployment"
                ),
                regulation_citation=(
                    "PDPC Model AI Governance Framework v2 (2020) — AI Impact "
                    "Assessment (AIIA) guidance for high-risk AI systems"
                ),
                requires_logging=True,
            )

        return SingaporeAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=SingaporeAIDecision.APPROVED,
            reason="Compliant with PDPC Model AI Governance Framework v2",
            regulation_citation=(
                "PDPC Model AI Governance Framework v2 (2020) — all applicable "
                "controls satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 2 — PDPA Data Protection
# ---------------------------------------------------------------------------


class PDPADataProtectionFilter:
    """
    Layer 2: Personal Data Protection Act 2012 (PDPA) — Singapore.

    The PDPA governs the collection, use, and disclosure of personal data by
    organisations in Singapore. Four obligations are most material for AI
    systems:

    (a) Consent Obligation (Section 13) — personal data must not be collected,
        used, or disclosed without the individual's consent or a prescribed
        PDPA exception; a Data Protection Notice (DPN) must be given before or
        at the time of collection;
    (b) Data Protection Officer (DPO) — while not strictly mandatory for all
        organisations, appointing a DPO is expected and recommended for medium
        and large organisations and for organisations processing sensitive
        personal data; non-GENERAL sector organisations without a DPO are
        flagged for human review;
    (c) Transfer Limitation Obligation (Section 26) — cross-border transfers
        of personal data require adequate protection, either through transfer
        to a PDPC Third Schedule white-listed jurisdiction or through binding
        contractual clauses that provide a comparable standard of protection;
    (d) Document-level personal data mismatch — if a document contains
        personal data but the processing context does not declare personal
        data involvement, the document must be redacted before processing
        to prevent inadvertent disclosure.

    References
    ----------
    Personal Data Protection Act 2012 (Act 26 of 2012), Singapore
    Personal Data Protection (Amendment) Act 2020
    PDPC — Advisory Guidelines on Key Concepts in the PDPA (2021)
    PDPC — Transfer to Third Countries (Third Schedule guidance)
    PDPC — Guide on Building Websites for SMEs — DPO obligations
    """

    FILTER_NAME = "PDPA_DATA_PROTECTION"

    def evaluate(
        self, context: SingaporeAIContext, document: SingaporeAIDocument
    ) -> SingaporeAIFilterResult:
        # Personal data without consent
        if context.involves_personal_data and not context.has_pdpa_consent:
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.DENIED,
                reason=(
                    "PDPA Section 13: Collection/use of personal data requires consent"
                ),
                regulation_citation=(
                    "Personal Data Protection Act 2012, Section 13 — Consent "
                    "Obligation; PDPC Advisory Guidelines on Key Concepts (2021)"
                ),
                requires_logging=True,
            )

        # Sector organisation without DPO (non-GENERAL sector)
        if (
            context.involves_personal_data
            and not context.has_data_protection_officer
            and context.sector != SingaporeSector.GENERAL
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "PDPA: Data Protection Officer recommended for medium/large "
                    "organisations"
                ),
                regulation_citation=(
                    "Personal Data Protection Act 2012 — DPO appointment guidance; "
                    "PDPC Advisory Guidelines — DPO responsibilities"
                ),
                requires_logging=True,
            )

        # Cross-border transfer without adequate protection
        if context.is_cross_border_transfer and not context.transfer_adequate_protection:
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.DENIED,
                reason=(
                    "PDPA Section 26: Cross-border transfer requires adequate "
                    "protection (Third Schedule or contractual)"
                ),
                regulation_citation=(
                    "Personal Data Protection Act 2012, Section 26 — Transfer "
                    "Limitation Obligation; PDPC Third Schedule"
                ),
                requires_logging=True,
            )

        # Document contains personal data but context does not declare it
        if document.contains_personal_data and not context.involves_personal_data:
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REDACTED,
                reason=(
                    "PDPA: Document contains personal data but context does not "
                    "declare it — redact"
                ),
                regulation_citation=(
                    "Personal Data Protection Act 2012 — Protection Obligation "
                    "(Section 24); PDPC Advisory Guidelines on Key Concepts"
                ),
                requires_logging=True,
            )

        return SingaporeAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=SingaporeAIDecision.APPROVED,
            reason="Compliant with PDPA 2012",
            regulation_citation=(
                "Personal Data Protection Act 2012 — all applicable obligations "
                "satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 3 — MAS FEAT Principles
# ---------------------------------------------------------------------------


class MASFEATFilter:
    """
    Layer 3: MAS FEAT Principles — Monetary Authority of Singapore (2018).

    The MAS FEAT Principles provide governance guidance for financial
    institutions using AI and data analytics in customer-facing and
    consequential decision-making. The four principles — Fairness, Ethics,
    Accountability, and Transparency — impose specific operational requirements
    on MAS-regulated institutions. Non-financial-institution organisations are
    outside the scope of FEAT and receive an immediate approval with a note.

    This filter evaluates three principal FEAT obligations:

    (a) Fairness (F.1) — AI models used in consequential financial decisions
        must be tested for bias and discriminatory outcomes; results must be
        documented and remediation applied where bias is identified;
    (b) Transparency (T.1) — For medium- and high-risk financial AI decisions,
        the institution must be able to explain individual decisions on request
        to customers and to MAS; black-box model outputs must be supplemented
        with compensating explainability mechanisms;
    (c) Accountability (A.2) — High-risk financial AI models should be reviewed
        within the MAS model risk management framework; institutions must
        demonstrate that governance structures exist for model validation and
        supervisory approval.

    References
    ----------
    MAS — Principles to Promote Fairness, Ethics, Accountability and
          Transparency (FEAT) in the Use of Artificial Intelligence and Data
          Analytics in Singapore's Financial Sector (2018)
    MAS — FEAT Assessment Methodology (2022)
    MAS — Veritas Initiative — FEAT assessment toolkit
    MAS Technology Risk Management Guidelines (2021)
    """

    FILTER_NAME = "MAS_FEAT"

    def evaluate(
        self, context: SingaporeAIContext, document: SingaporeAIDocument
    ) -> SingaporeAIFilterResult:
        # Not a financial institution — FEAT does not apply
        if not context.is_financial_institution:
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.APPROVED,
                reason="MAS FEAT not applicable — not a financial institution",
                regulation_citation=(
                    "MAS FEAT Principles (2018) — scope limited to MAS-regulated "
                    "financial institutions"
                ),
            )

        # FEAT Principle F.1 — bias testing required
        if not context.bias_testing_done:
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.DENIED,
                reason=(
                    "MAS FEAT Fairness: Bias testing required for financial AI "
                    "models (MAS FEAT Principle F.1)"
                ),
                regulation_citation=(
                    "MAS FEAT Principles (2018), Principle F.1 — Fairness: "
                    "AI models must be tested for biased or discriminatory outcomes"
                ),
                requires_logging=True,
            )

        # FEAT Principle T.1 — explainability for medium/high-risk financial AI
        if (
            not context.explainability_available
            and context.ai_risk_level in {SingaporeAIRiskLevel.HIGH, SingaporeAIRiskLevel.MEDIUM}
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.DENIED,
                reason=(
                    "MAS FEAT Transparency: Explainability required for material "
                    "financial AI decisions (T.1)"
                ),
                regulation_citation=(
                    "MAS FEAT Principles (2018), Principle T.1 — Transparency: "
                    "Financial institutions must explain AI-driven decisions on "
                    "request to customers and MAS"
                ),
                requires_logging=True,
            )

        # FEAT Principle A.2 — MAS supervisory approval for high-risk financial AI
        if (
            not context.has_mas_approval
            and context.ai_risk_level == SingaporeAIRiskLevel.HIGH
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "MAS FEAT Accountability: High-risk financial AI requires MAS "
                    "supervisory approval (A.2)"
                ),
                regulation_citation=(
                    "MAS FEAT Principles (2018), Principle A.2 — Accountability: "
                    "Model risk management framework and supervisory review required "
                    "for high-risk financial AI"
                ),
                requires_logging=True,
            )

        return SingaporeAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=SingaporeAIDecision.APPROVED,
            reason="Compliant with MAS FEAT Principles",
            regulation_citation=(
                "MAS FEAT Principles (2018) — Fairness, Ethics, Accountability, "
                "and Transparency obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 4 — IMDA AI Testing Framework
# ---------------------------------------------------------------------------


class IMDATestingFilter:
    """
    Layer 4: IMDA AI Testing Framework — Infocomm Media Development Authority
    (AI Verify, 2022, updated 2023).

    The IMDA developed AI Verify in partnership with the PDPC as Singapore's
    national AI testing framework. AI Verify provides standardised test kits
    aligned with eleven internationally-recognised responsible AI principles,
    covering fairness, explainability, robustness, and transparency. Two
    principal procedural requirements are enforced:

    (a) Model Registration and Testing — high-risk AI models are expected to
        be registered and assessed using AI Verify before deployment;
        unregistered high-risk models are flagged for mandatory human review;
    (b) Bias and Fairness Testing — non-low-risk AI systems must complete bias
        and fairness testing using AI Verify's standardised test kits;
        untested medium- and high-risk systems are flagged for human review;
    (c) Human Decision Pathway — where a document or use case explicitly
        flags that a human decision is required (requires_human_decision=True)
        but the system is fully automated with no human review available, the
        request must be denied.

    References
    ----------
    IMDA — AI Verify Foundation: AI Verify Testing Framework (2022)
    IMDA — AI Verify v2.0 — Updated Test Methodology (2023)
    PDPC + IMDA — Companion to the Model AI Governance Framework: AI Verify
    IMDA — AI Governance Framework for Generative AI (2023)
    OECD AI Principles (aligned with AI Verify scope)
    """

    FILTER_NAME = "IMDA_AI_TESTING"

    def evaluate(
        self, context: SingaporeAIContext, document: SingaporeAIDocument
    ) -> SingaporeAIFilterResult:
        # High-risk AI without model registration
        if (
            context.ai_risk_level == SingaporeAIRiskLevel.HIGH
            and not context.model_registered
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "IMDA AI Testing Framework: High-risk AI models should be "
                    "registered and tested"
                ),
                regulation_citation=(
                    "IMDA AI Verify Testing Framework (2022) — high-risk AI model "
                    "registration and AI Verify assessment required before deployment"
                ),
                requires_logging=True,
            )

        # Document requires human decision but system is fully automated
        if (
            document.requires_human_decision
            and context.is_automated_decision
            and not context.human_review_available
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.DENIED,
                reason=(
                    "IMDA Framework: Document requires human decision but no human "
                    "review path available"
                ),
                regulation_citation=(
                    "IMDA AI Verify Testing Framework (2022) — human oversight "
                    "pathway mandatory where use case requires human decision"
                ),
                requires_logging=True,
            )

        # Non-low-risk AI without bias testing
        if (
            not context.bias_testing_done
            and context.ai_risk_level != SingaporeAIRiskLevel.LOW
        ):
            return SingaporeAIFilterResult(
                filter_name=self.FILTER_NAME,
                decision=SingaporeAIDecision.REQUIRES_HUMAN_REVIEW,
                reason="IMDA AI Testing: Bias and fairness testing required for non-low-risk AI",
                regulation_citation=(
                    "IMDA AI Verify Testing Framework (2022) — bias and fairness "
                    "test kits required for medium- and high-risk AI systems"
                ),
                requires_logging=True,
            )

        return SingaporeAIFilterResult(
            filter_name=self.FILTER_NAME,
            decision=SingaporeAIDecision.APPROVED,
            reason="Compliant with IMDA AI Testing Framework",
            regulation_citation=(
                "IMDA AI Verify Testing Framework (2022) — all applicable testing "
                "and registration requirements satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Four-filter orchestrator
# ---------------------------------------------------------------------------


class SingaporeAIGovernanceOrchestrator:
    """
    Four-layer Singapore AI governance orchestrator.

    Evaluation order:
        PDPCModelAIGovernanceFilter  →  PDPADataProtectionFilter  →
        MASFEATFilter                →  IMDATestingFilter

    All four filters are always evaluated regardless of earlier results,
    producing a complete picture of all compliance gaps simultaneously.
    Results are collected as a list of ``SingaporeAIFilterResult`` objects
    and passed to ``SingaporeAIGovernanceReport`` for aggregation.
    """

    def __init__(self) -> None:
        self._filters = [
            PDPCModelAIGovernanceFilter(),
            PDPADataProtectionFilter(),
            MASFEATFilter(),
            IMDATestingFilter(),
        ]

    def evaluate(
        self, context: SingaporeAIContext, document: SingaporeAIDocument
    ) -> List[SingaporeAIFilterResult]:
        """
        Run all four governance filters and return the collected results.

        Parameters
        ----------
        context : SingaporeAIContext
            The AI system processing context to evaluate.
        document : SingaporeAIDocument
            The document being processed by the AI system.

        Returns
        -------
        list[SingaporeAIFilterResult]
            One result per filter, in evaluation order.
        """
        return [f.evaluate(context, document) for f in self._filters]


# ---------------------------------------------------------------------------
# Aggregated governance report
# ---------------------------------------------------------------------------


@dataclass
class SingaporeAIGovernanceReport:
    """
    Aggregated Singapore AI governance report across all four filters.

    Decision aggregation:
    - Any DENIED result   → overall_decision is DENIED
    - No DENIED + any REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_REVIEW
    - All APPROVED        → APPROVED

    Attributes
    ----------
    context : SingaporeAIContext
        The AI system context that was evaluated.
    document : SingaporeAIDocument
        The document that was evaluated.
    filter_results : list[SingaporeAIFilterResult]
        Per-filter results in evaluation order.
    """

    context: SingaporeAIContext
    document: SingaporeAIDocument
    filter_results: List[SingaporeAIFilterResult]

    @property
    def overall_decision(self) -> SingaporeAIDecision:
        """
        Aggregate decision across all filters.

        Returns DENIED if any filter denied; REQUIRES_HUMAN_REVIEW if any
        filter requires human review (but none denied); APPROVED otherwise.
        """
        if any(r.is_denied for r in self.filter_results):
            return SingaporeAIDecision.DENIED
        if any(
            r.decision == SingaporeAIDecision.REQUIRES_HUMAN_REVIEW
            for r in self.filter_results
        ):
            return SingaporeAIDecision.REQUIRES_HUMAN_REVIEW
        return SingaporeAIDecision.APPROVED

    @property
    def is_compliant(self) -> bool:
        """
        True if no filter produced a DENIED decision.

        Note: REQUIRES_HUMAN_REVIEW is not a denial — the request can still
        proceed after human review; REDACTED indicates partial compliance
        pending document remediation.
        """
        return not any(r.is_denied for r in self.filter_results)

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary across all four filters.

        Returns a multi-line string listing each filter name, its decision,
        and either the approval reason or the denial/review reason.
        """
        lines: List[str] = [
            f"Singapore AI Governance Report — user_id={self.context.user_id}",
            f"Sector: {self.context.sector.value}  |  "
            f"Risk Level: {self.context.ai_risk_level.value}  |  "
            f"Overall Decision: {self.overall_decision.value}",
            "",
        ]
        for result in self.filter_results:
            lines.append(f"  [{result.decision.value}]  {result.filter_name}")
            if result.reason:
                lines.append(f"    Reason: {result.reason}")
            if result.regulation_citation:
                lines.append(f"    Citation: {result.regulation_citation}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scenario demonstrations
# ---------------------------------------------------------------------------


def _compliant_low_risk_general_base() -> tuple[SingaporeAIContext, SingaporeAIDocument]:
    """
    Base context: fully compliant LOW risk GENERAL sector system.
    Used as the baseline from which failing scenarios are derived.
    """
    context = SingaporeAIContext(
        user_id="SG-AI-001",
        sector=SingaporeSector.GENERAL,
        ai_risk_level=SingaporeAIRiskLevel.LOW,
        # PDPC Model AI Governance
        is_automated_decision=False,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=True,
        # PDPA
        involves_personal_data=False,
        has_pdpa_consent=True,
        has_data_protection_officer=False,
        is_cross_border_transfer=False,
        transfer_adequate_protection=False,
        # MAS FEAT
        is_financial_institution=False,
        has_mas_approval=False,
        bias_testing_done=True,
        # IMDA
        model_registered=True,
        # Smart Nation
        is_government_system=False,
    )
    document = SingaporeAIDocument(
        document_id="DOC-001",
        contains_personal_data=False,
        data_classification="INTERNAL",
        is_financial_data=False,
        is_health_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    return context, document


def _high_risk_financial_compliant_base() -> tuple[SingaporeAIContext, SingaporeAIDocument]:
    """
    Base context: fully compliant HIGH risk FINANCIAL_SERVICES system.
    All FEAT requirements satisfied.
    """
    context = SingaporeAIContext(
        user_id="SG-AI-002",
        sector=SingaporeSector.FINANCIAL_SERVICES,
        ai_risk_level=SingaporeAIRiskLevel.HIGH,
        # PDPC Model AI Governance
        is_automated_decision=True,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=True,
        # PDPA
        involves_personal_data=True,
        has_pdpa_consent=True,
        has_data_protection_officer=True,
        is_cross_border_transfer=False,
        transfer_adequate_protection=False,
        # MAS FEAT
        is_financial_institution=True,
        has_mas_approval=True,
        bias_testing_done=True,
        # IMDA
        model_registered=True,
        # Smart Nation
        is_government_system=False,
    )
    document = SingaporeAIDocument(
        document_id="DOC-002",
        contains_personal_data=True,
        data_classification="CONFIDENTIAL",
        is_financial_data=True,
        is_health_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    return context, document


def _run_scenario(
    label: str,
    context: SingaporeAIContext,
    document: SingaporeAIDocument,
) -> SingaporeAIGovernanceReport:
    orchestrator = SingaporeAIGovernanceOrchestrator()
    results = orchestrator.evaluate(context, document)
    report = SingaporeAIGovernanceReport(
        context=context, document=document, filter_results=results
    )
    print(f"\n{'=' * 70}")
    print(f"SCENARIO: {label}")
    print("=" * 70)
    print(report.compliance_summary)
    return report


def main() -> None:  # noqa: C901
    print("Singapore AI Governance Framework — Scenario Demonstrations")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # Scenario 1: Compliant LOW risk GENERAL sector — should APPROVE all layers
    # -----------------------------------------------------------------------
    ctx1, doc1 = _compliant_low_risk_general_base()
    report1 = _run_scenario("Compliant low-risk general sector AI", ctx1, doc1)
    assert report1.overall_decision == SingaporeAIDecision.APPROVED, (
        f"Scenario 1 expected APPROVED, got {report1.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 2: HIGH risk automated, no human review → DENIED (PDPC Layer 1)
    # -----------------------------------------------------------------------
    ctx2 = SingaporeAIContext(
        user_id="SG-AI-003",
        sector=SingaporeSector.HEALTHCARE,
        ai_risk_level=SingaporeAIRiskLevel.HIGH,
        is_automated_decision=True,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=False,      # <-- triggers DENIED
        involves_personal_data=True,
        has_pdpa_consent=True,
        has_data_protection_officer=True,
        is_cross_border_transfer=False,
        transfer_adequate_protection=False,
        is_financial_institution=False,
        has_mas_approval=False,
        bias_testing_done=True,
        model_registered=True,
        is_government_system=False,
    )
    doc2 = SingaporeAIDocument(
        document_id="DOC-003",
        contains_personal_data=True,
        data_classification="RESTRICTED",
        is_financial_data=False,
        is_health_data=True,
        is_government_data=False,
        requires_human_decision=False,
    )
    report2 = _run_scenario(
        "High-risk automated decision, no human review pathway → DENIED", ctx2, doc2
    )
    assert report2.overall_decision == SingaporeAIDecision.DENIED, (
        f"Scenario 2 expected DENIED, got {report2.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 3: Personal data without PDPA consent → DENIED (PDPA Layer 2)
    # -----------------------------------------------------------------------
    ctx3 = SingaporeAIContext(
        user_id="SG-AI-004",
        sector=SingaporeSector.HEALTHCARE,
        ai_risk_level=SingaporeAIRiskLevel.MEDIUM,
        is_automated_decision=False,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=True,
        involves_personal_data=True,
        has_pdpa_consent=False,            # <-- triggers DENIED
        has_data_protection_officer=True,
        is_cross_border_transfer=False,
        transfer_adequate_protection=False,
        is_financial_institution=False,
        has_mas_approval=False,
        bias_testing_done=True,
        model_registered=True,
        is_government_system=False,
    )
    doc3 = SingaporeAIDocument(
        document_id="DOC-004",
        contains_personal_data=True,
        data_classification="CONFIDENTIAL",
        is_financial_data=False,
        is_health_data=True,
        is_government_data=False,
        requires_human_decision=False,
    )
    report3 = _run_scenario(
        "Personal data without PDPA consent → DENIED", ctx3, doc3
    )
    assert report3.overall_decision == SingaporeAIDecision.DENIED, (
        f"Scenario 3 expected DENIED, got {report3.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 4: Financial institution without bias testing → DENIED (MAS FEAT)
    # -----------------------------------------------------------------------
    ctx4, doc4 = _high_risk_financial_compliant_base()
    # Override bias_testing_done to False
    ctx4 = SingaporeAIContext(
        user_id=ctx4.user_id,
        sector=ctx4.sector,
        ai_risk_level=ctx4.ai_risk_level,
        is_automated_decision=ctx4.is_automated_decision,
        has_ai_impact_assessment=ctx4.has_ai_impact_assessment,
        explainability_available=ctx4.explainability_available,
        audit_trail_enabled=ctx4.audit_trail_enabled,
        human_review_available=ctx4.human_review_available,
        involves_personal_data=ctx4.involves_personal_data,
        has_pdpa_consent=ctx4.has_pdpa_consent,
        has_data_protection_officer=ctx4.has_data_protection_officer,
        is_cross_border_transfer=ctx4.is_cross_border_transfer,
        transfer_adequate_protection=ctx4.transfer_adequate_protection,
        is_financial_institution=ctx4.is_financial_institution,
        has_mas_approval=ctx4.has_mas_approval,
        bias_testing_done=False,           # <-- triggers MAS FEAT DENIED
        model_registered=ctx4.model_registered,
        is_government_system=ctx4.is_government_system,
    )
    report4 = _run_scenario(
        "MAS-regulated institution without bias testing → DENIED", ctx4, doc4
    )
    assert report4.overall_decision == SingaporeAIDecision.DENIED, (
        f"Scenario 4 expected DENIED, got {report4.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 5: Cross-border transfer without adequate protection → DENIED
    # -----------------------------------------------------------------------
    ctx5 = SingaporeAIContext(
        user_id="SG-AI-006",
        sector=SingaporeSector.GENERAL,
        ai_risk_level=SingaporeAIRiskLevel.LOW,
        is_automated_decision=False,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=True,
        involves_personal_data=True,
        has_pdpa_consent=True,
        has_data_protection_officer=False,
        is_cross_border_transfer=True,
        transfer_adequate_protection=False,  # <-- triggers DENIED
        is_financial_institution=False,
        has_mas_approval=False,
        bias_testing_done=True,
        model_registered=True,
        is_government_system=False,
    )
    doc5 = SingaporeAIDocument(
        document_id="DOC-006",
        contains_personal_data=True,
        data_classification="INTERNAL",
        is_financial_data=False,
        is_health_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    report5 = _run_scenario(
        "Cross-border transfer without adequate protection → DENIED", ctx5, doc5
    )
    assert report5.overall_decision == SingaporeAIDecision.DENIED, (
        f"Scenario 5 expected DENIED, got {report5.overall_decision}"
    )

    # -----------------------------------------------------------------------
    # Scenario 6: Document personal data mismatch → REDACTED (not DENIED)
    # -----------------------------------------------------------------------
    ctx6 = SingaporeAIContext(
        user_id="SG-AI-007",
        sector=SingaporeSector.GENERAL,
        ai_risk_level=SingaporeAIRiskLevel.LOW,
        is_automated_decision=False,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=True,
        involves_personal_data=False,      # context says no personal data
        has_pdpa_consent=True,
        has_data_protection_officer=False,
        is_cross_border_transfer=False,
        transfer_adequate_protection=False,
        is_financial_institution=False,
        has_mas_approval=False,
        bias_testing_done=True,
        model_registered=True,
        is_government_system=False,
    )
    doc6 = SingaporeAIDocument(
        document_id="DOC-007",
        contains_personal_data=True,       # but document has personal data → REDACTED
        data_classification="INTERNAL",
        is_financial_data=False,
        is_health_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    report6 = _run_scenario(
        "Document personal data mismatch → REDACTED filter result", ctx6, doc6
    )
    redact_results = [
        r for r in report6.filter_results
        if r.decision == SingaporeAIDecision.REDACTED
    ]
    assert len(redact_results) == 1, (
        f"Scenario 6 expected exactly one REDACTED filter result, "
        f"got {len(redact_results)}"
    )

    # -----------------------------------------------------------------------
    # Scenario 7: Compliant HIGH risk financial services — APPROVED
    # -----------------------------------------------------------------------
    ctx7, doc7 = _high_risk_financial_compliant_base()
    report7 = _run_scenario(
        "Fully compliant high-risk financial services AI → APPROVED", ctx7, doc7
    )
    assert report7.overall_decision == SingaporeAIDecision.APPROVED, (
        f"Scenario 7 expected APPROVED, got {report7.overall_decision}"
    )

    print(f"\n{'=' * 70}")
    print("All 7 scenario assertions passed.")


if __name__ == "__main__":
    main()
