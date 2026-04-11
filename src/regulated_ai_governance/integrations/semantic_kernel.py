"""
semantic_kernel.py — Semantic Kernel integration for regulated AI governance.

Wraps Semantic Kernel ``KernelFunction`` objects with an ``ActionPolicy``
guard. Each function invocation is evaluated against the policy before the
underlying kernel function executes.

Compatible with semantic-kernel ≥ 1.0.0.

Installation:
    pip install regulated-ai-governance[semantic-kernel]

Usage::

    from semantic_kernel import Kernel
    from regulated_ai_governance.integrations.semantic_kernel import (
        GovernedKernelPlugin,
    )
    from regulated_ai_governance.regulations.hipaa import make_hipaa_agent_policy

    kernel = Kernel()
    governed_plugin = GovernedKernelPlugin.from_object(
        plugin_name="PatientDataPlugin",
        target=my_plugin_instance,
        policy=make_hipaa_agent_policy(),
        regulation="HIPAA",
        actor_id="nurse-101",
        audit_sink=audit_log.append,
    )
    kernel.add_plugin(governed_plugin.plugin, plugin_name="PatientDataPlugin")
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy


class GovernedKernelPlugin:
    """
    Wraps a set of Semantic Kernel functions with regulated governance enforcement.

    Each function registered via ``add_function`` is wrapped so that the
    governance policy is checked before the underlying Semantic Kernel function
    executes. The resulting plugin object is stored as ``.plugin``.

    This class is framework-agnostic at instantiation time — the optional
    ``semantic_kernel`` dependency is not imported at module level. Build the
    ``plugin`` attribute separately using your Kernel's plugin registration API.

    Args:
        guard: Configured ``GovernedActionGuard`` for all functions in this plugin.
        plugin_name: Name for this plugin (used in audit records).
    """

    def __init__(self, guard: GovernedActionGuard, plugin_name: str) -> None:
        self._guard = guard
        self.plugin_name = plugin_name
        self._functions: dict[str, Callable[..., Any]] = {}

    @classmethod
    def from_object(
        cls,
        plugin_name: str,
        target: Any,
        policy: ActionPolicy,
        regulation: str,
        actor_id: str,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
    ) -> GovernedKernelPlugin:
        """
        Factory: create a ``GovernedKernelPlugin`` from any object.

        Args:
            plugin_name: Name for this plugin in the kernel.
            target: Object whose callable methods will be wrapped.
            policy: ``ActionPolicy`` governing function invocations.
            regulation: Regulation label for audit records.
            actor_id: Identifier of the user on whose behalf functions run.
            audit_sink: Callable receiving each ``GovernanceAuditRecord``.
            block_on_escalation: If True, escalated function calls are blocked.

        Returns:
            A ``GovernedKernelPlugin`` with all callable methods of *target* wrapped.
        """
        guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink or (lambda _: None),
            block_on_escalation=block_on_escalation,
            raise_on_deny=True,
        )
        instance = cls(guard=guard, plugin_name=plugin_name)
        # Auto-register all public callable methods from the target object.
        for attr_name in dir(target):
            if attr_name.startswith("_"):
                continue
            attr = getattr(target, attr_name)
            if callable(attr):
                instance.add_function(attr_name, attr)
        return instance

    def add_function(self, function_name: str, fn: Callable[..., Any]) -> GovernedKernelPlugin:
        """
        Register a function under this plugin with policy enforcement.

        Args:
            function_name: The policy action name (must match the allow-list).
            fn: The underlying callable to wrap.

        Returns:
            Self, for fluent chaining.
        """

        def _governed(*args: Any, **kwargs: Any) -> Any:
            return self._guard.guard(
                action_name=function_name,
                execute_fn=lambda: fn(*args, **kwargs),
                context={"plugin": self.plugin_name, "function": function_name},
            )

        _governed.__name__ = fn.__name__ if hasattr(fn, "__name__") else function_name
        _governed.__doc__ = fn.__doc__
        self._functions[function_name] = _governed
        return self

    def get_governed_function(self, function_name: str) -> Callable[..., Any]:
        """
        Return the governed wrapper for a registered function.

        Args:
            function_name: The name used in ``add_function()``.

        Returns:
            The governed callable.

        Raises:
            KeyError: If *function_name* was not registered.
        """
        return self._functions[function_name]

    @property
    def function_names(self) -> list[str]:
        """Return names of all registered governed functions."""
        return list(self._functions.keys())
