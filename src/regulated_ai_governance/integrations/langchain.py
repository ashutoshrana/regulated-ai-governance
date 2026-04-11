"""
LangChain integration — ``FERPAComplianceCallbackHandler``.

Intercepts retrieval results in a LangChain chain and applies identity-scoped
FERPA filtering before retrieved documents reach the LLM context window.
Produces a ``GovernanceAuditRecord`` for each retrieval event.

This integration enforces the two-layer FERPA boundary described in the
enterprise-rag-patterns library:

- Layer 1 (identity pre-filter): only documents with matching ``student_id``
  and ``institution_id`` metadata pass.
- Layer 2 (category authorization): only documents whose ``category`` field
  is in ``allowed_categories`` pass.

The ``GovernanceAuditRecord`` emitted per retrieval satisfies the disclosure
logging requirement at 34 CFR § 99.32.

Installation:
    pip install regulated-ai-governance[langchain]

Usage:
    from langchain_community.vectorstores import FAISS
    from regulated_ai_governance.integrations.langchain import (
        FERPAComplianceCallbackHandler,
    )

    audit_log = []
    handler = FERPAComplianceCallbackHandler(
        student_id="stu-alice",
        institution_id="univ-east",
        allowed_categories={"academic_record", "financial_record"},
        audit_sink=audit_log.append,
    )

    retriever = vector_store.as_retriever(callbacks=[handler])
    docs = retriever.invoke("What is my enrollment status?")
    # docs contains only Alice's authorized records at univ-east
"""

from __future__ import annotations

import uuid
from typing import Any, Callable

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.documents import Document
except ImportError as exc:
    raise ImportError(
        "langchain-core is required for this integration. "
        "Install it with: pip install regulated-ai-governance[langchain]"
    ) from exc

from regulated_ai_governance.audit import GovernanceAuditRecord


class FERPAComplianceCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that enforces FERPA identity boundaries on
    retrieval results before they enter the LLM context window.

    Integrates with LangChain's callback system by intercepting
    ``on_retriever_end`` events. For each retrieval result:

    1. Applies an identity pre-filter (``student_id`` + ``institution_id`` match).
    2. Applies a category authorization filter (if ``allowed_categories`` is set).
    3. Returns only the authorized subset to the chain.
    4. Emits a ``GovernanceAuditRecord`` to the ``audit_sink``.

    **FERPA compliance note:** ``student_id`` and ``institution_id`` must
    originate from the authenticated session token — not from the request body
    or query. The ``audit_sink`` should write to a durable, student-accessible
    store as required by 34 CFR § 99.32.

    :param student_id: Authenticated student identifier from the session.
    :param institution_id: Authenticated institution identifier from the session.
    :param allowed_categories: Optional set of permitted document category values.
        If None, no category filtering is applied (identity check only).
    :param audit_sink: Callable that receives a ``GovernanceAuditRecord`` for
        each retrieval event. Wire to a durable compliance log store.
    :param student_id_field: Metadata field name for the student identifier.
    :param institution_id_field: Metadata field name for the institution identifier.
    :param category_field: Metadata field name for the document category.
    :param raise_on_empty: If True, raise ``PermissionError`` when all documents
        are filtered out. Defaults to False.
    """

    def __init__(
        self,
        student_id: str,
        institution_id: str,
        allowed_categories: set[str] | None = None,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        student_id_field: str = "student_id",
        institution_id_field: str = "institution_id",
        category_field: str = "category",
        raise_on_empty: bool = False,
    ) -> None:
        super().__init__()
        self.student_id = student_id
        self.institution_id = institution_id
        self.allowed_categories = allowed_categories
        self.audit_sink = audit_sink
        self.student_id_field = student_id_field
        self.institution_id_field = institution_id_field
        self.category_field = category_field
        self.raise_on_empty = raise_on_empty

    def _apply_identity_filter(self, documents: list[Document]) -> list[Document]:
        """Layer 1: filter by student_id + institution_id."""
        return [
            doc for doc in documents
            if (
                doc.metadata.get(self.student_id_field) == self.student_id
                and doc.metadata.get(self.institution_id_field) == self.institution_id
            )
        ]

    def _apply_category_filter(self, documents: list[Document]) -> list[Document]:
        """Layer 2: filter by allowed_categories."""
        if not self.allowed_categories:
            return documents
        return [
            doc for doc in documents
            if doc.metadata.get(self.category_field) in self.allowed_categories
        ]

    def on_retriever_end(
        self,
        documents: list[Document],
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> list[Document]:
        """
        Intercept retrieval results and apply FERPA identity filtering.

        Called by the LangChain callback system immediately after a retriever
        returns results. The filtered list is returned to replace the original
        result in the chain.

        :param documents: Raw documents returned by the retriever.
        :param run_id: LangChain run identifier for this retrieval event.
        :param parent_run_id: Parent run identifier.
        :returns: Filtered list of authorized documents.
        :raises PermissionError: If ``raise_on_empty=True`` and all documents
            are filtered out.
        """
        raw_count = len(documents)

        # Two-layer enforcement
        after_identity = self._apply_identity_filter(documents)
        authorized = self._apply_category_filter(after_identity)

        # Emit audit record (34 CFR § 99.32)
        if self.audit_sink is not None:
            record = GovernanceAuditRecord(
                regulation="FERPA",
                actor_id=f"{self.student_id}@{self.institution_id}",
                action_name="retrieval",
                permitted=True,
                context={
                    "documents_in_store": raw_count,
                    "after_identity_filter": len(after_identity),
                    "after_category_filter": len(authorized),
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "student_id": self.student_id,
                    "institution_id": self.institution_id,
                    "allowed_categories": (
                        sorted(self.allowed_categories)
                        if self.allowed_categories
                        else None
                    ),
                },
            )
            self.audit_sink(record)

        if self.raise_on_empty and not authorized:
            raise PermissionError(
                f"FERPAComplianceCallbackHandler: all {raw_count} retrieved documents "
                f"were filtered out for student_id='{self.student_id}' "
                f"institution_id='{self.institution_id}'. "
                "Verify that the document store contains records for this identity."
            )

        return authorized
