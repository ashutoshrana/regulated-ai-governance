---
name: New Framework Integration
about: Propose integration of regulated-ai-governance with an AI or LLM framework
title: "[INTEGRATION] "
labels: enhancement, framework-integration
assignees: ''
---

## Framework
<!-- e.g. "DSPy", "LangGraph", "PydanticAI", "Smolagents" -->

## Framework Version
<!-- What version are you targeting? -->

## Integration Point
<!-- How does regulated-ai-governance fit into this framework?
     e.g. "as a DSPy module wrapper that checks ActionPolicy before forward() runs" -->

## Wrapping Strategy
<!-- Which base class or hook does the integration use?
     e.g. extends BaseTool, implements __call__, wraps the agent's run() method -->

## Regulation Coverage
<!-- Which regulations should the integration handle? FERPA / HIPAA / GDPR / all? -->

## Proposed API (sketch)
```python
# Show the key class and method signatures
```

## Dependencies Required
<!-- What new optional dependencies would be added to pyproject.toml? -->

## Would you like to implement this?
- [ ] Yes, I will submit a PR
- [ ] No, requesting someone else implement it
