# EU AI Act Goes Live in 90 Days: What Developers Building AI Agents Actually Need to Do

> *Published on [dev.to](https://dev.to/ashutoshrana/eu-ai-act-goes-live-in-90-days-what-developers-building-ai-agents-actually-need-to-do-4bah) — May 1, 2026*

---

If you're building AI agents for anything enterprise — education platforms, HR tools, healthcare apps, financial services — August 2, 2026 is a date worth knowing.

That's when the EU AI Act's Annex III obligations kick in for high-risk AI systems. Not "start planning" — actual legal enforcement, with fines up to €30 million or 6% of global annual turnover for non-compliance.

Most developer guides on the EU AI Act read like they were written by lawyers for other lawyers. This one is for people who write code.

---

## What Actually Applies to You

The first question is always: does this apply to me?

The EU AI Act uses a four-tier risk classification:

- **Prohibited** (Article 5): Manipulation, social scoring, real-time biometric surveillance in public spaces. Most developers aren't building this.
- **High-risk** (Article 6 + Annex III): This is where most enterprise AI agents land.
- **Limited-risk**: Chatbots, AI-generated content — transparency obligations apply.
- **Minimal-risk**: Spam filters, recommendation engines, game AI. Essentially unregulated.

You're in the high-risk category if your system is either a safety component in a regulated product (medical device, vehicle) or operates in one of the sectors listed in Annex III:

- **Education**: AI that determines access to educational institutions, or evaluates students' learning outcomes
- **Employment**: Recruitment tools, CV screening, performance monitoring, task allocation
- **Essential services**: Credit scoring, insurance risk assessment, utility access
- **Law enforcement** and **migration/asylum management**
- **Critical infrastructure** management

If you're building an admissions AI, an HR screening tool, a financial risk model, or a medical triage agent — you're in Annex III territory.

### The multi-agent problem

When you chain agents together, the compliance question compounds. Each agent in a pipeline that makes a decision affecting a person in a covered sector needs to comply. There's no "the LLM just made a suggestion" defense if its output directly influences a consequential decision.

Frameworks like [Google ADK](https://github.com/google/adk-python), [CrewAI](https://github.com/crewAIInc/crewAI), [LangGraph](https://github.com/langchain-ai/langgraph), and [AutoGen](https://github.com/microsoft/autogen) are neutral infrastructure. They don't know whether you're building a compliance-sensitive admissions system or a low-risk content assistant. That means the compliance layer is entirely your responsibility to add.

---

## The Five Things You Actually Have to Build

### 1. Audit Logging (Article 12)

Every action your agent takes on behalf of someone covered by Annex III needs to be logged with enough detail to reconstruct the decision after the fact. This isn't optional debugging output — it's a legal record that must be retained and producible for auditors.

A useful audit log event for an agent action looks like this:

```python
import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

@dataclass
class AgentAuditEvent:
    timestamp: str
    session_id: str
    agent_id: str
    action: str
    inputs: dict
    outputs: dict
    confidence_score: float
    decision_rationale: str
    human_override_available: bool

def log_agent_action(event: AgentAuditEvent):
    record = asdict(event)
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    # Write to your SIEM, append-only database, or structured log store
    print(json.dumps(record))
```

Design this layer to be immutable and queryable from day one. Retrofitting audit logging into an existing agent pipeline is painful.

### 2. Human Oversight (Article 14)

Article 14 is the one that requires the most architectural thought. High-risk AI systems must be designed so that humans can:

- Monitor the system during operation
- Understand outputs well enough to exercise appropriate judgment
- **Override, interrupt, or stop** the system at any point

That last requirement is the hard one for agentic systems. When you have a multi-agent pipeline running autonomously, you need a *technical mechanism* — not just a documented policy — that allows a human to halt execution.

Confidence-gated escalation is one pattern that satisfies Article 14 structurally. The agent monitors its own uncertainty and routes to a human when confidence drops below a defined threshold, rather than proceeding with an unreliable answer:

```python
from confidence_escalation import ConfidenceEscalationMiddleware, ThresholdPolicy

policy = ThresholdPolicy(
    low_confidence_threshold=0.6,  # route to human review below this
    critical_threshold=0.3,        # hard stop below this
)

middleware = ConfidenceEscalationMiddleware(
    policy=policy,
    on_escalate=lambda ctx: human_review_queue.enqueue(ctx),
    on_critical=lambda ctx: session_halt(ctx),
)
```

The [`confidence-escalation`](https://github.com/ashutoshrana/confidence-escalation) package implements this pattern across LangChain, CrewAI, AutoGen, and Google ADK. But the pattern itself doesn't require any specific library. The key is that your agent has a defined behavior when it's uncertain, and that behavior routes to a human rather than guessing.

### 3. Transparency (Article 13)

Users interacting with a high-risk AI system must be told:

- That they're interacting with an AI
- What the system's capabilities and limitations are
- How to contact a human if they need to

For voice and chat interfaces, this means disclosure at the start of every session, not buried in terms of service. For backend decision systems — like a loan scoring model — it means the person affected by the decision receives a plain-language explanation.

Build disclosure into session initialization as a first-class feature, not as a one-time consent screen that users click past once.

### 4. Accuracy and Robustness (Article 15)

Your system must minimize errors, resist adversarial inputs, and degrade gracefully. For LLM-based agents, this maps to:

- **Hallucination mitigation**: Don't let uncertain outputs reach consequential decisions without a confidence check
- **Adversarial input handling**: The [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) covers prompt injection, data poisoning, and the Agentic AI Top 10 in detail — worth reading directly
- **Graceful degradation**: If the AI can't answer reliably, define the fallback path explicitly. "I'm not confident enough to answer this" is a valid agent output. A hallucinated answer is not.

### 5. Risk Management System (Article 9)

Article 9 requires an *ongoing* risk management process, not a one-time compliance review. For engineering teams, this means:

- A documented process for identifying new risks when you update the model or change the agent's tool set
- Regular testing against your accuracy and robustness baselines
- An incident log when the system behaves unexpectedly

This doesn't have to be heavyweight. A written process, a structured incident log, and a quarterly review cadence is a defensible starting point.

---

## Building the Compliance Stack for Multi-Agent Systems

Here's the architecture challenge: all the major agent frameworks are compliance-neutral. They don't know which sector your agent operates in. This means you need to add a policy enforcement layer that runs *before* each agent action.

The pattern that works is a pre-execution compliance gate — a check that validates any planned action against your regulatory rules before it executes. For Google ADK, this maps cleanly to a `BeforeToolInvocationCallback`:

```python
from regulated_ai_governance.adapters.google_adk_adapter import create_compliant_agent
from regulated_ai_governance import PolicyStack, FERPAPolicy, EUAIActPolicy

policy_stack = PolicyStack([
    EUAIActPolicy(
        risk_tier="high_risk",
        human_oversight_required=True,
        transparency_required=True,
    ),
    FERPAPolicy(
        authorized_user_types=["student", "registrar"],
    ),
])

agent = create_compliant_agent(
    base_agent=my_adk_agent,
    policy_stack=policy_stack,
    audit_logger=my_audit_logger,
)
```

The [`regulated-ai-governance`](https://github.com/ashutoshrana/regulated-ai-governance) package implements this gate across Google ADK, CrewAI, LangChain, AutoGen, and Semantic Kernel. The same architectural pattern applies regardless of which framework you're using — policy evaluation before the action, not after.

For RAG systems in regulated sectors, the compliance layer needs to operate at the retrieval layer too, not just at the agent action layer. A FERPA-covered education AI should filter documents *before* they enter the context window, not after the LLM has already processed unauthorized content. The [`enterprise-rag-patterns`](https://github.com/ashutoshrana/enterprise-rag-patterns) library handles this with pre-retrieval filtering that enforces access control based on user identity and regulatory scope.

---

## The August 2 Deadline: What's Actually Enforceable When

| Date | What Applies |
|------|-------------|
| February 2, 2025 | Prohibited practices (Article 5) — already in force |
| August 2, 2025 | GPAI model obligations (Article 51–56) |
| **August 2, 2026** | **High-risk AI systems in Annex III — education, employment, essential services** |
| August 2, 2027 | Annex I safety component systems |

Fines for Annex III non-compliance: up to **€20 million or 4% of global annual turnover**, whichever is higher. The full regulation text is [publicly available on EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689) — the recitals are worth reading because they explain the legislative intent behind specific articles in plain language.

The EU AI Act doesn't require pre-registration the way GDPR's Data Protection Impact Assessment does. But if an incident occurs or a regulator audits you, you need to demonstrate that Articles 9–15 were implemented. The burden of proof is on the system operator.

---

## Where to Start

If you're building AI agents in any Annex III sector, here's a practical starting checklist:

1. **Classify your system honestly.** "Educational AI" that influences student outcomes = high-risk. Don't minimize it.
2. **Add structured audit logging now.** Every agent action, every tool call, every confidence score. Retrofit is painful.
3. **Design in a human override path.** At minimum: a review queue where a human can halt any agent decision before it becomes final.
4. **Document your risk management process.** A one-page document describing how you identify and address new risks is better than nothing — and it's evidence.
5. **Build AI disclosure into session init.** Not a checkbox. An actual first-message disclosure at the start of every user session.
6. **Test for adversarial inputs.** At least run prompt injection and data poisoning test cases against your agent before August.

The technical implementations here — audit logging, confidence checks, human escalation, policy gates — are engineering best practices that happen to also be legally required. The systems that handle these well tend to work better anyway: fewer silent failures, clearer failure modes, more trustworthy outputs.

The deadline is real. Three months is enough time to build this right.

---

*If you want to dig into the implementation patterns, the repos referenced in this article all have working examples: [regulated-ai-governance](https://github.com/ashutoshrana/regulated-ai-governance), [confidence-escalation](https://github.com/ashutoshrana/confidence-escalation), [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns). The EU AI Act official consolidated text is on [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689).*
