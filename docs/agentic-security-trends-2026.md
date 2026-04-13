# Agentic AI Security Trends 2026

**Repo:** `regulated-ai-governance`
**Relates to:** [`examples/39_owasp_agentic_top10_governance.py`](../examples/39_owasp_agentic_top10_governance.py)
**ADR cross-reference:** [ADR-001 (policy-before-execution)](adr/001-policy-before-execution.md), [ADR-004 (framework-agnostic-core)](adr/004-framework-agnostic-core.md)

---

## 1. The Agentic AI Security Inflection Point (2025–2026)

The period from mid-2025 through early 2026 marks the most concentrated burst of standardisation activity in the history of AI security governance. In fewer than six months, three independent bodies published foundational frameworks for agentic AI security — frameworks that had been absent entirely twelve months earlier.

| Framework | Body | Published | Scope |
|---|---|---|---|
| OWASP Top 10 for Agentic Applications 2026 | OWASP Foundation | December 2025 | 10-category attack taxonomy for autonomous AI agents |
| NIST AI Agent Standards Initiative | NIST / ITL | February 2026 | Industry-led ISO/IEC standards + open protocols roadmap |
| CSA Agentic Trust Framework (ATF) | Cloud Security Alliance | February 2026 | 4-level autonomy maturity model tied to ISO/IEC 42001 |

Why 2026 specifically? Three converging forces:

**Production deployments at scale.** By mid-2025, agentic AI systems — agents with tool access, memory, and multi-step planning — moved from research prototypes to production workloads at major enterprises. The attack surface moved from theoretical to real, with confirmed incidents of indirect prompt injection in enterprise RAG pipelines, data exfiltration via tool invocation, and cross-session memory contamination.

**The Model Context Protocol (MCP) inflection.** Anthropic published the Model Context Protocol in November 2024. By mid-2025, MCP had become the dominant standard for agent-tool communication, replacing dozens of proprietary tool-calling schemes. The standardisation of agent-tool communication concentrated the attack surface: a single malicious MCP server could compromise any agent using standard discovery. The first confirmed malicious MCP package appeared in September 2025.

**Regulatory momentum.** The EU AI Act entered its high-risk AI application obligations period in August 2025. NIST AI 600-1 (GenAI Profile, July 2024) had already established that existing frameworks were incomplete for agentic autonomous action. The combination of regulatory pressure and confirmed production incidents created the conditions for standards bodies to act.

The result is that teams building agentic systems in 2026 operate in a materially different compliance environment than teams building the same systems in 2024. The frameworks documented in this note are not advisory guidance — they are the baseline expected by enterprise security teams, GRC auditors, and increasingly by regulators.

---

## 2. OWASP Top 10 for Agentic Applications 2026

Published December 2025 following review by 100+ security practitioners, red teamers, and AI safety researchers. This list is distinct from the earlier OWASP LLM Top 10 (2025), which focused on prompt injection and data leakage in LLM inference endpoints. The Agentic Top 10 targets autonomous agents with tool access, memory, and multi-step execution — the threat model is fundamentally different.

### ASI01 — Agent Goal Hijack

**Category:** Indirect prompt injection via documents, tool outputs, and environmental data.

An attacker embeds adversarial instructions in content that the agent will process — a retrieved document, a tool output, a web page, or a memory entry. When the agent processes the content, the embedded instructions redirect the agent's goal state. Unlike direct prompt injection (which targets the system or user prompt), indirect injection operates on the agent's context window through channels the agent trusts.

**Why it is the top threat:** Agents operate autonomously across many documents and tool calls. Each document is a potential injection vector. The agent cannot distinguish between legitimate retrieved content and adversarial instructions embedded in that content without explicit injection detection.

**Control:** Validate all external input against injection patterns before routing to agent context. Tag tool outputs with source metadata; route tool output through sanitisation before re-injection into agent context.

### ASI02 — Unsafe Tool Use

**Category:** Typosquatting attacks on tool names, over-privileged tool access, unverified tool registrations.

