"""
orchestrator.py — Multi-framework governance orchestration.

``GovernanceOrchestrator`` evaluates an AI agent action or RAG retrieval event
against **multiple compliance frameworks simultaneously**, aggregates the
decisions, and emits a single ``ComprehensiveAuditReport`` per evaluation.

Design principles
-----------------
- **Deny-all aggregation**: if *any* configured framework denies an action,
  the overall decision is DENY. The most-restrictive policy wins.
- **Unified audit trail**: a single ``ComprehensiveAuditReport`` captures every
  framework's individual decision, denial reasons, and escalation targets in one
  structured record — suitable for SIEM, GRC, and compliance log stores.
- **Framework-agnostic**: the orchestrator holds a list of
  ``GovernedActionGuard`` instances, one per framework. Each guard carries its
  own ``ActionPolicy``, regulation label, and actor scope.
- **Audit-only mode**: set ``audit_only=True`` to run all frameworks and log
  outcomes without blocking any action — useful for shadow-mode compliance
  evaluation during rollout.

Supported governance frameworks
---------------------------------
Any regulation or standard expressible as a ``GovernedActionGuard`` is
supported.  Pre-built factories for common frameworks are provided in
``regulated_ai_governance.regulations``:

    Regulatory / statutory:
    - FERPA 34 CFR § 99 — education records
    - HIPAA 45 CFR §§ 164.312, 164.502 — ePHI access
    - GDPR Articles 5, 6, 17 — data subject rights
    - GLBA 16 CFR § 314 — financial customer safeguards
    - CCPA / CPRA — California consumer privacy

    IT audit / security frameworks:
    - ISO/IEC 27001:2022 — ISMS Annex A CBAC
    - PCI DSS v4.0 — cardholder data, PAN masking
    - SOC 2 Type II — tenant isolation, CBAC, CC7.2 audit

    AI / technology governance:
    - NIST AI RMF 1.0 + AI 600-1 GenAI Profile
    - OWASP LLM Top 10 (2025)
    - ISO/IEC 42001:2023 — AI Management System

Usage
------

.. code-block:: python

    from regulated_ai_governance.orchestrator import (
        GovernanceOrchestrator,
        FrameworkGuard,
    )
    from regulated_ai_governance.agent_guard import GovernedActionGuard
    from regulated_ai_governance.policy import ActionPolicy

    ferpa_guard = GovernedActionGuard(
        policy=ActionPolicy(allowed_actions={"read_transcript"}),
        regulation="FERPA",
        actor_id="stu_alice",
    )
    hipaa_guard = GovernedActionGuard(
        policy=ActionPolicy(allowed_actions={"read_vitals"}),
        regulation="HIPAA",
        actor_id="nurse_bob",
    )

    orchestrator = GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard(regulation="FERPA", guard=ferpa_guard),
            FrameworkGuard(regulation="HIPAA", guard=hipaa_guard),
        ],
        audit_sink=my_compliance_log.append,
    )

    result = orchestrator.guard(
        action_name="read_transcript",
        execute_fn=lambda: {"credits": 45},
        actor_id="stu_alice",
    )

    # Access the comprehensive report
    report = orchestrator.last_report
    print(report.to_compliance_summary())
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.policy import PolicyDecision


@dataclass
class FrameworkGuard:
    """
    Associates a ``GovernedActionGuard`` with a regulation label for the orchestrator.

    Attributes:
        regulation: Regulation or framework name (e.g. ``"FERPA"``, ``"ISO_27001"``,
            ``"PCI_DSS_v4"``).  Written into the audit report per-framework result.
        guard: The ``GovernedActionGuard`` configured for this framework.
        enabled: If False, this framework is skipped during evaluation but still
            appears in the report as ``status: "skipped"``.
    """

    regulation: str
    guard: GovernedActionGuard
    enabled: bool = True


@dataclass
class FrameworkResult:
    """
    Per-framework evaluation result within a ``ComprehensiveAuditReport``.

    Attributes:
        regulation: Framework/regulation label.
        permitted: Whether this framework permitted the action.
        denial_reason: Denial reason if ``permitted`` is False.
        escalation_target: Escalation routing target if a rule fired.
        skipped: True if the framework was disabled at evaluation time.
    """

    regulation: str
    permitted: bool
    denial_reason: str | None = None
    escalation_target: str | None = None
    skipped: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "regulation": self.regulation,
            "permitted": self.permitted,
            "denial_reason": self.denial_reason,
            "escalation_target": self.escalation_target,
            "skipped": self.skipped,
        }


@dataclass
class MultiFrameworkDecision:
    """
    Aggregated decision from evaluating multiple governance frameworks.

    Deny-all semantics: ``overall_permitted`` is True only when *all*
    enabled frameworks permit the action.

    Attributes:
        overall_permitted: True iff all enabled frameworks permitted the action.
        framework_results: Per-framework results indexed by regulation name.
        denial_frameworks: Regulation names of frameworks that denied the action.
        escalation_targets: All escalation routing targets across frameworks.
        denial_reasons: All denial reasons across frameworks.
    """

    overall_permitted: bool
    framework_results: dict[str, FrameworkResult]
    denial_frameworks: list[str]
    escalation_targets: list[str]
    denial_reasons: list[str]


@dataclass
class ComprehensiveAuditReport:
    """
    Unified compliance audit record produced by ``GovernanceOrchestrator``.

    Captures every framework's individual decision in a single structured
    record suitable for SIEM ingestion, GRC platforms, and structured log stores.

    Attributes:
        action_name: The action that was evaluated.
        actor_id: Authenticated principal identifier.
        overall_permitted: Aggregate permit/deny across all frameworks.
        frameworks_evaluated: Regulation names of all frameworks configured.
        frameworks_permitted: Regulation names that permitted the action.
        frameworks_denied: Regulation names that denied the action.
        frameworks_skipped: Regulation names that were disabled / skipped.
        escalation_targets: All escalation routing targets from any framework.
        denial_reasons: All denial reasons from any framework.
        framework_results: Per-framework result dicts (one entry per framework).
        audit_only_mode: True if the orchestrator ran in audit-only (non-blocking) mode.
        report_id: Auto-generated UUID for this specific record.
        timestamp_utc: ISO 8601 UTC timestamp of the evaluation event.
        context: Optional request context dict.
    """

    action_name: str
    actor_id: str
    overall_permitted: bool
    frameworks_evaluated: list[str]
    frameworks_permitted: list[str]
    frameworks_denied: list[str]
    frameworks_skipped: list[str]
    escalation_targets: list[str]
    denial_reasons: list[str]
    framework_results: list[dict[str, Any]]
    audit_only_mode: bool = False
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: dict[str, Any] = field(default_factory=dict)

    def to_log_entry(self) -> str:
        """
        Serialize to a compact JSON log line for SIEM / compliance log storage.

        Sorts all list fields for deterministic output.
        """
        return json.dumps(
            {
                "event": "multi_framework_governance_evaluation",
                "report_id": self.report_id,
                "action_name": self.action_name,
                "actor_id": self.actor_id,
                "overall_permitted": self.overall_permitted,
                "audit_only_mode": self.audit_only_mode,
                "frameworks_evaluated": sorted(self.frameworks_evaluated),
                "frameworks_permitted": sorted(self.frameworks_permitted),
                "frameworks_denied": sorted(self.frameworks_denied),
                "frameworks_skipped": sorted(self.frameworks_skipped),
                "escalation_targets": sorted(set(self.escalation_targets)),
                "denial_reasons": self.denial_reasons,
                "framework_results": self.framework_results,
                "timestamp_utc": self.timestamp_utc,
                "context": self.context,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """
        SHA-256 hash of the audit report for tamper-evidence.

        Store alongside the log entry in a separate immutable store to detect
        unauthorized modification of audit records.
        """
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()

    def to_compliance_summary(self) -> str:
        """
        Return a human-readable multi-line compliance summary.

        Suitable for logging to stdout, writing to a GRC ticket, or embedding
        in a compliance workflow notification.
        """
        lines = [
            "=== Governance Evaluation Report ===",
            f"Report ID:      {self.report_id}",
            f"Action:         {self.action_name}",
            f"Actor:          {self.actor_id}",
            f"Timestamp:      {self.timestamp_utc}",
            f"Overall result: {'✓ PERMITTED' if self.overall_permitted else '✗ DENIED'}",
            f"Audit-only mode:{' YES (non-blocking)' if self.audit_only_mode else ' NO (enforcing)'}",
            "",
            f"Frameworks evaluated ({len(self.frameworks_evaluated)}):",
        ]
        for result in self.framework_results:
            status = "SKIP" if result.get("skipped") else ("PASS" if result.get("permitted") else "DENY")
            line = f"  [{status:4s}] {result['regulation']}"
            if result.get("denial_reason"):
                line += f" — {result['denial_reason']}"
            if result.get("escalation_target"):
                line += f" (escalate → {result['escalation_target']})"
            lines.append(line)

        if self.denial_reasons:
            lines += ["", "Denial reasons:"]
            for reason in self.denial_reasons:
                lines.append(f"  • {reason}")

        if self.escalation_targets:
            lines += ["", "Escalation targets:"]
            for target in sorted(set(self.escalation_targets)):
                lines.append(f"  → {target}")

        lines.append("=" * 36)
        return "\n".join(lines)


class GovernanceOrchestrator:
    """
    Evaluates agent actions against multiple governance frameworks simultaneously.

    The orchestrator applies **deny-all aggregation**: if *any* enabled framework
    denies an action, the overall decision is DENY regardless of how many other
    frameworks permit it.  This matches the principle of least privilege required
    by HIPAA, FERPA, PCI DSS, and ISO/IEC 27001.

    Audit-only mode
    ---------------
    Set ``audit_only=True`` to enable shadow-mode compliance evaluation: all
    frameworks are evaluated and their decisions are recorded, but no action is
    ever blocked.  Use this during rollout to understand your compliance posture
    without disrupting existing workflows.

    Args:
        framework_guards: List of ``FrameworkGuard`` instances, one per
            regulation or standard to enforce.
        audit_sink: Optional callable receiving each ``ComprehensiveAuditReport``.
            Wire to a durable compliance log store.
        audit_only: If True, evaluation results are logged but no action is
            blocked.  Defaults to False (enforcing mode).
        require_all_enabled: If True (default), all enabled frameworks must
            permit for the action to proceed.  If False, uses first-permit
            semantics (any permit allows).  Recommend keeping True for regulated
            environments.
    """

    def __init__(
        self,
        framework_guards: list[FrameworkGuard],
        audit_sink: Callable[[ComprehensiveAuditReport], None] | None = None,
        audit_only: bool = False,
        require_all_enabled: bool = True,
    ) -> None:
        self._framework_guards = framework_guards
        self._audit_sink = audit_sink
        self._audit_only = audit_only
        self._require_all_enabled = require_all_enabled
        self._last_report: ComprehensiveAuditReport | None = None

    @property
    def last_report(self) -> ComprehensiveAuditReport | None:
        """The ``ComprehensiveAuditReport`` produced by the most recent evaluation."""
        return self._last_report

    @property
    def audit_only(self) -> bool:
        """True if the orchestrator is running in non-blocking audit-only mode."""
        return self._audit_only

    def evaluate(
        self,
        action_name: str,
        actor_id: str = "",
        context: dict[str, Any] | None = None,
    ) -> MultiFrameworkDecision:
        """
        Evaluate *action_name* against all configured frameworks.

        Does not execute any action — use ``guard`` to both evaluate and execute.

        Args:
            action_name: The action to evaluate.
            actor_id: Authenticated principal identifier.
            context: Optional context dict (session ID, channel, request metadata).

        Returns:
            A ``MultiFrameworkDecision`` with per-framework results and
            aggregate permit/deny.
        """
        results: dict[str, FrameworkResult] = {}
        denial_frameworks: list[str] = []
        escalation_targets: list[str] = []
        denial_reasons: list[str] = []

        for fg in self._framework_guards:
            if not fg.enabled:
                results[fg.regulation] = FrameworkResult(
                    regulation=fg.regulation,
                    permitted=True,
                    skipped=True,
                )
                continue

            decision: PolicyDecision = fg.guard.evaluate(action_name, context)
            result = FrameworkResult(
                regulation=fg.regulation,
                permitted=decision.permitted,
                denial_reason=decision.denial_reason,
                escalation_target=(decision.escalation.escalate_to if decision.escalation else None),
            )
            results[fg.regulation] = result

            if not decision.permitted:
                denial_frameworks.append(fg.regulation)
                if decision.denial_reason:
                    denial_reasons.append(f"[{fg.regulation}] {decision.denial_reason}")
            if decision.escalation:
                escalation_targets.append(decision.escalation.escalate_to)

        if self._require_all_enabled:
            overall_permitted = len(denial_frameworks) == 0
        else:
            # any-permit semantics: at least one enabled framework must permit
            any_permitted = any(r.permitted for r in results.values() if not r.skipped)
            overall_permitted = any_permitted

        return MultiFrameworkDecision(
            overall_permitted=overall_permitted,
            framework_results=results,
            denial_frameworks=denial_frameworks,
            escalation_targets=escalation_targets,
            denial_reasons=denial_reasons,
        )

    def _build_report(
        self,
        action_name: str,
        actor_id: str,
        decision: MultiFrameworkDecision,
        context: dict[str, Any] | None,
    ) -> ComprehensiveAuditReport:
        framework_results = [r.to_dict() for r in decision.framework_results.values()]
        all_regulations = [fg.regulation for fg in self._framework_guards]
        permitted_regulations = [
            r for r, result in decision.framework_results.items() if result.permitted and not result.skipped
        ]
        skipped_regulations = [r for r, result in decision.framework_results.items() if result.skipped]

        return ComprehensiveAuditReport(
            action_name=action_name,
            actor_id=actor_id,
            overall_permitted=decision.overall_permitted,
            frameworks_evaluated=all_regulations,
            frameworks_permitted=permitted_regulations,
            frameworks_denied=decision.denial_frameworks,
            frameworks_skipped=skipped_regulations,
            escalation_targets=decision.escalation_targets,
            denial_reasons=decision.denial_reasons,
            framework_results=framework_results,
            audit_only_mode=self._audit_only,
            context=context or {},
        )

    def guard(
        self,
        action_name: str,
        execute_fn: Callable[..., Any],
        actor_id: str = "",
        context: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Evaluate all frameworks for *action_name* and, if permitted, execute *execute_fn*.

        Always emits a ``ComprehensiveAuditReport`` regardless of outcome.
        In audit-only mode, execution always proceeds after audit logging.

        Args:
            action_name: Name of the action being guarded.
            execute_fn: Callable to invoke if the action is permitted.
            actor_id: Authenticated principal identifier.
            context: Optional context dict.
            *args: Positional arguments forwarded to *execute_fn*.
            **kwargs: Keyword arguments forwarded to *execute_fn*.

        Returns:
            The return value of *execute_fn* if permitted (or in audit-only mode),
            or a denial string if blocked.

        Raises:
            PermissionError: Never raised by the orchestrator directly. Individual
                guards may raise if configured with ``raise_on_deny=True``.
        """
        decision = self.evaluate(action_name, actor_id=actor_id, context=context)
        report = self._build_report(action_name, actor_id, decision, context)
        self._last_report = report

        if self._audit_sink is not None:
            self._audit_sink(report)

        if self._audit_only or decision.overall_permitted:
            return execute_fn(*args, **kwargs)

        denial_summary = "; ".join(decision.denial_reasons)
        return (
            f"[regulated-ai-governance] Action '{action_name}' BLOCKED by "
            f"{len(decision.denial_frameworks)} framework(s): "
            f"{', '.join(sorted(decision.denial_frameworks))}. "
            f"Reasons: {denial_summary}"
        )

    def add_framework(self, framework_guard: FrameworkGuard) -> None:
        """
        Add a framework guard at runtime.

        Args:
            framework_guard: The ``FrameworkGuard`` to add.
        """
        self._framework_guards.append(framework_guard)

    def remove_framework(self, regulation: str) -> bool:
        """
        Remove a framework guard by regulation name.

        Args:
            regulation: Regulation label to remove (case-sensitive).

        Returns:
            True if a matching guard was found and removed, False otherwise.
        """
        before = len(self._framework_guards)
        self._framework_guards = [fg for fg in self._framework_guards if fg.regulation != regulation]
        return len(self._framework_guards) < before

    def enable_framework(self, regulation: str) -> None:
        """Enable a previously disabled framework guard."""
        for fg in self._framework_guards:
            if fg.regulation == regulation:
                fg.enabled = True

    def disable_framework(self, regulation: str) -> None:
        """Disable a framework guard without removing it."""
        for fg in self._framework_guards:
            if fg.regulation == regulation:
                fg.enabled = False

    @property
    def configured_regulations(self) -> list[str]:
        """List of all configured regulation names (enabled and disabled)."""
        return [fg.regulation for fg in self._framework_guards]

    @property
    def active_regulations(self) -> list[str]:
        """List of currently enabled regulation names."""
        return [fg.regulation for fg in self._framework_guards if fg.enabled]
