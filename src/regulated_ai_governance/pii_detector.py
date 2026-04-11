"""
pii_detector.py — PII pre-flight detection for regulated AI pipelines.

Provides lightweight, regex-based detection of common PII patterns before
content enters an LLM context window. This is a defence-in-depth control
complementing structural FERPA/HIPAA/GDPR policy enforcement — it catches
accidental PII leakage in prompt templates, tool outputs, and retrieved documents.

Design philosophy
-----------------
This detector is intentionally simple: it uses curated regex patterns for
high-confidence PII signals (SSN, email, phone, credit card) rather than a
large ML model. The goal is a zero-dependency pre-flight check that runs in
microseconds per document. For higher-recall detection in production, combine
this with a purpose-built NER model (AWS Comprehend, Azure Text Analytics,
Google Cloud DLP, or an on-premises spaCy model).

Usage::

    from regulated_ai_governance.pii_detector import PIIDetector, PIICategory

    detector = PIIDetector()
    result = detector.scan("Patient SSN is 123-45-6789 and email is pat@example.com")

    print(result.has_pii)                    # True
    print(result.detected_categories)       # {PIICategory.SSN, PIICategory.EMAIL}
    print(result.findings)                  # list of PIIFinding with match details
    redacted = detector.redact(text)         # Replace PII with [REDACTED-<category>]
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PIICategory(Enum):
    """Categories of PII detectable by ``PIIDetector``."""

    SSN = "SSN"  # US Social Security Number
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    CREDIT_CARD = "CREDIT_CARD"
    IP_ADDRESS = "IP_ADDRESS"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    PASSPORT = "PASSPORT"
    DRIVER_LICENSE = "DRIVER_LICENSE"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    MEDICAL_RECORD_NUMBER = "MEDICAL_RECORD_NUMBER"


@dataclass
class PIIFinding:
    """
    A single PII match found in a text.

    Attributes:
        category: The type of PII detected.
        match: The matched text (may be partially masked in logs).
        start: Start character offset in the source text.
        end: End character offset in the source text.
        confidence: ``"high"`` for regex-confirmed patterns; ``"medium"`` otherwise.
    """

    category: PIICategory
    match: str
    start: int
    end: int
    confidence: str = "high"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation (match is masked)."""
        return {
            "category": self.category.value,
            "match": self.match[:3] + "***" if len(self.match) > 3 else "***",
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
        }


@dataclass
class PIIScanResult:
    """
    The result of scanning a text for PII.

    Attributes:
        text_length: Length of the scanned text.
        findings: All PII findings detected.
        has_pii: True if any findings were detected.
        detected_categories: Set of PII categories found.
    """

    text_length: int
    findings: list[PIIFinding] = field(default_factory=list)

    @property
    def has_pii(self) -> bool:
        """True if at least one PII finding was detected."""
        return len(self.findings) > 0

    @property
    def detected_categories(self) -> set[PIICategory]:
        """Set of PII categories present in the findings."""
        return {f.category for f in self.findings}

    def to_audit_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable summary for audit logging."""
        return {
            "text_length": self.text_length,
            "has_pii": self.has_pii,
            "detected_categories": [c.value for c in sorted(self.detected_categories, key=lambda x: x.value)],
            "finding_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
        }


# Regex patterns — ordered from most specific to least specific.
_PII_PATTERNS: list[tuple[PIICategory, re.Pattern[str]]] = [
    (PIICategory.SSN, re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    (PIICategory.CREDIT_CARD, re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b")),
    (PIICategory.EMAIL, re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    (PIICategory.PHONE, re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    (PIICategory.IP_ADDRESS, re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    (
        PIICategory.DATE_OF_BIRTH,
        re.compile(
            r"\b(?:DOB|date of birth|born)[:\s]+\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
            re.IGNORECASE,
        ),
    ),
    (PIICategory.MEDICAL_RECORD_NUMBER, re.compile(r"\bMRN[:\s]+[A-Z0-9]{6,12}\b", re.IGNORECASE)),
    (PIICategory.BANK_ACCOUNT, re.compile(r"\b(?:account\s*(?:no|number|#)?[:\s]+)?\d{8,17}\b", re.IGNORECASE)),
]


class PIIDetector:
    """
    Lightweight regex-based PII detector for regulated AI pipelines.

    Uses curated patterns to identify high-confidence PII in text before it
    enters an LLM context window. Zero external dependencies.

    Args:
        categories: Subset of ``PIICategory`` values to check. If None, all
            categories are checked.
        custom_patterns: Additional ``(category, compiled_regex)`` tuples to
            include alongside the built-in patterns.
    """

    def __init__(
        self,
        categories: set[PIICategory] | None = None,
        custom_patterns: list[tuple[PIICategory, re.Pattern[str]]] | None = None,
    ) -> None:
        if categories is not None:
            self._patterns = [(cat, pat) for cat, pat in _PII_PATTERNS if cat in categories]
        else:
            self._patterns = list(_PII_PATTERNS)
        if custom_patterns:
            self._patterns.extend(custom_patterns)

    def scan(self, text: str) -> PIIScanResult:
        """
        Scan *text* for PII and return a ``PIIScanResult``.

        Args:
            text: Plain text to scan (may be a document, prompt, or tool output).

        Returns:
            A ``PIIScanResult`` with all findings.
        """
        findings: list[PIIFinding] = []
        for category, pattern in self._patterns:
            for m in pattern.finditer(text):
                findings.append(
                    PIIFinding(
                        category=category,
                        match=m.group(),
                        start=m.start(),
                        end=m.end(),
                    )
                )
        # Sort by start offset for deterministic output
        findings.sort(key=lambda f: f.start)
        return PIIScanResult(text_length=len(text), findings=findings)

    def redact(self, text: str) -> str:
        """
        Return a copy of *text* with detected PII replaced by ``[REDACTED-<CATEGORY>]``.

        Replacements are applied right-to-left to preserve character offsets.

        Args:
            text: Plain text to redact.

        Returns:
            Redacted copy of *text*.
        """
        result = scan = self.scan(text)
        findings = sorted(result.findings, key=lambda f: f.start, reverse=True)
        chars = list(text)
        for finding in findings:
            replacement = f"[REDACTED-{finding.category.value}]"
            chars[finding.start : finding.end] = list(replacement)
        _ = scan  # suppress unused variable
        return "".join(chars)

    def contains_pii(self, text: str) -> bool:
        """Quick check: return True if *text* contains any detectable PII."""
        return self.scan(text).has_pii