Agents select tools from a registry. An attacker can register a malicious tool with a name similar to a legitimate tool (`send_emial` vs `send_email`; `searh_web` vs `search_web`). The agent selects the malicious tool based on name similarity. Over-privileged access compounds the risk: a tool granted broad filesystem or network access exposes the full scope of its permissions to any successful injection.

**Control:** Enforce a cryptographically signed tool allowlist. Never discover and execute tools dynamically without allowlist verification. Apply least-privilege to all tool permissions.

### ASI03 — Data Leakage

**Category:** PII and sensitive data in agent responses, cross-session memory contamination.

Agents retrieve documents and synthesise responses. Without DLP (Data Loss Prevention) scanning of agent outputs, sensitive data — PII, credentials, proprietary information — can appear in responses to users who are not authorised to receive it. Memory systems that persist across sessions create a second vector: data from one user's session can contaminate another user's context.

**Control:** Apply DLP scanning to all agent outputs before delivery. Scope all memory (episodic, semantic, and working memory) to the current session and authenticated user. Purge memory on session end.

### ASI04 — Data Poisoning

**Category:** Corrupted retrieval sources, manipulated vector stores, poisoned training data.

An agent's retrieved context is only as trustworthy as its retrieval sources. An attacker who can write to a vector store, document repository, or web-accessible data source that the agent retrieves from can insert adversarial content that will eventually appear in the agent's context. Unlike ASI01 (which focuses on the injection moment), ASI04 focuses on the persistent compromise of retrieval infrastructure.

**Control:** Verify the integrity of retrieved documents using cryptographic checksums or digital signatures before routing to the agent. Monitor retrieval sources for anomalous content using semantic outlier detection. Apply anomaly scoring to retrieved content; flag high-anomaly documents for human review.

### ASI05 — Privilege Misuse

**Category:** Inherited privileges, retained cross-session permissions, identity escalation.

Agents commonly inherit the identity and permissions of the user or service account that invoked them. When an agent persists privileges across sessions — retaining tokens, credentials, or capability grants from previous invocations — it becomes a persistent high-privilege entity in the environment. A compromised or injected agent with cross-session privileges can access resources far beyond the scope of any single legitimate request.

**Control:** Issue per-session, time-limited credentials to agents. Do not persist agent identity credentials across session boundaries. Implement JIT (just-in-time) access — grant tool permissions at invocation time, revoke on session end.

### ASI06 — Supply Chain Risks

**Category:** Compromised plugins, malicious MCP packages, unverified tool registries.

The agent ecosystem depends on a supply chain of tool plugins, MCP servers, framework extensions, and third-party libraries. The first confirmed malicious MCP package appeared in September 2025 and remained undetected for two weeks. CVE-2025-6514 documented command injection in malicious MCP servers. Any unverified dependency in the tool supply chain is a potential lateral movement vector.

**Control:** Require cryptographic signature verification for all plugins and MCP tool definitions before registration. Maintain an internal, audited tool registry rather than relying on public discovery. Apply the same software supply chain controls to agent tools that you apply to application dependencies.

### ASI07 — Human-Agent Trust Exploitation

**Category:** Anthropomorphization attacks, hijacked agents manipulating users, social engineering via agents.

Users anthropomorphize AI agents — they attribute intent, trustworthiness, and authority to agents in ways they would not attribute to a database query. An adversary who hijacks an agent (via ASI01 or ASI06) can use the agent's trusted position to extract sensitive information from users, manipulate user decisions, or perform social engineering that would be immediately suspicious from a human attacker. The agent's perceived authority and the user's reduced skepticism create an asymmetric attack surface.

**Control:** Implement output verification to detect when agent outputs deviate from the agent's documented capability scope. Disclose AI nature clearly and consistently. Log all agent-to-user communications for post-hoc review.

### ASI08 — Cascading Failures

**Category:** Irreversible actions executed before human oversight, runaway multi-step execution.

