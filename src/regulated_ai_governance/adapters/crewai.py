"""
adapters/crewai.py — Duck-typed CrewAI adapter (legacy compatibility path).

.. deprecated::
    For **CrewAI 1.14+**, use :class:`regulated_ai_governance.integrations.crewai.EnterpriseActionGuard`
    instead. That implementation inherits from ``BaseTool``, satisfies CrewAI's
    ``isinstance(tool, BaseTool)`` checks, and is compatible with ``args_schema``
    (Pydantic v2).

    This module's duck-typed ``EnterpriseActionGuard`` works for scenarios where
    a ``BaseTool`` subclass is not strictly required, but will **fail silently**
    when CrewAI internally calls ``isinstance(tool, BaseTool)`` in 1.14+.

    Migration::

        # Before (duck-typed, legacy):
        from regulated_ai_governance.adapters.crewai import EnterpriseActionGuard

        # After (BaseTool-inheriting, CrewAI 1.14+ compatible):
        from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard

Regulatory basis: FERPA 34 CFR § 99.31(a)(1), HIPAA 45 CFR § 164.308(a)(4)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


@dataclass
class PolicyViolationError(Exception):
    """Raised when an agent attempts an action blocked by policy."""

    action: str
    policy_name: str
    regulation_citation: str = "FERPA 34 CFR § 99.31(a)(1)"

    def __str__(self) -> str:
        return (
            f"Policy violation: action '{self.action}' is not permitted under "
            f"policy '{self.policy_name}'. "
            f"Regulatory basis: {self.regulation_citation}"
        )


def _import_crewai() -> Any:
    try:
        import crewai  # noqa: F401

        return crewai
    except ImportError as exc:
        raise ImportError(
            "crewai is required for this integration. Install with: pip install 'regulated-ai-governance[crewai]'"
        ) from exc


class EnterpriseActionGuard:
    """
    Duck-typed CrewAI tool wrapper with enterprise policy enforcement.

    .. deprecated::
        Use :class:`regulated_ai_governance.integrations.crewai.EnterpriseActionGuard`
        for CrewAI 1.14+ (proper ``BaseTool`` inheritance, ``args_schema`` support).

    Checks ActionPolicy.can_run(tool_name) before delegating to the
    underlying tool. If the action is not permitted, raises PolicyViolationError
    and emits a structured audit log entry.

    Duck-typed to CrewAI BaseTool interface — no hard import at class definition.
    This means ``isinstance(tool, BaseTool)`` checks in CrewAI 1.14+ will fail.

    Args:
        tool: The CrewAI tool to guard (duck-typed, must have .name and ._run())
        policy: ActionPolicy defining which actions are permitted
        regulation_citation: Regulatory basis for the policy (default: FERPA)
        policy_name: Human-readable name for this policy (for audit logs)
    """

    def __init__(
        self,
        tool: Any,
        policy: Any,  # regulated_ai_governance.policy.ActionPolicy
        regulation_citation: str = "FERPA 34 CFR § 99.31(a)(1)",
        policy_name: str = "enterprise-action-policy",
    ) -> None:
        _import_crewai()
        self._tool = tool
        self._policy = policy
        self._regulation_citation = regulation_citation
        self._policy_name = policy_name
        # Mirror CrewAI tool attributes
        self.name: str = getattr(tool, "name", "unknown_tool")
        self.description: str = getattr(tool, "description", "")

    def _can_run(self, action_name: str) -> bool:
        """
        Delegate to policy.can_run if available; otherwise use policy.permits.

        ActionPolicy in this library uses permits(), which returns (bool, str).
        """
        if hasattr(self._policy, "can_run"):
            return bool(self._policy.can_run(action_name))
        if hasattr(self._policy, "permits"):
            permitted, _ = self._policy.permits(action_name)
            return permitted
        # Permissive fallback — should not occur in normal usage
        return True

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute tool if permitted by policy; raise PolicyViolationError otherwise.

        Audit log emitted on every call (permitted or denied) per regulated
        AI governance requirements.
        """
        permitted = self._can_run(self.name)

        if permitted:
            logger.info(
                "policy_check | action=%r | permitted=True | policy=%r | regulation=%s",
                self.name,
                self._policy_name,
                self._regulation_citation,
            )
            return self._tool._run(*args, **kwargs)
        else:
            logger.warning(
                "policy_check | action=%r | permitted=False | policy=%r | regulation=%s",
                self.name,
                self._policy_name,
                self._regulation_citation,
            )
            raise PolicyViolationError(
                action=self.name,
                policy_name=self._policy_name,
                regulation_citation=self._regulation_citation,
            )

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Public CrewAI interface (delegates to _run)."""
        return self._run(*args, **kwargs)
