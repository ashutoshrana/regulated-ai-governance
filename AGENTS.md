# Common Failure Patterns

| Symptom | Root cause | Fix |
|---|---|---|
| Historical audit content changes after record creation | Mutable dataclass retains nested caller-owned context | Freeze a JSON-compatible snapshot and export independent copies; regression tests cover nested mutation |
| Audit failure cannot be distinguished from action failure for retry decisions | Decision-only events have no execution boundary | Correlate optional outcomes and expose whether the action was invoked on sink failure |
| Required audit executes an action with an unawaited sink | Calling an async sink returns before delivery | Reject async sinks and awaitable returns before action execution |
| Release uploads can drift from tested package identity | Release publication previously rebuilt without tag/source/runtime/artifact checks | Check out the release event commit, require matching stable tag and package versions, rerun tests and validate wheel/sdist plus an isolated installed-wheel import before OIDC upload |
