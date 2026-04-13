# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.21.0] — 2026-04-13

### Added — Australian AI Governance (AI Ethics Framework + Privacy Act APPs + DTA ADM + AHRC Guidelines)

**`examples/19_australia_ai_governance.py`** — four-layer Australian AI governance orchestrator
covering the Australian AI Ethics Framework (DIIS 8 principles), Privacy Act 1988 Australian
Privacy Principles (APPs), Digital Transformation Agency (DTA) Automated Decision-Making
(ADM) Framework for Commonwealth government agencies, and Australian Human Rights Commission
(AHRC) AI and Human Rights guidelines.

**New classes:**
- `AustralianAIRiskLevel` — HIGH_RISK / MEDIUM_RISK / LOW_RISK / EXEMPT
- `AustralianAIDecision` — APPROVED / APPROVED_WITH_CONDITIONS / DENIED
- `AustralianSector` — GOVERNMENT / PRIVATE_SECTOR / HEALTH / FINANCIAL_SERVICES / EDUCATION
- `AustraliaAIContext` (frozen) — 20-field context: system identity, risk level, sector,
  AI Ethics Framework fields (7 principles: wellbeing, human-centred, privacy, reliability,
  transparency, contestability, accountability), Privacy Act APPs fields (APP 1/3/6/11),
  DTA ADM fields (human review right, explanation obligation, record-keeping — government only),
  AHRC fields (non-discrimination assessment, accessible design)
- `AustraliaAIGovernanceResult` — per-layer result with is_denied / has_conditions properties
- `AustralianAIEthicsFilter` — DIIS 8 principles: Principles 1–7 individually enforced;
  EXEMPT systems approved with monitoring note; Principle 8 (Fairness) in conditions
- `PrivacyActAPPsFilter` — Privacy Act 1988: APP 1 (transparency), APP 3 (collection),
  APP 6 (use/disclosure), APP 11 (security); NDB scheme and APP 12/13 rights in conditions
- `DTAADMFilter` — DTA ADM Framework: applies to GOVERNMENT sector only; human review right,
  explanation obligation, FOI-compatible record-keeping; non-government → pass with note
- `AHRCAIGuidelinesFilter` — AHRC guidelines: non-discrimination and equality assessment;
  accessibility (Disability Discrimination Act 1992) for medium/high-risk only; First Nations
  consultation referenced in conditions
- `AustraliaAIGovernanceOrchestrator` — sequential four-layer evaluation
- `AustraliaAIGovernanceReport` — `summary()` with system metadata, sector, and per-layer results

**Tests:** 32 tests in `tests/test_australia_ai_governance.py`

---

## [0.20.0] — 2026-04-13

### Added — Canadian AI Governance (AIDA Bill C-27 + CPPA + OPC AI Guidelines + Québec Law 25)

**`examples/18_canada_ai_governance.py`** — four-layer Canadian AI governance orchestrator
for AI systems deployed in Canada, enforcing Bill C-27 Artificial Intelligence and Data Act
(AIDA) high-impact system requirements, Consumer Privacy Protection Act (CPPA, replacing
PIPEDA) data governance obligations, OPC AI Guidelines 2023 cross-cutting principles, and
Québec Law 25 (Act 25) algorithmic transparency and privacy impact assessment requirements
(in force September 2023).

**New classes:**
- `CanadianAIRiskLevel` — HIGH_IMPACT / MEDIUM_IMPACT / LOW_IMPACT / EXEMPT
- `CanadianAIDecision` — APPROVED / APPROVED_WITH_CONDITIONS / DENIED
- `CanadaAIContext` (frozen) — 18-field context: system identity, risk level, deploying
  province (QC triggers Law 25), AIDA fields (is_high_impact_system,
  impact_assessment_completed, transparency_notice_provided, ministerial_order_compliant),
  CPPA fields (meaningful_consent_obtained, purpose_limitation_documented,
  data_minimization_applied, cross_border_transfer_safeguards), OPC fields
  (human_oversight_available, accuracy_measures_in_place, accountability_framework_exists),
  Québec Law 25 fields (privacy_impact_assessment_done, algorithmic_transparency_published,
  data_governance_officer_designated)
- `CanadaAIGovernanceResult` — per-layer result with is_denied / has_conditions properties
- `AIDAComplianceFilter` — Bill C-27 AIDA s.6/9/10/11/35: HIGH_IMPACT system impact
  assessment, transparency notice, ministerial order compliance; EXEMPT and LOW_IMPACT paths
- `CPPADataGovernanceFilter` — CPPA s.12/13/15/24: meaningful consent, purpose limitation,
  data minimization, cross-border transfer safeguards; s.62/63 portability conditions
- `OPCGuidelinesFilter` — OPC AI Guidelines 2023 (1–5): consent, human oversight, accuracy,
  accountability; conditions reference annual privacy audit
- `QuebecLaw25Filter` — Act 25 s.3.1/12/63.3: PIA before deployment, algorithmic
  transparency publication, CPO designation; non-QC provinces approved with monitoring note
- `CanadaAIGovernanceOrchestrator` — sequential four-layer evaluation
- `CanadaAIGovernanceReport` — `summary()` with system metadata, province, and per-layer results

**Tests:** 34 tests in `tests/test_canada_ai_governance.py`

---

## [0.19.0] — 2026-04-13

### Added — UK AI Governance (UK GDPR Article 22 + ICO AI Auditing + Equality Act 2010 + DSIT Safety Principles)

**`examples/17_uk_ai_governance.py`** — four-layer UK AI governance orchestrator for AI
systems deployed in the United Kingdom, enforcing UK GDPR Article 22 Automated Decision-Making
safeguards (lawful basis, human review, opt-out rights, special category consent), ICO AI
Auditing Framework 2022 requirements (bias testing, explainability, accuracy validation),
Equality Act 2010 protections (indirect discrimination assessment, reasonable adjustments,
Public Sector Equality Duty for s.149), and DSIT AI White Paper 2023 cross-sector safety
principles (Safety, Security, Accountability, Transparency, Contestability).

**New classes:**
- `UKAIRiskTier` — HIGH_RISK / MEDIUM_RISK / LOW_RISK
- `UKAIDecision` — APPROVED / APPROVED_WITH_CONDITIONS / DENIED
- `UKAIContext` (frozen) — 23-field context: system identity, risk tier, deploying sector,
  UK GDPR ADM fields (is_solely_automated, decision_has_legal_effect,
  processes_sensitive_categories, lawful_basis_documented, explicit_consent_obtained,
  human_review_available, opt_out_mechanism_provided), ICO audit fields
  (bias_testing_completed, explainability_mechanism_in_place, accuracy_validated),
  Equality Act fields (disparate_impact_assessment_done, reasonable_adjustments_supported,
  public_sector_equality_duty, equality_impact_documented), DSIT fields
  (safety_testing_completed, adversarial_testing_done, responsible_officer_designated,
  stakeholder_disclosure_made, contestability_mechanism_provided)
- `UKAIGovernanceResult` — per-layer result with decision=APPROVED default, findings list,
  conditions list; `is_denied` / `has_conditions` properties
- `UKGDPRAutomatedDecisionFilter` — Article 22 ADM: non-automated or non-legal-effect →
  APPROVED_WITH_CONDITIONS; solely-automated + legal-effect: checks lawful_basis,
  human_review, opt_out, sensitive_category consent; violations → DENIED
- `ICOAIAuditingFilter` — ICO AI Auditing Framework: checks bias_testing,
  explainability_mechanism, accuracy_validated; any missing → DENIED with ICO reference
- `UKEqualityActFilter` — Equality Act 2010: s.19 disparate impact assessment required;
  s.20/21 reasonable adjustments required; s.149 PSED equality impact assessment required
  for public sector only (private sector exempt)
- `DSITAISafetyPrinciplesFilter` — DSIT White Paper 2023 five principles: safety testing
  (Safety), adversarial testing (Security), responsible officer (Accountability),
  stakeholder disclosure (Transparency), contestability mechanism (Contestability)
- `UKAIGovernanceOrchestrator` — sequential four-layer evaluation; any DENIED → DENIED;
  all pass with conditions → APPROVED_WITH_CONDITIONS
- `UKAIGovernanceReport` — `summary()` returns dict with system metadata, final_decision,
  and per-layer results list

**Tests:** 32 tests in `tests/test_uk_ai_governance.py`

---

## [0.18.0] — 2026-04-13

