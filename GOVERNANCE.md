# Governance

## Maintainer

`regulated-ai-governance` is maintainer-led. The current maintainer is
**Ashutosh Rana** ([@ashutoshrana](https://github.com/ashutoshrana)).

Decisions about scope, API design, and releases are made by the maintainer.
Community input is welcomed via Issues and Discussions.

## Scope policy

This library is intentionally narrow: policy enforcement, PII detection,
consent management, and data lineage for regulated AI workloads. It does not
aim to be a general-purpose compliance platform. Contributions that expand
the regulation catalogue or add framework adapters are welcomed; features that
expand scope beyond compliance enforcement are out of scope.

## Releases

Releases follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
A new release is cut when a meaningful set of features or fixes has
accumulated. Release notes are published in `CHANGELOG.md` and as GitHub
Releases.

## Merging PRs

- The maintainer reviews all PRs.
- Tests must pass; type checks must pass; ruff must report no errors.
- A PR that adds a new regulation module or framework adapter must include
  a test file and a `CHANGELOG.md` entry.
- The maintainer may close PRs that are out of scope, duplicate existing
  functionality, or do not meet quality standards, without extended debate.

## Code of conduct

All interactions in this repository are governed by the
[Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
