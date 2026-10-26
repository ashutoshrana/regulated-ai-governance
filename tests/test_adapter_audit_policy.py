"""Adapter configuration must preserve mandatory audit and pre-action enforcement."""

import pytest

from regulated_ai_governance.agent_guard import AuditDeliveryError
from regulated_ai_governance.integrations.autogen import GovernedAutoGenAgent
from regulated_ai_governance.integrations.haystack import GovernedHaystackComponent
from regulated_ai_governance.integrations.llama_index import GovernedQueryEngine
from regulated_ai_governance.integrations.semantic_kernel import GovernedKernelPlugin
from regulated_ai_governance.policy import ActionPolicy


@pytest.mark.parametrize(
    "factory",
    [
        lambda **kw: GovernedAutoGenAgent.wrap(agent=object(), **kw),
        lambda **kw: GovernedQueryEngine.wrap(engine=object(), **kw),
        lambda **kw: GovernedKernelPlugin.from_object(plugin_name="fixture", target=object(), **kw),
        lambda **kw: GovernedHaystackComponent(action_name="retrieve", **kw),
    ],
)
def test_adapter_rejects_required_audit_without_sink(factory):
    with pytest.raises(ValueError, match="audit_sink"):
        factory(policy=ActionPolicy(), regulation="test", actor_id="fixture", require_audit=True)


@pytest.mark.parametrize("failure", ["denied", "audit"])
def test_query_engine_does_not_retrieve_before_policy_and_audit(failure):
    effects = []

    class Engine:
        def query(self, query):
            effects.append(query)

    def sink(record):
        if failure == "audit":
            raise OSError("audit unavailable")

    engine = GovernedQueryEngine.wrap(
        Engine(),
        policy=ActionPolicy(allowed_actions={"other"} if failure == "denied" else {"llama_index_query"}),
        regulation="test",
        actor_id="fixture",
        audit_sink=sink,
        require_audit=True,
    )
    with pytest.raises(PermissionError if failure == "denied" else AuditDeliveryError):
        engine.query("fixture")
    assert effects == []
