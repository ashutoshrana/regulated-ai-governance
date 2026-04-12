# Contributing to regulated-ai-governance

Thank you for your interest. This library provides policy enforcement, PII
detection, consent management, and data lineage tracking for AI agents
operating under FERPA, HIPAA, GDPR, CCPA, GLBA, and SOC 2.

Contributions that extend regulation coverage, add framework adapters, improve
audit accuracy, or strengthen compliance guarantees are welcome.

---

## Table of contents

1. [Development setup](#1-development-setup)
2. [Repository structure](#2-repository-structure)
3. [How to add a regulation module](#3-how-to-add-a-regulation-module)
4. [How to add a framework adapter](#4-how-to-add-a-framework-adapter)
5. [PR checklist](#5-pr-checklist)
6. [Out of scope](#6-out-of-scope)

---

## 1. Development setup

```bash
git clone https://github.com/ashutoshrana/regulated-ai-governance.git
cd regulated-ai-governance

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pre-commit install
```

Run tests:

```bash
pytest --tb=short -q
```

Type check and lint:

```bash
mypy src/
ruff check src/ tests/
ruff format src/ tests/
```

---

## 2. Repository structure

```
src/regulated_ai_governance/
├── regulations/         # One module per regulation (FERPA, HIPAA, GDPR …)
├── adapters/            # Framework-specific adapters (CrewAI, AutoGen, SK …)
├── integrations/        # LangChain, LlamaIndex, Haystack callbacks
├── pii_detector.py      # Zero-dependency PII scanning
├── consent_store.py     # Consent registry with expiry support
└── lineage_tracker.py   # Audit lineage trail for regulated pipelines
```

---

## 3. How to add a regulation module

1. Create `src/regulated_ai_governance/regulations/<regulation>.py`
2. Export a `<Regulation>Policy` class and a `<Regulation>Record` dataclass
3. Provide factory functions (e.g. `make_advisor_policy()`, `make_student_policy()`)
4. Add a test file `tests/regulations/test_<regulation>.py` covering:
   - Policy construction and attribute values
   - Record creation and `to_log_entry()` format
   - Edge cases (None fields, empty categories)
5. Add the module to `src/regulated_ai_governance/regulations/__init__.py`
6. Document in `ECOSYSTEM.md` under the appropriate regulatory table entry

---

## 4. How to add a framework adapter

1. Create `src/regulated_ai_governance/adapters/<framework>.py`
2. Wrap the framework's agent or tool class; add policy enforcement as a pre-call hook
3. Raise `PermissionError` on policy violation (consistent with existing adapters)
4. Add a test file `tests/adapters/test_<framework>.py`
5. Add a runnable example `examples/0N_<framework>_adapter.py`
6. Update `ECOSYSTEM.md` to list the framework under "Supported frameworks"

---

## 5. PR checklist

- [ ] Tests pass: `pytest -q`
- [ ] No mypy errors: `mypy src/`
- [ ] No ruff errors: `ruff check src/ tests/`
- [ ] New behaviour is tested; coverage does not decrease
- [ ] Public functions have docstrings
- [ ] `ECOSYSTEM.md` updated if adding a new framework or regulation
- [ ] `CHANGELOG.md` `[Unreleased]` section updated

---

## 6. Out of scope

- Vendor-specific credential storage or key management
- Runtime enforcement that requires network I/O (this library is synchronous and dependency-light)
- UI components or dashboards
- Non-compliance-related general AI agent features

When in doubt, open an issue before investing time in a PR.
