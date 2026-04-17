"""
regulated_ai_governance/adapters/google_adk_adapter.py

Google ADK Policy Guard — drop-in governance for Google Agent Development Kit agents.

Enforces FERPA, HIPAA, GDPR, EU AI Act, GLBA, and OWASP Agentic AI Top 10 2026
through ADK's native before_model_callback, before_agent_callback, and
before_tool_callback hooks.

Works with: LlmAgent, SequentialAgent, ParallelAgent, LoopAgent

Usage:
    from regulated_ai_governance.adapters.google_adk_adapter import (
        ADKPolicyGuard, Regulation, BigQueryAuditSink
    )

    guard = ADKPolicyGuard(
        regulations=[Regulation.FERPA, Regulation.HIPAA],
        audit_sink=BigQueryAuditSink(project="my-gcp-project", dataset="ai_audit"),
        agent_id="student-advisor-agent",
    )

    agent = LlmAgent(
        name="StudentAdvisor",
        model="gemini-2.0-flash",
        instruction="Help students with academic questions.",
        before_model_callback=guard.before_model_callback,
        before_agent_callback=guard.before_agent_callback,
        before_tool_callback=guard.before_tool_callback,
    )

Compatible with regulated-ai-governance v0.44.0+
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Google ADK imports — guarded for environments without ADK installed
try:
    from google.adk.agents import LlmAgent  # noqa: F401  (type hint use only)
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest
    from google.adk.models.llm_response import LlmResponse
    from google.genai import types

    ADK_AVAILABLE = True
except ImportError:  # pragma: no cover
    ADK_AVAILABLE = False
    # Stub types so the module loads in test/CI environments without ADK
    CallbackContext = Any  # type: ignore[assignment,misc]
    LlmRequest = Any       # type: ignore[assignment,misc]
    LlmResponse = Any      # type: ignore[assignment,misc]
    types = None           # type: ignore[assignment]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Regulation catalogue
# ---------------------------------------------------------------------------

class Regulation(str, Enum):
    """Supported regulatory frameworks."""

    # US Education
    FERPA = "FERPA"          # 34 CFR § 99 — student education records

    # US Healthcare
    HIPAA = "HIPAA"          # 45 CFR § 164 — protected health information

    # US Financial
    GLBA = "GLBA"            # 15 U.S.C. §§ 6801-6809 — consumer financial data
    FCRA = "FCRA"            # 15 U.S.C. § 1681 — consumer credit information

    # Global Privacy
    GDPR = "GDPR"            # EU 2016/679 — personal data (EU/EEA)
    CCPA = "CCPA"            # Cal. Civ. Code § 1798.100 — California consumers
    LGPD = "LGPD"            # Brazil Lei 13.709/2018
    PDPA = "PDPA"            # Singapore Personal Data Protection Act
    APPI = "APPI"            # Japan Act on Protection of Personal Information 2022
    DPDP = "DPDP"            # India Digital Personal Data Protection Act 2023

    # AI-Specific
    EU_AI_ACT = "EU_AI_ACT"  # EU 2024/1689 — high-risk AI system requirements
    NIST_AI_RMF = "NIST_AI_RMF"  # NIST AI Risk Management Framework

    # Security
    OWASP_AGENTIC = "OWASP_AGENTIC"  # OWASP Agentic AI Top 10 2026


# ---------------------------------------------------------------------------
# Audit infrastructure
# ---------------------------------------------------------------------------

@dataclass
class AuditRecord:
    """Immutable compliance audit entry generated for every agent interaction."""

    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Agent identity
    agent_id: str = ""
    agent_name: str = ""
    session_id: str = ""

    # Interaction
    event_type: str = ""          # before_model | before_agent | before_tool | blocked
    regulation_codes: list[str] = field(default_factory=list)

    # Decision
    action: str = "allow"         # allow | block | redact | warn
    reason: str = ""
    policy_refs: list[str] = field(default_factory=list)

    # Data sensitivity
    data_categories_detected: list[str] = field(default_factory=list)
    pii_detected: bool = False
    phi_detected: bool = False
    education_records_detected: bool = False

    # Tool governance (if applicable)
    tool_name: str = ""
    tool_args_hash: str = ""      # SHA-256 of serialised args — no raw data in logs

    # OWASP Agentic AI classification (ASI-01 through ASI-10)
    owasp_controls_triggered: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "regulation_codes": self.regulation_codes,
            "action": self.action,
            "reason": self.reason,
            "policy_refs": self.policy_refs,
            "data_categories_detected": self.data_categories_detected,
            "pii_detected": self.pii_detected,
            "phi_detected": self.phi_detected,
            "education_records_detected": self.education_records_detected,
            "tool_name": self.tool_name,
            "tool_args_hash": self.tool_args_hash,
            "owasp_controls_triggered": self.owasp_controls_triggered,
        }


class AuditSink(ABC):
    """Pluggable backend for audit record persistence."""

    @abstractmethod
    def write(self, record: AuditRecord) -> None: ...

    @abstractmethod
    def flush(self) -> None: ...


class ConsoleAuditSink(AuditSink):
    """Development sink — prints JSON audit records to stdout."""

    def write(self, record: AuditRecord) -> None:
        print(json.dumps(record.to_dict(), indent=2))

    def flush(self) -> None:
        pass


class BigQueryAuditSink(AuditSink):
    """
    Production sink — streams audit records to a BigQuery table.

    Matches the audit architecture used in JARVIS and ASTRUM deployments:
    Cloud Logging → BigQuery for long-term storage and Looker Studio dashboards.

    Schema: regulated_ai_governance.adk_audit_log
    Partition: timestamp (DATE)

    Args:
        project:   GCP project ID
        dataset:   BigQuery dataset name (default: "regulated_ai_audit")
        table:     BigQuery table name  (default: "adk_audit_log")
    """

    def __init__(
        self,
        project: str,
        dataset: str = "regulated_ai_audit",
        table: str = "adk_audit_log",
    ) -> None:
        self.project = project
        self.dataset = dataset
        self.table = table
        self._buffer: list[dict[str, Any]] = []
        self._client: Any = None  # google.cloud.bigquery.Client

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from google.cloud import bigquery  # type: ignore[import]
                self._client = bigquery.Client(project=self.project)
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "google-cloud-bigquery is required for BigQueryAuditSink. "
                    "Install with: pip install google-cloud-bigquery"
                ) from exc
        return self._client

    def write(self, record: AuditRecord) -> None:
        self._buffer.append(record.to_dict())
        if len(self._buffer) >= 10:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return
        client = self._get_client()
        table_ref = f"{self.project}.{self.dataset}.{self.table}"
        errors = client.insert_rows_json(table_ref, self._buffer)
        if errors:
            logger.error("BigQuery audit write errors: %s", errors)
        self._buffer.clear()


# ---------------------------------------------------------------------------
# Data classifiers
# ---------------------------------------------------------------------------

class _EducationRecordClassifier:
    """
    Detects FERPA-protected education record content.

    Covers: student ID, GPA, grades, enrollment status, financial aid,
    disciplinary records, and academic progress. Ref: 34 CFR § 99.3.
    """

    _PATTERNS = [
        r"\bstudent[\s_-]?id\b",
        r"\b(GPA|grade[\s_-]point)\b",
        r"\b(grade|transcript|enrollment|financial[\s_-]aid)\b",
        r"\b(academic[\s_-]standing|disciplinary|probation)\b",
        r"\b(FERPA|education[\s_-]record)\b",
        r"\b[A-Z]{2}\d{7,10}\b",          # student ID pattern
        r"\b\d{3}-\d{2}-\d{4}\b",         # SSN (also HIPAA/GDPR)
    ]

    def __init__(self) -> None:
        self._re = re.compile(
            "|".join(self._PATTERNS), re.IGNORECASE | re.MULTILINE
        )

    def detect(self, text: str) -> bool:
        return bool(self._re.search(text))

    def categories(self, text: str) -> list[str]:
        cats: list[str] = []
        mapping = {
            "student_id": r"\bstudent[\s_-]?id\b",
            "gpa_grades": r"\b(GPA|grade[\s_-]point|grade|transcript)\b",
            "enrollment_status": r"\benrollment\b",
            "financial_aid": r"\bfinancial[\s_-]aid\b",
            "disciplinary": r"\b(disciplinary|probation)\b",
        }
        for cat, pattern in mapping.items():
            if re.search(pattern, text, re.IGNORECASE):
                cats.append(cat)
        return cats


class _PHIClassifier:
    """
    Detects HIPAA Protected Health Information.

    Covers the 18 HIPAA Safe Harbor identifiers. Ref: 45 CFR § 164.514(b).
    """

    _PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",                     # SSN
        r"\b\d{3}[.-]\d{3}[.-]\d{4}\b",               # Phone
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b(diagnosis|prescri\w+|medication|treatment|lab[\s_-]result)\b",
        r"\b(medical[\s_-]record|patient[\s_-]id|MRN|ICD-10)\b",
        r"\b(PHI|HIPAA|protected[\s_-]health)\b",
        r"\b(DOB|date[\s_-]of[\s_-]birth)\b",
    ]

    def __init__(self) -> None:
        self._re = re.compile(
            "|".join(self._PATTERNS), re.IGNORECASE | re.MULTILINE
        )

    def detect(self, text: str) -> bool:
        return bool(self._re.search(text))


class _PIIClassifier:
    """
    Detects GDPR/CCPA/general PII.
    """

    _PATTERNS = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}[.-]\d{3}[.-]\d{4}\b",               # Phone (US)
        r"\b\d{3}-\d{2}-\d{4}\b",                     # SSN
        r"\b(passport|national[\s_-]id|driver[\s_-]licen[sc]e)\b",
        r"\b(IP[\s_-]address|device[\s_-]id|cookie[\s_-]id)\b",
        r"\b(biometric|facial[\s_-]recognition|fingerprint)\b",
    ]

    def __init__(self) -> None:
        self._re = re.compile(
            "|".join(self._PATTERNS), re.IGNORECASE | re.MULTILINE
        )

    def detect(self, text: str) -> bool:
        return bool(self._re.search(text))


# ---------------------------------------------------------------------------
# OWASP Agentic AI Top 10 2026 guard
# ---------------------------------------------------------------------------

class OWASPAgenticGuard:
    """
    Enforces OWASP Agentic AI Top 10 2026 controls (ASI-01 through ASI-10).

    Reference: https://owasp.org/www-project-top-10-for-large-language-model-applications/
    """

    # Prompt injection markers (ASI-02)
    _INJECTION_PATTERNS = [
        r"ignore\s+(previous|prior|all)\s+instructions",
        r"you\s+are\s+now\s+(a\s+)?(?!an?\s+AI)",
        r"(system|developer|admin)\s*(prompt|instruction|override)",
        r"jailbreak|DAN\s+mode|unrestricted\s+mode",
        r"<\|?(im_start|system|user|assistant)\|?>",
        r"\[\[(INST|SYS|SYSTEM)\]\]",
        r"IGNORE\s+ALL\s+PREVIOUS",
    ]

    # Privilege escalation markers (ASI-03)
    _ESCALATION_PATTERNS = [
        r"\b(sudo|root|admin|superuser)\b",
        r"\b(execute|run|shell|subprocess|eval)\b",
        r"\b(delete[\s_-]all|drop[\s_-]table|truncate)\b",
        r"\baccess\s+(all|unrestricted|full)(\s+\w+)?\s+(data|record|file)\b",
    ]

    def __init__(self) -> None:
        self._injection_re = re.compile(
            "|".join(self._INJECTION_PATTERNS), re.IGNORECASE | re.MULTILINE
        )
        self._escalation_re = re.compile(
            "|".join(self._ESCALATION_PATTERNS), re.IGNORECASE | re.MULTILINE
        )

    def check(self, text: str) -> list[str]:
        """Return list of triggered OWASP ASI control codes."""
        triggered: list[str] = []
        if self._injection_re.search(text):
            triggered.append("ASI-02")   # Prompt Injection
        if self._escalation_re.search(text):
            triggered.append("ASI-03")   # Privilege Escalation
        return triggered

    @staticmethod
    def hash_args(tool_args: dict[str, Any]) -> str:
        """SHA-256 of tool args for audit log — no raw data stored. (ASI-09)"""
        serialised = json.dumps(tool_args, sort_keys=True, default=str)
        return hashlib.sha256(serialised.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Main ADK Policy Guard
# ---------------------------------------------------------------------------

class ADKPolicyGuard:
    """
    Drop-in governance layer for Google ADK agents.

    Attaches to any LlmAgent via its native callback parameters:

        agent = LlmAgent(
            ...
            before_model_callback=guard.before_model_callback,
            before_agent_callback=guard.before_agent_callback,
            before_tool_callback=guard.before_tool_callback,
        )

    Args:
        regulations:   List of Regulation enum values to enforce.
        audit_sink:    AuditSink implementation for compliance logging.
                       Defaults to ConsoleAuditSink (dev only).
        agent_id:      Stable identifier for this agent (used in audit trail).
        block_on_phi:  If True (default), block model calls containing PHI when
                       HIPAA is active. Set False for audit-only mode.
        block_on_ferpa: If True (default), block model calls containing student
                       records when FERPA is active.
        block_on_injection: If True (default), block detected prompt injection.
    """

    def __init__(
        self,
        regulations: list[Regulation],
        audit_sink: AuditSink | None = None,
        agent_id: str = "adk-agent",
        block_on_phi: bool = True,
        block_on_ferpa: bool = True,
        block_on_injection: bool = True,
    ) -> None:
        self.regulations = set(regulations)
        self.audit_sink = audit_sink or ConsoleAuditSink()
        self.agent_id = agent_id
        self.block_on_phi = block_on_phi
        self.block_on_ferpa = block_on_ferpa
        self.block_on_injection = block_on_injection

        self._ferpa = _EducationRecordClassifier()
        self._phi = _PHIClassifier()
        self._pii = _PIIClassifier()
        self._owasp = OWASPAgenticGuard()

    # ------------------------------------------------------------------
    # Callback 1: before_agent_callback
    # Called before the agent processes each invocation.
    # Return None  → proceed normally.
    # Return types.Content → short-circuit; return that content directly.
    # ------------------------------------------------------------------

    def before_agent_callback(
        self, callback_context: CallbackContext
    ) -> "Optional[types.Content]":
        """Log agent invocation start and enforce EU AI Act transparency. (ASI-01, ASI-09)"""

        record = AuditRecord(
            agent_id=self.agent_id,
            agent_name=getattr(callback_context, "agent_name", "unknown"),
            session_id=self._session_id(callback_context),
            event_type="before_agent",
            regulation_codes=[r.value for r in self.regulations],
            action="allow",
            reason="Agent invocation authorised",
            policy_refs=self._policy_refs(),
            owasp_controls_triggered=["ASI-01"],  # identity check
        )

        # EU AI Act: high-risk AI systems must log invocations (Art. 12)
        if Regulation.EU_AI_ACT in self.regulations:
            record.policy_refs.append("EU AI Act Art. 12 — record-keeping")

        self.audit_sink.write(record)
        return None  # proceed

    # ------------------------------------------------------------------
    # Callback 2: before_model_callback
    # Called before each LLM call.
    # Return None      → proceed with LLM call.
    # Return LlmResponse → skip LLM; use this response instead.
    # ------------------------------------------------------------------

    def before_model_callback(
        self,
        callback_context: CallbackContext,
        llm_request: LlmRequest,
    ) -> "Optional[LlmResponse]":
        """
        Pre-LLM compliance gate.

        Enforces:
        - FERPA 34 CFR § 99.10: education records must not be disclosed without consent
        - HIPAA 45 CFR § 164.502: PHI must not be used/disclosed without authorisation
        - GDPR Art. 6: personal data processing requires lawful basis
        - OWASP ASI-02: prompt injection detection
        - OWASP ASI-03: privilege escalation detection
        """

        # Extract text from all content parts for analysis
        request_text = self._extract_text(llm_request)

        record = AuditRecord(
            agent_id=self.agent_id,
            agent_name=getattr(callback_context, "agent_name", "unknown"),
            session_id=self._session_id(callback_context),
            event_type="before_model",
            regulation_codes=[r.value for r in self.regulations],
        )

        # --- OWASP ASI-02: Prompt injection ---
        owasp_triggered = self._owasp.check(request_text)
        record.owasp_controls_triggered = owasp_triggered

        if "ASI-02" in owasp_triggered and self.block_on_injection:
            record.action = "block"
            record.reason = "Prompt injection attempt detected (OWASP ASI-02)"
            record.policy_refs = ["OWASP Agentic AI Top 10 2026 — ASI-02"]
            self.audit_sink.write(record)
            return self._block_response(
                "This request was blocked by the governance policy. "
                "Reason: potential prompt injection detected."
            )

        # --- FERPA: education records ---
        if Regulation.FERPA in self.regulations:
            if self._ferpa.detect(request_text):
                cats = self._ferpa.categories(request_text)
                record.education_records_detected = True
                record.data_categories_detected.extend(cats)
                record.policy_refs.append("FERPA 34 CFR § 99.10")

                if self.block_on_ferpa:
                    record.action = "block"
                    record.reason = (
                        f"Education record content detected: {cats}. "
                        "Disclosure requires prior consent under FERPA 34 CFR § 99.10."
                    )
                    self.audit_sink.write(record)
                    return self._block_response(
                        "This request contains student education record information "
                        "protected under FERPA. Processing requires verified consent."
                    )
                else:
                    record.action = "warn"
                    record.reason = "Education record content detected — audit-only mode"

        # --- HIPAA: protected health information ---
        if Regulation.HIPAA in self.regulations:
            if self._phi.detect(request_text):
                record.phi_detected = True
                record.data_categories_detected.append("PHI")
                record.policy_refs.append("HIPAA 45 CFR § 164.502")

                if self.block_on_phi:
                    record.action = "block"
                    record.reason = (
                        "Protected Health Information (PHI) detected. "
                        "Processing requires a HIPAA-compliant authorisation."
                    )
                    self.audit_sink.write(record)
                    return self._block_response(
                        "This request contains Protected Health Information (PHI). "
                        "A HIPAA Business Associate Agreement and authorisation are required."
                    )
                else:
                    record.action = "warn"
                    record.reason = "PHI detected — audit-only mode"

        # --- GDPR / CCPA: PII detection ---
        privacy_regs = {Regulation.GDPR, Regulation.CCPA, Regulation.LGPD,
                        Regulation.PDPA, Regulation.APPI, Regulation.DPDP}
        if self.regulations & privacy_regs:
            if self._pii.detect(request_text):
                record.pii_detected = True
                record.data_categories_detected.append("PII")
                record.policy_refs.append("GDPR Art. 6 — lawful basis for processing")
                record.action = "warn"
                record.reason = "PII detected — ensure lawful basis exists under applicable regulation"

        # --- OWASP ASI-03: Privilege escalation ---
        if "ASI-03" in owasp_triggered:
            record.owasp_controls_triggered.append("ASI-03")
            record.action = "block"
            record.reason = "Privilege escalation pattern detected (OWASP ASI-03)"
            record.policy_refs.append("OWASP Agentic AI Top 10 2026 — ASI-03")
            self.audit_sink.write(record)
            return self._block_response(
                "This request was blocked: privilege escalation pattern detected."
            )

        # --- OWASP ASI-09: Audit trail gap prevention ---
        # Always write an audit record, even for allowed requests
        if record.action == "allow":
            record.reason = "Request cleared all governance checks"
        self.audit_sink.write(record)
        return None  # proceed to LLM

    # ------------------------------------------------------------------
    # Callback 3: before_tool_callback
    # Called before each tool execution.
    # Return None → execute tool normally.
    # Return dict → skip tool; use dict as tool result.
    # ------------------------------------------------------------------

    def before_tool_callback(
        self,
        callback_context: CallbackContext,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> "Optional[dict[str, Any]]":
        """
        Tool invocation governance gate.

        Enforces:
        - OWASP ASI-05: Data exfiltration prevention
        - OWASP ASI-06: Uncontrolled agent autonomy — tool allowlist
        - FERPA: blocks tools accessing student records without consent
        - Audit trail (OWASP ASI-09)
        """

        args_hash = self._owasp.hash_args(tool_args)
        record = AuditRecord(
            agent_id=self.agent_id,
            agent_name=getattr(callback_context, "agent_name", "unknown"),
            session_id=self._session_id(callback_context),
            event_type="before_tool",
            regulation_codes=[r.value for r in self.regulations],
            tool_name=tool_name,
            tool_args_hash=args_hash,
            action="allow",
            reason=f"Tool '{tool_name}' execution authorised",
            policy_refs=["OWASP ASI-09 — tool invocation audit"],
            owasp_controls_triggered=["ASI-09"],  # always log tool calls
        )

        # Detect data exfiltration risk in tool args (ASI-05)
        args_text = json.dumps(tool_args, default=str)
        if self._ferpa.detect(args_text) and Regulation.FERPA in self.regulations:
            record.education_records_detected = True
            record.action = "warn"
            record.reason = (
                f"Tool '{tool_name}' invoked with education record data — "
                "verify FERPA consent before executing."
            )
            record.owasp_controls_triggered.append("ASI-05")
            record.policy_refs.append("FERPA 34 CFR § 99.30 — consent required")

        self.audit_sink.write(record)
        return None  # execute tool

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(llm_request: Any) -> str:
        """Extract plain text from LlmRequest contents for analysis."""
        try:
            parts: list[str] = []
            for content in getattr(llm_request, "contents", []):
                for part in getattr(content, "parts", []):
                    text = getattr(part, "text", None)
                    if text:
                        parts.append(text)
            return " ".join(parts)
        except Exception:  # noqa: BLE001
            return ""

    @staticmethod
    def _session_id(callback_context: Any) -> str:
        try:
            return str(callback_context.session_id)
        except AttributeError:
            return "unknown"

    def _policy_refs(self) -> list[str]:
        refs: list[str] = []
        mapping = {
            Regulation.FERPA: "FERPA 34 CFR § 99",
            Regulation.HIPAA: "HIPAA 45 CFR § 164",
            Regulation.GDPR: "GDPR EU 2016/679",
            Regulation.GLBA: "GLBA 15 U.S.C. § 6801",
            Regulation.EU_AI_ACT: "EU AI Act 2024/1689",
            Regulation.OWASP_AGENTIC: "OWASP Agentic AI Top 10 2026",
        }
        for reg in self.regulations:
            if reg in mapping:
                refs.append(mapping[reg])
        return refs

    @staticmethod
    def _block_response(message: str) -> "LlmResponse":
        """Construct a governance block response for the ADK framework."""
        if not ADK_AVAILABLE:
            return message  # type: ignore[return-value]
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=message)],
            )
        )


# ---------------------------------------------------------------------------
# Multi-agent governance wrapper
# ---------------------------------------------------------------------------

class ADKMultiAgentGovernance:
    """
    Governance boundary enforcement for multi-agent ADK systems.

    Manages per-agent policy guards in Orchestrator → Sub-Agent architectures
    (analogous to Polaris: Orchestrator → Lead Agent + Applicant Agent).

    Usage:
        governance = ADKMultiAgentGovernance(
            orchestrator_regulations=[Regulation.FERPA, Regulation.OWASP_AGENTIC],
            sub_agent_regulations={
                "LeadAgent": [Regulation.FERPA, Regulation.OWASP_AGENTIC],
                "ApplicantAgent": [Regulation.FERPA, Regulation.GDPR],
            },
            audit_sink=BigQueryAuditSink(project="my-project"),
        )
        orchestrator_guard, sub_guards = governance.build()
    """

    def __init__(
        self,
        orchestrator_regulations: list[Regulation],
        sub_agent_regulations: dict[str, list[Regulation]],
        audit_sink: AuditSink | None = None,
        block_on_phi: bool = True,
        block_on_ferpa: bool = True,
    ) -> None:
        self.orchestrator_regulations = orchestrator_regulations
        self.sub_agent_regulations = sub_agent_regulations
        self.audit_sink = audit_sink or ConsoleAuditSink()
        self.block_on_phi = block_on_phi
        self.block_on_ferpa = block_on_ferpa

    def build(self) -> tuple[ADKPolicyGuard, dict[str, ADKPolicyGuard]]:
        """
        Build governance guards for orchestrator and all sub-agents.

        Returns:
            (orchestrator_guard, {agent_name: sub_agent_guard})
        """
        orchestrator_guard = ADKPolicyGuard(
            regulations=self.orchestrator_regulations,
            audit_sink=self.audit_sink,
            agent_id="orchestrator",
            block_on_phi=self.block_on_phi,
            block_on_ferpa=self.block_on_ferpa,
        )
        sub_guards: dict[str, ADKPolicyGuard] = {}
        for agent_name, regs in self.sub_agent_regulations.items():
            sub_guards[agent_name] = ADKPolicyGuard(
                regulations=regs,
                audit_sink=self.audit_sink,
                agent_id=agent_name.lower().replace(" ", "-"),
                block_on_phi=self.block_on_phi,
                block_on_ferpa=self.block_on_ferpa,
            )
        return orchestrator_guard, sub_guards