### Added — EU AI Act Governance (Articles 5–7, 9–10, 13–14, 43–49, 61–62, 73)

**`examples/16_eu_ai_act_governance.py`** — four-layer governance orchestrator for AI systems
subject to the EU AI Act (Regulation (EU) 2024/1689), enforcing Risk Classification and
Prohibited Practices (Articles 5–7, Annex III), Conformity Assessment and CE Marking
(Articles 9, 43–49), Data Governance and Bias Examination (Article 10), and Transparency,
Human Oversight, and Post-Market Monitoring (Articles 13–14, 26, 61–62, 73).

**New classes:**
- `EUAIActRiskLevel` — PROHIBITED / HIGH_RISK / LIMITED_TRANSPARENCY / MINIMAL_RISK
- `AnnexIIICategory` — 8 high-risk categories: BIOMETRIC_IDENTIFICATION,
  CRITICAL_INFRASTRUCTURE, EDUCATION_VOCATIONAL, EMPLOYMENT_WORKERS, ESSENTIAL_SERVICES,
  LAW_ENFORCEMENT, MIGRATION_ASYLUM, JUSTICE_DEMOCRACY
- `EUConformityAssessmentRoute` — INTERNAL_CONTROL / THIRD_PARTY_NOTIFIED / NOT_REQUIRED
- `EUGovernanceDecision` — APPROVED / APPROVED_WITH_CONDITIONS / DENIED
- `EUAIActContext` (frozen) — 22-field governance review context covering risk level,
  Annex III category, conformity assessment route, RMS establishment, residual risk
  acceptability, post-market plan, data quality, bias examination, conformity assessment
  completion, CE marking, instructions for use, disclosure obligations, human oversight
  measures, override capability, deployer logs, and incident reporting
- `EUGovernanceResult` — per-layer result with `is_denied` / `has_conditions` properties
- `EURiskClassificationFilter` — Layer 1: unconditional DENIED for Article 5 prohibited
  practices; DENIED for HIGH_RISK without Annex III category; conditions for LIMITED_TRANSPARENCY
  disclosure; conditions for MINIMAL_RISK voluntary code adherence
- `EUConformityAssessmentFilter` — Layer 2: non-HIGH_RISK passes; HIGH_RISK checks RMS
  (Article 9), residual risk acceptance (Article 9(4)), post-market plan (Article 72),
  conformity assessment completion (Article 43), and CE marking (Article 49)
- `EUDataGovernanceFilter` — Layer 3: HIGH_RISK requires training data quality documentation
  (Article 10(2)), bias examination for protected characteristics (Article 10(5)), and active
  data monitoring; non-HIGH_RISK receives best-practice condition
- `EUTransparencyHumanOversightFilter` — Layer 4: MINIMAL_RISK early return; all non-minimal
  check instructions for use (Article 13); HIGH_RISK additionally checks human oversight
  measures (Article 14), override capability (Article 14(4)(d)), deployer logs (Article 26(6)),
  and serious incident reporting (Article 73)
- `EUAIActGovernanceOrchestrator` — four-layer orchestrator; any DENIED → DENIED; no DENIED
  + any CONDITIONS → APPROVED_WITH_CONDITIONS; all APPROVED → APPROVED
- `EUAIActGovernanceReport` — aggregated report with `summary()` method returning structured dict

**Test coverage:** 41 tests across all four layers and orchestrator, including the critical
Article 73 incident-reporting boundary: not required for LIMITED_TRANSPARENCY systems.

---

## [0.17.0] — 2026-04-13

### Added — Public Sector AI Governance (OMB M-24-10 + EO 14110 + NIST AI RMF + Section 508)

**`examples/15_public_sector_ai_governance.py`** — four-layer governance orchestrator for AI
systems deployed by or on behalf of US federal agencies, enforcing OMB M-24-10 (March 2024)
agency AI governance obligations, Executive Order 14110 (October 2023) safety and security
requirements, NIST AI Risk Management Framework AI 100-1 (2023) four-function maturity
requirements, and Section 508 / ADA accessibility and plain-language explanation obligations.

**New classes:**
- `FederalAIUseCase` — 10 use cases from BENEFITS_DETERMINATION (rights-impacting) through
  DOCUMENT_CLASSIFICATION (minimum-impact)
- `AIImpactLevel` — RIGHTS_IMPACTING / SAFETY_IMPACTING / LOW_IMPACT / MINIMUM_IMPACT
  per OMB M-24-10 classification
- `EO14110RiskTier` — DUAL_USE_FOUNDATION / SAFETY_CRITICAL / HIGH_RISK / STANDARD
- `NISTRMFLevel` — FULL / PARTIAL / MINIMAL / NONE maturity levels for AI RMF implementation
- `PublicSectorAIContext` (frozen) — 21-field governance review context covering all four
  framework dimensions
- `PublicSectorGovernanceResult` (dataclass) — per-layer result with default APPROVED
  decision, findings list, and conditions list
- `OMBM2410Filter` — Layer 1: CAIO + inventory for all non-minimum-impact AI; human review
  + appeal for rights-impacting; safety testing + incident reporting for safety-impacting;
  minimum-impact: inventory only
- `EO14110Filter` — Layer 2: red-team + TEVV for DUAL_USE_FOUNDATION; TEVV + safety testing
  for SAFETY_CRITICAL; safety testing for HIGH_RISK (with quarterly review condition);
  STANDARD: documentation condition only
- `NISTAIRMFFilter` — Layer 3: FULL → annual review condition; PARTIAL → conditions with
  missing function list; MINIMAL/NONE → denied for non-minimum-impact; minimum-impact accepts
  MINIMAL or higher
- `Section508Filter` — Layer 4: minimum-impact → employee accessibility condition; public-
  facing → 508 compliance required; rights/safety/citizen-services → plain-language
  explanations required
- `PublicSectorGovernanceReport` — aggregated report with summary() dict method
- `PublicSectorGovernanceOrchestrator` — four-layer evaluation; any DENIED → final DENIED;
  all layers evaluated regardless of earlier failures

**New tests:** 44 tests across `tests/test_public_sector_ai_governance.py`

---

## [0.16.0] — 2026-04-13

### Added — Insurance AI Governance (NAIC 2023 + FCRA + NY DFS + ECOA Disparate Impact)

**`examples/14_insurance_ai_governance.py`** — four-layer governance framework for AI/ML models
used in insurance underwriting, claims adjudication, and credit-based insurance scoring, enforcing
NAIC Model AI Governance Bulletin 2023 (documentation/validation/monitoring/explainability by risk
level), FCRA 15 U.S.C. §1681m adverse action notice requirements for credit-based insurance scores
(specific principal reasons, not generic "AI decision"), NY DFS Circular Letter 2019-1 ECDIS source
inventory and proxy discrimination validation for NY operations, and ECOA Regulation B 4/5 rule
disparate impact analysis with insufficient-data blocking.

**New classes:**
- `InsuranceAIUseCase` — UNDERWRITING_DECISION, CLAIMS_ADJUDICATION, CREDIT_SCORED_PRICING,
  FRAUD_DETECTION, MARKETING_SEGMENTATION, OPERATIONAL_ANALYTICS
- `InsuranceModelRiskLevel` — HIGH / MEDIUM / LOW (NAIC Bulletin 2023 classification)
- `FCRAAdverseActionStatus` — REQUIRED / NOT_REQUIRED / USES_PROHIBITED_FACTOR
- `DisparateImpactStatus` — PASS / FAIL / INSUFFICIENT_DATA
- `InsuranceGovernanceDecision` — APPROVED / APPROVED_WITH_CONDITIONS / DENIED
- `InsuranceModelContext` (frozen dataclass) — model_id, risk_level, use_case, intended_states,
  is_model_documented, is_model_validated, is_monitoring_active, is_explainability_available,
  uses_consumer_report, uses_credit_based_insurance_score, adverse_action_reasons_specific,
  uses_prohibited_factor, ecdis_sources_documented, non_discrimination_validated,
  disparate_impact_ratio, protected_class_sample_size, min_sample_size_for_di_test
- `InsuranceGovernanceResult` (dataclass) — layer, decision, findings, conditions; `is_denied` and
  `has_conditions` properties
- `NAICFilter` — Layer 1: documentation required all risk levels; HIGH/MEDIUM require independent
  validation + monitoring + explainability; HIGH adds annual review condition
- `FCRAFilter` — Layer 2: prohibited factor check (blocks regardless of other compliance);
  CBIS/consumer report in adverse action use cases requires specific reasons and explainability;
  APPROVED_WITH_CONDITIONS with notice requirement when compliant
