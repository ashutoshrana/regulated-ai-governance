"""
Tests for regulated_ai_governance.integrations.langchain:
  - FERPAComplianceCallbackHandler (retrieval filter)
  - GovernanceCallbackHandler (tool policy enforcement)

Uses sys.modules mocking to satisfy the langchain-core hard import at module
load time — no actual SDK install required.
"""

from __future__ import annotations

import sys
import types
import uuid
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Mock langchain_core before the module under test is imported.
# We do this at module level so the import at the top of langchain.py works.
# ---------------------------------------------------------------------------


def _install_langchain_core_mock() -> None:
    """Inject minimal langchain_core stubs into sys.modules."""
    if "langchain_core" in sys.modules:
        return  # already loaded (real or mock)

    # Build stub modules
    langchain_core = types.ModuleType("langchain_core")
    langchain_core_callbacks = types.ModuleType("langchain_core.callbacks")
    langchain_core_documents = types.ModuleType("langchain_core.documents")

    # BaseCallbackHandler stub
    class BaseCallbackHandler:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    # Document stub
    class Document:
        def __init__(self, page_content: str = "", metadata: dict | None = None) -> None:
            self.page_content = page_content
            self.metadata = metadata or {}

    langchain_core_callbacks.BaseCallbackHandler = BaseCallbackHandler  # type: ignore[attr-defined]
    langchain_core_documents.Document = Document  # type: ignore[attr-defined]

    sys.modules["langchain_core"] = langchain_core
    sys.modules["langchain_core.callbacks"] = langchain_core_callbacks
    sys.modules["langchain_core.documents"] = langchain_core_documents
    langchain_core.callbacks = langchain_core_callbacks  # type: ignore[attr-defined]
    langchain_core.documents = langchain_core_documents  # type: ignore[attr-defined]


_install_langchain_core_mock()

# Now import the module under test (langchain_core stubs are in sys.modules)
from regulated_ai_governance.audit import GovernanceAuditRecord  # noqa: E402
from regulated_ai_governance.integrations.langchain import (  # noqa: E402
    FERPAComplianceCallbackHandler,
    GovernanceCallbackHandler,
)
from regulated_ai_governance.policy import ActionPolicy, EscalationRule  # noqa: E402

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _FakeDocument:
    """Duck-typed Document stub with .metadata dict."""

    def __init__(self, content: str, metadata: dict[str, Any]) -> None:
        self.page_content = content
        self.metadata = metadata


def _run_id() -> uuid.UUID:
    return uuid.uuid4()


# ---------------------------------------------------------------------------
# FERPAComplianceCallbackHandler Tests
# ---------------------------------------------------------------------------


