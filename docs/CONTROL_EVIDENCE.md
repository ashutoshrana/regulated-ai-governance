# Control evidence and applicability

The library evaluates supplied inputs against encoded policy rules. A boolean
such as `consent_obtained=True` is caller-supplied evidence, not independent proof.
An allow decision is not a determination that a deployment complies with a law.
Examples may represent laws, proposals, standards, or guidance: assess each
source's current status and applicability before production use.

Maintain a versioned record alongside each deployed policy:

| Field | Required content |
|---|---|
| control_id / policy_version | Stable control identifier and deployed version |
| official_source / section | Authoritative URL and exact source section |
| source_status | Enacted law, draft, guidance, or standard; do not conflate |
| effective_date / reviewed_date | Verified dates, or explicitly unknown |
| applicability | Jurisdiction, role, processing purpose and exclusions |
| evidence_status | Supplied, independently verified, missing, or contradictory |
| verifier / evidence_locator | Authorized verifier and restricted evidence reference |
| test_reference | Executable allowed/denied cases for the implemented control |
| limitations | Requirements this software does not enforce |

Do not send private evidence or personal data to public issue trackers. Keep
source/evidence references separate from public synthetic fixtures. Missing or
contradictory required evidence should route to the application's review policy.

This schema is a review checklist, not a claim that the repository's historical
jurisdiction catalog has received a current legal review.
