"""
examples/46_ccpa_consumer_rights.py

CCPA Consumer Rights Enforcement for California-Based AI Agents

Demonstrates how to detect and honor California Consumer Privacy Act (CCPA)
consumer rights invocations in AI agent conversations, and route them to
the appropriate human review or automated fulfillment workflow.

Commercial use cases:

  +-------------------------------------+-------------------------------------------+
  | Platform / Product                  | Applicable Regulation(s)                  |
  +-------------------------------------+-------------------------------------------+
  | Retail / e-commerce AI agents       | CCPA §§ 1798.100–1798.145 + CPRA          |
  | Financial services chatbots         | CCPA + GLBA privacy rules                 |
  | Healthcare patient portals (non-HH) | CCPA + Cal. Health Safety Code §123148    |
  | HR / employment automation          | CCPA §1798.121 (automated decisions)      |
  | EdTech platforms (non-FERPA scope)  | CCPA (18+ students, non-nonprofit)        |
  | Real estate / mortgage bots         | CCPA + FCRA                               |
  +-------------------------------------+-------------------------------------------+

Regulatory frameworks enforced:

  Layer 1 — California Residency Gate
      CCPA applies to for-profit businesses that collect California consumers'
      personal information and meet threshold criteria (annual revenue > $25M,
      processes data of 100,000+ consumers, or derives 50%+ revenue from selling
      personal data). Cal. Civil Code §1798.140(d).

      CPRA (Prop 24, 2020) expanded CCPA effective January 1, 2023: established
      the California Privacy Protection Agency (CPPA) and added §1798.121
      (automated decision-making opt-out rights).

  Layer 2 — Consumer Rights Detection
      Five consumer rights are detected from conversation context:

      Right to Know (§1798.100): Consumer may request categories and specific
          pieces of personal information collected in the preceding 12 months.
          Business must respond within 45 days (§1798.105).

      Right to Delete (§1798.105): Consumer may request deletion of personal
          information. Business must delete and direct service providers to delete.
          Exceptions include legal obligation, transactional necessity, security
          research, and free speech (§1798.105(d)).

      Right to Opt-Out (§1798.120): Consumer may direct business to not sell or
          share personal information. Must be honored within 15 business days.
          Re-solicitation prohibited for 12 months.

      Right to Non-Discrimination (§1798.125): Business may not deny goods,
          charge different prices, or provide different quality for exercising
          CCPA rights. Financial incentives are permissible only with prior
          opt-in.

      Automated Decision-Making Opt-Out (CPRA §1798.121): Consumer may opt
          out of automated decision-making that significantly affects them,
          including profiling for employment, financial services, or housing.

  Layer 3 — Request Routing
      Voice and chat AI agents cannot fulfill CCPA requests inline:
      - Right to Know responses must be delivered within 45 days via authenticated
        channel (§1798.130(a)(2))
      - Deletion requires verification of consumer identity before execution
        (§1798.130(a)(3))
      - Opt-out must be logged and propagated to all data processors

      This layer routes all rights invocations to:
        (a) Human agent for verification
        (b) Automated queue for authenticated web/app channel fulfillment
        (c) Compliance audit log (Cal. Code Regs., tit. 11, §7102)

  Layer 4 — Audit Trail
      Every rights invocation and routing decision is recorded with:
      - Consumer identifier (anonymised until verified)
      - Request type and statutory citation
      - Timestamp and channel
      - Resolution path (human / automated)
      - Agent session ID for linkage to contact records

Requirements:
    pip install regulated-ai-governance

Run:
    python examples/46_ccpa_consumer_rights.py
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Policy Layer 1 — California Residency Gate
# ---------------------------------------------------------------------------

@dataclass
class ResidencyContext:
    """Consumer residency and business threshold context."""
    ip_geo_state: Optional[str] = None
    consumer_declared_state: Optional[str] = None
    business_threshold_met: bool = True  # assume true for demo

    @property
    def is_california(self) -> bool:
        for s in [self.ip_geo_state, self.consumer_declared_state]:
            if s and s.strip().upper() in ("CA", "CALIFORNIA"):
                return True
        return False


class CaliforniaResidencyFilter:
    """
    Layer 1: Apply CCPA only to California consumers.

    CCPA §1798.140(d): 'Consumer' means natural persons who are California
    residents as defined in Revenue and Taxation Code §17014.
    """

    def evaluate(self, context: ResidencyContext) -> bool:
        return context.is_california and context.business_threshold_met


# ---------------------------------------------------------------------------
# Policy Layer 2 — Consumer Rights Detection
# ---------------------------------------------------------------------------

_RIGHT_PHRASES: Dict[str, List[str]] = {
    "right_to_know": [
        "what data do you have on me",
        "what information do you collect",
        "what personal information",
        "right to know",
        "data disclosure request",
    ],
    "right_to_delete": [
        "delete my data",
        "delete my information",
        "remove my personal information",
        "right to delete",
        "erase my data",
    ],
    "right_to_opt_out": [
        "opt out",
        "stop selling my data",
        "don't sell my information",
        "do not share my data",
        "opt-out",
    ],
    "right_to_non_discrimination": [
        "right to non-discrimination",
        "you can't treat me differently",
        "equal treatment",
    ],
    "opt_out_automated_decision": [
        "opt out of automated decision",
        "no automated profiling",
        "human review required",
        "stop automated decisions",
    ],
}

_RIGHT_CITATIONS: Dict[str, str] = {
    "right_to_know": "Cal. Civil Code §1798.100",
    "right_to_delete": "Cal. Civil Code §1798.105",
    "right_to_opt_out": "Cal. Civil Code §1798.120",
    "right_to_non_discrimination": "Cal. Civil Code §1798.125",
    "opt_out_automated_decision": "CPRA §1798.121",
}


class CCPARightsDetector:
    """
    Layer 2: Detect CCPA consumer rights invocations in conversation text.

    Matches explicit right declarations and natural-language phrases.
    Explicit consumer_request_type always wins over phrase matching.
    """

    def detect(
        self,
        transcript: str,
        explicit_request: Optional[str] = None,
    ) -> Optional[str]:
        if explicit_request and explicit_request in _RIGHT_CITATIONS:
            return explicit_request
        lower = transcript.lower()
        for right, phrases in _RIGHT_PHRASES.items():
            if any(p in lower for p in phrases):
                return right
        return None


# ---------------------------------------------------------------------------
# Policy Layer 3 — Request Routing
# ---------------------------------------------------------------------------

@dataclass
class CCPARightInvocation:
    """Record of a detected consumer rights invocation."""
    request_type: str
    statutory_citation: str
    transcript_excerpt: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None
    consumer_id: Optional[str] = None
    channel: str = "voice"
    resolution_path: str = "human_review"


class CCPARequestRouter:
    """
    Layer 3: Route detected rights invocations to fulfillment queue.

    Voice/chat agents route ALL requests to human review or authenticated
    web channel — inline fulfillment is not permitted (§1798.130(a)(3)).
    """

    def __init__(self) -> None:
        self._queue: List[CCPARightInvocation] = []

    def route(self, invocation: CCPARightInvocation) -> str:
        self._queue.append(invocation)
        # Deletion and opt-out require immediate routing; know is lower urgency
        if invocation.request_type in ("right_to_delete", "opt_out_automated_decision"):
            return "immediate_human_review"
        return "authenticated_web_channel"

    @property
    def pending(self) -> List[CCPARightInvocation]:
        return list(self._queue)


# ---------------------------------------------------------------------------
# Policy Layer 4 — Audit Trail
# ---------------------------------------------------------------------------

class CCPAComplianceAudit:
    """
    Layer 4: Immutable audit record for CCPA rights events.

    Cal. Code Regs., tit. 11, §7102: businesses must maintain records of
    consumer requests and responses for 24 months.
    """

    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []

    def record(self, invocation: CCPARightInvocation, routing_result: str) -> None:
        self._entries.append({
            "timestamp": invocation.detected_at.isoformat(),
            "right": invocation.request_type,
            "citation": invocation.statutory_citation,
            "session_id": invocation.session_id,
            "consumer_id": invocation.consumer_id,
            "channel": invocation.channel,
            "routing": routing_result,
            "regulation": "CCPA Cal. Civil Code §§ 1798.100-1798.145 + CPRA §1798.121",
        })

    @property
    def entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class CCPAConsumerRightsPipeline:
    """
    Four-layer CCPA consumer rights enforcement pipeline for AI agents.

    Processes conversation turns through residency gate, rights detection,
    request routing, and audit logging.

    Returns a ComplianceCheckResult-compatible dict on each run.
    """

    def __init__(self) -> None:
        self._residency_filter = CaliforniaResidencyFilter()
        self._detector = CCPARightsDetector()
        self._router = CCPARequestRouter()
        self._audit = CCPAComplianceAudit()

    def run(
        self,
        transcript: str,
        residency: ResidencyContext,
        session_id: Optional[str] = None,
        consumer_id: Optional[str] = None,
        explicit_request: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self._residency_filter.evaluate(residency):
            return {
                "passed": True,
                "ccpa_applicable": False,
                "reason": "Consumer not identified as California resident",
            }

        right = self._detector.detect(transcript, explicit_request)
        if right is None:
            return {
                "passed": True,
                "ccpa_applicable": True,
                "right_invoked": None,
                "reason": "No CCPA rights invocation detected",
            }

        citation = _RIGHT_CITATIONS[right]
        invocation = CCPARightInvocation(
            request_type=right,
            statutory_citation=citation,
            transcript_excerpt=transcript[:200],
            session_id=session_id,
            consumer_id=consumer_id,
        )
        routing = self._router.route(invocation)
        self._audit.record(invocation, routing)

        return {
            "passed": False,
            "ccpa_applicable": True,
            "right_invoked": right,
            "citation": citation,
            "routing": routing,
            "required_actions": [
                f"Route to {routing} for authenticated fulfillment",
                f"Respond within 45 days per {citation}",
                "Log to 24-month audit record per Cal. Code Regs. §7102",
            ],
        }

    @property
    def audit_entries(self) -> List[Dict[str, Any]]:
        return self._audit.entries


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    pipeline = CCPAConsumerRightsPipeline()
    california = ResidencyContext(ip_geo_state="CA")
    non_california = ResidencyContext(ip_geo_state="TX")

    scenarios = [
        {
            "label": "California resident — opt-out request",
            "transcript": "I want to opt out of you selling my personal data.",
            "residency": california,
            "session_id": "sess_001",
        },
        {
            "label": "California resident — right to delete",
            "transcript": "Please delete my information from your systems immediately.",
            "residency": california,
            "session_id": "sess_002",
        },
        {
            "label": "California resident — CPRA automated decision opt-out",
            "transcript": "I don't want automated decisions about my loan application.",
            "residency": california,
            "explicit_request": "opt_out_automated_decision",
            "session_id": "sess_003",
        },
        {
            "label": "California resident — normal transaction (no rights invoked)",
            "transcript": "I need help checking my account balance.",
            "residency": california,
            "session_id": "sess_004",
        },
        {
            "label": "Non-California resident — CCPA not applicable",
            "transcript": "Delete my data please.",
            "residency": non_california,
            "session_id": "sess_005",
        },
    ]

    print("\nCCPA Consumer Rights Enforcement Pipeline")
    print("=" * 55)
    for scenario in scenarios:
        result = pipeline.run(
            transcript=scenario["transcript"],
            residency=scenario["residency"],
            session_id=scenario.get("session_id"),
            explicit_request=scenario.get("explicit_request"),
        )
        status = "⛔ BLOCKED" if not result["passed"] else "✅ PASSED"
        print(f"\n[{scenario['label']}]")
        print(f"  {status}")
        if not result["passed"]:
            print(f"  Right invoked: {result['right_invoked']}")
            print(f"  Citation: {result['citation']}")
            print(f"  Routing: {result['routing']}")

    print(f"\nAudit entries recorded: {len(pipeline.audit_entries)}")
    for entry in pipeline.audit_entries:
        print(f"  {entry['timestamp']} | {entry['right']} | {entry['citation']}")


if __name__ == "__main__":
    main()
