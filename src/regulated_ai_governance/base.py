"""
Base types and pipeline for regulated-ai-governance.

Provides the GovernanceFilter protocol, FilterResult dataclass, and
GovernancePipeline for chaining multiple governance filters.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import logging

logger = logging.getLogger(__name__)


@dataclass
class FilterResult:
    """
    Standard result returned by every governance filter.

    decision values:
      APPROVED               — document/action may proceed
      DENIED                 — document/action blocked; log and halt
      REDACTED               — content must be redacted before proceeding
      REQUIRES_HUMAN_REVIEW  — escalate to human reviewer; do not auto-proceed

    regulation_citation should follow the pattern:
      "Regulation Name Article/Section — plain-English description"
    """
    decision: str
    reason: str
    regulation_citation: str
    requires_logging: bool = True

    @property
    def is_denied(self) -> bool:
        """True only for DENIED — not for REDACTED or REQUIRES_HUMAN_REVIEW."""
        return self.decision == "DENIED"

    @property
    def is_approved(self) -> bool:
        return self.decision == "APPROVED"

    @property
    def requires_review(self) -> bool:
        return self.decision == "REQUIRES_HUMAN_REVIEW"


@runtime_checkable
class GovernanceFilter(Protocol):
    """
    Protocol that all governance filter classes satisfy.

    Any class with a `filter(doc: dict) -> FilterResult` method is a valid
    GovernanceFilter — no subclassing required.
    """
    def filter(self, doc: dict) -> FilterResult: ...


class GovernancePipeline:
    """
    Chains governance filters; short-circuits on first DENIED result.

    REQUIRES_HUMAN_REVIEW does NOT short-circuit by default — the pipeline
    continues and collects review flags. Set stop_on_review=True to treat
    REQUIRES_HUMAN_REVIEW like DENIED.

    Usage::

        pipeline = GovernancePipeline([
            EUAIActFilter(),
            GDPRDataFilter(),
            NISTRMFFilter(),
        ])
        result = pipeline.run(document)
        if result.is_denied:
            raise PermissionError(result.reason)
    """

    def __init__(
        self,
        filters: list,
        *,
        stop_on_review: bool = False,
    ) -> None:
        if not filters:
            raise ValueError("GovernancePipeline requires at least one filter")
        self._filters = filters
        self._stop_on_review = stop_on_review

    def run(self, doc: dict) -> FilterResult:
        """Run all filters. Returns first blocking result or APPROVED."""
        review_result: FilterResult | None = None
        for filt in self._filters:
            result = filt.filter(doc)
            if result.decision == "DENIED":
                logger.debug(
                    "Document DENIED by %s: %s",
                    type(filt).__name__,
                    result.reason,
                )
                return result
            if result.decision == "REQUIRES_HUMAN_REVIEW":
                if self._stop_on_review:
                    return result
                review_result = review_result or result  # capture first review
        if review_result is not None:
            return review_result
        return FilterResult(
            decision="APPROVED",
            reason="All governance filters passed",
            regulation_citation="",
            requires_logging=False,
        )

    def filter_batch(self, documents: list[dict]) -> list[FilterResult]:
        """Run pipeline over a list of documents."""
        return [self.run(doc) for doc in documents]

    def approved_only(self, documents: list[dict]) -> list[dict]:
        """Return only documents that pass all filters."""
        return [doc for doc in documents if self.run(doc).is_approved]

    def __len__(self) -> int:
        return len(self._filters)

    def __repr__(self) -> str:
        names = [type(f).__name__ for f in self._filters]
        return f"GovernancePipeline([{', '.join(names)}])"
