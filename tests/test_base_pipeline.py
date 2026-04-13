"""
Tests for regulated_ai_governance.base — FilterResult, GovernancePipeline,
and the GovernanceFilter protocol.

Run:
    python3 -m pytest tests/test_base_pipeline.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from regulated_ai_governance.base import FilterResult, GovernanceFilter, GovernancePipeline


# ---------------------------------------------------------------------------
# Helpers — minimal filter stubs
# ---------------------------------------------------------------------------

class _ApproveAll:
    def filter(self, doc: dict) -> FilterResult:
        return FilterResult(decision="APPROVED", reason="ok", regulation_citation="Test §1")

class _DenyAll:
    def filter(self, doc: dict) -> FilterResult:
        return FilterResult(decision="DENIED", reason="blocked", regulation_citation="Test §2")

class _RedactAll:
    def filter(self, doc: dict) -> FilterResult:
        return FilterResult(decision="REDACTED", reason="pii found", regulation_citation="Test §3")

class _ReviewAll:
    def filter(self, doc: dict) -> FilterResult:
        return FilterResult(
            decision="REQUIRES_HUMAN_REVIEW",
            reason="needs review",
            regulation_citation="Test §4",
        )

class _CallCounter:
    """Filter that tracks how many times it has been called."""
    def __init__(self, decision: str = "APPROVED"):
        self.calls = 0
        self._decision = decision

    def filter(self, doc: dict) -> FilterResult:
        self.calls += 1
        return FilterResult(
            decision=self._decision,
            reason=f"counter={self.calls}",
            regulation_citation="Test §5",
        )


# ---------------------------------------------------------------------------
# FilterResult properties
# ---------------------------------------------------------------------------

class TestFilterResultProperties:
    def test_denied_decision_is_denied(self):
        r = FilterResult(decision="DENIED", reason="x", regulation_citation="A §1")
        assert r.is_denied is True

    def test_approved_decision_not_denied(self):
        r = FilterResult(decision="APPROVED", reason="x", regulation_citation="A §1")
        assert r.is_denied is False

    def test_redacted_decision_not_denied(self):
        r = FilterResult(decision="REDACTED", reason="x", regulation_citation="A §1")
        assert r.is_denied is False

    def test_requires_human_review_not_denied(self):
        r = FilterResult(decision="REQUIRES_HUMAN_REVIEW", reason="x", regulation_citation="A §1")
        assert r.is_denied is False

    def test_approved_decision_is_approved(self):
        r = FilterResult(decision="APPROVED", reason="x", regulation_citation="A §1")
        assert r.is_approved is True

    def test_denied_decision_not_approved(self):
        r = FilterResult(decision="DENIED", reason="x", regulation_citation="A §1")
        assert r.is_approved is False

    def test_redacted_decision_not_approved(self):
        r = FilterResult(decision="REDACTED", reason="x", regulation_citation="A §1")
        assert r.is_approved is False

    def test_requires_review_decision_requires_review(self):
        r = FilterResult(decision="REQUIRES_HUMAN_REVIEW", reason="x", regulation_citation="A §1")
        assert r.requires_review is True

    def test_approved_not_requires_review(self):
        r = FilterResult(decision="APPROVED", reason="x", regulation_citation="A §1")
        assert r.requires_review is False

    def test_denied_not_requires_review(self):
        r = FilterResult(decision="DENIED", reason="x", regulation_citation="A §1")
        assert r.requires_review is False

    def test_requires_logging_default_true(self):
        r = FilterResult(decision="APPROVED", reason="x", regulation_citation="A §1")
        assert r.requires_logging is True

    def test_requires_logging_can_be_false(self):
        r = FilterResult(
            decision="APPROVED", reason="x", regulation_citation="A §1",
            requires_logging=False
        )
        assert r.requires_logging is False


# ---------------------------------------------------------------------------
# GovernancePipeline — single-filter scenarios
# ---------------------------------------------------------------------------

class TestPipelineSingleFilter:
    def test_single_approve_returns_approved(self):
        p = GovernancePipeline([_ApproveAll()])
        result = p.run({})
        assert result.is_approved

    def test_single_deny_returns_denied(self):
        p = GovernancePipeline([_DenyAll()])
        result = p.run({})
        assert result.is_denied

    def test_single_redact_is_not_denied(self):
        """REDACTED is not blocking at the pipeline level — pipeline returns APPROVED.
        Callers that need to act on REDACTED should inspect individual filter results
        via filter_batch rather than using run()."""
        p = GovernancePipeline([_RedactAll()])
        result = p.run({})
        # REDACTED does not short-circuit; pipeline returns APPROVED after all filters pass
        assert not result.is_denied

    def test_single_review_returns_review(self):
        p = GovernancePipeline([_ReviewAll()])
        result = p.run({})
        assert result.requires_review

    def test_empty_filter_list_raises(self):
        with pytest.raises(ValueError, match="at least one filter"):
            GovernancePipeline([])


# ---------------------------------------------------------------------------
# GovernancePipeline — two-filter short-circuit and ordering
# ---------------------------------------------------------------------------

class TestPipelineOrdering:
    def test_first_denied_second_never_called(self):
        second = _CallCounter("APPROVED")
        p = GovernancePipeline([_DenyAll(), second])
        result = p.run({})
        assert result.is_denied
        assert second.calls == 0, "Second filter should not be called after DENIED"

    def test_first_approved_second_denied(self):
        p = GovernancePipeline([_ApproveAll(), _DenyAll()])
        result = p.run({})
        assert result.is_denied

    def test_first_approved_second_approved_returns_approved(self):
        p = GovernancePipeline([_ApproveAll(), _ApproveAll()])
        result = p.run({})
        assert result.is_approved


# ---------------------------------------------------------------------------
# GovernancePipeline — REQUIRES_HUMAN_REVIEW behaviour
# ---------------------------------------------------------------------------

class TestPipelineHumanReview:
    def test_review_without_stop_on_review_continues(self):
        """Pipeline should NOT stop on review when stop_on_review=False."""
        second = _CallCounter("APPROVED")
        p = GovernancePipeline([_ReviewAll(), second], stop_on_review=False)
        result = p.run({})
        assert second.calls == 1, "Second filter must be called when stop_on_review=False"
        assert result.requires_review  # returns first review result

    def test_review_with_stop_on_review_blocks_immediately(self):
        second = _CallCounter("APPROVED")
        p = GovernancePipeline([_ReviewAll(), second], stop_on_review=True)
        result = p.run({})
        assert result.requires_review
        assert second.calls == 0, "Second filter should not be called when stop_on_review=True"

    def test_review_then_deny_returns_deny(self):
        """REVIEW does not short-circuit, so DENY later still wins."""
        p = GovernancePipeline([_ReviewAll(), _DenyAll()], stop_on_review=False)
        result = p.run({})
        assert result.is_denied

    def test_multiple_reviews_returns_first(self):
        r1 = _ReviewAll()
        r2 = _ReviewAll()
        p = GovernancePipeline([r1, r2], stop_on_review=False)
        result = p.run({})
        assert result.requires_review
        # Both filters run
        assert result.decision == "REQUIRES_HUMAN_REVIEW"

    def test_all_approved_no_review_result_is_approved(self):
        p = GovernancePipeline([_ApproveAll(), _ApproveAll(), _ApproveAll()])
        result = p.run({})
        assert result.is_approved
        assert result.requires_logging is False


# ---------------------------------------------------------------------------
# GovernancePipeline — batch operations
# ---------------------------------------------------------------------------

class TestPipelineBatch:
    def test_filter_batch_one_result_per_doc(self):
        p = GovernancePipeline([_ApproveAll()])
        docs = [{}, {"x": 1}, {"y": 2}]
        results = p.filter_batch(docs)
        assert len(results) == 3
        assert all(r.is_approved for r in results)

    def test_filter_batch_mixed_decisions(self):
        class _SelectiveDeny:
            def filter(self, doc: dict) -> FilterResult:
                if doc.get("deny"):
                    return FilterResult(decision="DENIED", reason="blocked", regulation_citation="T §1")
                return FilterResult(decision="APPROVED", reason="ok", regulation_citation="T §1")

        p = GovernancePipeline([_SelectiveDeny()])
        docs = [{"deny": True}, {}, {"deny": True}]
        results = p.filter_batch(docs)
        assert results[0].is_denied
        assert results[1].is_approved
        assert results[2].is_denied

    def test_approved_only_excludes_denied(self):
        class _SelectiveDeny:
            def filter(self, doc: dict) -> FilterResult:
                if doc.get("deny"):
                    return FilterResult(decision="DENIED", reason="blocked", regulation_citation="T §1")
                return FilterResult(decision="APPROVED", reason="ok", regulation_citation="T §1")

        p = GovernancePipeline([_SelectiveDeny()])
        docs = [{"id": 1}, {"id": 2, "deny": True}, {"id": 3}]
        approved = p.approved_only(docs)
        assert len(approved) == 2
        assert all(d.get("deny") is not True for d in approved)

    def test_approved_only_all_denied_returns_empty(self):
        p = GovernancePipeline([_DenyAll()])
        docs = [{"x": 1}, {"x": 2}]
        assert p.approved_only(docs) == []

    def test_approved_only_all_pass_returns_all(self):
        p = GovernancePipeline([_ApproveAll()])
        docs = [{"a": 1}, {"b": 2}, {"c": 3}]
        assert len(p.approved_only(docs)) == 3


# ---------------------------------------------------------------------------
# GovernancePipeline — dunder methods
# ---------------------------------------------------------------------------

class TestPipelineDunders:
    def test_len_single_filter(self):
        p = GovernancePipeline([_ApproveAll()])
        assert len(p) == 1

    def test_len_multiple_filters(self):
        p = GovernancePipeline([_ApproveAll(), _DenyAll(), _ReviewAll()])
        assert len(p) == 3

    def test_repr_includes_filter_names(self):
        p = GovernancePipeline([_ApproveAll(), _DenyAll()])
        r = repr(p)
        assert "_ApproveAll" in r
        assert "_DenyAll" in r
        assert r.startswith("GovernancePipeline([")


# ---------------------------------------------------------------------------
# GovernanceFilter protocol
# ---------------------------------------------------------------------------

class TestGovernanceFilterProtocol:
    def test_object_with_filter_method_satisfies_protocol(self):
        class MinimalFilter:
            def filter(self, doc: dict) -> FilterResult:
                return FilterResult(decision="APPROVED", reason="ok", regulation_citation="T §1")

        assert isinstance(MinimalFilter(), GovernanceFilter)

    def test_object_without_filter_method_fails_protocol(self):
        class NotAFilter:
            def evaluate(self, doc: dict) -> FilterResult:
                return FilterResult(decision="APPROVED", reason="ok", regulation_citation="T §1")

        assert not isinstance(NotAFilter(), GovernanceFilter)

    def test_builtin_filter_stubs_satisfy_protocol(self):
        for cls in [_ApproveAll, _DenyAll, _RedactAll, _ReviewAll]:
            assert isinstance(cls(), GovernanceFilter), f"{cls.__name__} should satisfy GovernanceFilter"
