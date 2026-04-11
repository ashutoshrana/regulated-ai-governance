"""Tests for regulation-specific policy helpers (FERPA, HIPAA, GLBA)."""

from __future__ import annotations

from regulated_ai_governance.regulations.ferpa import (
    ENROLLMENT_ADVISOR_ALLOWED_ACTIONS,
    FERPA_HIGH_RISK_ACTIONS,
    make_ferpa_advisor_policy,
    make_ferpa_student_policy,
)
from regulated_ai_governance.regulations.glba import (
    make_glba_customer_service_policy,
    make_glba_loan_officer_policy,
)
from regulated_ai_governance.regulations.hipaa import (
    make_hipaa_billing_staff_policy,
    make_hipaa_researcher_policy,
    make_hipaa_treating_provider_policy,
)

# ---------------------------------------------------------------------------
# FERPA
# ---------------------------------------------------------------------------


class TestFERPAStudentPolicy:
    def test_permits_standard_enrollment_advisor_actions(self):
        policy = make_ferpa_student_policy()
        for action in ENROLLMENT_ADVISOR_ALLOWED_ACTIONS:
            permitted, _ = policy.permits(action)
            assert permitted is True, f"Expected {action} to be permitted"

    def test_denies_high_risk_actions(self):
        policy = make_ferpa_student_policy()
        for action in FERPA_HIGH_RISK_ACTIONS:
            permitted, _ = policy.permits(action)
            assert permitted is False, f"Expected {action} to be denied"

    def test_escalates_export_action(self):
        policy = make_ferpa_student_policy(escalate_exports_to="ferpa_officer")
        result = policy.escalation_for("export_student_records_pdf", {})
        assert result is not None
        assert result.escalate_to == "ferpa_officer"

    def test_escalates_share_action(self):
        policy = make_ferpa_student_policy()
        result = policy.escalation_for("share_records_externally", {})
        assert result is not None

    def test_custom_allowed_categories_override(self):
        custom = {"read_enrollment_status"}
        policy = make_ferpa_student_policy(allowed_record_categories=custom)
        permitted, _ = policy.permits("read_enrollment_status")
        assert permitted is True
        # read_course_schedule not in custom set
        permitted, _ = policy.permits("read_course_schedule")
        assert permitted is False


class TestFERPAAdvisorPolicy:
    def test_permits_advisor_read_actions(self):
        policy = make_ferpa_advisor_policy()
        permitted, _ = policy.permits("read_student_academic_record")
        assert permitted is True

    def test_denies_bulk_export(self):
        policy = make_ferpa_advisor_policy()
        permitted, _ = policy.permits("bulk_export")
        assert permitted is False

    def test_denies_cross_student_query(self):
        policy = make_ferpa_advisor_policy()
        permitted, _ = policy.permits("cross_student_query")
        assert permitted is False


# ---------------------------------------------------------------------------
# HIPAA
# ---------------------------------------------------------------------------


class TestHIPAATreatingProviderPolicy:
    def test_permits_clinical_read_actions(self):
        policy = make_hipaa_treating_provider_policy()
        permitted, _ = policy.permits("read_diagnosis")
        assert permitted is True
        permitted, _ = policy.permits("read_treatment_notes")
        assert permitted is True

    def test_denies_phi_export(self):
        policy = make_hipaa_treating_provider_policy()
        permitted, _ = policy.permits("export_phi")
        assert permitted is False

    def test_escalates_external_share(self):
        policy = make_hipaa_treating_provider_policy(
            escalate_external_share_to="hipaa_privacy_officer"
        )
        result = policy.escalation_for("share_records_externally", {})
        assert result is not None
        assert result.escalate_to == "hipaa_privacy_officer"


class TestHIPAABillingStaffPolicy:
    def test_permits_billing_actions(self):
        policy = make_hipaa_billing_staff_policy()
        permitted, _ = policy.permits("read_procedure_codes")
        assert permitted is True

    def test_denies_clinical_notes(self):
        policy = make_hipaa_billing_staff_policy()
        permitted, _ = policy.permits("read_treatment_notes")
        assert permitted is False

    def test_denies_mental_health_records(self):
        policy = make_hipaa_billing_staff_policy()
        permitted, _ = policy.permits("read_mental_health_notes")
        assert permitted is False


class TestHIPAAResearcherPolicy:
    def test_permits_irb_approved_categories(self):
        irb_approved = {"read_diagnosis_codes", "read_lab_results"}
        policy = make_hipaa_researcher_policy(irb_approved_categories=irb_approved)
        permitted, _ = policy.permits("read_diagnosis_codes")
        assert permitted is True

    def test_denies_phi_export(self):
        policy = make_hipaa_researcher_policy(
            irb_approved_categories={"read_lab_results"}
        )
        permitted, _ = policy.permits("export_phi")
        assert permitted is False

    def test_denies_clinical_note_creation(self):
        policy = make_hipaa_researcher_policy(
            irb_approved_categories={"read_lab_results"}
        )
        permitted, _ = policy.permits("create_clinical_note")
        assert permitted is False


# ---------------------------------------------------------------------------
# GLBA
# ---------------------------------------------------------------------------


class TestGLBACustomerServicePolicy:
    def test_permits_account_read_actions(self):
        policy = make_glba_customer_service_policy()
        permitted, _ = policy.permits("read_account_balance")
        assert permitted is True

    def test_denies_ssn_access(self):
        policy = make_glba_customer_service_policy()
        permitted, _ = policy.permits("read_social_security_number")
        assert permitted is False

    def test_denies_nnpi_export(self):
        policy = make_glba_customer_service_policy()
        permitted, _ = policy.permits("export_customer_financial_data")
        assert permitted is False

    def test_escalates_export_attempt(self):
        policy = make_glba_customer_service_policy(escalate_nnpi_export_to="glba_officer")
        result = policy.escalation_for("export_transaction_history", {})
        assert result is not None
        assert result.escalate_to == "glba_officer"


class TestGLBALoanOfficerPolicy:
    def test_permits_credit_access(self):
        policy = make_glba_loan_officer_policy()
        permitted, _ = policy.permits("read_credit_score")
        assert permitted is True

    def test_denies_bulk_export(self):
        policy = make_glba_loan_officer_policy()
        permitted, _ = policy.permits("bulk_export_customer_data")
        assert permitted is False

    def test_denies_cross_customer_query(self):
        policy = make_glba_loan_officer_policy()
        permitted, _ = policy.permits("cross_customer_query")
        assert permitted is False
