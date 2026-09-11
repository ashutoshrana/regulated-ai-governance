# Common Failure Patterns

| Symptom | Root cause | Fix |
|---|---|---|
| Historical audit content changes after record creation | Mutable dataclass retains nested caller-owned context | Freeze a JSON-compatible snapshot and export independent copies; regression tests cover nested mutation |
| Audit failure cannot be distinguished from action failure for retry decisions | Decision-only events have no execution boundary | Correlate optional outcomes and expose whether the action was invoked on sink failure |
