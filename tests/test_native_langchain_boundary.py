"""Use a fresh interpreter so legacy SDK stubs cannot replace the real framework."""

import subprocess
import sys
import textwrap
from importlib.metadata import PackageNotFoundError, version

import pytest


@pytest.mark.parametrize(
    "scenario",
    [
        "tool_deny",
        "tool_audit",
        "retrieve_deny",
        "retrieve_audit",
        "filter",
        "empty_categories",
        "skill_deny",
    ],
)
def test_native_langchain_boundary(scenario):
    try:
        version("langchain-core")
    except PackageNotFoundError:
        pytest.skip("langchain-core is not installed")
    code = '''
import uuid
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import tool
from regulated_ai_governance.agent_guard import AuditDeliveryError
from regulated_ai_governance.integrations.langchain import FERPAComplianceCallbackHandler, GovernanceCallbackHandler
from regulated_ai_governance.policy import ActionPolicy
effects = []
scenario = SCENARIO
class Retriever(BaseRetriever):
    def _get_relevant_documents(self, query, *, run_manager):
        effects.append("retrieval")
        return [Document(page_content="a", metadata={"student_id":"a","institution_id":"x"}),
                Document(page_content="b", metadata={"student_id":"b","institution_id":"x"})]
@tool
def write() -> str:
    """A synthetic side effect."""
    effects.append("tool")
    return "done"
def sink(record):
    if scenario.endswith("audit"):
        raise OSError("unavailable")
handler = GovernanceCallbackHandler(
    ActionPolicy(allowed_actions={"other"} if scenario.endswith("deny") else {"retrieval", "write"}),
    audit_sink=sink, **({"require_audit": True} if scenario.endswith("audit") else {}),
)
if scenario in ("filter", "empty_categories"):
    filter_handler = FERPAComplianceCallbackHandler(
        "a", "x", allowed_categories=set() if scenario == "empty_categories" else None,
    )
    result = Retriever().invoke("fixture", config={"callbacks":[filter_handler]})
    expected = [] if scenario == "empty_categories" else ["a"]
    assert [doc.page_content for doc in result] == expected
else:
    if scenario == "skill_deny":
        from regulated_ai_governance.skill import GovernanceAuditSkill
        skill = GovernanceAuditSkill.for_education(actor_id="fixture", allowed_actions={"other"})
        handler = skill.as_langchain_handler()
    try:
        if scenario.startswith("tool"):
            write.invoke({}, config={"callbacks":[handler]})
        else:
            Retriever().invoke("fixture", config={"callbacks":[handler]})
    except (PermissionError, AuditDeliveryError):
        pass
    else:
        raise AssertionError("denial did not propagate")
    assert effects == [], effects
'''
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code).replace("SCENARIO", repr(scenario))],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
