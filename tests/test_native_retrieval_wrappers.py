"""Protect native retrieval entry points, rather than downstream document callbacks."""

import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

import pytest


@pytest.mark.parametrize("framework,distribution", [("llama", "llama-index-core"), ("haystack", "haystack-ai")])
@pytest.mark.parametrize("failure", ["deny", "audit"])
def test_native_retrieval_wrapper(framework, distribution, failure):
    try:
        version(distribution)
    except PackageNotFoundError:
        pytest.skip(f"{distribution} is not installed")
    code = """
from regulated_ai_governance.agent_guard import AuditDeliveryError
from regulated_ai_governance.policy import ActionPolicy
effects = []
def sink(record):
    if FAILURE == "audit":
        raise OSError("unavailable")
options = dict(policy=ActionPolicy(allowed_actions={"retrieve"} if FAILURE == "audit" else {"other"}),
               regulation="test", actor_id="fixture", audit_sink=sink, require_audit=True)
if FRAMEWORK == "llama":
    from llama_index.core.query_engine import CustomQueryEngine
    from regulated_ai_governance.integrations.llama_index import GovernedQueryEngine
    class Engine(CustomQueryEngine):
        def custom_query(self, query_str):
            effects.append("retrieval")
            return "done"
    protected = GovernedQueryEngine.wrap(Engine(), query_action="retrieve", **options)
    invoke = lambda: protected.query("fixture")
else:
    from haystack import Pipeline, component
    from regulated_ai_governance.integrations.haystack import GovernedHaystackComponent
    @component
    class Retriever:
        @component.output_types(documents=list)
        def run(self):
            effects.append("retrieval")
            return {"documents": []}
    pipeline = Pipeline()
    pipeline.add_component("retrieve", Retriever())
    protected = GovernedHaystackComponent(action_name="retrieve", **options)
    invoke = lambda: protected.guard_callable(pipeline.run, {})
try:
    invoke()
except (PermissionError, AuditDeliveryError):
    pass
else:
    raise AssertionError("call was not blocked")
assert effects == [], effects
""".replace("FAILURE", repr(failure)).replace("FRAMEWORK", repr(framework))
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
