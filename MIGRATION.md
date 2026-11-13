# Migration notes

## CrewAI security quarantine (0.46.0)

The CrewAI extra is removed from package metadata and `[all]` because its SDK graph brings unresolved ChromaDB advisories. Existing adapter modules and callable APIs remain for legacy callers, but native CrewAI support is suspended. Recreate environments using supported extras; removing an extra does not uninstall old dependencies. Restoration gates and review limits are documented in SECURITY.md. The Semantic Kernel extra separately requires Werkzeug>=3.1.9 to exclude its affected transitive versions.

## Python support by installation path

The core package remains supported on Python 3.10+. `llama-index`, `autogen`, `semantic-kernel` and `all` require Python 3.11+ because the patched Pillow 13 / dnspython 2.9 dependency versions no longer support 3.10. These fixed dependencies are unconditional: requesting an affected extra on Python 3.10 fails dependency resolution rather than silently omitting its SDK or selecting an affected older fallback. The native SDK CI matrix for these paths runs on Python 3.11 and 3.12. Other extras and core tests retain their declared Python 3.10 support.

## Category and audit boundary migration (0.47.0)

Omitted, `None` and empty category grants now deny private categories. An intentional trusted wildcard must set `unrestricted_categories=True`; only actual booleans are accepted (strings such as `"false"` and integers such as `1` are rejected). Explicit public classification remains an ingestion trust decision, and identity/tenant checks remain mandatory. Authenticate the caller and derive grants in the host application; this option is not authentication or legal eligibility.

`FERPAComplianceCallbackHandler(..., allowed_categories={"academic_record"})` supplies a finite grant. The old identity-only `None` behavior now requires `unrestricted_categories=True`; do not silently pass an empty caller grant set as unrestricted. The callback filters retrieval results after the read; use a governance start guard when the read itself must be authorized.

With `audit_execution=True`, synchronous action cancellation now emits a correlated `execution` event with outcome `cancelled` and re-raises the original cancellation. Other action failures emit `failed` and re-raise the original action exception. If terminal audit delivery also fails, the original action exception remains primary and the delivery error is chained as its cause (ordinary sink errors retain `AuditDeliveryError.action_executed=True`). A terminal sink BaseException is likewise chained without replacing the original action error. A sink failure after a successful action still raises `AuditDeliveryError(action_executed=True)`. No rollback, blind retry, awaited async-completion or abrupt-process-exit guarantee is added.

The security-supported SDK floors are now LangChain Core 1.3.3 and LlamaIndex Core 0.13.0; older functional minimums are no longer advertised because they match known official advisories. Haystack 2.20.0 remains the minimum native pipeline test version. Current SDK versions are not upgraded solely for novelty.

## Legacy AutoGen install quarantine (0.47.0)

The `autogen` extra is removed: the advertised pyautogen 0.4 minimum brings DiskCache with unresolved advisories, while current pyautogen releases target a different AgentChat API. A direct-package advisory lookup returning no findings does not clear that transitive graph. Existing object wrappers and callable APIs remain for compatibility, but native SDK installation/support is quarantined. Do not treat an unknown-extra pip warning as SDK installation or migrate silently to a different agent API. No licenses or third-party history are removed. Restoration requires a reviewed clean dependency graph and native boundary tests for the actual supported API.

Sink cancellation keeps the original `CancelledError` identity and task semantics. It now carries `action_executed` and `correlation_id` (False before action invocation, True at terminal delivery) instead of being wrapped as an ordinary sink error. Inspect these markers and reconcile application state; do not assume cancellation means no side effect or automatically retry it.

## Corrected OWASP example citations (0.47.1)

Example 39 retains class names, metadata inputs and allow/deny/review predicates,
but its `regulation` and `reason` strings now use corrected category references.
Consumers that parsed these display strings must update mappings: old ASI04
poisoning -> ASI06; old ASI05 privilege -> ASI03; old ASI06 supply chain -> ASI04;
old ASI07 trust -> ASI09; old ASI10 composition -> ASI07. Output DLP and audit
checks use `LOCAL-DLP` and `LOCAL-AUDIT`; memory isolation uses ASI06.
The taxonomy constant now contains the official ten categories, including ASI05
code execution and ASI10 rogue agents, for which this example has no dedicated
check. It must not be represented as full Top 10 enforcement.

Existing missing-metadata and review behavior is unchanged: wrappers raise only
on `DENIED`. Explicitly stop and route `REQUIRES_HUMAN_REVIEW` before executing
an action. These duck-typed examples are not qualified SDK integrations or a
production security boundary. See [scope](docs/agentic-security-trends-2026.md).