Agents take actions in the world: sending emails, modifying files, executing API calls, purchasing resources, deleting records. Unlike a human who pauses before an irreversible action, an agent will execute irreversible actions as readily as reversible ones unless explicitly constrained. In multi-step workflows, a single compromised early step can trigger a cascade of irreversible downstream actions before any human oversight mechanism detects the anomaly.

**Control:** Gate all irreversible actions on rollback capability verification. Implement a human-in-the-loop checkpoint for high-impact actions. Design workflows with compensation transactions (rollback procedures) for every write operation.

### ASI09 — Inadequate Monitoring and Audit

**Category:** No observability into agent decisions, missing audit trails, opaque tool invocation logs.

Agent systems are fundamentally harder to audit than request-response systems. A single user interaction may trigger dozens of tool calls, memory reads, and sub-agent invocations. Without per-step audit trails, it is impossible to reconstruct what the agent did, why it did it, and what data it accessed. Most production agentic deployments in 2025 had no audit trails covering agent decision steps — only coarse-grained application logs.

**Control:** Emit a structured audit record for every tool invocation, memory access, and agent decision step. Include: actor identity, session ID, tool name, input/output hash, timestamp, and reasoning trace where available. Store audit records in an append-only, tamper-evident log.

### ASI10 — Unvalidated Agent Composition

**Category:** Multi-agent trust boundaries, unverified sender identity, orchestrator-subagent injection.

Multi-agent systems — orchestrators delegating to subagents, peer-to-peer agent coordination, human-agent-agent pipelines — introduce trust boundary problems that do not exist in single-agent systems. A message from a subagent carries no inherent authority; it may have been generated by a compromised agent, injected by an adversary, or fabricated entirely. Without cryptographic sender verification, any agent in a pipeline can be impersonated.

**Control:** Verify the identity of all message senders in multi-agent pipelines using agent-specific credentials (not inherited user credentials). Treat messages from other agents as untrusted input subject to the same validation as external data.

### Summary Table

| ID | Name | Primary Attack Vector | Decision If Violated |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | Indirect prompt injection | DENIED |
| ASI02 | Unsafe Tool Use | Tool typosquatting, over-privilege | DENIED |
| ASI03 | Data Leakage | PII in outputs, memory contamination | DENIED |
| ASI04 | Data Poisoning | Corrupted retrieval sources | DENIED |
| ASI05 | Privilege Misuse | Cross-session persistent credentials | DENIED |
| ASI06 | Supply Chain Risks | Malicious plugins/MCP packages | DENIED |
| ASI07 | Human-Agent Trust Exploitation | Hijacked agent social engineering | DENIED |
| ASI08 | Cascading Failures | Irreversible actions without rollback | DENIED |
| ASI09 | Inadequate Monitoring | No audit trail for agent decisions | DENIED |
| ASI10 | Unvalidated Agent Composition | Unverified multi-agent sender identity | DENIED |

---

## 3. NIST AI Agent Standards Initiative (February 2026)

The NIST Information Technology Laboratory published the AI Agent Standards Initiative roadmap in February 2026, responding to the recognition that NIST AI 600-1 (July 2024, GenAI Profile) did not cover the risks introduced by autonomous agentic action. The initiative has three pillars:

### Pillar 1 — Industry-Led ISO/IEC Standards

NIST is coordinating with ISO/IEC JTC 1/SC 42 (Artificial Intelligence) to develop agent-specific extensions to existing AI standards:

- **ISO/IEC 42001:2023 (AI Management System):** Agent-specific annex covering agent governance, tool access policies, and multi-agent trust management.
- **ISO/IEC 27001:2022 (ISMS):** New control categories for agent identity management, agent audit logging, and agent access control.
- **ISO/IEC 23894:2023 (AI Risk Management):** Risk guidance specific to autonomous action, irreversible effects, and cascading failures.

### Pillar 2 — Open Protocol Adoption (MCP and A2A)

The initiative formally endorses two open protocols as the interoperability baseline for agentic systems:

