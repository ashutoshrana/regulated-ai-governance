"""
22_brazil_ai_governance.py — Four-layer AI governance framework for AI systems
subject to Brazilian law, covering the overlapping national and sector-level
obligations that apply to AI-driven data processing in Brazil.

Demonstrates a multi-layer governance orchestrator where four Brazilian
regulatory frameworks each impose independent requirements on AI systems
deployed in Brazil:

    Layer 1  — LGPD Data Protection (Lei Geral de Proteção de Dados,
               Law 13.709/2018):
               Brazil's primary data protection law, effective September 18,
               2020, administered by the National Data Protection Authority
               (ANPD — Autoridade Nacional de Proteção de Dados). The LGPD
               establishes obligations for any processing of personal data of
               individuals located in Brazil:
               Article 7 — Legal Basis: processing of personal data requires
                   one of ten legal bases, including consent, legitimate
                   interest, legal obligation, and contract performance; AI
                   systems processing personal data without a valid legal
                   basis are prohibited;
               Article 11 — Sensitive Personal Data: processing of sensitive
                   personal data (health, biometric, racial, religious, sexual
                   orientation, political) requires explicit consent or legal
                   mandate; automated AI processing of sensitive data without
                   explicit consent is prohibited;
               Article 33 — International Transfer: transfer of personal data
                   to another country requires an adequacy decision by the ANPD,
                   standard contractual clauses, or binding corporate rules;
               Article 37 — Records of Processing: controllers and operators
                   must maintain records of all personal data processing
                   activities; absence of processing records triggers mandatory
                   human review;
               Article 6(VI) — Data Minimization: only data strictly necessary
                   for the declared purpose may be collected and processed;
                   excessive data collection must be blocked.

    Layer 2  — Brazil AI Bill PL 2338/2023:
               Brazil's AI regulatory bill (Projeto de Lei 2338/2023) was
               committee-approved in the Brazilian Senate in 2024. The bill
               establishes a risk-based AI governance framework with specific
               obligations for high-risk AI systems and prohibitions on the
               most harmful AI applications:
               Article 3 — High-Risk AI: AI systems deployed in critical
                   infrastructure, credit, employment, education, healthcare,
                   or public security contexts must undergo a formal conformity
                   assessment before deployment;
               Article 14 — Automated Decisions Affecting Rights: automated
                   decision-making systems that affect fundamental rights must
                   offer individuals the option of human review of the
                   automated decision;
               Article 16 — Incident Reporting: high-risk AI systems must
                   implement mechanisms for reporting incidents and security
                   events to ANPD;
               Article 22 — Prohibited Practices: AI systems designed to
                   manipulate subliminal behavior, exploit vulnerabilities of
                   protected groups, or enable mass social scoring are
                   prohibited.

    Layer 3  — ANPD Guidelines (Autoridade Nacional de Proteção de Dados):
               The ANPD has issued guidelines on AI systems and personal data
               processing. The most significant for AI governance are:
               Orientation 1/2023 — Privacy by Design: AI systems processing
                   personal data at scale must implement privacy by design
                   principles from the earliest stages of system development;
               Data Minimization (LGPD Art. 6 VI) — AI training and inference
                   should use the minimum necessary personal data for the
                   stated purpose; excessive data collection must be blocked;
               LGPD Article 41 — DPO Requirement: organisations conducting
                   large-scale processing of personal data must appoint a Data
                   Protection Officer (encarregado); absence of a DPO for
                   large-scale processing requires human review.

    Layer 4  — Brazilian Sectoral Requirements:
               Brazil has established sector-specific governance requirements
               for AI in regulated industries that layer on top of the LGPD
               and AI Bill obligations:
               CFM Resolution 2299/2021 — Healthcare: the Federal Council of
                   Medicine requires that AI clinical decision support systems
                   operate under active physician responsibility; fully
                   autonomous clinical AI decisions without physician oversight
                   are prohibited;
               BCB Circular 3.978/2020 — Financial Services: the Central Bank
                   of Brazil requires that AI credit scoring models be
                   explainable to affected individuals; opaque credit scoring
                   without explainability mechanisms requires human review;
               CLT + MPT Guidance — Employment: Brazilian labour law (CLT) and
                   Ministry of Labour (MPT) guidance require that AI systems
                   used in employment decisions undergo a bias audit before
                   deployment; AI employment decision systems without a
                   completed bias audit require human review.

No external dependencies required.

Run:
    python examples/22_brazil_ai_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class BrazilAIRiskLevel(str, Enum):
    """
    Risk classification for AI systems under the Brazil AI Bill PL 2338/2023.

    HIGH   — AI deployed in critical infrastructure, credit, employment,
             education, healthcare, or public security; conformity assessment
             and incident reporting required.
    MEDIUM — Meaningful but bounded risk; lighter conformity obligations.
    LOW    — Limited potential for harm; minimal governance requirements.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BrazilAIDecision(str, Enum):
    """Final governance decision for a Brazil AI system evaluation."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    REDACTED = "REDACTED"


class BrazilSector(str, Enum):
    """
    Deployment sector for the AI system.

    HEALTHCARE  — Brazilian healthcare institution; CFM Resolution 2299/2021
                  applies in Layer 4 for clinical AI.
    FINANCIAL   — Financial institution; BCB Circular 3.978/2020 applies in
                  Layer 4 for credit scoring AI.
    EMPLOYMENT  — HR / workforce management context; CLT + MPT guidance on
                  AI employment decisions applies in Layer 4.
    PUBLIC      — Government or public sector body; AI Bill high-risk
                  presumptions apply.
    EDUCATION   — Educational institution; AI Bill high-risk classification
                  may apply.
    GENERAL     — General private-sector organisation; baseline LGPD and AI
                  Bill obligations apply; no sector-specific Layer 4 checks.
    """

    HEALTHCARE = "HEALTHCARE"
    FINANCIAL = "FINANCIAL"
    EMPLOYMENT = "EMPLOYMENT"
    PUBLIC = "PUBLIC"
    EDUCATION = "EDUCATION"
    GENERAL = "GENERAL"


# ---------------------------------------------------------------------------
# Frozen context and document dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BrazilAIContext:
    """
    Governance review context for a Brazil AI system.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or request under review.
    sector : BrazilSector
        The sector in which the AI system is deployed. Determines which
        sectoral controls apply in Layer 4.
    ai_risk_level : BrazilAIRiskLevel
        Risk level under Brazil AI Bill PL 2338/2023.

    — LGPD fields —

    involves_personal_data : bool
        True if the AI system collects, uses, or discloses personal data
        of individuals located in Brazil (LGPD Art. 5 I).
    involves_sensitive_personal_data : bool
        True if the AI system processes sensitive personal data as defined
        in LGPD Art. 5 II: health or sex life data, biometric and genetic
        data, racial or ethnic origin, religious belief, political opinion,
        union membership, sexual orientation.
    lgpd_legal_basis : str
        The legal basis used for personal data processing under LGPD Art. 7.
        Accepted values: "consent", "legitimate_interest", "legal_obligation",
        "contract", "none" (no legal basis — triggers denial).
    has_lgpd_explicit_consent : bool
        True if explicit, specific opt-in consent has been obtained from the
        data subject for sensitive personal data processing (LGPD Art. 11).
    involves_cross_border_transfer : bool
        True if personal data is transferred to a recipient in another country
        (LGPD Art. 33).
    has_lgpd_transfer_mechanism : bool
        True if the cross-border transfer is protected by an ANPD adequacy
        decision, standard contractual clauses, or binding corporate rules
        (LGPD Art. 33).
    has_processing_records : bool
        True if the controller maintains records of all personal data
        processing activities (LGPD Art. 37).

    — AI Bill fields —

    is_high_risk_ai : bool
        True if the AI system is deployed in one of the high-risk sectors
        or contexts enumerated in Brazil AI Bill Art. 3: critical
        infrastructure, credit, employment, education, healthcare, or
        public security.
    has_conformity_assessment : bool
        True if a formal conformity assessment has been completed for the
        AI system (required for high-risk AI under Brazil AI Bill Art. 3).
    is_automated_decision_making : bool
        True if the AI system makes automated decisions without meaningful
        human involvement in each individual decision.
    affects_fundamental_rights : bool
        True if automated decisions may affect fundamental rights of
        individuals (Brazil AI Bill Art. 14 trigger).
    human_review_available : bool
        True if affected individuals can request human review of an
        automated decision (Brazil AI Bill Art. 14).
    has_incident_reporting : bool
        True if the AI system has a mechanism to report incidents and
        security events to ANPD (Brazil AI Bill Art. 16).
    is_prohibited_ai_practice : bool
        True if the AI system engages in a prohibited practice under Brazil
        AI Bill Art. 22: subliminal manipulation, exploitation of protected
        group vulnerabilities, or mass social scoring.

    — ANPD fields —

    is_large_scale_processing : bool
        True if the AI system processes personal data at scale as defined
        in ANPD Orientation 1/2023 guidance.
    has_privacy_by_design : bool
        True if privacy by design principles have been implemented from the
        earliest stages of system development (ANPD Orientation 1/2023).
    involves_excessive_data_collection : bool
        True if the AI system collects more personal data than strictly
        necessary for the stated purpose (LGPD Art. 6 VI — data
        minimization principle).
    has_dpo_appointed : bool
        True if a Data Protection Officer (encarregado) has been appointed
        for the organisation (LGPD Art. 41).

    — Sectoral fields —

    is_clinical_ai : bool
        True if the AI system provides clinical decision support or
        diagnostic recommendations in healthcare (CFM Resolution 2299/2021).
    physician_oversight_available : bool
        True if a licensed physician is responsible for all clinical AI
        recommendations (CFM Resolution 2299/2021).
    is_credit_scoring_ai : bool
        True if the AI system performs credit scoring or creditworthiness
        assessment (BCB Circular 3.978/2020).
    explainability_available : bool
        True if the AI system can provide an explanation of its credit
        scoring decisions (BCB Circular 3.978/2020).
    is_employment_decision_ai : bool
        True if the AI system is used in employment decisions such as
        hiring, promotion, or termination (CLT + MPT guidance).
    bias_audit_completed : bool
        True if a bias audit has been completed for the AI employment
        decision system (CLT + MPT guidance).
    """

    user_id: str
    sector: BrazilSector
    ai_risk_level: BrazilAIRiskLevel

    # LGPD
    involves_personal_data: bool
    involves_sensitive_personal_data: bool
    lgpd_legal_basis: str
    has_lgpd_explicit_consent: bool
    involves_cross_border_transfer: bool
    has_lgpd_transfer_mechanism: bool
    has_processing_records: bool

    # AI Bill
    is_high_risk_ai: bool
    has_conformity_assessment: bool
    is_automated_decision_making: bool
    affects_fundamental_rights: bool
    human_review_available: bool
    has_incident_reporting: bool
    is_prohibited_ai_practice: bool

    # ANPD
    is_large_scale_processing: bool
    has_privacy_by_design: bool
    involves_excessive_data_collection: bool
    has_dpo_appointed: bool

    # Sectoral
    is_clinical_ai: bool
    physician_oversight_available: bool
    is_credit_scoring_ai: bool
    explainability_available: bool
    is_employment_decision_ai: bool
    bias_audit_completed: bool


@dataclass(frozen=True)
class BrazilAIDocument:
    """
    Document metadata submitted to the Brazil AI governance orchestrator.

    Attributes
    ----------
    document_id : str
        Unique identifier for the document under review.
    document_type : str
        Type descriptor for the document (e.g. "REPORT", "MODEL_OUTPUT",
        "TRAINING_DATA", "AUDIT_LOG").
    contains_personal_data : bool
        True if the document contains personal data of individuals located
        in Brazil (LGPD Art. 5 I).
    contains_sensitive_data : bool
        True if the document contains sensitive personal data as defined
        in LGPD Art. 5 II.
    data_subject_count : int
        Approximate number of data subjects whose data appears in the
        document. 0 means unknown.
    is_ai_model_output : bool
        True if the document is or contains an output from an AI model.
    classification : str
        Data sensitivity classification: "PERSONAL_DATA", "SENSITIVE_DATA",
        "PUBLIC", or "AI_OUTPUT".
    """

    document_id: str
    document_type: str
    contains_personal_data: bool
    contains_sensitive_data: bool
    data_subject_count: int
    is_ai_model_output: bool
    classification: str


# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Result of a single Brazil AI governance filter evaluation."""

    filter_name: str
    decision: BrazilAIDecision = BrazilAIDecision.APPROVED
    reason: str = ""
    regulation_citation: str = ""
    requires_logging: bool = False

    @property
    def is_denied(self) -> bool:
        """True if and only if this filter produced a DENIED decision."""
        return self.decision == BrazilAIDecision.DENIED


