# Roadmap

This roadmap supersedes historical future-version labels that fell behind source
releases. Source versions do not imply PyPI or GitHub release publication.

## Implemented in the reliability branch

- Immutable audit snapshots and independent serialization.
- Required audit sink configuration and optional execution outcome records.
- Correlated failure semantics with regression checks.
- Explicit control evidence and applicability guidance.

## Adoption validation

- Run the cross-repository synthetic service workflow on supported dependencies.
- Validate application-specific durable audit sinks and redaction requirements.
- Collect reproducible external integration reports; no external adoption is claimed.

## Expansion gate

Add a framework or jurisdiction only with a concrete use case, authoritative
control mapping, real integration tests, and a maintainer for version drift.