- **Model Context Protocol (MCP):** Anthropic's November 2024 standard for agent-tool communication. NIST endorsement means federal agencies and regulated industries are expected to adopt MCP as the tool interface standard, replacing proprietary implementations.
- **Agent-to-Agent (A2A) Protocol:** Google's open protocol for peer agent communication. Provides standardised message format, sender identity fields, and capability negotiation — addressing ASI10 (Unvalidated Agent Composition) at the protocol layer.

### Pillar 3 — Fundamental Research Agenda

NIST is funding research into:

- Formal verification methods for agent goal preservation (ASI01 detection)
- Semantic integrity checking for retrieved content (ASI04 detection)
- JIT credential management for stateless agent sessions (ASI05 mitigation)
- Rollback-capable workflow primitives (ASI08 mitigation)

### Planned Deliverable: AI Agent Interoperability Profile (Q4 2026)

The primary standards deliverable is the **AI Agent Interoperability Profile**, targeted for Q4 2026 publication. Key provisions:

| Provision | Description |
|---|---|
| Agent identity | Unique, verifiable identity per agent instance (not inherited from user) |
| JIT access | Tool permissions granted at invocation, revoked at session end |
| SP 800-53 overlays | Agent-specific control overlays for the NIST SP 800-53 Rev 5 control catalog |
| Audit record schema | Standardised JSON schema for agent audit events |
| Multi-agent trust | Protocol-level sender verification requirements for A2A communication |

### The NIST AI 600-1 Gap

NIST AI 600-1 (July 2024) established the GenAI Profile — risk management guidance for generative AI systems. However, AI 600-1 explicitly scoped out autonomous agentic action: it addresses generative outputs (text, images, code) but does not cover agents that take actions in the world through tool calls, API invocations, or multi-step planning. The AI Agent Interoperability Profile is intended to fill this gap. Until it publishes, teams should treat AI 600-1 as necessary but not sufficient for agentic system governance.

---

## 4. MITRE ATLAS v5.1 (November 2025) — Agentic Additions

MITRE ATLAS (Adversarial Threat Landscape for AI Systems) published version 5.1 in November 2025 in collaboration with Zenity Labs, expanding the technique library from 70 to 84 techniques. The additions focus on agentic and GenAI-specific attack patterns.

### New Technique Categories

**Agent Tool Invocation** (`AML.T0067`): Adversary manipulates an agent into invoking a tool with attacker-controlled parameters — file paths, API endpoints, shell commands — by embedding the parameters in content the agent retrieves or processes.

**Exfiltration via Tool Invocation** (`AML.T0068`): Agent is manipulated into invoking a tool (HTTP request, file write, email send) that exfiltrates data to an attacker-controlled endpoint. Combines ASI01 (goal hijack) with a real-world exfiltration primitive.

**RAG Database Prompting** (`AML.T0069`): Attacker inserts adversarial content into a vector store or document repository that the RAG system retrieves. When the adversarial document is retrieved and injected into the agent's context, it carries embedded instructions. This is ATLAS's formalization of ASI04 (Data Poisoning).

### Zenity Labs Integration

The Zenity Labs contribution added 14 techniques based on confirmed production incidents involving enterprise agentic systems. Key additions:

- Prompt injection through PDF metadata fields
- Instruction smuggling via markdown link labels
- Tool name collision (formalization of ASI02 typosquatting)
- Session persistence via compromised memory store writes

### The Primary Attack Chain

ATLAS v5.1 documents the canonical multi-step agentic attack chain:

```
Adversary embeds instructions in document
       │
       ▼
AML.T0051.000 — Indirect Prompt Injection
       │  Agent retrieves adversarial document
       ▼
AML.T0067 — Agent Goal Hijack
       │  Agent goal state redirected to attacker objective
       ▼
AML.T0067 — Tool Invocation with attacker parameters
       │  Agent invokes tool (HTTP, file, shell) under adversary control
       ▼
AML.T0068 — Exfiltration via Tool Invocation
              Data exfiltrated to attacker-controlled endpoint
```

This chain can execute entirely within the normal operational flow of a RAG-augmented agent — no anomalous authentication events, no unusual network patterns at the infrastructure level.

---

## 5. CSA Agentic Trust Framework (ATF) — February 2026