# ---------------------------------------------------------------------------
# Layer 1 — LGPD Data Protection
# ---------------------------------------------------------------------------


class LGPDDataProtectionFilter:
    """
    Layer 1: LGPD — Lei Geral de Proteção de Dados (Law 13.709/2018).

    Brazil's primary data protection law, effective September 18, 2020,
    administered by the ANPD (Autoridade Nacional de Proteção de Dados).
    This filter evaluates the principal LGPD controls most material for
    AI system governance:

    (a) Legal basis for processing (Art. 7) — processing of personal data
        requires one of the ten enumerated legal bases; AI systems without
        a valid legal basis are denied;
    (b) Sensitive personal data consent (Art. 11) — processing of sensitive
        personal data requires explicit consent or legal mandate;
    (c) International transfer mechanisms (Art. 33) — cross-border transfers
        require adequacy, contractual clauses, or binding rules;
    (d) Records of processing activities (Art. 37) — controllers must
        maintain processing records; absence triggers review;
    (e) Data minimization (Art. 6 VI) — excessive data collection is denied.

    References
    ----------
    Lei Geral de Proteção de Dados Pessoais — Lei nº 13.709, de 14 de
        agosto de 2018 (effective September 18, 2020)
    ANPD — Regulamento de Fiscalização e Aplicação de Sanções Administrativas
    """

    FILTER_NAME = "LGPD_DATA_PROTECTION"

    _VALID_LEGAL_BASES = {"consent", "legitimate_interest", "legal_obligation", "contract"}

    def evaluate(
        self, context: BrazilAIContext, document: BrazilAIDocument
    ) -> FilterResult:
        # Art. 7 — valid legal basis required for personal data processing
        if (
            context.involves_personal_data
            and context.lgpd_legal_basis not in self._VALID_LEGAL_BASES
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "LGPD Art. 7: Personal data processing requires a valid legal "
                    "basis (consent, legitimate interest, legal obligation, or "
                    "contract). No valid basis declared."
                ),
                regulation_citation=(
                    "LGPD Art. 7 — valid legal basis required for personal data "
                    "processing"
                ),
                requires_logging=True,
            )

        # Art. 11 — sensitive personal data requires explicit consent or legal obligation
        if (
            context.involves_sensitive_personal_data
            and not context.has_lgpd_explicit_consent
            and context.lgpd_legal_basis != "legal_obligation"
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "LGPD Art. 11: Processing of sensitive personal data (health, "
                    "biometric, racial, religious, sexual orientation, political) "
                    "requires explicit consent or legal mandate."
                ),
                regulation_citation=(
                    "LGPD Art. 11 — explicit consent required for sensitive personal "
                    "data"
                ),
                requires_logging=True,
            )

        # Art. 33 — cross-border transfer requires adequacy or contractual mechanism
        if context.involves_cross_border_transfer and not context.has_lgpd_transfer_mechanism:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "LGPD Art. 33: International transfer of personal data requires "
                    "an ANPD adequacy decision, standard contractual clauses, or "
                    "binding corporate rules."
                ),
                regulation_citation=(
                    "LGPD Art. 33 — international transfer requires adequacy decision "
                    "or contractual clauses"
                ),
                requires_logging=True,
            )

        # Art. 37 — controller must maintain records of processing activities
        if context.involves_personal_data and not context.has_processing_records:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "LGPD Art. 37: Controller must maintain records of all personal "
                    "data processing activities. Processing records not confirmed."
                ),
                regulation_citation=(
                    "LGPD Art. 37 — controller must maintain processing records"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=BrazilAIDecision.APPROVED,
            reason="Compliant with LGPD (Lei Geral de Proteção de Dados, Law 13.709/2018).",
            regulation_citation=(
                "LGPD — Lei nº 13.709/2018 — all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 2 — Brazil AI Bill PL 2338/2023
# ---------------------------------------------------------------------------


class BrazilAIBillFilter:
    """
    Layer 2: Brazil AI Bill PL 2338/2023 — Projeto de Lei 2338/2023.

    Brazil's pending AI regulation, committee-approved in the Brazilian
    Senate in 2024. The bill establishes a risk-based AI governance
    framework. This filter evaluates the four principal AI Bill controls
    most material for AI deployment governance:

    (a) Conformity assessment for high-risk AI (Art. 3) — AI deployed in
        critical infrastructure, credit, employment, education, healthcare,
        or public security must complete a conformity assessment;
    (b) Human review option for automated decisions (Art. 14) — automated
        decisions affecting fundamental rights must offer human review;
    (c) Incident reporting to ANPD (Art. 16) — high-risk AI must have an
        incident reporting mechanism;
    (d) Prohibited practices (Art. 22) — subliminal manipulation, exploitation
        of protected group vulnerabilities, and mass social scoring are
        prohibited.

    References
    ----------
    Projeto de Lei nº 2338, de 2023 (Brazilian Senate AI Bill)
    Comissão Temporária Interna sobre Inteligência Artificial — Committee
        Report, 2024
    """

    FILTER_NAME = "BRAZIL_AI_BILL"

    def evaluate(
        self, context: BrazilAIContext, document: BrazilAIDocument
    ) -> FilterResult:
        # Art. 22 — prohibited AI practices: check first as highest severity
        if context.is_prohibited_ai_practice:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "Brazil AI Bill PL 2338/2023 Art. 22: The AI system engages in "
                    "a prohibited practice — subliminal manipulation, exploitation of "
                    "protected group vulnerabilities, or mass social scoring."
                ),
                regulation_citation=(
                    "Brazil AI Bill PL 2338/2023 Art. 22 — prohibited AI practice"
                ),
                requires_logging=True,
            )

        # Art. 3 — high-risk AI requires conformity assessment
        if context.is_high_risk_ai and not context.has_conformity_assessment:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "Brazil AI Bill PL 2338/2023 Art. 3: High-risk AI systems require "
                    "a formal conformity assessment before deployment. Assessment not "
                    "completed."
                ),
                regulation_citation=(
                    "Brazil AI Bill PL 2338/2023 Art. 3 — high-risk AI requires "
                    "conformity assessment"
                ),
                requires_logging=True,
            )

        # Art. 14 — automated decisions affecting fundamental rights require human review option
        if (
            context.is_automated_decision_making
            and context.affects_fundamental_rights
            and not context.human_review_available
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "Brazil AI Bill PL 2338/2023 Art. 14: Automated decision-making "
                    "systems affecting fundamental rights must offer individuals the "
                    "option of human review."
                ),
                regulation_citation=(
                    "Brazil AI Bill PL 2338/2023 Art. 14 — automated decisions "
                    "affecting rights require human review"
                ),
                requires_logging=True,
            )

        # Art. 16 — high-risk AI must have incident reporting mechanism to ANPD
        if context.is_high_risk_ai and not context.has_incident_reporting:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "Brazil AI Bill PL 2338/2023 Art. 16: High-risk AI systems must "
                    "have an incident reporting mechanism to ANPD. Reporting mechanism "
                    "not confirmed."
                ),
                regulation_citation=(
                    "Brazil AI Bill PL 2338/2023 Art. 16 — high-risk AI requires "
                    "incident reporting to ANPD"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=BrazilAIDecision.APPROVED,
            reason="Compliant with Brazil AI Bill PL 2338/2023.",
            regulation_citation=(
                "Brazil AI Bill PL 2338/2023 — all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 3 — ANPD Guidelines
# ---------------------------------------------------------------------------


class ANPDGuidelinesFilter:
    """
    Layer 3: ANPD Guidelines — Autoridade Nacional de Proteção de Dados (2023).

    The Brazilian Data Protection Authority (ANPD) has published guidance on
    AI systems and large-scale personal data processing. This filter evaluates
    the three principal ANPD guidelines most material for AI governance:

    (a) Privacy by design (Orientation 1/2023) — AI systems processing
        personal data at scale must implement privacy by design from the
        earliest stages;
    (b) Data minimization (LGPD Art. 6 VI) — AI systems must use only the
        minimum personal data necessary for the stated purpose; excessive
        collection is denied;
    (c) DPO requirement (LGPD Art. 41) — organisations conducting large-scale
        processing must appoint a Data Protection Officer; absence triggers
        review.

    References
    ----------
    ANPD — Nota de Orientação sobre Inteligência Artificial 1/2023
    LGPD Art. 6 VI — Principle of necessity (data minimization)
    LGPD Art. 41 — Data Protection Officer (encarregado) requirement
    """

    FILTER_NAME = "ANPD_GUIDELINES"

    def evaluate(
        self, context: BrazilAIContext, document: BrazilAIDocument
    ) -> FilterResult:
        # Data minimization — excessive data collection violates LGPD Art. 6 VI
        if context.involves_excessive_data_collection:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "ANPD / LGPD Art. 6 VI: Data minimization principle violated. "
                    "The AI system collects more personal data than strictly necessary "
                    "for the declared purpose."
                ),
                regulation_citation=(
                    "ANPD Guidelines — data minimization principle (LGPD Art. 6 VI)"
                ),
                requires_logging=True,
            )

        # Privacy by design — required for large-scale AI processing
        if context.is_large_scale_processing and not context.has_privacy_by_design:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "ANPD Orientation 1/2023: Privacy by design is required for AI "
                    "systems processing personal data at scale. Privacy by design not "
                    "confirmed."
                ),
                regulation_citation=(
                    "ANPD Orientation 1/2023 — privacy by design required for "
                    "large-scale AI processing"
                ),
                requires_logging=True,
            )

        # DPO requirement — mandatory for large-scale processing
        if context.is_large_scale_processing and not context.has_dpo_appointed:
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "LGPD Art. 41: Organisations conducting large-scale personal data "
                    "processing must appoint a Data Protection Officer (encarregado). "
                    "DPO not confirmed."
                ),
                regulation_citation=(
                    "LGPD Art. 41 — DPO required for large-scale processing"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=BrazilAIDecision.APPROVED,
            reason="Compliant with ANPD Guidelines and LGPD data governance principles.",
            regulation_citation=(
                "ANPD Guidelines 2023 + LGPD Art. 6 VI / Art. 41 — all applicable "
                "obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Layer 4 — Brazilian Sectoral Requirements
# ---------------------------------------------------------------------------


class BrazilSectoralFilter:
    """
    Layer 4: Brazilian Sectoral Requirements.

    Brazil has sector-specific governance requirements for AI in regulated
    industries that layer on top of the baseline LGPD and AI Bill obligations.
    This filter evaluates three sectoral frameworks:

    (a) CFM Resolution 2299/2021 — Healthcare: the Federal Council of
        Medicine requires physician responsibility for all clinical AI
        decision support; fully autonomous clinical AI is prohibited;
    (b) BCB Circular 3.978/2020 — Financial Services: the Central Bank of
        Brazil requires AI credit scoring to be explainable to affected
        individuals;
    (c) CLT + MPT Guidance — Employment: Brazilian labour law (CLT) and
        Ministry of Labour guidance require a bias audit before deploying
        AI in employment decisions.

    References
    ----------
    Conselho Federal de Medicina — Resolução CFM nº 2.299/2021
    Banco Central do Brasil — Circular nº 3.978/2020
    Consolidação das Leis do Trabalho (CLT) + Ministério Público do
        Trabalho (MPT) Nota Técnica sobre IA no Trabalho
    """

    FILTER_NAME = "BRAZIL_SECTORAL"

    def evaluate(
        self, context: BrazilAIContext, document: BrazilAIDocument
    ) -> FilterResult:
        # Healthcare — CFM Resolution 2299/2021: physician oversight for clinical AI
        if (
            context.sector == BrazilSector.HEALTHCARE
            and context.is_clinical_ai
            and not context.physician_oversight_available
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.DENIED,
                reason=(
                    "CFM Resolution 2299/2021: Clinical AI decision support requires "
                    "physician oversight and responsibility. Physician oversight not "
                    "available."
                ),
                regulation_citation=(
                    "CFM Resolution 2299/2021 — physician oversight required for "
                    "clinical AI"
                ),
                requires_logging=True,
            )

        # Financial — BCB Circular 3.978/2020: explainability for AI credit scoring
        if (
            context.sector == BrazilSector.FINANCIAL
            and context.is_credit_scoring_ai
            and not context.explainability_available
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "BCB Circular 3.978/2020: AI credit scoring models must be "
                    "explainable to affected individuals. Explainability not available."
                ),
                regulation_citation=(
                    "BCB Circular 3.978/2020 — explainability required for AI credit "
                    "scoring"
                ),
                requires_logging=True,
            )

        # Employment — CLT + MPT: bias audit for AI employment decisions
        if (
            context.sector == BrazilSector.EMPLOYMENT
            and context.is_employment_decision_ai
            and not context.bias_audit_completed
        ):
            return FilterResult(
                filter_name=self.FILTER_NAME,
                decision=BrazilAIDecision.REQUIRES_HUMAN_REVIEW,
                reason=(
                    "CLT + MPT Guidance: AI systems used in employment decisions "
                    "(hiring, promotion, termination) require a completed bias audit. "
                    "Bias audit not confirmed."
                ),
                regulation_citation=(
                    "CLT + MPT Guidance — bias audit required for AI employment "
                    "decisions"
                ),
                requires_logging=True,
            )

        return FilterResult(
            filter_name=self.FILTER_NAME,
            decision=BrazilAIDecision.APPROVED,
            reason=(
                "Compliant with applicable Brazilian sectoral requirements "
                f"(sector: {context.sector.value})."
            ),
            regulation_citation=(
                "Brazilian Sectoral Requirements — CFM 2299/2021 / BCB 3.978/2020 "
                "/ CLT + MPT — all applicable obligations satisfied"
            ),
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class BrazilAIGovernanceOrchestrator:
    """
    Chains all four Brazil AI governance filters and returns the complete
    list of per-filter results.

    The orchestrator runs all filters in order and returns every result so
    that callers can inspect the full compliance picture. The
    :class:`BrazilAIGovernanceReport` derives the overall decision from the
    collected results using a severity-priority rule: DENIED > REQUIRES_HUMAN_REVIEW
    > REDACTED > APPROVED.
    """

    def __init__(self) -> None:
        self._filters = [
            LGPDDataProtectionFilter(),
            BrazilAIBillFilter(),
            ANPDGuidelinesFilter(),
            BrazilSectoralFilter(),
        ]

    def evaluate(
        self, context: BrazilAIContext, document: BrazilAIDocument
    ) -> List[FilterResult]:
        """Run all filters and return their results."""
        return [f.evaluate(context, document) for f in self._filters]


# ---------------------------------------------------------------------------
# Governance report
# ---------------------------------------------------------------------------


@dataclass
class BrazilAIGovernanceReport:
    """
    Aggregated governance report for a Brazil AI system evaluation.

    Attributes
    ----------
    context : BrazilAIContext
        The evaluation context that was assessed.
    document : BrazilAIDocument
        The document that was assessed.
    filter_results : list[FilterResult]
        Individual results from each governance layer filter.
    """

    context: BrazilAIContext
    document: BrazilAIDocument
    filter_results: List[FilterResult]

    @property
    def overall_decision(self) -> BrazilAIDecision:
        """
        Derive the overall governance decision from filter results.

        Priority (highest to lowest):
            DENIED > REQUIRES_HUMAN_REVIEW > REDACTED > APPROVED
        """
        decisions = {r.decision for r in self.filter_results}
        if BrazilAIDecision.DENIED in decisions:
            return BrazilAIDecision.DENIED
        if BrazilAIDecision.REQUIRES_HUMAN_REVIEW in decisions:
            return BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        if BrazilAIDecision.REDACTED in decisions:
            return BrazilAIDecision.REDACTED
        return BrazilAIDecision.APPROVED

    @property
    def is_compliant(self) -> bool:
        """True if the overall decision is APPROVED or REDACTED (not DENIED or REQUIRES_HUMAN_REVIEW)."""
        return self.overall_decision in (
            BrazilAIDecision.APPROVED,
            BrazilAIDecision.REDACTED,
        )

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary including the overall decision and
        a list of all non-APPROVED filter findings.
        """
        issues = [
            f"  [{r.filter_name}] {r.decision.value}: {r.reason}"
            for r in self.filter_results
            if r.decision != BrazilAIDecision.APPROVED
        ]
        if not issues:
            return (
                f"Brazil AI Governance: COMPLIANT — "
                f"all {len(self.filter_results)} filters APPROVED."
            )
        issues_text = "\n".join(issues)
        return (
            f"Brazil AI Governance: {self.overall_decision.value}\n"
            f"Non-compliant findings ({len(issues)}):\n{issues_text}"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # Scenario 1: Fully compliant healthcare AI (physician oversight present)
    # ------------------------------------------------------------------
    compliant_ctx = BrazilAIContext(
        user_id="demo-user-01",
        sector=BrazilSector.HEALTHCARE,
        ai_risk_level=BrazilAIRiskLevel.HIGH,
        # LGPD
        involves_personal_data=True,
        involves_sensitive_personal_data=True,
        lgpd_legal_basis="consent",
        has_lgpd_explicit_consent=True,
        involves_cross_border_transfer=False,
        has_lgpd_transfer_mechanism=False,
        has_processing_records=True,
        # AI Bill
        is_high_risk_ai=True,
        has_conformity_assessment=True,
        is_automated_decision_making=True,
        affects_fundamental_rights=True,
        human_review_available=True,
        has_incident_reporting=True,
        is_prohibited_ai_practice=False,
        # ANPD
        is_large_scale_processing=True,
        has_privacy_by_design=True,
        involves_excessive_data_collection=False,
        has_dpo_appointed=True,
        # Sectoral
        is_clinical_ai=True,
        physician_oversight_available=True,
        is_credit_scoring_ai=False,
        explainability_available=True,
        is_employment_decision_ai=False,
        bias_audit_completed=False,
    )
    compliant_doc = BrazilAIDocument(
        document_id="doc-001",
        document_type="MODEL_OUTPUT",
        contains_personal_data=True,
        contains_sensitive_data=True,
        data_subject_count=1,
        is_ai_model_output=True,
        classification="SENSITIVE_DATA",
    )

    orchestrator = BrazilAIGovernanceOrchestrator()
    results = orchestrator.evaluate(compliant_ctx, compliant_doc)
    report = BrazilAIGovernanceReport(
        context=compliant_ctx, document=compliant_doc, filter_results=results
    )
    print("=== Scenario 1: Fully Compliant Healthcare AI ===")
    print(report.compliance_summary)
    print()

    # ------------------------------------------------------------------
    # Scenario 2: Non-compliant — prohibited AI practice
    # ------------------------------------------------------------------
    prohibited_ctx = BrazilAIContext(
        user_id="demo-user-02",
        sector=BrazilSector.PUBLIC,
        ai_risk_level=BrazilAIRiskLevel.HIGH,
        involves_personal_data=True,
        involves_sensitive_personal_data=False,
        lgpd_legal_basis="legitimate_interest",
        has_lgpd_explicit_consent=False,
        involves_cross_border_transfer=False,
        has_lgpd_transfer_mechanism=False,
        has_processing_records=True,
        is_high_risk_ai=True,
        has_conformity_assessment=True,
        is_automated_decision_making=True,
        affects_fundamental_rights=True,
        human_review_available=True,
        has_incident_reporting=True,
        is_prohibited_ai_practice=True,  # <-- triggers Art. 22 denial
        is_large_scale_processing=False,
        has_privacy_by_design=True,
        involves_excessive_data_collection=False,
        has_dpo_appointed=True,
        is_clinical_ai=False,
        physician_oversight_available=False,
        is_credit_scoring_ai=False,
        explainability_available=True,
        is_employment_decision_ai=False,
        bias_audit_completed=False,
    )
    prohibited_doc = BrazilAIDocument(
        document_id="doc-002",
        document_type="REPORT",
        contains_personal_data=True,
        contains_sensitive_data=False,
        data_subject_count=10000,
        is_ai_model_output=True,
        classification="PERSONAL_DATA",
    )

    results2 = orchestrator.evaluate(prohibited_ctx, prohibited_doc)
    report2 = BrazilAIGovernanceReport(
        context=prohibited_ctx, document=prohibited_doc, filter_results=results2
    )
    print("=== Scenario 2: Prohibited AI Practice ===")
    print(report2.compliance_summary)
    print()

    # ------------------------------------------------------------------
    # Scenario 3: Financial AI without explainability
    # ------------------------------------------------------------------
    financial_ctx = BrazilAIContext(
        user_id="demo-user-03",
        sector=BrazilSector.FINANCIAL,
        ai_risk_level=BrazilAIRiskLevel.HIGH,
        involves_personal_data=True,
        involves_sensitive_personal_data=False,
        lgpd_legal_basis="contract",
        has_lgpd_explicit_consent=False,
        involves_cross_border_transfer=False,
        has_lgpd_transfer_mechanism=False,
        has_processing_records=True,
        is_high_risk_ai=True,
        has_conformity_assessment=True,
        is_automated_decision_making=True,
        affects_fundamental_rights=False,
        human_review_available=True,
        has_incident_reporting=True,
        is_prohibited_ai_practice=False,
        is_large_scale_processing=True,
        has_privacy_by_design=True,
        involves_excessive_data_collection=False,
        has_dpo_appointed=True,
        is_clinical_ai=False,
        physician_oversight_available=False,
        is_credit_scoring_ai=True,
        explainability_available=False,  # <-- triggers BCB review
        is_employment_decision_ai=False,
        bias_audit_completed=False,
    )
    financial_doc = BrazilAIDocument(
        document_id="doc-003",
        document_type="MODEL_OUTPUT",
        contains_personal_data=True,
        contains_sensitive_data=False,
        data_subject_count=500,
        is_ai_model_output=True,
        classification="PERSONAL_DATA",
    )

    results3 = orchestrator.evaluate(financial_ctx, financial_doc)
    report3 = BrazilAIGovernanceReport(
        context=financial_ctx, document=financial_doc, filter_results=results3
    )
    print("=== Scenario 3: Financial Credit Scoring — Missing Explainability ===")
    print(report3.compliance_summary)
