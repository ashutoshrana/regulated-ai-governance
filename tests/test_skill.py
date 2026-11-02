"""Tests for GovernanceAuditSkill — factory constructors, audit_action, audit_retrieval."""

from __future__ import annotations

import pytest

from regulated_ai_governance import (
    ActionPolicy,
    ComprehensiveAuditReport,
    FrameworkConfig,
    GovernanceAuditSkill,
    GovernanceConfig,
    GovernedActionGuard,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _education_skill(
    allowed: set[str] | None = None,
    audit_only: bool = False,
) -> GovernanceAuditSkill:
    return GovernanceAuditSkill.for_education(
        actor_id="advisor_007",
        allowed_actions=allowed,
        audit_only=audit_only,
    )


def _make_docs(n: int = 3) -> list[dict]:
    return [{"doc_id": f"doc_{i}", "content": f"content {i}"} for i in range(n)]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestGovernanceAuditSkillConstruction:
    def test_for_education_creates_skill(self):
        skill = GovernanceAuditSkill.for_education(actor_id="adv_001")
        assert skill is not None
        assert "FERPA" in skill.active_frameworks

    def test_for_healthcare_creates_skill(self):
        skill = GovernanceAuditSkill.for_healthcare(actor_id="nurse_001")
        assert skill is not None
        assert "HIPAA" in skill.active_frameworks

    def test_for_enterprise_creates_skill(self):
        skill = GovernanceAuditSkill.for_enterprise(
            actor_id="agent_001",
            regulations=["FERPA", "HIPAA"],
        )
        assert "FERPA" in skill.active_frameworks
        assert "HIPAA" in skill.active_frameworks

    def test_for_enterprise_configured_vs_active(self):
        skill = GovernanceAuditSkill.for_enterprise(
            actor_id="agent_001",
            regulations=["FERPA"],
        )
        # configured_frameworks includes all possible frameworks
        assert "FERPA" in skill.configured_frameworks
        # active_frameworks only includes enabled ones
        assert "FERPA" in skill.active_frameworks

    def test_direct_construction(self):
        skill = GovernanceAuditSkill(
            config=GovernanceConfig(
                frameworks=[
                    FrameworkConfig(
                        regulation="FERPA",
                        guard=GovernedActionGuard(
                            policy=ActionPolicy(allowed_actions={"read"}),
                            regulation="FERPA",
                            actor_id="actor",
                        ),
                    )
                ]
            )
        )
        assert "FERPA" in skill.active_frameworks

    def test_audit_only_property(self):
        skill = GovernanceAuditSkill.for_education(actor_id="x", audit_only=True)
        assert skill.audit_only is True

    def test_audit_only_default_false(self):
        skill = GovernanceAuditSkill.for_education(actor_id="x")
        assert skill.audit_only is False


# ---------------------------------------------------------------------------
# audit_action()
# ---------------------------------------------------------------------------


class TestAuditAction:
    def test_permitted_action_returns_fn_result(self):
        skill = _education_skill(allowed={"read_transcript"})
        result = skill.audit_action(
            action_name="read_transcript",
            execute_fn=lambda: {"gpa": 3.9},
            actor_id="advisor_007",
        )
        assert result == {"gpa": 3.9}

    def test_denied_action_returns_blocked_message(self):
        skill = _education_skill(allowed={"read_transcript"})
        result = skill.audit_action(
            action_name="delete_student_record",
            execute_fn=lambda: "DELETED",
            actor_id="advisor_007",
        )
        assert isinstance(result, str)
        assert "BLOCKED" in result or "blocked" in result.lower()

    def test_denied_action_names_framework(self):
        skill = _education_skill(allowed={"read_transcript"})
        result = skill.audit_action(
            action_name="delete_student_record",
            execute_fn=lambda: "DELETED",
            actor_id="advisor_007",
        )
        assert "FERPA" in result

    def test_audit_sink_receives_report(self):
        log: list[ComprehensiveAuditReport] = []
        skill = GovernanceAuditSkill.for_education(
            actor_id="adv_001",
            allowed_actions={"read"},
            audit_sink=log.append,
        )
        skill.audit_action("read", execute_fn=lambda: "data")
        assert len(log) == 1
        assert log[0].action_name == "read"

    def test_last_report_updated(self):
        skill = _education_skill(allowed={"read_transcript"})
        assert skill.last_report is None
        skill.audit_action("read_transcript", execute_fn=lambda: None)
        assert skill.last_report is not None
        assert skill.last_report.action_name == "read_transcript"

    def test_audit_only_permits_denied_action(self):
        skill = _education_skill(allowed=set(), audit_only=True)
        result = skill.audit_action(
            action_name="forbidden_action",
            execute_fn=lambda: "EXECUTED",
        )
        assert result == "EXECUTED"

    def test_audit_only_report_flags_mode(self):
        log: list[ComprehensiveAuditReport] = []
        skill = GovernanceAuditSkill.for_education(
            actor_id="x",
            allowed_actions=set(),
            audit_only=True,
            audit_sink=log.append,
        )
        skill.audit_action("forbidden", execute_fn=lambda: None)
        assert log[0].audit_only_mode is True

    def test_frameworks_scoping_restricts_evaluation(self):
        """Per-call framework scoping: only evaluate specified frameworks."""
        log: list[ComprehensiveAuditReport] = []
        skill = GovernanceAuditSkill.for_enterprise(
            actor_id="agent_001",
            allowed_actions={"read_document"},
            regulations=["FERPA", "HIPAA"],
            audit_sink=log.append,
        )

        skill.audit_action(
            action_name="read_document",
            execute_fn=lambda: "data",
            frameworks=["FERPA"],  # only FERPA
        )
        assert len(log) == 1
        report = log[0]
        # HIPAA should be skipped — only FERPA evaluated for this call
        assert "FERPA" in (report.frameworks_evaluated or report.frameworks_permitted)

    def test_context_forwarded_to_report(self):
        log: list[ComprehensiveAuditReport] = []
        skill = GovernanceAuditSkill.for_education(
            actor_id="adv_001",
            allowed_actions={"read"},
            audit_sink=log.append,
        )
        skill.audit_action("read", execute_fn=lambda: None, context={"session": "s_123"})
        assert log[0].context.get("session") == "s_123"


# ---------------------------------------------------------------------------
# audit_retrieval()
# ---------------------------------------------------------------------------


class TestAuditRetrieval:
    def test_returns_all_docs_when_permitted(self):
        skill = GovernanceAuditSkill.for_healthcare(
            actor_id="nurse_001",
            allowed_actions={"document_retrieval"},
        )
        docs = _make_docs(4)
        returned, report = skill.audit_retrieval(docs, actor_id="nurse_001")
        assert len(returned) == 4

    def test_returns_empty_when_denied(self):
        skill = GovernanceAuditSkill.for_education(
            actor_id="adv_001",
            allowed_actions=set(),  # deny everything
        )
        docs = _make_docs(3)
        returned, report = skill.audit_retrieval(docs, actor_id="adv_001")
        assert len(returned) == 0

    def test_returns_report_object(self):
        skill = GovernanceAuditSkill.for_healthcare(
            actor_id="nurse_001",
            allowed_actions={"document_retrieval"},
        )
        docs = _make_docs(2)
        _, report = skill.audit_retrieval(docs, actor_id="nurse_001")
        assert isinstance(report, ComprehensiveAuditReport)
        assert report.action_name == "document_retrieval"

    def test_audit_sink_receives_report(self):
        log: list[ComprehensiveAuditReport] = []
        skill = GovernanceAuditSkill.for_healthcare(
            actor_id="nurse_001",
            allowed_actions={"document_retrieval"},
            audit_sink=log.append,
        )
        skill.audit_retrieval(_make_docs(2), actor_id="nurse_001")
        assert len(log) == 1

    def test_audit_only_returns_docs_even_when_denied(self):
        skill = GovernanceAuditSkill.for_education(
            actor_id="x",
            allowed_actions=set(),
            audit_only=True,
        )
        docs = _make_docs(3)
        returned, report = skill.audit_retrieval(docs)
        assert len(returned) == 3

    def test_context_document_count_in_report(self):
        log: list[ComprehensiveAuditReport] = []
        skill = GovernanceAuditSkill.for_healthcare(
            actor_id="nurse_001",
            allowed_actions={"document_retrieval"},
            audit_sink=log.append,
        )
        docs = _make_docs(5)
        skill.audit_retrieval(docs, actor_id="nurse_001")
        ctx = log[0].context
        assert ctx.get("retrieval_document_count") == 5 or ctx.get("documents_input") == 5

    def test_empty_doc_list_still_produces_report(self):
        skill = GovernanceAuditSkill.for_healthcare(
            actor_id="nurse_001",
            allowed_actions={"document_retrieval"},
        )
        returned, report = skill.audit_retrieval([], actor_id="nurse_001")
        assert returned == []
        assert report is not None


# ---------------------------------------------------------------------------
# Channel adapter ImportError behaviour
# ---------------------------------------------------------------------------


class TestChannelAdapters:
    def test_langchain_handler_raises_import_error(self, monkeypatch):
        """An installed SDK must also be hidden explicitly, not just evicted."""
        import sys

        monkeypatch.setitem(sys.modules, "langchain_core.callbacks", None)
        with pytest.raises(ImportError, match="langchain"):
            _education_skill().as_langchain_handler()

    @pytest.mark.parametrize(
        "module,factory",
        [
            ("crewai.tools", lambda skill: skill.as_crewai_tool("read", lambda: None)),
            ("llama_index.core.postprocessor.types", lambda skill: skill.as_llama_index_postprocessor()),
            ("haystack", lambda skill: skill.as_haystack_component()),
            ("agent_framework", lambda skill: skill.as_maf_middleware()),
        ],
    )
    def test_missing_optional_sdk(self, monkeypatch, module, factory):
        import sys

        monkeypatch.setitem(sys.modules, module, None)
        with pytest.raises(ImportError):
            factory(_education_skill())


@pytest.mark.parametrize(
    "framework,distribution",
    [
        ("crewai", "crewai"),
        ("llama", "llama-index-core"),
        ("haystack", "haystack-ai"),
        ("maf", "agent-framework-core"),
        ("maf_policy", "agent-framework-core"),
    ],
)
@pytest.mark.parametrize("mode", ["allow", "deny", "audit_only", "sink_failure"])
def test_native_skill_factory(framework, distribution, mode, tmp_path):
    """Native SDK execution runs outside the legacy suite's global SDK stubs."""
    import os
    import subprocess
    import sys
    from importlib.metadata import PackageNotFoundError, version

    if framework == "maf_policy" and mode == "audit_only":
        pytest.skip("The single-policy adapter has no skill audit-only mode")
    try:
        version(distribution)
    except PackageNotFoundError:
        pytest.skip(f"{distribution} is not installed")
    code = '''
import asyncio
from regulated_ai_governance.skill import GovernanceAuditSkill
framework = FRAMEWORK
mode = MODE
effects = []
records = []
def sink(record):
    records.append(record)
    if mode == "sink_failure":
        raise OSError("audit unavailable")
action = "write" if framework in ("crewai", "maf", "maf_policy") else "document_retrieval"
skill = GovernanceAuditSkill.for_education(
    actor_id="fixture", allowed_actions={"other"} if mode in ("deny", "audit_only") else {action},
    audit_only=mode == "audit_only", audit_sink=sink,
)
if framework == "crewai":
    import appdirs
    import os
    # CrewAI initializes credential storage during import; keep test writes temporary.
    appdirs.user_data_dir = lambda *args, **kwargs: os.environ["CREWAI_STORAGE_DIR"]
    from pathlib import Path
    from crewai_core.token_manager import TokenManager
    storage = Path(os.environ["CREWAI_STORAGE_DIR"])
    storage.mkdir(parents=True, exist_ok=True)
    TokenManager._get_secure_storage_path = staticmethod(lambda: storage)
    from crewai.tools import BaseTool
    def write(value: str) -> str:
        """Write a synthetic value."""
        effects.append(value)
        return value
    tool = skill.as_crewai_tool("write", write, tool_name="record", tool_description="Synthetic fixture")
    assert isinstance(tool, BaseTool)
    assert tool.name == "record"
    invoke = lambda: tool.run(value="done")
elif framework == "llama":
    from llama_index.core.schema import NodeWithScore, TextNode
    from llama_index.core.postprocessor.types import BaseNodePostprocessor
    processor = skill.as_llama_index_postprocessor(actor_id="fixture")
    assert isinstance(processor, BaseNodePostprocessor)
    nodes = [NodeWithScore(node=TextNode(text="fixture"))]
    invoke = lambda: processor.postprocess_nodes(nodes, query_str="fixture")
elif framework == "haystack":
    from haystack import Pipeline, Document
    pipeline = Pipeline()
    pipeline.add_component("governance", skill.as_haystack_component(actor_id="fixture"))
    documents = [Document(content="fixture")]
    invoke = lambda: pipeline.run({"governance": {"documents": documents}})["governance"]["documents"]
else:
    from agent_framework import FunctionMiddleware, FunctionInvocationContext, tool
    if framework == "maf_policy":
        from regulated_ai_governance.integrations.maf import PolicyMiddleware
        from regulated_ai_governance.policy import ActionPolicy
        middleware = PolicyMiddleware(
            policy=ActionPolicy(allowed_actions={"other"} if mode == "deny" else {"write"}),
            audit_sink=sink, require_audit=True,
        ).as_native()
    else:
        middleware = skill.as_maf_middleware(actor_id="fixture")
    assert isinstance(middleware, FunctionMiddleware)
    @tool
    def write(value: str) -> str:
        """Write a synthetic value."""
        effects.append(value)
        return value
    context = FunctionInvocationContext(function=write, arguments={"value":"done"})
    async def invoke_middleware():
        async def call_next():
            context.result = await write.invoke(arguments=context.arguments)
        await middleware.process(context, call_next)
        return context.result
    invoke = lambda: asyncio.run(invoke_middleware())
try:
    result = invoke()
except Exception as exc:
    assert mode == "sink_failure" or (mode == "deny" and framework in ("maf", "maf_policy")), repr(exc)
else:
    assert mode != "sink_failure"
    if framework in ("llama", "haystack"):
        assert len(result) == (0 if mode == "deny" else 1)
assert effects == ([] if framework in ("llama", "haystack") or mode in ("deny", "sink_failure") else ["done"])
assert len(records) == 1
assert records[0].action_name == action
'''
    code = code.replace("FRAMEWORK", repr(framework)).replace("MODE", repr(mode))
    env = dict(
        os.environ,
        CREWAI_STORAGE_DIR=str(tmp_path),
        CREWAI_TELEMETRY_OPTOUT="true",
        OTEL_SDK_DISABLED="true",
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Framework scoping context manager (_framework_scope)
# ---------------------------------------------------------------------------


class TestFrameworkScope:
    def test_scoping_restores_after_exit(self):
        """After the context manager exits, disabled frameworks are re-enabled."""
        skill = GovernanceAuditSkill.for_enterprise(
            actor_id="agent_001",
            allowed_actions={"read"},
            regulations=["FERPA", "HIPAA"],
        )
        # Both active before scope
        assert "FERPA" in skill.active_frameworks
        assert "HIPAA" in skill.active_frameworks

        with skill._framework_scope(skill, ["FERPA"]):
            # Inside scope: only FERPA active
            assert "FERPA" in skill.active_frameworks
            assert "HIPAA" not in skill.active_frameworks

        # After scope: both restored
        assert "FERPA" in skill.active_frameworks
        assert "HIPAA" in skill.active_frameworks

    def test_none_frameworks_is_noop(self):
        """Passing frameworks=None to scope leaves all frameworks active."""
        skill = _education_skill()
        active_before = set(skill.active_frameworks)
        with skill._framework_scope(skill, None):
            assert set(skill.active_frameworks) == active_before
        assert set(skill.active_frameworks) == active_before