The Cloud Security Alliance published the Agentic Trust Framework in February 2026, developed by the AI Safety Working Group with input from 60+ enterprise practitioners. The ATF provides a maturity model for evaluating and granting autonomy to AI agents based on demonstrated trustworthiness rather than capability assertions.

### Core Principle: Autonomy Must Be Earned

The ATF's foundational principle is that agent autonomy is not a feature to be configured — it is a property to be earned through demonstrated trustworthiness in progressively higher-stakes environments. An agent must prove safe behaviour at each level before being permitted to operate at the next.

### The Four Maturity Levels

| Level | Name | Permitted Actions | Required Controls |
|---|---|---|---|
| 1 | Sandbox | Read-only; no external tool calls; no memory persistence | Basic input/output logging |
| 2 | Controlled Production | Limited tool calls with allowlist; session-scoped memory; human review for irreversible actions | DLP scan on outputs; tool allowlist; anomaly scoring |
| 3 | Trusted Production | Full tool access within defined scope; persistent episodic memory; asynchronous human review | Cryptographic tool verification; JIT credentials; full audit trail; formal capability attestation |
| 4 | Autonomous | Delegated authority for defined decision classes; no per-action human review | Continuous monitoring; formal verification of goal preservation; quarterly red team assessment |

### Level Promotion Gates

Promotion from one level to the next requires:

1. **Incident history review:** Zero high-severity incidents at current level for a defined observation period (90 days minimum for Levels 1→2 and 2→3; 180 days for 3→4).
2. **Red team assessment:** Structured adversarial testing targeting the techniques in MITRE ATLAS v5.1.
3. **Formal capability attestation:** Documentation of the agent's intended capability scope, signed by the responsible product owner.
4. **Control verification:** Independent verification that all required controls for the target level are implemented and operational.

### Regulatory Alignment

The ATF maps explicitly to:

- **ISO/IEC 42001:2023:** Level 3/4 requirements align with ISO 42001 Clause 6.1 (AI risk assessment) and Clause 9.1 (monitoring and measurement).
- **NIST AI RMF:** ATF levels map to GOVERN, MAP, MEASURE, and MANAGE functions; Level 4 requires implementation of the full MANAGE function including continuous improvement.
- **EU AI Act Article 9:** High-risk AI systems (Article 6, Annex III) operating at ATF Level 3 or above require documentation consistent with EU AI Act Article 11 (technical documentation) and Article 12 (logging obligations).

---

## 6. Model Context Protocol (MCP) Security — The New Attack Surface

### Background

Anthropic introduced the Model Context Protocol in November 2024 as an open standard for agent-tool communication. MCP defines: a JSON-RPC based transport, a server-side tool definition schema, a client-side tool discovery mechanism, and a credential management model. Within six months of publication, MCP had been adopted by the major agent frameworks (LangChain, LlamaIndex, CrewAI, AutoGen/MAF, Haystack) as the standard tool interface, replacing dozens of proprietary implementations.

The concentration of the tool interface into a single protocol is architecturally beneficial — it enables interoperability, standardised testing, and consistent tooling. It is also a single point of failure: an attacker who compromises an MCP server, or who successfully registers a malicious MCP server in an agent's discovery path, can affect every agent that trusts that server.

### The First Malicious MCP Package

In September 2025, the first confirmed malicious MCP package was discovered in a public MCP server registry. The package masqueraded as a legitimate file system tool, providing genuine file read/write functionality while silently exfiltrating file path metadata and content hashes to an external endpoint. It remained undetected for approximately two weeks before being identified through network traffic analysis.

The incident established that:
1. Public MCP registries are not curated and do not enforce authenticity.
2. Malicious MCP servers can provide legitimate functionality while performing secondary malicious operations.
3. The standard MCP client discovery mechanism does not authenticate server identity.

### CVE-2025-6514: Command Injection via Malicious MCP Servers