- `NYDFSFilter` — Layer 3: NY-only ("NY" not in intended_states → pass-through APPROVED);
  requires ECDIS source inventory and proxy-discrimination validation
- `ECOADisparateImpactFilter` — Layer 4: 4/5 rule (ratio < 0.80 → DENIED); insufficient sample
  size blocks deployment; None ratio with sufficient sample → DENIED; non-adverse-action use
  cases pass through
- `InsuranceGovernanceReport` (dataclass) — model_id, final_decision, layer_results list,
  `summary()` dict
- `InsuranceGovernanceOrchestrator` — NAIC → FCRA → NY DFS → ECOA; all layers evaluated
  regardless of earlier failures; any DENIED → DENIED; else conditions → APPROVED_WITH_CONDITIONS

**Tests:** 45 new tests in `tests/test_insurance_ai_governance.py`

---

## [0.15.0] — 2026-04-13

### Added — Financial Model Risk Governance (FRB SR 11-7 + Basel III/IV + EU DORA + OCC 2011-12)

**`examples/13_financial_ai_governance.py`** — four-layer governance framework for AI/ML models
used in financial risk management contexts (credit risk, market risk, AML/BSA, capital calculation),
enforcing FRB SR 11-7 Model Risk Management guidance (April 2011), Basel III/IV (BCBS 239 Principles
+ CRR III/FRTB IMA requirements), EU DORA (Regulation 2022/2554, effective January 2025), and
OCC Bulletin 2011-12/2023-17 Third-Party Risk Management independently and simultaneously.

New classes (self-contained in the example):
- `ModelTier` — TIER_1 (capital/trading/AML; highest scrutiny), TIER_2 (credit scoring/pricing),
  TIER_3 (operational/analytical; lowest scrutiny)
- `ModelApprovalStatus` — APPROVED, CONDITIONAL_APPROVAL, PENDING_REVIEW, REJECTED, NOT_REQUIRED
- `DORAClassification` — CRITICAL_ICT (full DORA requirements), IMPORTANT_ICT (lighter oversight),
  NON_CRITICAL (Chapter II basic requirements only)
- `ThirdPartyRiskLevel` — CRITICAL (full DD + audit rights + annual reassessment), HIGH (enhanced DD),
  MODERATE (standard DD), LOW (simplified)
- `FinancialGovernanceDecision` — APPROVED, APPROVED_WITH_CONDITIONS, DENIED
- `FinancialModelContext` — frozen dataclass: model_id, model_name, tier, is_validated_independently,
  validation_findings_resolved, ongoing_monitoring_active, last_performance_review_days_ago,
  model_approval_status, is_capital_model, bcbs239_lineage_verified, frtb_backtesting_passed,
  dora_classification, dora_resilience_documented, dora_incident_reporting_active, is_third_party,
  third_party_risk_level, third_party_due_diligence_complete, third_party_contract_has_audit_rights,
  intended_jurisdiction (tuple), model_inventory_registered
- `FinancialFilterResult` — layer, decision, violations, conditions, notes; `is_denied` property
- `SR117Filter` — Layer 1: `_MAX_REVIEW_AGE = {TIER_1: 365, TIER_2: 730, TIER_3: 1095}`; Tier 1/2:
  independent validation required (developer ≠ validator), validation findings must be resolved,
  ongoing monitoring required; all tiers: inventory registration + review age check; Tier 3 note
  (recommended not required); Tier 1/2 approved with quarterly/semi-annual monitoring conditions
- `Basel3Filter` — Layer 2: non-capital model → APPROVED pass-through; capital model: supervisor
  approval required (CRR III Art. 143); BCBS 239 data lineage verification required; Tier 1 capital
  model: FRTB IMA backtesting required (Basel IV §325bc); CONDITIONAL_APPROVAL → condition note
- `DORAFilter` — Layer 3: non-EU jurisdiction → APPROVED pass-through; NON_CRITICAL → basic requirements;
  CRITICAL/IMPORTANT: resilience documentation (Art. 11) + incident reporting (Art. 19) required;
  CRITICAL third-party without Art. 28 contract → DENIED; CRITICAL approved → TLPT condition (Art. 26)
- `OCC2011Filter` — Layer 4: non-third-party → APPROVED pass-through; `_DD_REQUIRED_LEVELS` =
  {CRITICAL, HIGH, MODERATE}; `_AUDIT_RIGHTS_REQUIRED_LEVELS` = {CRITICAL, HIGH}; CRITICAL/HIGH
  approved → annual reassessment condition
- `FinancialGovernanceResult` — model_id, model_name, final_decision, layer_results, all_violations,
  all_conditions, all_notes, review_id (UUID); `summary()` → formatted string
- `FinancialModelGovernanceOrchestrator` — four-layer orchestrator (SR 11-7 → Basel → DORA → OCC);
  any DENIED → overall DENIED; mix with APPROVED_WITH_CONDITIONS → overall APPROVED_WITH_CONDITIONS

Four demo scenarios: (A) Tier 1 IRB credit model fully compliant → APPROVED_WITH_CONDITIONS;
(B) Tier 1 VaR trading model with unresolved findings → DENIED (SR 11-7); (C) third-party AML
screening AI with DORA Critical ICT and no resilience docs → DENIED (DORA); (D) Tier 3 internal
operational model → APPROVED.

**Tests:** `tests/test_financial_ai_governance.py` — 54 tests covering all four governance layers,
all tier combinations, jurisdiction scoping, third-party risk levels, and orchestrator decision
aggregation. Full suite: 690 passed.

---

## [0.14.0] — 2026-04-13

### Added — Medical Device AI Governance (FDA SaMD + IEC 62304 + ISO 14971 + EU MDR/MDCG 2021-1)

**`examples/12_medtech_ai_governance.py`** — four-layer governance framework for AI systems
embedded in or used alongside medical devices, enforcing FDA Software as a Medical Device
guidance (2019) + 21 CFR Part 820, IEC 62304:2006+AMD1:2015 software lifecycle requirements,
ISO 14971:2019 risk management, and EU MDR 2017/745 + MDCG 2021-1 AI/ML guidance.

New classes (self-contained in the example):
- `IEC62304SafetyClass` — CLASS_A (no injury possible), CLASS_B (non-serious injury possible),
  CLASS_C (death or serious injury possible); drives required lifecycle rigor
- `FDASaMDClass` — CLASS_I (general controls), CLASS_II (510(k) + special controls),
  CLASS_III (PMA required)
- `FDAClearancePathway` — EXEMPT, K510_CLEARED, PMA_APPROVED, DE_NOVO, NOT_CLEARED
- `EUMDRClass` — CLASS_I (self-certification), CLASS_IIA (NB QMS), CLASS_IIB (NB technical file),
  CLASS_III (NB + clinical evaluation)
- `ISO14971RiskLevel` — ACCEPTABLE (deploy), ALARP (deploy with PMS conditions), UNACCEPTABLE (block)
- `SaMDChangeType` — PERFORMANCE_IMPROVEMENT (within PCCP), INTENDED_USE_CHANGE (new 510(k)),
  OUTPUT_TYPE_CHANGE (new 510(k)), MINOR_BUG_FIX (no submission required)
- `DeploymentDecision` — APPROVED, APPROVED_WITH_CONDITIONS, DENIED
- `MedicalAIRequestContext` — frozen dataclass: system_id, system_name, safety class, FDA class,
  clearance pathway, EU MDR class, residual risk level, intended use, has_notified_body_certificate,
  has_pccp, lifecycle_documentation_complete, formal_verification_complete,
  risk_management_file_complete, clinical_validation_study_complete, change_type, intended_markets
- `FilterResult` — single-layer result: layer name, decision, violations, conditions, notes;
  `is_denied` property
- `IEC62304SafetyFilter` — Layer 1: Class A → lightweight lifecycle permitted (no block);
  Class B → lifecycle docs required; Class C → lifecycle docs + formal verification required
  (IEC 62304 §5.5.3); conditions for change management on Class B/C deployments
- `ISO14971RiskFilter` — Layer 2: UNACCEPTABLE residual risk → DENY (§8 risk controls insufficient);
  incomplete risk management file → DENY (§9); ALARP → APPROVED_WITH_CONDITIONS with PMS note
  (§10); ACCEPTABLE → APPROVED; all paths check risk_management_file_complete
