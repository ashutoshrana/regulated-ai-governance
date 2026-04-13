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
    def test_langchain_handler_raises_import_error(self):
        """as_langchain_handler() raises ImportError if langchain not installed."""
        import sys
        # Temporarily hide langchain modules
        saved = {}
        for mod in list(sys.modules):
            if "langchain" in mod:
                saved[mod] = sys.modules.pop(mod)
        try:
            skill = _education_skill()
            with pytest.raises(ImportError, match="langchain"):
                skill.as_langchain_handler()
        finally:
            sys.modules.update(saved)

    def test_crewai_tool_raises_import_error(self):
        import sys
        saved = {}
        for mod in list(sys.modules):
            if "crewai" in mod:
                saved[mod] = sys.modules.pop(mod)
        try:
            skill = _education_skill()
            with pytest.raises(ImportError, match="crewai"):
                skill.as_crewai_tool("read", execute_fn=lambda: None)
        finally:
            sys.modules.update(saved)

    def test_llama_index_raises_import_error(self):
        import sys
        saved = {}
        for mod in list(sys.modules):
            if "llama" in mod:
                saved[mod] = sys.modules.pop(mod)
        try:
            skill = _education_skill()
            with pytest.raises(ImportError, match="llama"):
                skill.as_llama_index_postprocessor()
        finally:
            sys.modules.update(saved)

    def test_haystack_raises_import_error(self):
        import sys
        saved = {}
        for mod in list(sys.modules):
            if "haystack" in mod:
                saved[mod] = sys.modules.pop(mod)
        try:
            skill = _education_skill()
            with pytest.raises(ImportError, match="haystack"):
                skill.as_haystack_component()
        finally:
            sys.modules.update(saved)


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
