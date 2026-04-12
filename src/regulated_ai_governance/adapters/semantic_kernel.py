"""
Semantic Kernel adapter for regulated-ai-governance.

Provides PolicyKernelPlugin — an SK plugin that exposes policy check as
a native SK function, enabling policy enforcement within SK pipelines.

Regulatory basis: FERPA 34 CFR § 99.31, HIPAA 45 CFR § 164.308

Usage:
    from regulated_ai_governance.adapters.semantic_kernel import PolicyKernelPlugin
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _import_semantic_kernel() -> Any:
    try:
        import semantic_kernel  # noqa: F401

        return semantic_kernel
    except ImportError as exc:
        raise ImportError(
            "semantic-kernel is required for this integration. "
            "Install with: pip install 'regulated-ai-governance[semantic-kernel]'"
        ) from exc


class PolicyKernelPlugin:
    """
    Semantic Kernel plugin that exposes policy enforcement as SK functions.

    Adds two SK-callable functions:
    - check_action_permitted(action_name): returns bool
    - get_permitted_actions(): returns list of permitted action names

    Duck-typed — does not inherit from SK base class at definition time.
    Register with kernel.add_plugin(PolicyKernelPlugin(...), plugin_name="policy")

    Args:
        policy: ActionPolicy defining which actions are permitted
        regulation_citation: Regulatory basis string for audit logs
    """

    def __init__(
        self,
        policy: Any,
        regulation_citation: str = "FERPA 34 CFR § 99.31(a)(1)",
    ) -> None:
        _import_semantic_kernel()
        self._policy = policy
        self._regulation_citation = regulation_citation

    def _is_permitted(self, action_name: str) -> bool:
        """Delegate to policy using can_run or permits, handling both interfaces."""
        if hasattr(self._policy, "can_run"):
            return bool(self._policy.can_run(action_name))
        if hasattr(self._policy, "permits"):
            permitted, _ = self._policy.permits(action_name)
            return permitted
        return True

    def check_action_permitted(self, action_name: str) -> bool:
        """
        SK-callable function: check if action_name is permitted by policy.

        Args:
            action_name: Name of the action/tool to check

        Returns:
            True if permitted, False otherwise
        """
        permitted = self._is_permitted(action_name)

        logger.info(
            "sk_policy_check | action=%r | permitted=%s | regulation=%s",
            action_name,
            permitted,
            self._regulation_citation,
        )
        return permitted

    def get_permitted_actions(self) -> list[str]:
        """
        SK-callable function: return list of all permitted action names.

        Returns:
            List of action names that policy allows
        """
        if hasattr(self._policy, "allowed_actions"):
            return sorted(self._policy.allowed_actions)
        return []
