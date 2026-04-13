"""
haystack.py — Haystack integration for regulated AI governance.

Provides a Haystack pipeline component that wraps a ``GovernedActionGuard``
around any document-processing step, enforcing ``ActionPolicy`` before
documents are passed to the LLM context window.

Compatible with Haystack 2.x (haystack-ai ≥ 2.0.0).

Installation:
    pip install regulated-ai-governance[haystack]

Usage::

    from regulated_ai_governance.integrations.haystack import GovernedHaystackComponent
    from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy
    from haystack import Pipeline

    governed = GovernedHaystackComponent(
        action_name="retrieve_student_documents",
        policy=make_ferpa_student_policy(),
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=audit_log.append,
    )

    pipeline = Pipeline()
    pipeline.add_component("governed_retriever", governed)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy


class GovernedHaystackComponent:
    """
    A Haystack-compatible pipeline component that enforces regulated AI governance.

    Wraps a document-processing callable (e.g. a retriever run function) with an
    ``ActionPolicy`` guard. If the action is denied, ``PermissionError`` is raised
    and the pipeline fails fast rather than leaking unauthorised documents.

    This class does NOT import ``haystack`` at module level — the optional
    dependency is only needed at runtime when integrated into a Haystack pipeline.
    To register it as a ``@component``, wrap it using the Haystack component
    decorator in your application code.

    Args:
        action_name: Policy action name evaluated for every ``run()`` call.
        policy: ``ActionPolicy`` governing document processing.
        regulation: Regulation label for audit records.
        actor_id: Identifier of the user on whose behalf the component runs.
        audit_sink: Callable receiving each ``GovernanceAuditRecord``.
        block_on_escalation: If True, escalated calls are blocked.
    """

    def __init__(
        self,
        action_name: str,
        policy: ActionPolicy,
        regulation: str,
        actor_id: str,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
    ) -> None:
        self.action_name = action_name
        self._guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink or (lambda _: None),
            block_on_escalation=block_on_escalation,
            raise_on_deny=True,
        )

    def run(self, documents: list[Any], query: str = "") -> dict[str, Any]:
        """
        Govern a document-processing step in the Haystack pipeline.

        The action is evaluated against the policy before ``documents`` are
        passed downstream. If denied, ``PermissionError`` is raised.

        Args:
            documents: List of Haystack ``Document`` objects to process.
            query: The query string (included in audit context).

        Returns:
            Dict with ``"documents"`` key containing the original documents if
            the action is permitted.

        Raises:
            PermissionError: If the action is denied by policy.
        """
        return self._guard.guard(
            action_name=self.action_name,
            execute_fn=lambda: {"documents": documents},
            context={"query": query, "document_count": len(documents)},
        )

    def guard_callable(
        self,
        fn: Callable[..., Any],
        *args: Any,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Guard an arbitrary callable under this component's policy.

        Use this to protect any document-processing function beyond the standard
        ``run()`` interface.

        Args:
            fn: Callable to execute if the action is permitted.
            *args: Positional arguments forwarded to *fn*.
            context: Optional context dict for audit records.
            **kwargs: Keyword arguments forwarded to *fn*.

        Returns:
            The result of *fn* if permitted.

        Raises:
            PermissionError: If the action is denied by policy.
        """
        return self._guard.guard(
            action_name=self.action_name,
            execute_fn=lambda: fn(*args, **kwargs),
            context=context,
        )


# ---------------------------------------------------------------------------
# Haystack 2.27 @component factory
# ---------------------------------------------------------------------------


def make_haystack_policy_guard(
    policy: ActionPolicy,
    regulation: str,
    actor_id: str,
    action_name: str = "haystack_pipeline_step",
    audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
    block_on_escalation: bool = True,
) -> type:
    """
    Factory that returns a Haystack 2.x ``@component``-decorated class enforcing
    regulated AI governance in a Haystack pipeline.

    Requires ``haystack-ai>=2.20.0``.  Import and apply the ``@component``
    decorator at call time so the package is importable without Haystack installed.

    The returned class has a ``run(documents, query)`` method matching the
    Haystack 2.27 component contract.  Add it to a pipeline with
    ``pipeline.add_component("policy_guard", make_haystack_policy_guard(...)())``.

    Installation::

        pip install 'regulated-ai-governance[haystack]'

    Usage::

        from haystack import Pipeline
        from regulated_ai_governance.integrations.haystack import make_haystack_policy_guard
        from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

        GuardClass = make_haystack_policy_guard(
            policy=make_ferpa_student_policy(),
            regulation="FERPA",
            actor_id="stu-alice",
            action_name="retrieve_student_documents",
            audit_sink=audit_log.append,
        )

        pipeline = Pipeline()
        pipeline.add_component("retriever", retriever)
        pipeline.add_component("policy_guard", GuardClass())
        pipeline.connect("retriever.documents", "policy_guard.documents")

    Args:
        policy: ``ActionPolicy`` governing each pipeline call.
        regulation: Regulation label for audit records.
        actor_id: Authenticated principal identifier.
        action_name: Policy action name evaluated on every ``run()`` call.
        audit_sink: Optional callable receiving each ``GovernanceAuditRecord``.
        block_on_escalation: If True, escalated actions are blocked.

    Returns:
        A ``@component``-decorated Haystack 2.x class.

    Raises:
        ImportError: If ``haystack-ai`` is not installed.
    """
    try:
        from haystack import component  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "haystack-ai>=2.20.0 is required for make_haystack_policy_guard. "
            "Install it with: pip install 'regulated-ai-governance[haystack]'"
        ) from exc

    _guard = GovernedActionGuard(
        policy=policy,
        regulation=regulation,
        actor_id=actor_id,
        audit_sink=audit_sink or (lambda _: None),
        block_on_escalation=block_on_escalation,
        raise_on_deny=True,
    )
    _action_name = action_name

    @component
    class HaystackPolicyGuard:
        """
        Haystack 2.x pipeline component enforcing regulated AI governance.

        Evaluates ``ActionPolicy`` before passing documents downstream.
        Raises ``PermissionError`` if the action is denied or escalation-blocked.
        """

        @component.output_types(documents=list)
        def run(self, documents: list[Any], query: str = "") -> dict[str, Any]:
            """
            Govern a document batch in the Haystack pipeline.

            Args:
                documents: List of Haystack ``Document`` objects.
                query: Original query string (included in audit context).

            Returns:
                ``{"documents": documents}`` if the action is permitted.

            Raises:
                PermissionError: If the action is denied by policy.
            """
            return _guard.guard(
                action_name=_action_name,
                execute_fn=lambda: {"documents": documents},
                context={"query": query, "document_count": len(documents)},
            )

    return HaystackPolicyGuard
