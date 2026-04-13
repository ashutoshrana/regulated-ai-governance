"""
dspy.py — DSPy integration for regulated AI governance.

Wraps any DSPy ``Module`` so that every ``forward()`` call is evaluated
against an ``ActionPolicy`` before execution.  Denied actions raise
``PermissionError``; escalated actions route to the configured escalation
sink while still permitting or blocking according to ``block_on_escalation``.

Compatible with DSPy ≥ 2.5.0 (requires Pydantic v2).

Installation:
    pip install regulated-ai-governance[dspy]

Usage::

    import dspy
    from regulated_ai_governance.integrations.dspy import GovernedDSPyModule
    from regulated_ai_governance.policy import ActionPolicy, EscalationRule

    policy = ActionPolicy(
        allowed_actions={"EnrollmentAdvisor", "CourseSearch"},
        escalation_rules=[
            EscalationRule("grade_modification", "GradeEditor", "registrar"),
        ],
    )

    advisor = dspy.ChainOfThought("question -> answer")
    governed = GovernedDSPyModule(
        wrapped_module=advisor,
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice-123",
        audit_sink=lambda rec: compliance_log.append(rec.to_log_entry()),
        block_on_escalation=True,
    )

    # Use exactly like the original module — the guard is invisible to callers
    answer = governed(question="What are my graduation requirements?")

    # Composing with other DSPy modules
    retriever = dspy.Retrieve(k=5)
    pipeline = dspy.Sequential(retriever, governed)

Governance action name convention:
    The ``ActionPolicy`` action name is derived from the wrapped module's class
    name: ``type(wrapped_module).__name__``.  Configure ``policy.allowed_actions``
    with the exact class name of each module you wish to permit.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy


class GovernedDSPyModule:
    """
    Policy-enforcing wrapper for any DSPy ``Module``.

    Intercepts ``forward()`` (via ``__call__``) and evaluates the call against
    the configured ``ActionPolicy`` before delegating to the wrapped module.

    The action name used for policy evaluation is the wrapped module's class
    name (``type(wrapped_module).__name__``).  Set ``allowed_actions`` in the
    ``ActionPolicy`` to the class names of modules you wish to permit.

    This class intentionally does **not** inherit from ``dspy.Module`` to avoid
    a hard dependency on DSPy at import time.  It mimics the DSPy Module API
    by forwarding ``__call__`` to ``forward()`` and delegating attribute access
    to the wrapped module for DSPy's introspection (``predictors()``,
    ``parameters()``, etc.).

    Args:
        wrapped_module: The DSPy ``Module`` to wrap.
        policy: ``ActionPolicy`` defining which modules are permitted.
        regulation: Regulation label written to audit records (``"FERPA"``,
            ``"HIPAA"``, ``"GLBA"``, etc.).
        actor_id: Authenticated principal identifier — must originate from the
            verified session, not from user input.
        audit_sink: Callable receiving a ``GovernanceAuditRecord`` for each
            invocation.  Wire to a durable compliance log store.
        block_on_escalation: If True (default), escalated calls are blocked
            and a ``PermissionError`` is raised.  If False, escalations are
            logged and execution continues.
        action_name: Override the policy action name.  Defaults to
            ``type(wrapped_module).__name__``.
        context: Optional static dict included in every audit record
            (e.g. session ID, pipeline stage).
    """

    def __init__(
        self,
        wrapped_module: Any,
        policy: ActionPolicy,
        regulation: str = "FERPA",
        actor_id: str = "",
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
        action_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        self._wrapped = wrapped_module
        self._action_name = action_name or type(wrapped_module).__name__
        self._context: dict[str, Any] = context or {}
        self._guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink,
            block_on_escalation=block_on_escalation,
            raise_on_deny=True,
        )

    # ------------------------------------------------------------------
    # DSPy Module protocol
    # ------------------------------------------------------------------

    def forward(self, *args: Any, **kwargs: Any) -> Any:
        """
        Evaluate policy and invoke the wrapped module's forward pass.

        Matches the DSPy ``Module.forward()`` signature so that this wrapper
        participates correctly in DSPy's pipeline composition.

        Args:
            *args: Positional arguments forwarded to the wrapped module.
            **kwargs: Keyword arguments forwarded to the wrapped module.

        Returns:
            The wrapped module's result if the action is permitted.

        Raises:
            PermissionError: If the policy denies the action.
        """
        ctx = {
            **self._context,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()),
        }
        return self._guard.guard(
            action_name=self._action_name,
            execute_fn=lambda: self._wrapped(*args, **kwargs),
            context=ctx,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Delegate to ``forward()`` — matches the DSPy Module ``__call__`` contract."""
        return self.forward(*args, **kwargs)

    # ------------------------------------------------------------------
    # Transparent delegation for DSPy introspection
    # ------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        """
        Forward attribute access to the wrapped module.

        This allows DSPy's compilation / teleprompter tooling (``predictors()``,
        ``parameters()``, ``deepcopy()``, etc.) to work transparently through
        the guard wrapper.
        """
        return getattr(self._wrapped, name)

    def __repr__(self) -> str:
        return f"GovernedDSPyModule(action={self._action_name!r}, wrapped={self._wrapped!r})"


class GovernedDSPyPipeline:
    """
    Policy-enforcing wrapper for a sequential DSPy pipeline.

    Applies the same ``ActionPolicy`` guard to every module in the pipeline.
    Each module is wrapped individually so that denied intermediate steps fail
    fast, before later modules execute.

    Args:
        modules: Ordered list of DSPy modules forming the pipeline.
        policy: ``ActionPolicy`` applied to all modules.
        regulation: Regulation label for audit records.
        actor_id: Authenticated principal identifier.
        audit_sink: Callable receiving audit records for every step.
        block_on_escalation: If True, any escalated step blocks the pipeline.

    Example::

        retriever = dspy.Retrieve(k=5)
        advisor = dspy.ChainOfThought("context, question -> answer")

        pipeline = GovernedDSPyPipeline(
            modules=[retriever, advisor],
            policy=policy,
            regulation="FERPA",
            actor_id="stu-alice",
        )

        result = pipeline(question="What courses remain?")
    """

    def __init__(
        self,
        modules: list[Any],
        policy: ActionPolicy,
        regulation: str = "FERPA",
        actor_id: str = "",
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
    ) -> None:
        self._steps = [
            GovernedDSPyModule(
                wrapped_module=mod,
                policy=policy,
                regulation=regulation,
                actor_id=actor_id,
                audit_sink=audit_sink,
                block_on_escalation=block_on_escalation,
            )
            for mod in modules
        ]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the pipeline sequentially.

        The first module receives ``*args, **kwargs``.  Each subsequent module
        receives the previous module's output — if the output is a dict-like
        object it is unpacked as keyword arguments; otherwise it is passed as
        the single positional argument.
        """
        result: Any = None
        for i, step in enumerate(self._steps):
            if i == 0:
                result = step(*args, **kwargs)
            elif isinstance(result, dict):
                result = step(**result)
            else:
                result = step(result)
        return result

    def __repr__(self) -> str:
        steps = " -> ".join(s._action_name for s in self._steps)
        return f"GovernedDSPyPipeline([{steps}])"
