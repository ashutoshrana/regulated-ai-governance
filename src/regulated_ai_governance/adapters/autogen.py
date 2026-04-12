"""
AutoGen adapter for regulated-ai-governance.

Provides PolicyEnforcingAgent — wraps AutoGen ConversableAgent to check
CompliancePolicy before generating replies involving regulated data.

Regulatory basis: FERPA 34 CFR § 99.3, HIPAA 45 CFR § 164.514

Usage:
    from regulated_ai_governance.adapters.autogen import PolicyEnforcingAgent
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _import_autogen() -> Any:
    for pkg in ("autogen", "pyautogen", "autogen_agentchat"):
        try:
            import importlib

            return importlib.import_module(pkg)
        except ImportError:
            continue
    raise ImportError(
        "autogen or pyautogen is required for this integration. "
        "Install with: pip install 'regulated-ai-governance[autogen]'"
    )


class PolicyEnforcingAgent:
    """
    Duck-typed AutoGen ConversableAgent wrapper that checks policy before
    generating replies.

    In regulated environments, every agent reply involving PHI/FERPA records
    must be gated by access policy. This wrapper intercepts generate_reply
    and blocks responses that would violate configured policy.

    Args:
        agent: The underlying AutoGen ConversableAgent (duck-typed)
        policy: ActionPolicy or CompliancePolicy defining permitted actions
        blocked_reply: Message to send when policy blocks a reply
        regulation_citation: Regulatory basis string for audit logs
    """

    def __init__(
        self,
        agent: Any,
        policy: Any,
        blocked_reply: str = "[Response blocked by compliance policy]",
        regulation_citation: str = "FERPA 34 CFR § 99.3",
    ) -> None:
        _import_autogen()
        self._agent = agent
        self._policy = policy
        self._blocked_reply = blocked_reply
        self._regulation_citation = regulation_citation
        # Mirror agent attributes
        self.name: str = getattr(agent, "name", "policy-enforcing-agent")

    def _is_permitted(self) -> bool:
        """Check policy using can_run or permits, handling both interfaces."""
        if hasattr(self._policy, "can_run"):
            return bool(self._policy.can_run(self.name))
        if hasattr(self._policy, "permits"):
            permitted, _ = self._policy.permits(self.name)
            return permitted
        return True

    def generate_reply(
        self,
        messages: list[dict[str, Any]] | None = None,
        sender: Any = None,
        **kwargs: Any,
    ) -> str | dict[str, Any] | None:
        """
        Generate a reply only if policy permits.

        Checks whether the agent's name (which represents its role/action scope)
        is permitted by the configured policy. If not, returns the blocked_reply
        message and emits a warning audit log.
        """
        permitted = self._is_permitted()

        logger.info(
            "autogen_policy_check | agent=%r | permitted=%s | regulation=%s",
            self.name,
            permitted,
            self._regulation_citation,
        )

        if not permitted:
            logger.warning(
                "autogen_policy_blocked | agent=%r | regulation=%s",
                self.name,
                self._regulation_citation,
            )
            return self._blocked_reply

        return self._agent.generate_reply(messages=messages, sender=sender, **kwargs)

    def initiate_chat(self, *args: Any, **kwargs: Any) -> Any:
        """Delegate to underlying agent."""
        return self._agent.initiate_chat(*args, **kwargs)

    def receive(self, *args: Any, **kwargs: Any) -> Any:
        """Delegate to underlying agent."""
        return self._agent.receive(*args, **kwargs)