- `FDASaMDFilter` — Layer 3 (US market only): Class I exempt → APPROVED_WITH_CONDITIONS (general
  controls); Class II → K510_CLEARED or DE_NOVO required + clinical study complete; no-PCCP →
  condition added (PCCP required for adaptive algorithms per FDA AI/ML Action Plan 2021);
  INTENDED_USE_CHANGE/OUTPUT_TYPE_CHANGE → new 510(k) required even with current clearance;
  Class III → PMA_APPROVED required; non-US markets → pass-through
- `MDCGEUFilter` — Layer 4 (EU market only): Class I → self-certification + MDCG 2021-1 IFU
  transparency; Class IIa → Notified Body required; Class IIb/III → NB + clinical validation;
  Class III → formal verification + EU AI Act Annex I §5 high-risk note; EU AI Act registration
  required for Class III; PMS/PSUR conditions for Class IIa+; non-EU markets → pass-through
- `MedicalDeviceGovernanceResult` — aggregated result: final_decision, layer_results list,
  all_violations, all_conditions, all_notes; `summary()` method for human-readable report
- `MedicalDeviceAIOrchestrator` — four-layer orchestrator; any DENIED layer → overall DENIED;
  any APPROVED_WITH_CONDITIONS → overall APPROVED_WITH_CONDITIONS; violations and conditions
  aggregated across all layers

4 end-to-end scenarios: (A) Class IIb diagnostic imaging assistant (ALARP → approved with PCCP/PMS
conditions), (B) Class I administrative scheduling optimizer (exempt, fully approved), (C) Class III
autonomous chemotherapy dosing with unacceptable residual risk and no PMA (denied by ISO 14971 + FDA),
(D) Class II/IIa sepsis monitoring AI with valid NB cert but incomplete clinical study (denied by FDA).

Tests: 43 new tests in `tests/test_medtech_ai_governance.py` — TestIEC62304SafetyFilter (9),
TestISO14971RiskFilter (7), TestFDASaMDFilter (9), TestMDCGEUFilter (7),
TestMedicalDeviceAIOrchestrator (7), TestScenarios (4)

---

## [0.13.0] — 2026-04-13

### Added — Automotive / Transportation AI Governance (UNECE WP.29 R155/R156 + ISO 26262 + NHTSA AV)

**`examples/11_automotive_ai_governance.py`** — layered governance framework for AI deployed in
automotive and mobility systems, covering three regulatory pillars: ISO 26262 Functional Safety
(ASIL classification), UNECE WP.29 Regulations R155 (cybersecurity management) and R156 (software
update management), and NHTSA AV safety guidance.

New classes (self-contained in the example):
- `ASILLevel` — QM, ASIL_A, ASIL_B, ASIL_C, ASIL_D (ISO 26262-1:2018 §3.6)
- `SAELevel` — L0 through L5 (SAE J3016 automation taxonomy)
- `AISystemFunction` — 14 automotive AI functions including EMERGENCY_BRAKING (ASIL D),
  STEERING_CONTROL (ASIL D), PATH_PLANNING (ASIL C), LANE_KEEP_ASSIST (ASIL B),
  OTA_UPDATE_EXECUTION (ASIL D per ISO 26262-8 §7), INFOTAINMENT (QM)
- `GovernanceOutcome` — ALLOW, ALLOW_WITH_CONDITIONS, ESCALATE_HUMAN, DENY
- `SafetyClassifier` — ISO 26262 ASIL assignment table; `verify_requirements_met()` checks that
  all ASIL-required verification activities (unit_testing, code_review, fmea_complete, hara_complete,
  independent_safety_assessment, safety_case_documented, formal_verification,
  safety_element_out_of_context) have been completed
- `CybersecurityContext` — frozen dataclass: csms_certified, csms_certificate_id, threat_assessment_current,
  known_vulnerabilities_mitigated, intrusion_detection_active, incident_response_tested, security_logging_enabled
- `R155CybersecFilter` — UNECE WP.29 R155 CSMS compliance; missing CSMS cert (§7.3.1) or
  unmitigated vulnerabilities (§7.3.3) → DENY; missing IDS (§7.3.5) or logging (§7.3.7) →
  ALLOW_WITH_CONDITIONS
- `SoftwareUpdateContext` — frozen dataclass: sums_documented, update_cryptographically_signed,
  rollback_capability_present, over_the_air, driver_consent_obtained, installation_state_verified,
  asil_change_requires_reapproval
- `R156SUMSFilter` — UNECE WP.29 R156 SUMS compliance; unsigned OTA (§7.2.2) or no rollback (§7.2.4) →
  DENY; ASIL D + any violation → DENY; OTA without consent (§7.2.6) → ALLOW_WITH_CONDITIONS for lower ASILs
- `NHTSAAVContext` — frozen dataclass: sae_level, odd_documented, safety_performance_tested,
  cybersecurity_compliance, crash_avoidance_validated, sgo_reporting_enabled,
  fallback_minimal_risk_condition, human_machine_interface_tested, data_recording_capability
- `NHTSAAVFilter` — NHTSA AV Safety Principles and SGO 2021-01; missing ODD or safety testing →
  DENY; L3+ without MRC → DENY; L2+ without SGO reporting → ALLOW_WITH_CONDITIONS
- `AutomotiveGovernanceAuditRecord` — OEM-grade audit: all per-layer outcomes, ASIL level,
  missing activities, final_outcome, denial_reasons, conditions
- `AutomotiveAIOrchestrator` — orchestrates all four checks; DENY from any layer blocks deployment;
  conditions surfaced in audit even when final outcome is ALLOW

Four scenarios: ADAS lane-keep (ASIL B fully compliant → ALLOW), L3 conditional automation
(no CSMS → DENY), OTA update to ASIL D (unsigned + no rollback → DENY), L4 robotaxi
(SGO reporting not wired → ALLOW_WITH_CONDITIONS).

**Test coverage:** 36 tests (`tests/test_automotive_ai_governance.py`)

---

## [0.12.0] — 2026-04-13

### Added — EU AI Act Standalone Governance Example (Regulation 2024/1689)

**`examples/10_eu_ai_act_governance.py`** — standalone EU AI Act governance framework
implementing the full risk-based approach: prohibited practices (Article 5), high-risk
classification (Article 6 / Annex III), transparency obligations (Article 13), human
oversight (Article 14), accuracy/robustness (Article 15), and GPAI model obligations
(Articles 51–55).

New classes (self-contained in the example):
- `AIRiskLevel` — UNACCEPTABLE_RISK (Article 5 prohibited), HIGH_RISK (Annex III),
  LIMITED_RISK (Article 50 transparency), MINIMAL_RISK (voluntary code only)
- `AnnexIIICategory` — 8 high-risk domains: BIOMETRIC_ID, CRITICAL_INFRASTRUCTURE,
  EDUCATION, EMPLOYMENT, ESSENTIAL_SERVICES, LAW_ENFORCEMENT, MIGRATION_BORDER, JUSTICE
- `ProhibitedAIType` — 7 Article 5(1) prohibited practices: real-time biometric ID
  in public spaces, social scoring, subliminal manipulation, vulnerability exploitation,
  predictive policing of individuals, emotion recognition in workplace/schools,
  untargeted facial image scraping
- `GovernanceOutcome` — ALLOW, ALLOW_WITH_CONDITIONS, ESCALATE_HUMAN, DENY
- `EUAIActRequestContext` — governance evaluation boundary: annex_iii_category,
  prohibited_ai_type, is_gpai, gpai_flops_training, transparency/oversight/accuracy/
  robustness flags, model_card_published, adversarial_testing_completed,
  incident_reporting_capability, conformity_assessment_done, public authority/space flags
- `Article5ProhibitionGuard` — absolute prohibition guard; Article 5 denials have no
  mitigation path regardless of safeguards or oversight measures in place
- `Article6ClassificationGuard` — Annex III classification + Article 43 conformity
  assessment verification; covers all 8 Annex III domains
- `Article13TransparencyGuard` — high-risk AI systems must have complete capability
  documentation, accuracy ranges, intended purpose, and oversight specifications
- `Article14OversightGuard` — high-risk AI systems must have meaningful review
  capability, override mechanism, and active monitoring duty
- `Article15RobustnessGuard` — accuracy validation (Art. 15(1)) and resilience
  against errors, faults, and adversarial inputs (Art. 15(2))
- `GPAIGuard` — Articles 51–55: model card required for all GPAI (Art. 53(1)(d));
  systemic risk threshold 10^25 FLOPs (Art. 51) triggers adversarial testing
  (Art. 55(1)(a)) and incident reporting capability (Art. 55(1)(c))