class TestFERPAComplianceCallbackHandler:
    """Tests for the retrieval identity-scope filter."""

    def _make_handler(
        self,
        student_id: str = "stu_alice",
        institution_id: str = "univ_east",
        allowed_categories: set[str] | None = None,
        audit_sink: Any = None,
        raise_on_empty: bool = False,
    ) -> FERPAComplianceCallbackHandler:
        return FERPAComplianceCallbackHandler(
            student_id=student_id,
            institution_id=institution_id,
            allowed_categories=allowed_categories,
            audit_sink=audit_sink,
            raise_on_empty=raise_on_empty,
        )

    def test_allows_authorized_document(self) -> None:
        handler = self._make_handler()
        docs = [
            _FakeDocument(
                "Transcript", {"student_id": "stu_alice", "institution_id": "univ_east", "category": "academic_record"}
            )
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1

    def test_blocks_cross_student(self) -> None:
        handler = self._make_handler(student_id="stu_alice")
        docs = [
            _FakeDocument("Alice", {"student_id": "stu_alice", "institution_id": "univ_east"}),
            _FakeDocument("Bob", {"student_id": "stu_bob", "institution_id": "univ_east"}),
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1
        assert result[0].metadata["student_id"] == "stu_alice"

    def test_blocks_cross_institution(self) -> None:
        handler = self._make_handler(institution_id="univ_east")
        docs = [
            _FakeDocument("Alice at East", {"student_id": "stu_alice", "institution_id": "univ_east"}),
            _FakeDocument("Alice at West", {"student_id": "stu_alice", "institution_id": "univ_west"}),
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1
        assert result[0].metadata["institution_id"] == "univ_east"

    def test_category_filter_blocks_unauthorized(self) -> None:
        handler = self._make_handler(allowed_categories={"academic_record"})
        docs = [
            _FakeDocument(
                "Transcript", {"student_id": "stu_alice", "institution_id": "univ_east", "category": "academic_record"}
            ),
            _FakeDocument(
                "Health", {"student_id": "stu_alice", "institution_id": "univ_east", "category": "health_record"}
            ),
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1
        assert result[0].metadata["category"] == "academic_record"

    def test_no_category_filter_when_none(self) -> None:
        handler = self._make_handler(allowed_categories=None)
        docs = [
            _FakeDocument(
                "Health", {"student_id": "stu_alice", "institution_id": "univ_east", "category": "health_record"}
            ),
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1

    def test_document_without_identity_fields_is_filtered(self) -> None:
        """
        Documents without student/institution fields are filtered out.

        Note: This implementation requires an exact student_id + institution_id
        match. Documents with no identity metadata do not pass through — they
        are treated as unidentified records, not as shared KB content.
        For shared-KB pass-through behavior, use the enterprise-rag-patterns
        FERPAHaystackFilter which has explicit shared-KB logic.
        """
        handler = self._make_handler()
        docs = [_FakeDocument("General FAQ", {})]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        # No identity fields → identity filter blocks (None != "stu_alice")
        assert len(result) == 0

    def test_empty_input_returns_empty(self) -> None:
        handler = self._make_handler()
        result = handler.on_retriever_end([], run_id=_run_id())
        assert result == []

    def test_raise_on_empty_raises_permission_error(self) -> None:
        handler = self._make_handler(raise_on_empty=True)
        docs = [_FakeDocument("Bob", {"student_id": "stu_bob", "institution_id": "univ_east"})]
        with pytest.raises(PermissionError, match="stu_alice"):
            handler.on_retriever_end(docs, run_id=_run_id())

    def test_raise_on_empty_false_does_not_raise(self) -> None:
        handler = self._make_handler(raise_on_empty=False)
        docs = [_FakeDocument("Bob", {"student_id": "stu_bob", "institution_id": "univ_east"})]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert result == []

    def test_audit_sink_called_on_retrieval(self) -> None:
        audit_log: list[GovernanceAuditRecord] = []
        handler = self._make_handler(audit_sink=audit_log.append)
        docs = [_FakeDocument("Transcript", {"student_id": "stu_alice", "institution_id": "univ_east"})]
        handler.on_retriever_end(docs, run_id=_run_id())
        assert len(audit_log) == 1
        record = audit_log[0]
        assert record.regulation == "FERPA"
        assert record.action_name == "retrieval"
        assert record.permitted is True

    def test_audit_sink_not_called_when_none(self) -> None:
        """No error when audit_sink is None."""
        handler = self._make_handler(audit_sink=None)
        docs = [_FakeDocument("Transcript", {"student_id": "stu_alice", "institution_id": "univ_east"})]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1

    def test_audit_record_contains_document_counts(self) -> None:
        audit_log: list[GovernanceAuditRecord] = []
        handler = self._make_handler(
            allowed_categories={"academic_record"},
            audit_sink=audit_log.append,
        )
        docs = [
            _FakeDocument(
                "T", {"student_id": "stu_alice", "institution_id": "univ_east", "category": "academic_record"}
            ),
            _FakeDocument("B", {"student_id": "stu_bob", "institution_id": "univ_east", "category": "academic_record"}),
            _FakeDocument("H", {"student_id": "stu_alice", "institution_id": "univ_east", "category": "health_record"}),
        ]
        handler.on_retriever_end(docs, run_id=_run_id())
        ctx = audit_log[0].context
        assert ctx["documents_in_store"] == 3
        assert ctx["after_identity_filter"] == 2  # alice's docs
        assert ctx["after_category_filter"] == 1  # only academic_record

    def test_custom_field_names(self) -> None:
        handler = FERPAComplianceCallbackHandler(
            student_id="stu_alice",
            institution_id="univ_east",
            student_id_field="learner_id",
            institution_id_field="school_id",
        )
        docs = [
            _FakeDocument("Alice", {"learner_id": "stu_alice", "school_id": "univ_east"}),
            _FakeDocument("Bob", {"learner_id": "stu_bob", "school_id": "univ_east"}),
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert len(result) == 1
        assert result[0].metadata["learner_id"] == "stu_alice"

    def test_mixed_batch_all_filtered(self) -> None:
        handler = self._make_handler(raise_on_empty=False)
        docs = [
            _FakeDocument("Bob", {"student_id": "stu_bob", "institution_id": "univ_east"}),
            _FakeDocument("Cross-inst", {"student_id": "stu_alice", "institution_id": "univ_west"}),
        ]
        result = handler.on_retriever_end(docs, run_id=_run_id())
        assert result == []

    def test_parent_run_id_in_audit_context(self) -> None:
        audit_log: list[GovernanceAuditRecord] = []
        handler = self._make_handler(audit_sink=audit_log.append)
        parent = _run_id()
        docs = [_FakeDocument("T", {"student_id": "stu_alice", "institution_id": "univ_east"})]
        handler.on_retriever_end(docs, run_id=_run_id(), parent_run_id=parent)
        assert audit_log[0].context["parent_run_id"] == str(parent)


# ---------------------------------------------------------------------------
# GovernanceCallbackHandler Tests
# ---------------------------------------------------------------------------


class TestGovernanceCallbackHandler:
    """Tests for the tool-level ActionPolicy enforcement handler."""

    def _make_handler(
        self,
        allowed_actions: set[str] | None = None,
        denied_actions: set[str] | None = None,
        regulation: str = "FERPA",
        actor_id: str = "stu_alice",
        audit_sink: Any = None,
        block_on_escalation: bool = True,
        escalation_rules: list | None = None,
    ) -> GovernanceCallbackHandler:
        policy = ActionPolicy(
            allowed_actions=allowed_actions or {"search_catalog", "read_transcript"},
            denied_actions=denied_actions or set(),
            escalation_rules=escalation_rules or [],
        )
        return GovernanceCallbackHandler(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink,
            block_on_escalation=block_on_escalation,
        )

    def _serialized(self, name: str) -> dict[str, Any]:
        return {"name": name, "description": f"Tool: {name}"}

    def test_permitted_tool_does_not_raise(self) -> None:
        handler = self._make_handler(allowed_actions={"search_catalog"})
        # Should not raise
        handler.on_tool_start(self._serialized("search_catalog"), "query", run_id=_run_id())

    def test_denied_tool_raises_permission_error(self) -> None:
        handler = self._make_handler(allowed_actions={"search_catalog"})
        with pytest.raises(PermissionError, match="export_records"):
            handler.on_tool_start(self._serialized("export_records"), "args", run_id=_run_id())

    def test_explicitly_denied_tool_raises(self) -> None:
        handler = self._make_handler(
            allowed_actions={"search_catalog", "delete_record"},
            denied_actions={"delete_record"},
        )
        with pytest.raises(PermissionError, match="delete_record"):
            handler.on_tool_start(self._serialized("delete_record"), "id=123", run_id=_run_id())

    def test_error_message_contains_actor_and_regulation(self) -> None:
        handler = self._make_handler(
            allowed_actions={"safe_tool"},
            regulation="HIPAA",
            actor_id="nurse_101",
        )
        with pytest.raises(PermissionError) as exc_info:
            handler.on_tool_start(self._serialized("dangerous_tool"), "", run_id=_run_id())
        msg = str(exc_info.value)
        assert "nurse_101" in msg
        assert "HIPAA" in msg
        assert "dangerous_tool" in msg

    def test_regulation_and_actor_stored_on_handler(self) -> None:
        handler = self._make_handler(regulation="GLBA", actor_id="advisor_007")
        assert handler.regulation == "GLBA"
        assert handler.actor_id == "advisor_007"

    def test_unknown_tool_denied_when_require_all_allowed(self) -> None:
        handler = self._make_handler(allowed_actions={"known_tool"})
        with pytest.raises(PermissionError, match="unknown_action"):
            handler.on_tool_start(self._serialized("unknown_action"), "", run_id=_run_id())

    def test_on_tool_end_does_not_raise(self) -> None:
        handler = self._make_handler()
        handler.on_tool_end("result text", run_id=_run_id())

    def test_on_tool_error_does_not_raise(self) -> None:
        handler = self._make_handler()
        handler.on_tool_error(RuntimeError("tool failed"), run_id=_run_id())

    def test_custom_tool_name_field(self) -> None:
        policy = ActionPolicy(allowed_actions={"search_catalog"})
        handler = GovernanceCallbackHandler(
            policy=policy,
            tool_name_field="tool_name",
        )
        # Using custom field name — should work
        handler.on_tool_start({"tool_name": "search_catalog", "description": "..."}, "", run_id=_run_id())

    def test_missing_tool_name_falls_back_to_unknown(self) -> None:
        """When serialized dict has no name field, 'unknown_tool' is used."""
        policy = ActionPolicy(allowed_actions={"search_catalog"})
        handler = GovernanceCallbackHandler(policy=policy)
        with pytest.raises(PermissionError, match="unknown_tool"):
            handler.on_tool_start({}, "", run_id=_run_id())

    def test_audit_sink_called_for_permitted_tool(self) -> None:
        audit_log: list[GovernanceAuditRecord] = []
        handler = self._make_handler(
            allowed_actions={"search_catalog"},
            audit_sink=audit_log.append,
        )
        handler.on_tool_start(self._serialized("search_catalog"), "q", run_id=_run_id())
        assert len(audit_log) == 1
        assert audit_log[0].permitted is True

    def test_audit_sink_called_for_denied_tool(self) -> None:
        audit_log: list[GovernanceAuditRecord] = []
        handler = self._make_handler(
            allowed_actions={"safe"},
            audit_sink=audit_log.append,
        )
        with pytest.raises(PermissionError):
            handler.on_tool_start(self._serialized("dangerous"), "arg", run_id=_run_id())
        assert len(audit_log) == 1
        assert audit_log[0].permitted is False
        assert audit_log[0].action_name == "dangerous"

    def test_audit_sink_not_called_when_none(self) -> None:
        """No error when audit_sink is None."""
        handler = self._make_handler(allowed_actions={"safe"}, audit_sink=None)
        handler.on_tool_start(self._serialized("safe"), "", run_id=_run_id())

    def test_escalated_tool_blocked_when_block_on_escalation_true(self) -> None:
        rule = EscalationRule(
            condition="export_attempt",
            action_pattern="export",
            escalate_to="compliance_officer",
        )
        handler = self._make_handler(
            allowed_actions={"export_report"},
            escalation_rules=[rule],
            block_on_escalation=True,
        )
        with pytest.raises(PermissionError):
            handler.on_tool_start(self._serialized("export_report"), "", run_id=_run_id())

    def test_multiple_tools_independent_decisions(self) -> None:
        handler = self._make_handler(allowed_actions={"tool_a", "tool_b"})
        # Both should succeed
        handler.on_tool_start(self._serialized("tool_a"), "", run_id=_run_id())
        handler.on_tool_start(self._serialized("tool_b"), "", run_id=_run_id())
        # Third should fail
        with pytest.raises(PermissionError):
            handler.on_tool_start(self._serialized("tool_c"), "", run_id=_run_id())

    def test_multiple_permitted_calls_accumulate_audit_records(self) -> None:
        audit_log: list[GovernanceAuditRecord] = []
        handler = self._make_handler(
            allowed_actions={"tool_a", "tool_b"},
            audit_sink=audit_log.append,
        )
        handler.on_tool_start(self._serialized("tool_a"), "", run_id=_run_id())
        handler.on_tool_start(self._serialized("tool_b"), "", run_id=_run_id())
        assert len(audit_log) == 2
        assert {r.action_name for r in audit_log} == {"tool_a", "tool_b"}