CVE-2025-6514 documented a class of vulnerabilities in MCP client implementations that trusted server-provided tool definitions without sanitising parameter schemas. A malicious MCP server could include shell metacharacters or command injection sequences in tool parameter default values or description fields. When the client generated a tool invocation from these definitions, the injected commands executed in the client's process context.

### The OWASP MCP Top 10 (In Progress)

OWASP has initiated a working group to develop an MCP-specific Top 10 list, expected Q3 2026. Current draft categories include:

1. Tool definition poisoning (malicious parameter schemas)
2. Credential centralisation (MCP credentials grant access to all registered tools)
3. Discovery spoofing (DNS/registry manipulation to redirect tool discovery)
4. Transport interception (unencrypted MCP transports)
5. Tool name collision (typosquatting at the MCP registry level)
6. Excessive tool scope (tools registered with broader permissions than stated)
7. Stateful session abuse (MCP session state persisted across agent invocations)
8. Server impersonation (no cryptographic server identity in base MCP spec)
9. Callback injection (malicious content in tool return values)
10. Registry supply chain (compromised dependencies in MCP server implementations)

### Key Threats and Controls

| Threat | Description | Control |
|---|---|---|
| Tool poisoning via discovery | Malicious MCP server registered in discovery path | Maintain internal, signed tool registry; do not use public discovery in production |
| Credential centralisation | Single MCP credential grants access to all tools | Issue per-tool, per-session credentials; rotate on session end |
| Tool name collision | Malicious tool with similar name to legitimate tool | Enforce allowlist by exact name + cryptographic signature; reject name-only matching |
| Malicious return values | Tool output contains embedded adversarial instructions | Sanitise all tool outputs before re-injection into agent context (ASI01 control) |

### Recommended MCP Security Configuration

```python
# Minimum secure MCP configuration for production agents

MCP_SECURITY_CONFIG = {
    # Never use dynamic public discovery in production
    "tool_discovery": "internal_registry_only",
    # Require cryptographic signature for all tool definitions
    "tool_signature_verification": True,
    # Per-session credentials; revoke on session end
    "credential_scope": "session",
    # Sanitise tool outputs before routing to agent context
    "output_sanitization": True,
    # Log all tool invocations with full input/output
    "audit_all_invocations": True,
    # Reject tools not in the explicit allowlist
    "tool_allowlist_enforcement": "strict",
}
```

---

## 7. Key 2026 Python Ecosystem Versions

Developer reference for agent framework versions current as of 2026. Use these versions when resolving dependencies in agentic governance tooling.

### Agent Orchestration Frameworks

| Framework | Current Version | Status | Notes |
|---|---|---|---|
| LangChain | 0.3.x | Active | Primary entry point remains `langchain-core`; `langchain-community` for integrations |
| LlamaIndex | 0.14.x | Active | Workflow API (`llama-index-core.workflow`) is the recommended agent pattern |
| CrewAI | 1.14.x | Active | Multi-agent orchestration; `crewai.tools` for tool integration |
| Haystack | 2.27.x | Active | Pipeline-based; `@component` decorator for governance integration points |
| DSPy | 2.5.x | Active | Programmatic LM interaction; `Module.forward()` for guard integration |
| AutoGen | 0.4.x (maintenance) | Maintenance | Superseded by Microsoft Agent Framework; no new feature development |
| Semantic Kernel | 1.41.x (maintenance) | Maintenance | Superseded by Microsoft Agent Framework; `Plugin` API still functional |
| Microsoft Agent Framework (MAF) | 1.0.x | Active | Enterprise successor to AutoGen + Semantic Kernel; `process(message, next_handler)` middleware pattern |
| Pydantic AI | 0.x (emerging) | Active | Type-safe agent tool definitions; native Pydantic v2 integration |

### Data and Type Libraries

| Library | Current Version | Notes |
|---|---|---|
| Pydantic | 2.12.x | Required for all modern framework integrations; v1 compatibility layer deprecated |
| FastAPI | 0.135.x | Primary framework for agent API endpoints |
| Pydantic AI | 0.x | New library for type-safe agent tool definitions |

### Vector Store Clients