- `EUAIActGovernanceOrchestrator` — applies all 6 guards; outcome priority:
  DENY > ESCALATE_HUMAN > ALLOW_WITH_CONDITIONS > ALLOW; notified body required
  for biometric ID, law enforcement, migration/border, and justice categories
- `EUAIActAuditRecord` — conformity assessment required flag, notified body required
  flag, applicable articles list, all violations, risk level, GPAI systemic risk flag

Key design decisions:
- **Article 5 prohibitions are absolute:** no safeguard, transparency measure, or
  oversight mechanism makes a prohibited AI practice lawful — DENY with no escalation
- **Missing conformity assessment → ESCALATE, not DENY:** an assessable high-risk
  system that hasn't completed conformity assessment goes to ESCALATE_HUMAN (notified
  body review) rather than outright DENY — the system could become compliant
- **GPAI model card is required for all GPAI models:** not just those with systemic risk;
  the systemic risk threshold (10^25 FLOPs) adds adversarial testing + incident reporting
- **Notified body required only for highest-risk Annex III categories:** biometric ID,
  law enforcement, migration/border control, administration of justice — others may
  self-assess under Annex VI

Four scenarios: high-risk employment screening (ALLOW_WITH_CONDITIONS), prohibited
social scoring (DENY), GPAI systemic risk with missing model card (DENY), minimal-risk
chatbot (ALLOW).

Tests: 50 new test cases in `tests/test_eu_ai_act_governance.py`.

Regulated environments covered: **10** (added EU AI Act standalone + GPAI obligations).

---

## [0.11.0] — 2026-04-13

### Added — Financial Services AI Governance (SEC Reg BI + FINRA Rule 3110 + SR 11-7)

**`examples/09_finra_sec_governance.py`** — multi-framework AI governance for a
registered broker-dealer's AI investment advisory assistant:

New classes (self-contained in the example):
- `CustomerType` — RETAIL (full Reg BI protections) vs. INSTITUTIONAL (Reg BI exempted)
- `RecommendationAction` — BUY, SELL, HOLD, REBALANCE, GENERATE_REPORT,
  GENERATE_SUITABILITY_ANALYSIS, SCREEN_SECURITIES
- `GovernanceOutcome` — ALLOW, DENY, ESCALATE_HUMAN, ADVISORY_ONLY, SHADOW_ALLOW;
  `ADVISORY_ONLY` is distinct from `DENY` — recommendation is generated but must
  include explicit model limitation disclosure (SEC Model Risk stale validation)
- `BrokerDealerRequestContext` — request boundary: customer type, action, securities,
  portfolio concentration %, firm inventory positions, suitability data age, model ID,
  model validation age, conflicts disclosed flag
- `RegBIGuard` — enforces SEC Reg BI §240.15l-1: (1) firm inventory conflict without
  disclosure → DENY; (2) BUY recommendation for conflicted security requires care
  obligation review even when disclosed; applies only to retail customers
- `FINRA3110Guard` — enforces FINRA Rule 3110: (1) concentration > 25% requires
  registered principal review → ESCALATE_HUMAN; (2) suitability data > 365 days
  requires KYC refresh; (3) large transaction (> 10% portfolio) requires supervisory
  review; principal review = ESCALATE_HUMAN (not DENY)
- `SECModelRiskGuard` — enforces SR 11-7 principles: (1) model must be in firm model
  inventory; (2) model validated > 365 days ago → ADVISORY_ONLY (not DENY — model is
  useful but must be presented as non-binding with limitation disclosure); unregistered
  model → DENY
- `BrokerDealerAuditRecord` — FINRA Rule 4511 / SEC Reg S-P compliant audit record:
  per-framework results, governance outcome, conflicts_detected, principal_review_required,
  advisory_only_mode
- `BrokerDealerGovernanceOrchestrator` — outcome priority: DENY > ESCALATE_HUMAN >
  ADVISORY_ONLY > ALLOW; shadow mode for FINRA exam / SEC model risk quarterly review

Scenarios:
- A: Standard diversified BUY (5% concentration, no conflicts, model validated 180d) → ALLOW
- B: High-concentration BUY (35% in single security) → ESCALATE_HUMAN (FINRA 3110)
- C: BUY in firm inventory security, conflicts not disclosed → DENY (Reg BI)
- D: Model last validated 420 days ago → ADVISORY_ONLY (SR 11-7; not DENY)
- E: Shadow audit mode — 4 scenarios logged without blocking for FINRA exam prep

Framework coverage now spans 9 regulated sectors:
healthcare · OT/manufacturing · government/defense · insurance · **broker-dealer/investment**

Closes #28.

---

## [0.10.0] — 2026-04-13

### Added — Insurance Sector AI Governance (NAIC Model Bulletin + State Anti-Discrimination + FCRA/GLBA)

**`examples/08_insurance_ai_governance.py`** — multi-framework AI governance for an
insurance underwriting and claims triage assistant, combining three compliance frameworks:

New classes (self-contained in the example):
- `InsuranceLine` — line of business (PERSONAL_AUTO, HOMEOWNERS, COMMERCIAL_PROPERTY,
  WORKERS_COMP, LIFE, HEALTH)
- `InsuranceAction` — agent actions (GENERATE_AUTO_QUOTE, UNDERWRITE_STANDARD_RISK,
  UNDERWRITE_ADVERSE_DECISION, TRIAGE_CLAIM, APPROVE_CLAIM, DENY_CLAIM,
  ISSUE_ADVERSE_ACTION_NOTICE, GENERATE_EXPLANATION)
- `InsuranceRequestContext` — request boundary: line of business, action, applicant state,
  model features, preliminary outcome, premium change %, credit report usage, MRM inventory ID
- `NAICModelBulletinGuard` — enforces NAIC Model Bulletin on AI (2023): (1) AI system must
  be in MRM inventory, (2) adverse decisions ≥ 15% premium impact require human attestation,
  (3) claims denials require human review under §IV.B
- `StateAntiDiscriminationGuard` — enforces state prohibited proxy variable registries;
  state-specific: CA bans credit_score + zip_code for auto (CA Ins. Code §1861.02), NY
  bans credit_score (N.Y. Ins. Law §2611), MI bans credit_score; federal baseline bans
  race/religion/national_origin/sex; blocks decisions using prohibited proxy features
- `FCRAGLBAGuard` — enforces FCRA §615 (credit-based adverse action requires written
  consumer disclosure) and GLBA Safeguards Rule (NPI features — SSN, account_number,
  income, credit_history — must not appear unprotected in AI payload)
- `InsuranceGovernanceAuditRecord` — NAIC MRM-required audit record: request context,
  per-framework results, governance outcome, prohibited proxies detected, human oversight
  required flag, adverse action disclosure required flag
- `InsuranceGovernanceOrchestrator` — deny-all aggregation; `ESCALATE_HUMAN` when NAIC
  requires human oversight; `DENY` for state anti-discrimination violations; shadow mode
  for quarterly MRM reporting

Scenarios:
- A: Standard CA auto quote (no prohibited proxies, no adverse outcome) — ALLOW
- B: Adverse underwriting decision (premium +28%, CA) — NAIC threshold exceeded →
  ESCALATE_HUMAN (human attestation required)
- C: Underwriting with `credit_score` feature in CA — state anti-discrimination guard
  detects prohibited proxy → DENY (escalate to compliance review)
- D: Claims denial with credit report (NY) — NAIC (§IV.B human attestation) + FCRA §615
  (written disclosure) both fire → ESCALATE_HUMAN with adverse_action_disclosure=True
- E: Shadow mode — all 4 actions evaluated without blocking; violation counts logged
  for NAIC quarterly MRM review (§IV.C)

Framework coverage now spans 8 regulated sectors:
HIPAA + NIST AI RMF + EU AI Act (healthcare) · ISO 42001 + IEC 62443 + DORA (OT) ·
CMMC L2 + FedRAMP + NIST 800-53 (defense) · **NAIC + state anti-discrimination + FCRA/GLBA (insurance)**

Closes #27.

---

## [0.9.0] — 2026-04-13

### Added — Government/Defense AI Governance Example (CMMC L2 + FedRAMP + NIST 800-53)

**`examples/07_government_ai_governance.py`** — multi-framework AI governance for a
DoD procurement AI assistant, combining CMMC Level 2 (32 CFR Part 170), FedRAMP
Moderate authorization boundary, and NIST 800-53 AC-3 access control:

Three `FrameworkGuard`s orchestrated by a single `GovernanceOrchestrator` (deny-all
aggregation — any one framework blocking an action stops execution):

- **CMMC Level 2 Guard (32 CFR Part 170):** Defense contractors handling CUI must be
  CMMC Level 2 certified. Allowed actions restricted to the 11 domains of CMMC L2
  (`CMMC_L2_ALLOWED_ACTIONS`). Non-certified entities have a minimal allowed set.
- **FedRAMP Moderate Guard:** Actions touching federal systems must operate within
  the FedRAMP authorization boundary. `FEDRAMP_DENIED_ACTIONS` (use_commercial_api,
  store_data_commercial_cloud, export_controlled_data_transfer) are blocked regardless
  of CMMC status; `FEDRAMP_ALLOWED_ACTIONS` defines the approved surface.
- **NIST 800-53 AC-3 Guard:** Privileged functions (`run_privileged_query`,
  `modify_system_configuration`, `export_controlled_data_transfer`) are restricted to
  the `nist_privileged` role; standard government users are denied.

Scenarios:
- A: CMMC L2 certified contractor + FedRAMP boundary + standard role → `query_procurement_database`
  allowed by all three frameworks (ALLOW)
- B: Non-certified vendor attempts CUI access → CMMC L2 guard denies immediately (DENY);
  uses a separate `GovernanceOrchestrator` with an uncertified policy to accurately model
  a non-certified entity
- C: Certified contractor calls `use_commercial_api` → FedRAMP guard denies (DENY);
  action is in `FEDRAMP_DENIED_ACTIONS` regardless of CMMC certification
- D: Standard user attempts `run_privileged_query` → NIST AC-3 guard denies (DENY);
  action restricted to `nist_privileged` role
- E: Public notice action (`publish_solicitation_notice`) → all three frameworks allow
  (ALLOW); action is in all approved sets and requires no privileged role

Closes #26.

---

## [0.8.0] — 2026-04-13

### Added — Manufacturing/OT Governance Example + Implementation Notes

**`examples/06_manufacturing_ot_governance.py`** — multi-framework AI governance for a
predictive maintenance agent in a chemical plant, combining ISO/IEC 42001:2023 AI Management
System, IEC 62443 OT Security Levels, and DORA ICT Risk Management (Art. 28):
- ISO 42001 A.6.2.10: operating-scope enforcement (advisory monitoring zone only)
- ISO 42001 A.9.5: human oversight required for autonomous actuation (HIGH-risk classification)
- IEC 62443 SL-2: agent authorized at Security Level 2; SL-3 Control Zone actions denied
- IEC 62443 zone/conduit model: Process Control Zone → Business Zone crossing denied
- DORA Art. 28: third-party ML services not in the ICT service register are denied
- Scenario A: `sensor_anomaly_detection` — advisory monitoring, all frameworks permit (ALLOW)
- Scenario B: `autonomous_valve_control` — ISO 42001 + IEC 62443 both deny (DENY)
- Scenario C: `third_party_ml_inference` — DORA Art. 28 undocumented dependency (DENY)
- Scenario D: `maintenance_scheduling_recommendation` — advisory, all frameworks permit (ALLOW)
- Scenario E: `cross_plant_data_sharing` — IEC 62443 zone boundary violation (DENY)
- Closes #21.

**`docs/implementation-note-01.md`** — "Multi-Framework AI Governance: Why Single-Layer Compliance Fails":
- Deny-all aggregation rationale and the conjunctive nature of compliance obligations
- Escalation routing: why different violations go to different targets
- Skip vs. deny distinction for jurisdictional applicability
- Concrete failure scenario: HIPAA-only system lacking NIST AI RMF guard
- Three-step pattern for adding a new framework to an existing orchestrator
- Closes #20 (partially).

**`docs/implementation-note-02.md`** — "Audit Trail Design for Regulated AI: What to Log and Why":
- `GovernanceAuditRecord` and `ComprehensiveAuditReport` field-by-field rationale
- Retention requirements by regulation: HIPAA (6yr), EU AI Act (10yr), GDPR, DORA, SOC 2
- Shadow (audit-only) mode and its compliance implications
- What the governance audit trail is NOT responsible for
- Closes #20 (partially).

**`docs/implementation-note-03.md`** — "Adapter Pattern for Multi-Framework Integrations":
- Why adapter-over-inheritance (ADR-003) keeps the compliance core framework-agnostic
- Complete integration table: 8 framework adapters (CrewAI, LangChain, AutoGen, SK, Haystack, LlamaIndex, DSPy, MAF)
- Step-by-step guide to adding a new framework adapter
- Testing strategy: unit testing guards vs. integration testing adapters
- Framework version migration pattern (e.g. AutoGen 0.2 → MAF)
- Closes #20.

---

## [0.7.1] — 2026-04-13

### Added — Healthcare AI Governance Example

**`examples/05_healthcare_ai_governance.py`** — multi-framework AI governance for an
ICU clinical decision support (CDS) agent combining HIPAA, NIST AI RMF AI 600-1,
and EU AI Act HIGH_RISK classification:
- Deny-all aggregation: `GovernanceOrchestrator` with three `FrameworkGuard`s active
  simultaneously — one DENY from any framework stops the action.
- Scenario A: `read_vitals` — allowed by all three frameworks (ALLOW)
- Scenario B: `recommend_medication_dosage` — HIPAA allows; NIST AI RMF + EU AI Act
  trigger mandatory escalation with `block_on_escalation=True` (DENY, human review required)
- Scenario C: `share_phi_externally` — explicitly denied by HIPAA (DENY immediately)
- Scenario D: `create_clinical_note` — allowed by all frameworks (ALLOW)
- Scenario E: Audit-only mode — all four actions evaluated without blocking; full
  `ComprehensiveAuditReport` emitted per evaluation for shadow compliance assessment
- Governance design notes: minimum-necessary scoping, MANAGE function escalation,
  Art. 14 human oversight, audit-only rollout pattern
- Closes #19.

---

## [0.7.0] — 2026-04-13

### Added — DSPy Framework Integration

- `integrations/dspy.py`: `GovernedDSPyModule` and `GovernedDSPyPipeline` —
  policy-enforcing wrappers for DSPy `Module` objects (DSPy ≥ 2.5.0, Pydantic v2).

  **`GovernedDSPyModule`** wraps any DSPy module:
  - `forward(*args, **kwargs)` and `__call__` evaluate the `ActionPolicy` before
    delegating to the wrapped module.  Denied actions raise `PermissionError`.
  - `action_name` defaults to `type(wrapped_module).__name__` — configure
    `ActionPolicy.allowed_actions` with class names of permitted modules.
  - Emits a `GovernanceAuditRecord` for every call (permitted, denied, escalated).
  - `__getattr__` delegation — DSPy introspection (`predictors()`, `parameters()`,
    etc.) works transparently through the guard wrapper.
  - Optional `context` dict included in every audit record (session ID, pipeline
    stage, etc.).

  **`GovernedDSPyPipeline`** wraps a sequential pipeline:
  - Each module is individually guarded; denied intermediate steps fail fast.
  - Dict outputs are unpacked as `**kwargs` for the next step; non-dict outputs
    are passed as a single positional argument.

  Closes #2. 27 new tests.

- `integrations/__init__.py`: exports `GovernedDSPyModule`, `GovernedDSPyPipeline`.

---

## [0.6.0] — 2026-04-13

### Added — Cross-Industry AI Governance Regulation Modules

**EU AI Act 2024/1689** (`regulations/eu_ai_act.py`):
- `EUAIActRiskCategory`: UNACCEPTABLE / HIGH_RISK / LIMITED_RISK / MINIMAL_RISK.
- `EUAIActSystemProfile`: declares system risk category, prohibited practices, high-risk domains, conformity assessment status, FRIA completion, transparency obligations.
- `EUAIActGovernancePolicy.evaluate_action()`: six-step evaluation — Art. 5 prohibited practices → Art. 6–9 risk category check → Art. 43 conformity assessment gate (high-risk) → Art. 27 FRIA check → Art. 14 human oversight routing → Art. 12 logging requirement.
- `EUAIActAuditRecord`: structured audit record with SHA-256 tamper evidence.
- `make_eu_ai_act_minimal_risk_policy()` / `make_eu_ai_act_high_risk_policy()`: factory constructors.
- `EU_AI_ACT_PROHIBITED_PRACTICES`, `EU_AI_ACT_HIGH_RISK_DOMAINS`: curated constant sets for Art. 5 and Annex III.
- 58 tests in `tests/test_eu_ai_act.py`.

