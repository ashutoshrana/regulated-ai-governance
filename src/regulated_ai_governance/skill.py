"""
skill.py — Comprehensive AI governance audit skill.

``GovernanceAuditSkill`` is a high-level entry point that assembles a
``GovernanceOrchestrator`` from a declarative ``GovernanceConfig`` and exposes
the full orchestration capability as:

  1. A direct Python API (``audit_action``, ``audit_retrieval``).
  2. A LangChain callback handler (``as_langchain_handler``).
  3. A CrewAI tool wrapper (``as_crewai_tool``).
  4. A LlamaIndex query-time postprocessor (``as_llama_index_postprocessor``).
  5. A Haystack component (``as_haystack_component``).
  6. A Microsoft Agent Framework middleware (``as_maf_middleware``).

The skill supports **any combination** of governance frameworks drawn from
the complete cross-industry compliance catalogue:

  Regulatory / statutory:
  - FERPA, HIPAA, GDPR, GLBA, CCPA

  IT audit / security:
  - ISO/IEC 27001:2022 (ISMS CBAC)
  - PCI DSS v4.0 (CHD access + PAN masking)
  - SOC 2 Type II (tenant + confidentiality CBAC)

  AI / technology governance:
  - NIST AI RMF 1.0 + AI 600-1 GenAI Profile
  - OWASP LLM Top 10 2025
  - ISO/IEC 42001:2023 (AI Management System)
  - EU AI Act Article 9/10/12 (high-risk AI)
  - DORA Article 9/28 (EU financial operational resilience)
  - CMMC 2.0 Level 2 (US DoD supply chain)
  - CSA CCM v4.0 / STAR for AI

Architecture
-------------

.. code-block:: text

    GovernanceConfig
      ├─ FrameworkConfig[]  (one per regulation)
      │    ├─ regulation: str
      │    ├─ guard: GovernedActionGuard
      │    └─ enabled: bool
      └─ audit_only: bool

    GovernanceAuditSkill
      └─ GovernanceOrchestrator  (multi-framework deny-all aggregation)
           ├─ audit_action()     → ComprehensiveAuditReport
           ├─ audit_retrieval()  → (filtered_docs, ComprehensiveAuditReport)
           └─ channel adapters   → LangChain / CrewAI / LlamaIndex / Haystack / MAF

Usage — Direct API
-------------------

.. code-block:: python

    from regulated_ai_governance.skill import (
        GovernanceAuditSkill,
        GovernanceConfig,
        FrameworkConfig,
    )
    from regulated_ai_governance.agent_guard import GovernedActionGuard
    from regulated_ai_governance.policy import ActionPolicy

    skill = GovernanceAuditSkill(
        GovernanceConfig(
            frameworks=[
                FrameworkConfig(
                    regulation="FERPA",
                    guard=GovernedActionGuard(
                        policy=ActionPolicy(
                            allowed_actions={"read_transcript", "read_enrollment"}
                        ),
                        regulation="FERPA",
                        actor_id="advisor_007",
                    ),
                ),
                FrameworkConfig(
                    regulation="HIPAA",
                    guard=GovernedActionGuard(
                        policy=ActionPolicy(
                            allowed_actions={"read_vitals", "read_labs"}
                        ),
                        regulation="HIPAA",
                        actor_id="nurse_abc",
                    ),
                ),
            ],
            audit_only=False,
        ),
        audit_sink=my_compliance_log.append,
    )

    # Guard an agent action
    result = skill.audit_action(
        action_name="read_transcript",
        execute_fn=lambda: {"gpa": 3.9},
        actor_id="advisor_007",
        context={"session_id": "sess_001", "channel": "crewai"},
    )

    # Get the full compliance report
    print(skill.last_report.to_compliance_summary())

Usage — LangChain
------------------

.. code-block:: python

    handler = skill.as_langchain_handler()
    # Pass to LangChain chain: llm.invoke(prompt, config={"callbacks": [handler]})

Usage — CrewAI
---------------

.. code-block:: python

    tool = skill.as_crewai_tool(
        action_name="search_knowledge_base",
        execute_fn=lambda query: vector_store.similarity_search(query),
    )
    # Pass to CrewAI agent as a tool in the tools list

Usage — audit_retrieval (RAG pre-filter)
-----------------------------------------

.. code-block:: python

    safe_docs, report = skill.audit_retrieval(
        documents=retrieved_docs,
        actor_id="stu_alice",
        frameworks=["FERPA", "ISO_27001"],  # subset of configured frameworks
        context={"query": "What are my grades?"},
    )
    # safe_docs = documents allowed by all specified frameworks
    # report = ComprehensiveAuditReport with per-framework results
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.orchestrator import (
    ComprehensiveAuditReport,
    FrameworkGuard,
    GovernanceOrchestrator,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class FrameworkConfig:
    """
    Declarative configuration for a single governance framework within the skill.

    Attributes:
        regulation: Framework/regulation label (e.g. ``"FERPA"``, ``"ISO_42001"``).
        guard: Pre-configured ``GovernedActionGuard`` for this framework.
        enabled: Whether this framework participates in evaluations.
            Disabled frameworks appear in reports as ``status: "skipped"``.
    """

    regulation: str
    guard: GovernedActionGuard
    enabled: bool = True


@dataclass
class GovernanceConfig:
    """
    Top-level configuration for ``GovernanceAuditSkill``.

    Attributes:
        frameworks: List of ``FrameworkConfig`` instances — one per regulation
            or standard to enforce.
        audit_only: If True, the skill evaluates all frameworks and emits
            ``ComprehensiveAuditReport`` records but never blocks any action.
            Use this during shadow-mode compliance evaluation.
        require_all_enabled: If True (default), all enabled frameworks must
            permit an action for it to proceed (deny-all aggregation, most
            restrictive wins). If False, any-permit semantics apply.
    """

    frameworks: list[FrameworkConfig] = field(default_factory=list)
    audit_only: bool = False
    require_all_enabled: bool = True


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------


class GovernanceAuditSkill:
    """
    Comprehensive AI governance audit skill — multi-framework, multi-channel.

    Wraps ``GovernanceOrchestrator`` with a channel-aware API for direct use in
    LangChain, CrewAI, LlamaIndex, Haystack, MAF, and plain Python workflows.

    Args:
        config: ``GovernanceConfig`` defining which frameworks to enforce.
        audit_sink: Optional callable receiving each ``ComprehensiveAuditReport``.
            Wire to a durable compliance log store or SIEM sink.
    """

    def __init__(
        self,
        config: GovernanceConfig,
        audit_sink: Callable[[ComprehensiveAuditReport], None] | None = None,
    ) -> None:
        self._config = config
        self._audit_sink = audit_sink
        self._orchestrator = GovernanceOrchestrator(
            framework_guards=[
                FrameworkGuard(
                    regulation=fc.regulation,
                    guard=fc.guard,
                    enabled=fc.enabled,
                )
                for fc in config.frameworks
            ],
            audit_sink=audit_sink,
            audit_only=config.audit_only,
            require_all_enabled=config.require_all_enabled,
        )

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    @property
    def last_report(self) -> ComprehensiveAuditReport | None:
        """The ``ComprehensiveAuditReport`` produced by the most recent evaluation."""
        return self._orchestrator.last_report

    @property
    def active_frameworks(self) -> list[str]:
        """List of currently enabled framework/regulation names."""
        return self._orchestrator.active_regulations

    @property
    def configured_frameworks(self) -> list[str]:
        """List of all configured framework names (enabled and disabled)."""
        return self._orchestrator.configured_regulations

    @property
    def audit_only(self) -> bool:
        """True if this skill is running in non-blocking audit-only mode."""
        return self._orchestrator.audit_only

    def audit_action(
        self,
        action_name: str,
        execute_fn: Callable[..., Any],
        actor_id: str = "",
        frameworks: list[str] | None = None,
        context: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Evaluate *action_name* against all (or selected) governance frameworks
        and, if permitted, execute *execute_fn*.

        Always emits a ``ComprehensiveAuditReport`` regardless of outcome.

        Args:
            action_name: Name of the action to guard.
            execute_fn: Callable to invoke if all frameworks permit the action.
            actor_id: Authenticated principal identifier (from session — never
                from user input).
            frameworks: Optional list of regulation names to restrict evaluation
                to a subset of configured frameworks.  ``None`` = all active
                frameworks.
            context: Optional context dict (session ID, channel, request
                metadata). Written into the audit report.
            *args: Positional arguments forwarded to *execute_fn*.
            **kwargs: Keyword arguments forwarded to *execute_fn*.

        Returns:
            The return value of *execute_fn* if permitted, or a denial string.
        """
        ctx = dict(context or {})
        if actor_id:
            ctx.setdefault("actor_id", actor_id)

        with self._framework_scope(self, frameworks):
            return self._orchestrator.guard(
                action_name=action_name,
                execute_fn=execute_fn,
                actor_id=actor_id,
                context=ctx,
                *args,
                **kwargs,
            )

    def audit_retrieval(
        self,
        documents: list[dict[str, Any]],
        actor_id: str = "",
        frameworks: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], ComprehensiveAuditReport]:
        """
        Check whether this actor is authorized to perform document retrieval
        and return the documents (or an empty list if not authorized).

        **Important distinction**: this method enforces *action-level*
        authorization — is the actor permitted to perform retrieval at all?
        Content-level filtering (which specific documents the actor may see
        based on document metadata such as student_id, PHI category, tenant)
        is the responsibility of ``enterprise-rag-patterns`` pre-filters.

        A single ``ComprehensiveAuditReport`` is emitted per call, recording
        the authorization decision and document count.

        Args:
            documents: List of document dicts from the vector store or retriever.
            actor_id: Authenticated principal identifier.
            frameworks: Optional subset of configured frameworks to apply.
            context: Optional base context dict.

        Returns:
            A tuple of (documents_if_authorized, comprehensive_audit_report).
            If authorized (or in audit-only mode), returns all input documents.
            If denied, returns an empty list.
        """
        base_ctx = dict(context or {})
        if actor_id:
            base_ctx.setdefault("actor_id", actor_id)
        base_ctx["retrieval_document_count"] = len(documents)

        with self._framework_scope(self, frameworks):
            decision = self._orchestrator.evaluate(
                action_name="document_retrieval",
                actor_id=actor_id,
                context=base_ctx,
            )
            report = self._orchestrator._build_report(
                action_name="document_retrieval",
                actor_id=actor_id,
                decision=decision,
                context={
                    **base_ctx,
                    "documents_input": len(documents),
                    "documents_returned": len(documents) if (decision.overall_permitted or self.audit_only) else 0,
                },
            )
            self._orchestrator._last_report = report

            if self._audit_sink is not None:
                self._audit_sink(report)

        if decision.overall_permitted or self.audit_only:
            return documents, report
        else:
            logger.debug(
                "[GovernanceAuditSkill] retrieval BLOCKED by: %s",
                ", ".join(decision.denial_frameworks),
            )
            return [], report

    def enable_framework(self, regulation: str) -> None:
        """Enable a previously disabled governance framework."""
        self._orchestrator.enable_framework(regulation)

    def disable_framework(self, regulation: str) -> None:
        """Disable a governance framework without removing it."""
        self._orchestrator.disable_framework(regulation)

    # ------------------------------------------------------------------
    # Channel adapters
    # ------------------------------------------------------------------

    def as_langchain_handler(self) -> Any:
        """
        Return a LangChain ``BaseCallbackHandler`` that intercepts retrieval
        events and evaluates them against all configured governance frameworks.

        Requires: ``pip install 'regulated-ai-governance[langchain]'``

        The handler intercepts ``on_retriever_end`` events to apply governance
        controls before documents reach the chain.

        Returns:
            A ``GovernanceCallbackHandler`` instance (lazy import).

        Raises:
            ImportError: If ``langchain-core`` is not installed.
        """
        try:
            from regulated_ai_governance.integrations.langchain import GovernanceCallbackHandler  # type: ignore[import]

            return GovernanceCallbackHandler(skill=self)
        except ImportError as exc:
            raise ImportError(
                "LangChain integration requires langchain-core. "
                "Install with: pip install 'regulated-ai-governance[langchain]'"
            ) from exc

    def as_crewai_tool(
        self,
        action_name: str,
        execute_fn: Callable[..., Any],
        actor_id: str = "",
        tool_name: str | None = None,
        tool_description: str | None = None,
    ) -> Any:
        """
        Return a CrewAI-compatible tool that wraps *execute_fn* with governance
        enforcement from this skill.

        Requires: ``pip install 'regulated-ai-governance[crewai]'``

        Args:
            action_name: Governance action name for policy evaluation.
            execute_fn: The underlying function the CrewAI agent will call.
            actor_id: Agent/principal identifier written to audit records.
            tool_name: Optional tool name (defaults to *action_name*).
            tool_description: Optional tool description for the agent.

        Returns:
            A CrewAI-compatible tool object (lazy import).

        Raises:
            ImportError: If ``crewai`` is not installed.
        """
        try:
            from regulated_ai_governance.integrations.crewai import GovernedCrewAITool  # type: ignore[import]

            return GovernedCrewAITool(
                skill=self,
                action_name=action_name,
                execute_fn=execute_fn,
                actor_id=actor_id,
                name=tool_name or action_name,
                description=tool_description or f"Governed action: {action_name}",
            )
        except ImportError as exc:
            raise ImportError(
                "CrewAI integration requires crewai. "
                "Install with: pip install 'regulated-ai-governance[crewai]'"
            ) from exc

    def as_llama_index_postprocessor(self, actor_id: str = "") -> Any:
        """
        Return a LlamaIndex ``BaseNodePostprocessor`` that applies governance
        controls to retrieved nodes before they are assembled into context.

        Requires: ``pip install 'regulated-ai-governance[llama-index]'``

        Returns:
            A ``GovernanceNodePostprocessor`` instance (lazy import).

        Raises:
            ImportError: If ``llama-index-core`` is not installed.
        """
        try:
            from regulated_ai_governance.integrations.llama_index import (
                GovernanceNodePostprocessor,  # type: ignore[import]
            )

            return GovernanceNodePostprocessor(skill=self, actor_id=actor_id)
        except ImportError as exc:
            raise ImportError(
                "LlamaIndex integration requires llama-index-core. "
                "Install with: pip install 'regulated-ai-governance[llama-index]'"
            ) from exc

    def as_haystack_component(self, actor_id: str = "") -> Any:
        """
        Return a Haystack 2.x ``Component`` that applies governance controls
        to retrieved documents before they reach the prompt builder.

        Requires: ``pip install 'regulated-ai-governance[haystack]'``

        Returns:
            A ``GovernanceFilter`` Haystack component (lazy import).

        Raises:
            ImportError: If ``haystack-ai`` is not installed.
        """
        try:
            from regulated_ai_governance.integrations.haystack import GovernanceFilter  # type: ignore[import]

            return GovernanceFilter(skill=self, actor_id=actor_id)
        except ImportError as exc:
            raise ImportError(
                "Haystack integration requires haystack-ai. "
                "Install with: pip install 'regulated-ai-governance[haystack]'"
            ) from exc

    def as_maf_middleware(self, actor_id: str = "") -> Any:
        """
        Return a Microsoft Agent Framework ``AgentMiddleware`` that evaluates
        governance policies before each agent action.

        Requires: ``pip install 'regulated-ai-governance[maf]'``

        Returns:
            A ``GovernanceMAFMiddleware`` instance (lazy import).

        Raises:
            ImportError: If ``microsoft-agents`` is not installed.
        """
        try:
            from regulated_ai_governance.integrations.maf import GovernanceMAFMiddleware  # type: ignore[import]

            return GovernanceMAFMiddleware(skill=self, actor_id=actor_id)
        except ImportError as exc:
            raise ImportError(
                "MAF integration requires microsoft-agents. "
                "Install with: pip install 'regulated-ai-governance[maf]'"
            ) from exc

    # ------------------------------------------------------------------
    # Convenience factories
    # ------------------------------------------------------------------

    @classmethod
    def for_education(
        cls,
        actor_id: str,
        allowed_actions: set[str] | None = None,
        audit_sink: Callable[[ComprehensiveAuditReport], None] | None = None,
        audit_only: bool = False,
    ) -> GovernanceAuditSkill:
        """
        Factory: FERPA-compliant governance for educational AI systems.

        Configures FERPA (34 CFR § 99) policy enforcement for the given actor.

        Args:
            actor_id: Authenticated user/agent ID from the verified session.
            allowed_actions: Set of permitted action names.  Defaults to a
                conservative baseline (read-only student record operations).
            audit_sink: Optional compliance log sink.
            audit_only: Shadow-mode flag.

        Returns:
            A ``GovernanceAuditSkill`` with FERPA enforcement configured.
        """
        from regulated_ai_governance.policy import ActionPolicy

        default_allowed = allowed_actions or {
            "read_transcript",
            "read_enrollment_status",
            "read_financial_aid_status",
            "read_course_schedule",
        }
        return cls(
            config=GovernanceConfig(
                frameworks=[
                    FrameworkConfig(
                        regulation="FERPA",
                        guard=GovernedActionGuard(
                            policy=ActionPolicy(allowed_actions=default_allowed),
                            regulation="FERPA",
                            actor_id=actor_id,
                        ),
                    ),
                ],
                audit_only=audit_only,
            ),
            audit_sink=audit_sink,
        )

    @classmethod
    def for_healthcare(
        cls,
        actor_id: str,
        allowed_actions: set[str] | None = None,
        audit_sink: Callable[[ComprehensiveAuditReport], None] | None = None,
        audit_only: bool = False,
    ) -> GovernanceAuditSkill:
        """
        Factory: HIPAA-compliant governance for healthcare AI systems.

        Configures HIPAA (45 CFR §§ 164.312, 164.502) minimum-necessary
        enforcement for the given healthcare actor.

        Args:
            actor_id: Authenticated clinician/staff ID.
            allowed_actions: Permitted action names.  Defaults to treatment-
                context read operations.
            audit_sink: Optional compliance log sink.
            audit_only: Shadow-mode flag.

        Returns:
            A ``GovernanceAuditSkill`` with HIPAA enforcement configured.
        """
        from regulated_ai_governance.policy import ActionPolicy

        default_allowed = allowed_actions or {
            "read_patient_vitals",
            "read_lab_results",
            "read_medication_list",
            "read_diagnosis",
            "read_care_plan",
        }
        return cls(
            config=GovernanceConfig(
                frameworks=[
                    FrameworkConfig(
                        regulation="HIPAA",
                        guard=GovernedActionGuard(
                            policy=ActionPolicy(allowed_actions=default_allowed),
                            regulation="HIPAA",
                            actor_id=actor_id,
                        ),
                    ),
                ],
                audit_only=audit_only,
            ),
            audit_sink=audit_sink,
        )

    @classmethod
    def for_enterprise(
        cls,
        actor_id: str,
        allowed_actions: set[str] | None = None,
        regulations: list[str] | None = None,
        audit_sink: Callable[[ComprehensiveAuditReport], None] | None = None,
        audit_only: bool = False,
    ) -> GovernanceAuditSkill:
        """
        Factory: Multi-regulation governance for enterprise AI systems.

        Configures FERPA + HIPAA + GDPR + GLBA + SOC2 simultaneously,
        applying deny-all aggregation across all enabled frameworks.

        Use this factory for enterprise AI agents that may handle data
        across multiple regulated domains, or when the regulatory context
        is not known in advance.

        Args:
            actor_id: Authenticated principal ID.
            allowed_actions: Actions permitted across all frameworks.
                Defaults to a conservative baseline.
            regulations: Subset of frameworks to enable.  Defaults to
                ``["FERPA", "HIPAA", "GDPR", "GLBA"]``.
            audit_sink: Optional compliance log sink.
            audit_only: Shadow-mode flag for initial rollout.

        Returns:
            A ``GovernanceAuditSkill`` with multi-regulation enforcement.
        """
        from regulated_ai_governance.policy import ActionPolicy

        enabled = set(regulations or ["FERPA", "HIPAA", "GDPR", "GLBA"])
        default_allowed = allowed_actions or {
            "read_document",
            "search_knowledge_base",
            "summarize_document",
            "answer_question",
        }
        policy = ActionPolicy(allowed_actions=default_allowed)
        frameworks = []
        for reg in ["FERPA", "HIPAA", "GDPR", "GLBA", "SOC2"]:
            frameworks.append(
                FrameworkConfig(
                    regulation=reg,
                    guard=GovernedActionGuard(
                        policy=policy,
                        regulation=reg,
                        actor_id=actor_id,
                    ),
                    enabled=reg in enabled,
                )
            )
        return cls(
            config=GovernanceConfig(frameworks=frameworks, audit_only=audit_only),
            audit_sink=audit_sink,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    class _framework_scope:
        """Context manager that temporarily restricts active frameworks."""

        def __init__(
            self,
            skill_or_orchestrator: Any,
            frameworks: list[str] | None,
        ) -> None:
            # When frameworks is None, no scoping needed — this is a no-op CM.
            self._orchestrator: GovernanceOrchestrator | None = None
            self._previously_disabled: list[str] = []

            if frameworks is not None and hasattr(skill_or_orchestrator, "_orchestrator"):
                self._orchestrator = skill_or_orchestrator._orchestrator
                active = set(self._orchestrator.active_regulations)
                requested = set(frameworks)
                to_disable = active - requested
                for reg in to_disable:
                    self._orchestrator.disable_framework(reg)
                    self._previously_disabled.append(reg)
            elif frameworks is not None and isinstance(skill_or_orchestrator, GovernanceOrchestrator):
                self._orchestrator = skill_or_orchestrator
                active = set(self._orchestrator.active_regulations)
                requested = set(frameworks)
                to_disable = active - requested
                for reg in to_disable:
                    self._orchestrator.disable_framework(reg)
                    self._previously_disabled.append(reg)

        def __enter__(self) -> GovernanceAuditSkill._framework_scope:
            return self

        def __exit__(self, *_: Any) -> None:
            if self._orchestrator is not None:
                for reg in self._previously_disabled:
                    self._orchestrator.enable_framework(reg)