| Library | Current Version | Notes |
|---|---|---|
| Pinecone | 8.x | `pinecone.Index` for retrieval; batch upsert for indexed content verification |
| Weaviate | 4.x | `weaviate.connect_to_*` factory pattern in v4 client |
| ChromaDB | 1.5.x | `chromadb.HttpClient` for production; persistent client for local development |
| Qdrant | 1.x | `qdrant_client.QdrantClient`; supports payload filtering for anomaly scoring |

### Version Pinning Recommendation

```toml
# pyproject.toml — minimum secure versions for agentic governance tooling
[project]
dependencies = [
    # Agent frameworks — pin to minor version for stability
    "langchain-core>=0.3.0,<0.4.0",
    "llama-index-core>=0.14.0,<0.15.0",
    "crewai>=1.14.0,<2.0.0",
    "haystack-ai>=2.27.0,<3.0.0",
    # Type safety
    "pydantic>=2.12.0,<3.0.0",
    # MAF — new enterprise standard
    "microsoft-agent-framework>=1.0.0",
]
```

---

## 8. Gap Analysis: What Most Teams Are Missing in 2026

Based on analysis of production agentic deployments reviewed against the OWASP Agentic Top 10 2026 and CSA ATF, the following gaps are systematically present in teams that have deployed agents but have not yet applied the 2026 governance frameworks.

### The 2026 Agentic Security Checklist

Use this checklist to assess a production agentic system. Each item maps to one or more OWASP ASI categories.

```
TOOL SECURITY
[ ] Tool allowlisting (not blocklisting) — only explicitly approved tools
    may be invoked; all others are denied by default.          [ASI02]
    
[ ] Cryptographic verification of tool definitions — MCP server 
    identity and tool parameter schemas verified against signed 
    registry entries before use.                               [ASI06]
    
[ ] Per-session, JIT credentials — tool access credentials issued 
    at session start, scoped to session, revoked at session end.
    No persistent cross-session agent credentials.             [ASI05]

CONTEXT SECURITY
[ ] Injection detection on all external input — documents, tool 
    outputs, web content, and memory entries validated against 
    injection pattern library before routing to agent context. [ASI01]
    
[ ] Document integrity verification — retrieved documents verified 
    against checksums or digital signatures; anomaly scoring 
    applied; high-anomaly documents flagged before agent sees 
    them.                                                      [ASI04]
    
[ ] Tool output sanitisation — all tool return values sanitised 
    before re-injection into agent context; no raw tool output 
    in agent prompt.                                           [ASI01]

MEMORY SECURITY
[ ] Session-scoped memory — episodic, semantic, and working memory 
    scoped to authenticated session and user; no cross-session 
    or cross-user memory reads.                                [ASI03]
    
[ ] Memory purge on session end — all session memory purged or 
    encrypted with session-specific keys on session termination.[ASI03]

OUTPUT SECURITY
[ ] DLP scan on all agent outputs — outputs scanned for PII, 
    credentials, and sensitive data before delivery to user.   [ASI03]
    
[ ] Capability scope verification — agent outputs verified to be 
    within the documented capability scope; outputs claiming 
    capabilities the agent does not have are blocked.          [ASI07]
    
[ ] Confidence disclosure — low-confidence outputs disclosed 
    as such; confidence score included in response metadata.   [ASI07]

ACTION SECURITY
[ ] Irreversible action gates — all irreversible actions (deletes, 
    sends, purchases, publishes) require rollback capability 
    verification before execution.                             [ASI08]
    
[ ] High-impact human-in-the-loop — actions classified as 
    high-impact require human confirmation before execution.   [ASI08]
    
[ ] Compensation transactions — every write operation in the 
    agent workflow has a documented rollback/compensation 
    procedure.                                                 [ASI08]

MULTI-AGENT SECURITY
[ ] Sender identity verification — all messages in multi-agent 
    pipelines carry cryptographically verifiable sender identity; 
    messages from unverified senders are rejected.             [ASI10]
    
[ ] Agent-specific credentials — agents have separate identity 
    credentials distinct from user credentials; do not inherit 
    user identity.                                             [ASI05, ASI10]

OBSERVABILITY
[ ] Per-step audit trail — structured audit record emitted for 
    every tool invocation, memory access, and agent decision step;
    records include actor, session, tool, input hash, output hash,
    timestamp.                                                 [ASI09]
    
[ ] Append-only audit log — audit records stored in tamper-evident,
    append-only log; not in mutable application database.      [ASI09]
    
[ ] Intent verification before tool invocation — agent's stated 
    intent for a tool call is logged and verified against the 
    tool's purpose specification before execution.             [ASI02, ASI09]
```

