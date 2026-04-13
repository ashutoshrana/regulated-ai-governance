---
description: How to add a new AI governance filter example to regulated-ai-governance
---

# Skill: Add a New Governance Filter

Use this when adding a new regulatory jurisdiction or framework to regulated-ai-governance. Focus on US and EU jurisdictions first.

## Files to create

1. `examples/NN_<jurisdiction>_ai_governance.py` — the filter implementation
2. `tests/test_NN_<jurisdiction>_ai_governance.py` — tests using importlib loader

## Filter structure (frozen dataclass)

Every filter is a `@dataclass(frozen=True)` with a single `filter(self, doc: dict) -> FilterResult` method.

```python
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FilterResult:
    decision: str               # APPROVED / DENIED / REDACTED / REQUIRES_HUMAN_REVIEW
    reason: str
    regulation_citation: str
    requires_logging: bool = True

    @property
    def is_denied(self) -> bool:
        return self.decision == "DENIED"  # NOT True for REDACTED or REQUIRES_HUMAN_REVIEW

@dataclass(frozen=True)
class MyJurisdictionAIFilter:
    def filter(self, doc: dict) -> FilterResult:
        # Rule: block prohibited use case
        if doc.get("use_case") == "prohibited":
            return FilterResult(
                decision="DENIED",
                reason="Prohibited AI use case under Regulation Name",
                regulation_citation="Regulation Name Art. N — description",
            )
        # Rule: escalate high-risk without oversight
        if doc.get("risk_level") == "high" and not doc.get("human_oversight"):
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                reason="High-risk AI requires human oversight",
                regulation_citation="Regulation Name Art. N — oversight requirement",
            )
        return FilterResult(
            decision="APPROVED",
            reason="Compliant with Regulation Name",
            regulation_citation="Regulation Name Art. N",
        )
```

## Using GovernancePipeline (src/ package)

```python
from regulated_ai_governance.base import GovernancePipeline, FilterResult

pipeline = GovernancePipeline([
    MyJurisdictionAIFilter(),
    MyCrossBorderFilter(),
], stop_on_review=False)  # True to block on REQUIRES_HUMAN_REVIEW too

result = pipeline.run(document)
if result.is_denied:
    raise PermissionError(result.reason)
if result.requires_review:
    escalate_to_human(document, result.reason)
```

## 4-filter structure per example

Every example must have exactly 4 filter classes:
1. Primary AI governance filter (main regulation)
2. Sector-specific or data protection filter
3. Transparency / human oversight filter
4. Cross-border transfer filter (if jurisdiction-specific)

## Test import pattern (required)

```python
import importlib.util, sys, types, os

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = types.ModuleType(name)
    sys.modules[name] = mod   # MUST register before exec_module
    spec.loader.exec_module(mod)
    return mod

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples')
m = load_module("gov", os.path.join(EXAMPLES_DIR, "NN_jurisdiction_ai_governance.py"))
```

## Integration wrappers (required at bottom of every example)

Copy the 8 wrapper stubs from the previous example and rename the prefix:
`LangChain`, `CrewAI`, `AutoGen`, `SemanticKernel`, `LlamaIndex`, `Haystack`, `DSPy`, `MAF`

Each wrapper enforces all 4 filters and raises `PermissionError` on DENIED.
Haystack wrapper silently excludes denied documents instead of raising.

## README update (required)

1. **Header** (line 9): `29 examples, 16 jurisdictions, 1491 tests` → increment all three
2. **Catalog table heading**: increment count
3. **Catalog row**: `| NN | \`file.py\` | Jurisdiction | Key framework + cross-border rules |`
4. **Jurisdiction coverage matrix**: add row `| **Jurisdiction** | Laws + provisions | NN |`
5. **`examples/ # NN runnable`**: update in repo structure section
6. **Trilogy footer** — update in ALL THREE repo READMEs

## CHANGELOG entry

```markdown
## [vX.Y.Z] — YYYY-MM-DD

### Added — Jurisdiction AI Governance (`NN_file.py`)

- `JurisdictionFilter1` (Law Name YYYY) — DENIED condition; REQUIRES_HUMAN_REVIEW condition
- `JurisdictionFilter2` (Law Name YYYY) — DENIED condition
- `JurisdictionFilter3` (Law Name YYYY) — DENIED condition
- `JurisdictionCrossBorderFilter` — adequacy list; sanction-country denial

N new tests. Total: **NNNN passed**.
```

## Version bump

Bump `version` in `pyproject.toml`, `__version__` in `src/regulated_ai_governance/__init__.py`, and citation in README.

## Priority jurisdictions

Current priority order (US and EU first):
1. US state AI laws (Colorado SB 205, Connecticut SB 2, Illinois BIPA, Virginia CDPA)
2. EU sector-specific (DORA for financial, NIS2 for critical infrastructure)
3. EU AI Act high-risk system details
4. GDPR enforcement additions