**DORA EU 2022/2554** (`regulations/dora.py`):
- `DORAICTRiskLevel`: CRITICAL / HIGH / MEDIUM / LOW.
- `DORAICTCapabilityArea`: IDENTIFY / PROTECT / DETECT / RESPOND / RECOVER (Art. 9 five-function model).
- `DORAThirdPartyRecord`: third-party ICT provider risk assessment (Art. 28).
- `DORAICTIncidentRecord`: ICT incident report with impact, RTO, response timeline (Art. 17–18).
- `make_dora_ict_management_policy()` / `make_dora_third_party_policy()`: factory constructors.
- `DORA_HIGH_RISK_ICT_ACTIONS`: curated set of actions triggering DORA Art. 9 controls.
- Tests in `tests/test_dora.py`.

**NIST AI RMF 1.0 + AI 600-1 GenAI Profile** (`regulations/nist_ai_rmf.py`):
- `NISTAIRMFFunction`: GOVERN / MAP / MEASURE / MANAGE.
- `NISTAIRMFRiskCategory`: CONFABULATION / DATA_BIAS / HUMAN_AI_CONFIGURATION / HARMFUL_CONTENT / PRIVACY / SECURITY / ACCOUNTABILITY / TRANSPARENCY.
- `NISTAIRMFRiskAssessment`: structured risk assessment across RMF functions with severity and likelihood.
- `make_nist_ai_rmf_policy()`: factory constructor mapping GenAI profile controls.
- `NIST_GENAI_HIGH_RISK_ACTIONS`: actions requiring MANAGE-function controls per AI 600-1.
- Tests in `tests/test_nist_ai_rmf.py`.

**OWASP LLM Top 10 (2025)** (`regulations/owasp_llm.py`):
- `OWASPLLMRisk`: LLM01 Prompt Injection / LLM02 Sensitive Info Disclosure / LLM05 Output Handling / LLM06 Excessive Agency / LLM07 System Prompt Leakage / LLM09 Misinformation / LLM10 Unbounded Consumption.
- `make_owasp_llm_policy()`: factory constructor blocking the 7 highest-severity OWASP LLM risks.
- `OWASP_LLM_DENIED_ACTIONS`, `OWASP_LLM_2025_ALL_RISKS`: curated constants.
- Tests in `tests/test_owasp_llm.py`.

**`regulations/__init__.py`**: updated to export all symbols from the four new modules alongside existing `iso42001` exports.

### Tests
- +198 new tests (58 EU AI Act, 51 DORA, 49 NIST AI RMF, 40 OWASP LLM).
- Total test count: **480 passing**.

---

## [0.5.0] — 2026-04-13

### Added — Comprehensive Governance Architecture

**Multi-Framework Orchestrator** (`orchestrator.py`):
- `GovernanceOrchestrator`: evaluates agent actions against multiple compliance frameworks simultaneously with deny-all aggregation — if any framework denies, the overall decision is DENY. Suitable for regulated environments requiring simultaneous FERPA + HIPAA + GDPR + ISO 42001 enforcement.
- `FrameworkGuard`: associates a `GovernedActionGuard` with a regulation label and enabled/disabled state.
- `FrameworkResult`: per-framework evaluation result (regulation, permitted, denial_reason, escalation_target, skipped).
- `MultiFrameworkDecision`: aggregated decision across all frameworks with framework-level attribution.
- `ComprehensiveAuditReport`: unified compliance audit record capturing every framework's decision, denial reasons, escalation targets, tamper-evident SHA-256 hash, `to_log_entry()` (SIEM-ready JSON), `to_compliance_summary()` (human-readable GRC report).
- `GovernanceOrchestrator.audit_only`: shadow mode — evaluate all frameworks and log outcomes without blocking any action. For progressive rollout and compliance posture assessment.

**ISO/IEC 42001:2023 AI Management System** (`regulations/iso42001.py`):
- `ISO42001OperatingScope`: defines permitted/prohibited use cases, deployment approval status, and human oversight requirements per the ISO 42001 operating scope (A.6.2.10).
- `ISO42001GovernancePolicy.evaluate_action()`: three-step evaluation — A.6.2.5 deployment gate → A.6.2.10 prohibited/permitted use → A.9.5 human oversight routing.
- `ISO42001DataProvenanceRecord`: documents chain of custody for AI training/knowledge data (A.7.2/A.7.5/A.7.6).
- `ISO42001DeploymentRecord`: formal deployment approval record with risk assessment and impact assessment outcomes (A.5.2/A.5.3/A.6.2.5).
- `ISO42001AuditRecord`: structured audit record per governance evaluation with SHA-256 tamper evidence.
- `ISO42001PolicyDecision`: decision with `human_oversight_required` flag for A.9.5 routing.

**Governance Audit Skill** (`skill.py`):
- `GovernanceAuditSkill`: high-level skill wrapping `GovernanceOrchestrator` with framework-aware factory constructors and multi-channel adapters.
- `GovernanceAuditSkill.for_education()`: FERPA-compliant skill factory for educational AI systems.
- `GovernanceAuditSkill.for_healthcare()`: HIPAA-compliant skill factory for healthcare AI systems.
- `GovernanceAuditSkill.for_enterprise()`: multi-regulation skill factory (FERPA + HIPAA + GDPR + GLBA + SOC2 simultaneously) for enterprise AI agents.
- `GovernanceAuditSkill.audit_action()`: evaluate and execute with per-call framework scoping — restrict evaluation to a subset of configured frameworks for individual actions.
- `GovernanceAuditSkill.audit_retrieval()`: action-level authorization gate for document retrieval. Returns all documents if actor is authorized; empty list if denied. Content-level filtering remains in `enterprise-rag-patterns`.
- `GovernanceAuditSkill._framework_scope`: context manager for per-call framework restriction; automatically restores disabled frameworks on exit.
- Channel adapters: `as_langchain_handler()`, `as_crewai_tool()`, `as_llama_index_postprocessor()`, `as_haystack_component()`, `as_maf_middleware()` — all lazy imports.
- `GovernanceConfig`, `FrameworkConfig`: declarative configuration dataclasses.

**Examples**:
- `examples/03_multi_framework_orchestration.py`: FERPA + HIPAA + ISO 42001 simultaneous orchestration with `ComprehensiveAuditReport`.
- `examples/04_governance_audit_skill.py`: all five scenarios — education/healthcare/enterprise factories, per-call framework scoping, audit-only shadow mode.

**Tests** (+80 new, 282 total):
- `tests/test_orchestrator.py` (42 tests): `FrameworkGuard`, `FrameworkResult`, orchestrator evaluate/guard, `ComprehensiveAuditReport` JSON/hash/summary, add/remove/enable/disable framework.
- `tests/test_iso42001.py` (27 tests): `ISO42001OperatingScope`, `ISO42001GovernancePolicy` evaluate_action (deployment gate, prohibited, permitted, human oversight), all three record types, orchestrator integration test.
- `tests/test_skill.py` (29 tests): factory constructors, `audit_action`, `audit_retrieval`, channel adapter ImportError, `_framework_scope` context manager.

**Top-level exports** (added to `__init__.py`):
`FrameworkGuard`, `FrameworkResult`, `MultiFrameworkDecision`, `ComprehensiveAuditReport`, `GovernanceOrchestrator`, `FrameworkConfig`, `GovernanceConfig`, `GovernanceAuditSkill`.

---

## [0.4.1] — 2026-04-13

### Added
- `integrations/llama_index.py`: `PolicyWorkflowGuard` — LlamaIndex 0.12+ event-driven Workflow guard step. Receives a `PolicyWorkflowEvent`, evaluates `ActionPolicy`, emits `GovernanceAuditRecord`, and either passes the event downstream (permitted) or raises `PermissionError` (denied/escalation-blocked). Closes #17.
- `integrations/llama_index.py`: `PolicyWorkflowEvent` — Workflow event type carrying `documents`, `query`, and `action_name` between Workflow steps.
- `integrations/haystack.py`: `make_haystack_policy_guard()` — factory that returns a Haystack 2.27 `@component`-decorated class enforcing `ActionPolicy` inside a Haystack pipeline. Applies `@component` and `@component.output_types(documents=list)` at call time (lazy Haystack import). Closes #18.
- `integrations/__init__.py`: exports `PolicyWorkflowGuard`, `PolicyWorkflowEvent`, `make_haystack_policy_guard`