### The Most Common Critical Gaps

**Gap 1: Blocklisting instead of allowlisting for tools (ASI02)**

The most common configuration error. Teams define a list of prohibited tools (blocklist) rather than an explicit list of permitted tools (allowlist). A blocklist can never be complete — it must be updated every time a new attack technique is discovered. An allowlist is complete by construction — anything not on the list is denied. In 2026, tool allowlisting is the expected baseline; blocklisting is not an acceptable control.

**Gap 2: No cryptographic verification of MCP tool definitions (ASI06)**

Following CVE-2025-6514 and the September 2025 malicious MCP package incident, cryptographic verification of MCP server identity and tool definitions is required. Most teams that adopted MCP in 2024–2025 have not implemented signature verification — they trust the tool definition as received. This trust is exploitable.

**Gap 3: Agent identities inherited from users (ASI05, ASI10)**

The most architecturally expensive gap to remediate. When an agent inherits the user's identity and credentials, the agent's access scope equals the user's access scope — typically far broader than the agent's operational requirements. Separate agent identity requires changes to identity infrastructure, credential management, and audit systems. The CSA ATF makes this a Level 2 requirement (Controlled Production) — it is not optional for production deployments.

**Gap 4: No JIT access — tools have permanent permissions (ASI05)**

Related to Gap 3. Tools are typically granted permanent access during configuration. A tool that is granted filesystem read access has that access continuously, not just during the invocations where it is legitimately needed. JIT access — granting permissions at invocation time, revoking at session end — dramatically reduces the window of exposure from a compromised tool.

**Gap 5: No semantic output validation before agent actions (ASI07, ASI08)**

Agents sometimes claim capabilities they do not have, or produce outputs with confidence levels that do not warrant the claimed certainty. Without semantic validation of outputs against the agent's documented capability scope, users receive outputs that may be fabricated, over-confident, or outside the agent's design parameters.

**Gap 6: Memory not session-scoped — cross-session data leakage risk (ASI03)**

Persistent memory that spans sessions creates cross-contamination risk: data from User A's session can appear in User B's context. This is a data leakage vulnerability that cannot be addressed by DLP scanning alone — it requires architectural changes to memory storage and retrieval.

**Gap 7: No intent verification before tool invocation (ASI02, ASI09)**

An agent should be able to articulate why it is invoking a specific tool. If the agent cannot provide a coherent justification — or if the justification does not match the tool's intended purpose — the invocation should be blocked and reviewed. Most frameworks do not implement intent verification; it requires an additional reasoning step before each tool call.

---

## References

- OWASP Top 10 for Agentic Applications 2026 (December 2025). OWASP Foundation. Available at: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Agent Standards Initiative (February 2026). National Institute of Standards and Technology, Information Technology Laboratory.
- NIST AI 600-1: Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (July 2024). NIST.
- CSA Agentic Trust Framework v1.0 (February 2026). Cloud Security Alliance AI Safety Working Group.
- MITRE ATLAS v5.1 (November 2025). MITRE Corporation. Available at: https://atlas.mitre.org/
- ISO/IEC 42001:2023 — Artificial Intelligence Management System. International Organisation for Standardisation.
- Anthropic. Model Context Protocol Specification (November 2024). Available at: https://modelcontextprotocol.io/
- CVE-2025-6514. NIST National Vulnerability Database.
- Zenity Labs. Enterprise Agentic AI Attack Patterns (2025). Contributed to MITRE ATLAS v5.1.
