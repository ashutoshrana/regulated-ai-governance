# EU AI Act: corrected developer guide for AI agents

> Originally published as “EU AI Act Goes Live in 90 Days” on
> [dev.to, May 1, 2026](https://dev.to/ashutoshrana/eu-ai-act-goes-live-in-90-days-what-developers-building-ai-agents-actually-need-to-do-4bah).
> **Repository correction: November 13, 2026.** The external article has not been
> edited by this repository change. The original repository text remains in
> [Git history](https://github.com/ashutoshrana/regulated-ai-governance/blob/63bf5ef3647f21e7ac11b52a2bfda5aa4404e6fd/articles/eu-ai-act-agents-developer-guide.md).

The earlier text overstated sector-based classification, misstated fines and
registration, conflated Articles 13 and 50, and included illustrative imports
that are not the current public API. Its countdown is obsolete. This corrected
note is engineering guidance, not a legal determination or complete checklist.

## Classify the intended system, not just its sector

An education, HR or financial-services agent is not automatically high-risk.
[Article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6)
requires reviewing the intended use, Annex I product/conformity-assessment
conditions or specific Annex III use, and applicable exceptions. Article 6(3)
has limited exceptions; profiling of natural persons in Annex III remains
high-risk. Document the assessment and review provider/deployer roles, including
changes to intended purpose in a multi-agent system. A human suggestion label
does not by itself settle classification.

## Timing must be checked against the amended text

The Commission's [Article 113](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113)
explorer, based on the July 27, 2026 consolidated text, now distinguishes:

- General application from August 2, 2026, with exceptions.
- Chapter III Sections 1–3, except Article 6(5): December 2, 2027 for
  Article 6(2)/Annex III systems; August 2, 2028 for Article 6(1)/Annex I systems.

These are not dates for every obligation in the Act. Consult the full transitional
provisions, Article 111 and the law applicable to the specific system before
setting a compliance deadline. The original article's August 2026 blanket
high-risk deadline must not be used as current guidance.

## Engineering patterns and their limits

- **Record-keeping (Article 12):** design appropriate event logging. An example
  print statement is not an immutable audit system. Limit sensitive data in logs,
  control access, and establish applicable retention and integrity controls.
- **Human oversight (Article 14):** provide effective, tested intervention paths.
  A confidence threshold alone does not satisfy the article; calibrate it and
  test whether the responsible human can understand and stop the system.
- **Transparency:** [Article 13](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13)
  concerns high-risk system transparency and instructions to deployers.
  [Article 50(1)](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50)
  addresses informing people of direct AI interaction, subject to exceptions.
  Article 50(5) addresses timing and accessibility. Do not conflate these with
  all explanation or human-contact duties that may apply under other provisions.
- **Accuracy, robustness and cybersecurity (Article 15):** evaluate actual failure
  modes and adversarial behavior; self-reported confidence is not proof of accuracy.
- **Risk management (Article 9):** maintain a lifecycle process, not just a
  one-page declaration or a fixed quarterly review checklist.

These are selected engineering concerns, not all legal obligations. See the
[official AI Act explorer](https://ai-act-service-desk.ec.europa.eu/en/ai-act)
for the cited articles. Use the repository's [tested quick start](../README.md#quick-start-an-installed-core-guard)
and [integration support boundaries](../ECOSYSTEM.md), rather than the earlier
article's conceptual `PolicyStack` / `create_compliant_agent` code.

## Registration and penalties

[Article 49](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-49)
contains registration duties before market placement/service for relevant
providers and systems, including certain Article 6(3) assessments, and for
specified public-sector deployers. It has special arrangements and exceptions;
there is no blanket “no pre-registration” rule. GDPR DPIAs are a separate concept.

[Article 99](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-99)
sets different penalty tiers: prohibited-practice breaches can attract up to
€35 million/7% of worldwide annual turnover; specified other breaches up to
€15 million/3%. These are ceilings, not automatic penalties. Applicability,
undertaking status, SME rules and other paragraphs matter. The previous
€30 million/6% and €20 million/4% figures were incorrect.

Before deployment, obtain a use-case-specific legal assessment and record the
source version, applicability rationale, technical evidence and unresolved gaps.
Installing a governance package does not establish legal compliance.