---

## [0.4.0] — 2026-04-12

### Added
- `integrations/maf.py`: `PolicyMiddleware` — Microsoft Agent Framework (MAF) middleware intercepting agent messages, evaluating `ActionPolicy`, emitting `GovernanceAuditRecord` per call, and blocking escalated actions. MAF is the enterprise successor to AutoGen and Semantic Kernel (2026).
- `[maf]` optional dependency: `microsoft-agent-framework>=1.0.0`
- `[all]` extra combining all framework integrations (crewai, langchain, llama-index, semantic-kernel, haystack, maf)

### Changed
- Bumped ecosystem compatibility pins:
  - `crewai`: `>=1.0.0` → `>=1.14.0` (CrewAI 1.14.1 current; tool-search support, Anthropic contextvars propagation)
  - `semantic-kernel`: `>=1.0.0` → `>=1.41.0` (Semantic Kernel 1.41.1 current)
  - `haystack-ai`: `>=2.0.0` → `>=2.20.0` (Haystack 2.27.0 current)
- `integrations/__init__.py`: added MAF deprecation notice for AutoGen and Semantic Kernel; exports updated
- `pyproject.toml`: version bumped to 0.4.0

### Deprecation Notice
AutoGen (`pyautogen`) is in maintenance mode as of 2026 — Microsoft has moved to Microsoft Agent Framework (MAF). The `autogen.py` integration remains functional for backward compatibility. **New projects should use `integrations/maf.py`** (`PolicyMiddleware`). The `autogen` optional dependency will be removed in v1.0.0.

Similarly, Semantic Kernel (`semantic-kernel`) projects are recommended to migrate to MAF per Microsoft guidance.

---

## [0.3.0] — 2026-04-12

### Added
- Enhanced CI: coverage reporting (Codecov), ruff format check, build-check job, pip cache, concurrency cancellation
- Automation: PR auto-labeler, stale bot, Conventional Commits PR title check, first-contributor welcome bot
- Dependabot; CODEOWNERS; SECURITY.md; pre-commit config
- `adapters/crewai.py`: `EnterpriseActionGuard` — CrewAI tool wrapper with `ActionPolicy` enforcement + `PolicyViolationError`
- `adapters/autogen.py`: `PolicyEnforcingAgent` — AutoGen `ConversableAgent` duck-typing with policy-gated `generate_reply`
- `adapters/semantic_kernel.py`: `PolicyKernelPlugin` — SK-callable `check_action_permitted()` and `get_permitted_actions()`
- `integrations/langchain.py`: `GovernanceCallbackHandler` — `on_tool_start` enforcement with escalation support
- ADRs: `docs/adr/003-adapter-over-inheritance.md`, `004-framework-agnostic-core.md`
- README: badges, governance flow diagram, 30-second CrewAI example, framework/regulations tables, BibTeX citation
- GitHub Discussions; 22 standardized labels; milestones v0.3.0 + v1.0.0

---

## [0.2.0] - 2026-04-11

### Added

**Regulation modules:**
- `regulations.gdpr` — GDPR (EU 2016/679) policy helpers:
  - `make_gdpr_processing_policy()` — policy factory with DPO escalation rules
  - `GDPRSubjectRequest` — Art. 15/17 subject access/erasure requests with 30-day deadline
  - `GDPRProcessingRecord` — Art. 30 Record of Processing Activities (RoPA)
- `regulations.ccpa` — CCPA/CPRA (Cal. Civil Code §§ 1798.100–1798.199) policy helpers:
  - `make_ccpa_processing_policy()` — policy factory for California consumer data
  - `CCPAConsumerRequest` — know/delete/opt-out/correct requests with 45-day deadline
  - `CCPADataInventoryRecord` — data category inventory for § 1798.110 disclosures
- `regulations.soc2` — SOC 2 Trust Services Criteria policy helpers:
  - `make_soc2_agent_policy()` — policy factory enforcing CC6 logical access controls
  - `SOC2ControlTestResult` — structured evidence record for SOC 2 audit packages
  - `SOC2TrustCategory` — Security, Availability, Processing Integrity, Confidentiality, Privacy

**Framework integrations:**
- `integrations.autogen.GovernedAutoGenAgent` — wraps any AutoGen ConversableAgent;
  `.guarded_tool()` and `.guard_action()` enforce policy on every tool call
- `integrations.llama_index.GovernedQueryEngine` — wraps any LlamaIndex QueryEngine;
  `.query()` and `.aquery()` evaluated against policy before execution
- `integrations.semantic_kernel.GovernedKernelPlugin` — wraps Semantic Kernel functions;
  `.from_object()` auto-registers all public methods with policy enforcement;
  `.add_function()` for manual registration with fluent chaining
- `integrations.haystack.GovernedHaystackComponent` — Haystack-compatible component
  wrapping document processing steps; `.run()` and `.guard_callable()` interfaces

**Cross-cutting compliance primitives:**
- `pii_detector.PIIDetector` — zero-dependency regex PII pre-flight scanner:
  - Detects SSN, EMAIL, PHONE, CREDIT_CARD, IP_ADDRESS, DATE_OF_BIRTH, MRN, BANK_ACCOUNT
  - `.scan()` returns `PIIScanResult` with `PIIFinding` list and category set
  - `.redact()` replaces matches with `[REDACTED-<CATEGORY>]`
  - Category filtering for targeted detection
- `consent.ConsentStore` — in-memory consent registry with pluggable database backend:
  - `ConsentRecord.grant()` / `.revoke()` factories
  - `.is_consented()`, `.latest()`, `.history()` lookups
  - Expiry support (GDPR Art. 7(3) revocation)
- `lineage.LineageTracker` — data lineage trail for regulated pipeline runs:
  - `LineageEventType` — RETRIEVAL, COMPLIANCE_FILTER, CONTEXT_ASSEMBLY, LLM_INPUT, LLM_OUTPUT, TOOL_CALL, DISCLOSURE
  - `.record_retrieval()` and `.record_compliance_filter()` typed helpers
  - `.to_audit_trail()` — JSON-serialisable audit trail per pipeline execution

**OSS infrastructure:**
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- `ECOSYSTEM.md` — regulation and framework coverage matrix
- Issue templates: new-regulation, new-framework-integration

### Changed
- `pyproject.toml` → version `0.2.0`; added `autogen`, `llama-index`, `semantic-kernel`,
  `haystack` optional dependency groups; expanded keywords

---

## [0.1.0] - 2026-04-11

### Added

- `ActionPolicy` — defines allowed/denied actions and escalation rules for a regulated agent context
- `EscalationRule` — triggers human-in-the-loop or compliance routing when a matching action is attempted
- `PolicyDecision` — result type returned by `ActionPolicy.permits()`
- `GovernedActionGuard` — framework-agnostic guard that checks policy, emits audit records, and optionally blocks on escalation before executing any callable
- `GovernanceAuditRecord` — structured compliance audit record covering FERPA (34 CFR § 99.32), HIPAA (45 CFR § 164.312(b)), and GLBA (16 CFR § 314.4(e)) logging requirements
- `regulations.ferpa` — `make_ferpa_student_policy()` and `make_ferpa_advisor_policy()` pre-built policy factories for FERPA-regulated agents
- `regulations.hipaa` — `make_hipaa_treating_provider_policy()`, `make_hipaa_billing_staff_policy()`, `make_hipaa_researcher_policy()` for HIPAA-regulated agents
- `regulations.glba` — `make_glba_customer_service_policy()` and `make_glba_loan_officer_policy()` for GLBA-regulated agents
- `integrations.crewai.EnterpriseActionGuard` — CrewAI `BaseTool` wrapper backed by `GovernedActionGuard`
- `integrations.langchain.FERPAComplianceCallbackHandler` — LangChain `BaseCallbackHandler` that applies two-layer FERPA identity filtering to retrieval results and emits `GovernanceAuditRecord` per 34 CFR § 99.32
- GitHub Actions CI matrix (Python 3.10, 3.11, 3.12) with pytest, ruff, mypy
- PyPI OIDC trusted publishing workflow (triggers on GitHub release)
- 50+ unit tests covering policy evaluation, audit record structure, regulation helpers, and guard execution paths

[0.1.0]: https://github.com/ashutoshrana/regulated-ai-governance/releases/tag/v0.1.0
