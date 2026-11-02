# Common Failure Patterns

| Symptom | Root cause | Fix |
|---|---|---|
| Historical audit content changes after record creation | Mutable dataclass retains nested caller-owned context | Freeze a JSON-compatible snapshot and export independent copies; regression tests cover nested mutation |
| Audit failure cannot be distinguished from action failure for retry decisions | Decision-only events have no execution boundary | Correlate optional outcomes and expose whether the action was invoked on sink failure |
| Required audit executes an action with an unawaited sink | Calling an async sink returns before delivery | Reject async sinks and awaitable returns before action execution |
| Release uploads can drift from tested package identity | Release publication previously rebuilt without tag/source/runtime/artifact checks | Check out the release event commit, require matching stable tag and package versions, rerun tests and validate wheel/sdist plus an isolated installed-wheel import before OIDC upload |
| Denied native LangChain tools still execute, or filtered documents remain in results | Callbacks swallow exceptions by default and ignore returned replacement lists | Propagate start-callback exceptions, guard retrieval before reads, and filter the native result list in place; verify actual tool and retriever invocation |
| An integration cannot require an audit sink, or silently substitutes a no-op sink | Factories omitted the shared guard's require_audit configuration and invented fallback sinks | Forward the requirement through integration factories and preserve missing sinks so guard construction rejects them |
| Advertised skill factories fail even with their SDKs installed | Factories passed unsupported constructors or imported nonexistent wrapper classes, while tests only simulated missing imports | Delegate existing skill audit methods through native SDK types and test allow, deny, audit-only and sink-failure behavior with installed frameworks |
| Release workflow uses an advisory-affected or mutable publishing action | A dependency update in one repository left equivalent release workflows unchanged | Pin every publishing workflow to the verified patched action commit and validate each workflow before release |
| Installed MAF dependencies still fail the middleware availability check | The legacy adapter imported microsoft_agent_framework rather than the installed agent_framework namespace and claimed a nonexistent middleware base | Check the native namespace, preserve legacy on_message explicitly, and register the tested as_native function-middleware bridge |

| Installed-package quick starts fail before evaluating a policy | README used undefined application objects and imported a nonexistent packaged examples module | Use a complete public-core guard example, execute its fenced code in a regression test, and label repository sketches separately |

| Combined optional dependencies select an advisory-affected Werkzeug | Semantic Kernel brings an older openapi-core graph whose broad constraint permits the affected release | Add the patched Werkzeug floor to the Semantic Kernel extra and rescan the resolved graph without suppressing independent upstream findings |

| A supported optional install automatically brings outstanding advisory findings | SDK transitive graphs contain unresolved vulnerabilities and no reviewed compatible clean graph | Remove affected extras from metadata and all, preserve adapter APIs as security quarantined, and require fresh per-extra/Python audits plus native tests before restoration |

| Python 3.10 optional installs select vulnerable dependencies while Python 3.12 scans clear | Fixed dependency releases require Python 3.11, so the resolver falls back to affected older versions | Keep core 3.10 support, add unconditional patched floors to affected extras, document 3.11 SDK contracts and treat 3.10 rejection as an excluded support cell |

| README describes an available release as unpublished or labels an older release current | A release-time version snapshot was kept as permanent project status prose | Link to the stable PyPI project and changelog instead of embedding current-release assertions; preserve historical published artifact text |
