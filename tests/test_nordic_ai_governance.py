"""
Tests for 28_nordic_ai_governance.py — Nordic/Scandinavian AI Governance
framework covering Sweden (IMY AI Guidelines 2023 + SFS 2018:218), Denmark
(Datatilsynet AI Guidance 2023 + Act No. 502/2018), Finland (TSV AI Guidelines
2023 + Data Protection Act 1050/2018), and the Nordic cross-border transfer
framework.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load():
    _name = "nordic_ai_governance_28"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "28_nordic_ai_governance.py",
        ),
    )
    mod = types.ModuleType(_name)
    sys.modules[_name] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _base_ctx(**overrides):
    """Return a fully-compliant Swedish minimal-risk general-sector context."""
    defaults = dict(
        user_id="u1",
        jurisdiction="SE",
        sector="general",
        ai_risk_level="minimal",
        is_public_authority=False,
        has_gdpr_basis=True,
        has_dpia=True,
        is_automated_decision=False,
        has_human_oversight=True,
        involves_sensitive_data=False,
        has_explicit_consent=True,
        is_registered_ai_system=True,
        has_transparency_notice=True,
        source_jurisdiction="SE",
        destination_jurisdiction="SE",
        has_transfer_safeguards=False,
    )
    defaults.update(overrides)
    return mod.NordicAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal document."""
    defaults = dict(
        content="test document content",
        document_id="d1",
        doc_type="ai_decision_record",
    )
    defaults.update(overrides)
    return mod.NordicAIDocument(**defaults)


# ===========================================================================
# TestSwedenAIFilter
# ===========================================================================


class TestSwedenAIFilter:
    """Layer 1: Sweden — IMY AI Guidelines 2023 + SFS 2018:218."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.SwedenAIFilter().evaluate(ctx, doc)

    # --- IMY Guideline §3.2 — public authority automated decision without oversight ---

    def test_public_authority_automated_no_oversight_denied(self):
        """Public authority + automated decision + no oversight → DENIED."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_public_authority_automated_no_oversight_cites_imy_32(self):
        """DENIED for public authority without oversight cites IMY §3.2."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "3.2" in combined

    def test_public_authority_automated_with_oversight_approved(self):
        """Public authority + automated decision WITH oversight → APPROVED."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_public_authority_automated_no_oversight_approved(self):
        """Non-public-authority automated decision without oversight → APPROVED (§3.2 not triggered)."""
        ctx = _base_ctx(
            is_public_authority=False,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_public_authority_non_automated_no_oversight_approved(self):
        """Public authority + NOT automated decision + no oversight → APPROVED (§3.2 not triggered)."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=False,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- SFS 2018:218 §3 — sensitive data without consent or GDPR basis ---

    def test_sensitive_data_no_consent_no_basis_denied(self):
        """Sensitive data + no explicit consent + no GDPR basis → DENIED."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_sensitive_data_no_consent_no_basis_cites_sfs_3(self):
        """DENIED for sensitive data without consent/basis cites SFS 2018:218 §3."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "2018:218" in combined or "SFS" in combined

    def test_sensitive_data_with_explicit_consent_approved(self):
        """Sensitive data + explicit consent (no GDPR basis) → APPROVED."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=True,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_sensitive_data_with_gdpr_basis_no_consent_approved(self):
        """Sensitive data + GDPR basis (no explicit consent) → APPROVED."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_no_sensitive_data_no_consent_no_basis_approved(self):
        """No sensitive data + no consent + no basis → APPROVED (§3 not triggered)."""
        ctx = _base_ctx(
            involves_sensitive_data=False,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- IMY Guideline §4.1 — high-risk AI without transparency notice ---

    def test_high_risk_no_transparency_notice_requires_review(self):
        """High-risk AI + no transparency notice → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_transparency_notice_cites_imy_41(self):
        """REQUIRES_HUMAN_REVIEW for missing transparency notice cites IMY §4.1."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "4.1" in combined

    def test_high_risk_with_transparency_notice_approved(self):
        """High-risk AI WITH transparency notice → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_limited_risk_no_transparency_notice_approved(self):
        """Limited-risk AI + no transparency notice → APPROVED (§4.1 not triggered)."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_compliant_baseline_approved(self):
        """Fully compliant context → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_cites_imy_and_sfs(self):
        """Compliant approval cites IMY Guidelines and SFS 2018:218."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "IMY" in combined or "SFS" in combined

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_denied_requires_logging(self):
        """DENIED result sets requires_logging=True."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestDenmarkAIFilter
# ===========================================================================


class TestDenmarkAIFilter:
    """Layer 2: Denmark — Datatilsynet AI Guidance 2023 + Act No. 502/2018."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.DenmarkAIFilter().evaluate(ctx, doc)

    # --- Act No. 502/2018 §7 — high-risk + sensitive data + no DPIA: denied ---

    def test_high_risk_sensitive_no_dpia_denied(self):
        """High-risk + sensitive data + no DPIA → DENIED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_sensitive_no_dpia_cites_act_502_s7(self):
        """DENIED for missing DPIA cites Act 502/2018 §7."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "502" in combined and "7" in combined

    def test_high_risk_sensitive_with_dpia_approved(self):
        """High-risk + sensitive data + DPIA present → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_limited_risk_sensitive_no_dpia_not_denied(self):
        """Limited-risk + sensitive data + no DPIA → not DENIED (§7 requires high risk)."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            involves_sensitive_data=True,
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision != "DENIED"

    def test_high_risk_no_sensitive_no_dpia_approved(self):
        """High-risk + no sensitive data + no DPIA → APPROVED (§7 not triggered)."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=False,
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Datatilsynet AI Guidance §2.3 — limited/high automated without oversight ---

    def test_high_risk_automated_no_oversight_requires_review(self):
        """High-risk + automated decision + no oversight → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="high",
            is_automated_decision=True,
            has_human_oversight=False,
            involves_sensitive_data=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_limited_risk_automated_no_oversight_requires_review(self):
        """Limited-risk + automated decision + no oversight → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"

    def test_datatilsynet_23_cites_s23(self):
        """REQUIRES_HUMAN_REVIEW for missing oversight cites Datatilsynet §2.3."""
        ctx = _base_ctx(
            ai_risk_level="high",
            is_automated_decision=True,
            has_human_oversight=False,
            involves_sensitive_data=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "2.3" in combined

    def test_minimal_risk_automated_no_oversight_approved(self):
        """Minimal-risk + automated decision + no oversight → APPROVED (§2.3 not triggered)."""
        ctx = _base_ctx(
            ai_risk_level="minimal",
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_high_risk_non_automated_no_oversight_approved(self):
        """High-risk + NOT automated + no oversight → APPROVED (§2.3 not triggered)."""
        ctx = _base_ctx(
            ai_risk_level="high",
            is_automated_decision=False,
            has_human_oversight=False,
            involves_sensitive_data=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Datatilsynet AI Guidance §3.1 — public sector high-risk without registry ---

    def test_public_sector_high_risk_not_registered_requires_review(self):
        """Public sector + high-risk + not registered → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector="public_sector",
            ai_risk_level="high",
            is_registered_ai_system=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"

    def test_public_sector_high_risk_not_registered_cites_s31(self):
        """REQUIRES_HUMAN_REVIEW for unregistered system cites Datatilsynet §3.1."""
        ctx = _base_ctx(
            sector="public_sector",
            ai_risk_level="high",
            is_registered_ai_system=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "3.1" in combined

    def test_public_sector_high_risk_registered_approved(self):
        """Public sector + high-risk + registered → APPROVED."""
        ctx = _base_ctx(
            sector="public_sector",
            ai_risk_level="high",
            is_registered_ai_system=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_general_sector_high_risk_not_registered_approved(self):
        """General sector + high-risk + not registered → APPROVED (§3.1 only applies to public sector)."""
        ctx = _base_ctx(
            sector="general",
            ai_risk_level="high",
            is_registered_ai_system=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_compliant_baseline_approved(self):
        """Fully compliant context → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_cites_datatilsynet_and_act502(self):
        """Compliant approval cites Datatilsynet Guidance and Act No. 502/2018."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Datatilsynet" in combined or "502" in combined

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False


# ===========================================================================
# TestFinlandAIFilter
# ===========================================================================


class TestFinlandAIFilter:
    """Layer 3: Finland — TSV AI Guidelines 2023 + Data Protection Act 1050/2018."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.FinlandAIFilter().evaluate(ctx, doc)

    # --- Data Protection Act §6 — sensitive data without consent or legal basis ---

    def test_sensitive_data_no_consent_no_basis_denied(self):
        """Sensitive data + no explicit consent + no GDPR basis → DENIED."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_sensitive_data_no_consent_no_basis_cites_dpa_s6(self):
        """DENIED for sensitive data without basis cites Data Protection Act §6."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "1050" in combined or "§6" in combined or "6" in combined

    def test_sensitive_data_with_explicit_consent_approved(self):
        """Sensitive data + explicit consent → APPROVED."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=True,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_sensitive_data_with_gdpr_basis_approved(self):
        """Sensitive data + GDPR legal basis (no explicit consent) → APPROVED."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_no_sensitive_data_no_consent_approved(self):
        """No sensitive data + no consent → APPROVED (§6 not triggered)."""
        ctx = _base_ctx(
            involves_sensitive_data=False,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- TSV AI Guidelines §2.2 — public authority automated without transparency notice ---

    def test_public_authority_automated_no_transparency_denied(self):
        """Public authority + automated decision + no transparency notice → DENIED."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_public_authority_automated_no_transparency_cites_tsv_22(self):
        """DENIED for missing transparency notice cites TSV §2.2."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "2.2" in combined

    def test_public_authority_automated_with_transparency_approved(self):
        """Public authority + automated decision + transparency notice present → APPROVED."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_public_authority_automated_no_transparency_approved(self):
        """Non-public-authority + automated + no transparency → APPROVED (§2.2 not triggered)."""
        ctx = _base_ctx(
            is_public_authority=False,
            is_automated_decision=True,
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_public_authority_non_automated_no_transparency_approved(self):
        """Public authority + NOT automated + no transparency → APPROVED (§2.2 not triggered)."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=False,
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- TSV AI Guidelines §3.3 — high-risk AI without DPIA ---

    def test_high_risk_no_dpia_requires_review(self):
        """High-risk AI + no DPIA → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_dpia_cites_tsv_33(self):
        """REQUIRES_HUMAN_REVIEW for missing DPIA cites TSV §3.3."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_dpia=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "3.3" in combined

    def test_high_risk_with_dpia_approved(self):
        """High-risk AI + DPIA present → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_dpia=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_limited_risk_no_dpia_approved(self):
        """Limited-risk AI + no DPIA → APPROVED (§3.3 not triggered)."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_compliant_baseline_approved(self):
        """Fully compliant context → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_cites_tsv_and_dpa(self):
        """Compliant approval cites TSV Guidelines and Data Protection Act 1050/2018."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "TSV" in combined or "1050" in combined

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_denied_requires_logging(self):
        """DENIED result sets requires_logging=True."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestNordicCrossBorderFilter
# ===========================================================================


class TestNordicCrossBorderFilter:
    """Layer 4: Nordic + EEA cross-border transfer framework."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.NordicCrossBorderFilter().evaluate(ctx, doc)

    # --- Intra-EEA (Nordic) transfers ---

    def test_se_to_se_approved(self):
        """SE→SE intra-EEA transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="SE", destination_jurisdiction="SE")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_se_to_dk_approved(self):
        """SE→DK intra-Nordic EEA transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="SE", destination_jurisdiction="DK")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_fi_to_no_approved(self):
        """FI→NO EEA transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="FI", destination_jurisdiction="NO")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_dk_to_is_approved(self):
        """DK→IS (Iceland, EEA member) transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="DK", destination_jurisdiction="IS")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_dk_to_li_approved(self):
        """DK→LI (Liechtenstein, EEA member) transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="DK", destination_jurisdiction="LI")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Intra-EU transfers ---

    def test_se_to_de_approved(self):
        """SE→DE (Germany, EU member) transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="SE", destination_jurisdiction="DE")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_fi_to_fr_approved(self):
        """FI→FR (France, EU member) transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="FI", destination_jurisdiction="FR")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_dk_to_nl_approved(self):
        """DK→NL (Netherlands, EU member) transfer → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="DK", destination_jurisdiction="NL")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_not_requires_logging(self):
        """Intra-EEA approved transfer sets requires_logging=False."""
        ctx = _base_ctx(source_jurisdiction="SE", destination_jurisdiction="DK")
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_intra_eea_cites_gdpr_art45(self):
        """Intra-EEA approval cites GDPR Article 45 adequacy."""
        ctx = _base_ctx(source_jurisdiction="SE", destination_jurisdiction="DK")
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "45" in combined or "EEA" in combined

    # --- Non-EEA with GDPR Art. 46 safeguards ---

    def test_se_to_us_with_safeguards_approved(self):
        """SE→US with transfer safeguards (SCCs) → APPROVED."""
        ctx = _base_ctx(
            source_jurisdiction="SE",
            destination_jurisdiction="US",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_fi_to_sg_with_safeguards_approved(self):
        """FI→SG with transfer safeguards → APPROVED."""
        ctx = _base_ctx(
            source_jurisdiction="FI",
            destination_jurisdiction="SG",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_eea_with_safeguards_cites_gdpr_art46(self):
        """Non-EEA transfer with safeguards cites GDPR Article 46."""
        ctx = _base_ctx(
            source_jurisdiction="DK",
            destination_jurisdiction="JP",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "46" in combined or "SCC" in combined or "BCR" in combined

    def test_non_eea_with_safeguards_requires_logging(self):
        """Non-EEA transfer with safeguards sets requires_logging=True."""
        ctx = _base_ctx(
            source_jurisdiction="SE",
            destination_jurisdiction="BR",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True

    # --- Non-EEA without safeguards — jurisdiction-specific denials ---

    def test_se_to_us_no_safeguards_denied(self):
        """SE→US without safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="SE",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_se_to_us_no_safeguards_cites_sfs_33(self):
        """SE→US denial cites Sweden SFS 2018:218 §33."""
        ctx = _base_ctx(
            source_jurisdiction="SE",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "33" in combined and ("SFS" in combined or "2018:218" in combined)

    def test_dk_to_us_no_safeguards_denied(self):
        """DK→US without safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="DK",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"

    def test_dk_to_us_no_safeguards_cites_act502_s25(self):
        """DK→US denial cites Denmark Act 502/2018 §25."""
        ctx = _base_ctx(
            source_jurisdiction="DK",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "502" in combined and "25" in combined

    def test_fi_to_us_no_safeguards_denied(self):
        """FI→US without safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="FI",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"

    def test_fi_to_us_no_safeguards_cites_dpa_1050_s33(self):
        """FI→US denial cites Finland Data Protection Act 1050/2018 §33."""
        ctx = _base_ctx(
            source_jurisdiction="FI",
            destination_jurisdiction="JP",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "1050" in combined and "33" in combined

    def test_unknown_source_no_safeguards_denied(self):
        """Unknown source jurisdiction → DENIED with generic Nordic GDPR message."""
        ctx = _base_ctx(
            source_jurisdiction="XX",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"

    def test_denied_transfer_requires_logging(self):
        """DENIED transfer sets requires_logging=True."""
        ctx = _base_ctx(
            source_jurisdiction="SE",
            destination_jurisdiction="CN",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestNordicAIGovernanceOrchestrator
# ===========================================================================


class TestNordicAIGovernanceOrchestrator:
    """Full orchestrator pipeline tests."""

    def _run(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.NordicAIGovernanceOrchestrator().evaluate(ctx, doc)

    def test_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        ctx = _base_ctx()
        results = self._run(ctx)
        assert len(results) == 4

    def test_all_four_filters_run_on_denial(self):
        """All four filters run regardless of earlier DENIED results."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        results = self._run(ctx)
        assert len(results) == 4

    def test_filter_names_present(self):
        """Each result carries a non-empty filter_name."""
        ctx = _base_ctx()
        results = self._run(ctx)
        for r in results:
            assert r.filter_name

    def test_fully_compliant_all_approved(self):
        """Fully compliant context → all four results APPROVED."""
        ctx = _base_ctx()
        results = self._run(ctx)
        for r in results:
            assert r.decision == "APPROVED", f"{r.filter_name}: {r.decision}"

    def test_sweden_denial_appears_in_first_result(self):
        """Sweden DENIED appears in first result for public authority without oversight."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        results = self._run(ctx)
        assert results[0].decision == "DENIED"

    def test_denmark_denial_appears_in_second_result(self):
        """Denmark DENIED appears in second result for high-risk sensitive without DPIA."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=False,
            has_transparency_notice=True,
        )
        results = self._run(ctx)
        assert results[1].decision == "DENIED"

    def test_finland_denial_appears_in_third_result(self):
        """Finland DENIED appears in third result for public authority without transparency."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_transparency_notice=False,
        )
        results = self._run(ctx)
        assert results[2].decision == "DENIED"

    def test_cross_border_denial_appears_in_fourth_result(self):
        """Cross-border DENIED appears in fourth result for non-EEA without safeguards."""
        ctx = _base_ctx(
            source_jurisdiction="SE",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        results = self._run(ctx)
        assert results[3].decision == "DENIED"

    def test_sweden_requires_review_propagates(self):
        """Sweden REQUIRES_HUMAN_REVIEW for high-risk without transparency notice."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        results = self._run(ctx)
        assert results[0].decision == "REQUIRES_HUMAN_REVIEW"

    def test_denmark_requires_review_propagates(self):
        """Denmark REQUIRES_HUMAN_REVIEW for high-risk automated without oversight."""
        ctx = _base_ctx(
            ai_risk_level="high",
            is_automated_decision=True,
            has_human_oversight=False,
            involves_sensitive_data=False,
            has_transparency_notice=True,
        )
        results = self._run(ctx)
        assert results[1].decision == "REQUIRES_HUMAN_REVIEW"

    def test_finland_requires_review_propagates(self):
        """Finland REQUIRES_HUMAN_REVIEW for high-risk without DPIA."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_dpia=False,
        )
        results = self._run(ctx)
        assert results[2].decision == "REQUIRES_HUMAN_REVIEW"


# ===========================================================================
# TestNordicAIGovernanceReport
# ===========================================================================


class TestNordicAIGovernanceReport:
    """Report aggregation, overall_decision, is_compliant, and compliance_summary tests."""

    def _make_report(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.NordicAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.NordicAIGovernanceReport(
            context=ctx,
            document=doc,
            filter_results=results,
        )

    # --- overall_decision aggregation ---

    def test_all_approved_overall_approved(self):
        """All filters APPROVED → overall_decision == APPROVED."""
        report = self._make_report(_base_ctx())
        assert report.overall_decision == "APPROVED"

    def test_all_approved_is_compliant(self):
        """All filters APPROVED → is_compliant == True."""
        report = self._make_report(_base_ctx())
        assert report.is_compliant is True

    def test_one_denied_overall_denied(self):
        """One DENIED filter → overall_decision == DENIED."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"

    def test_one_denied_not_compliant(self):
        """One DENIED filter → is_compliant == False."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        report = self._make_report(ctx)
        assert report.is_compliant is False

    def test_requires_review_only_overall_requires_review(self):
        """REQUIRES_HUMAN_REVIEW (no DENIED) → overall_decision == REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"

    def test_requires_review_is_compliant(self):
        """REQUIRES_HUMAN_REVIEW without DENIED → is_compliant == True."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        report = self._make_report(ctx)
        assert report.is_compliant is True

    def test_denied_takes_priority_over_requires_review(self):
        """DENIED takes priority over REQUIRES_HUMAN_REVIEW in overall_decision."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"

    # --- compliance_summary content ---

    def test_compliance_summary_contains_user_id(self):
        """compliance_summary includes the user_id."""
        ctx = _base_ctx(user_id="nordic-test-user-99")
        report = self._make_report(ctx)
        assert "nordic-test-user-99" in report.compliance_summary

    def test_compliance_summary_contains_overall_decision(self):
        """compliance_summary includes the overall decision string."""
        ctx = _base_ctx()
        report = self._make_report(ctx)
        assert report.overall_decision in report.compliance_summary

    def test_compliance_summary_contains_all_filter_names(self):
        """compliance_summary lists all four filter names."""
        ctx = _base_ctx()
        report = self._make_report(ctx)
        summary = report.compliance_summary
        assert "SWEDEN_AI_FILTER" in summary
        assert "DENMARK_AI_FILTER" in summary
        assert "FINLAND_AI_FILTER" in summary
        assert "NORDIC_CROSS_BORDER_FILTER" in summary

    def test_compliance_summary_contains_jurisdiction(self):
        """compliance_summary includes the jurisdiction."""
        ctx = _base_ctx(jurisdiction="DK")
        report = self._make_report(ctx)
        assert "DK" in report.compliance_summary

    def test_compliance_summary_contains_sector(self):
        """compliance_summary includes the sector."""
        ctx = _base_ctx(sector="healthcare")
        report = self._make_report(ctx)
        assert "healthcare" in report.compliance_summary

    def test_compliance_summary_contains_risk_level(self):
        """compliance_summary includes the risk level."""
        ctx = _base_ctx(ai_risk_level="high", has_transparency_notice=True, has_dpia=True)
        report = self._make_report(ctx)
        assert "high" in report.compliance_summary

    # --- FilterResult.is_denied semantics ---

    def test_filter_result_is_denied_false_for_approved(self):
        """FilterResult.is_denied is False for APPROVED decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="APPROVED",
            reason="ok",
            regulation_citation="",
        )
        assert result.is_denied is False

    def test_filter_result_is_denied_false_for_requires_review(self):
        """FilterResult.is_denied is False for REQUIRES_HUMAN_REVIEW decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="REQUIRES_HUMAN_REVIEW",
            reason="needs review",
            regulation_citation="",
        )
        assert result.is_denied is False

    def test_filter_result_is_denied_true_for_denied(self):
        """FilterResult.is_denied is True only for DENIED decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="DENIED",
            reason="denied",
            regulation_citation="",
        )
        assert result.is_denied is True

    # --- Cross-jurisdiction scenarios ---

    def test_fi_to_us_no_safeguards_cross_border_denial(self):
        """FI→US without safeguards triggers cross-border denial in report."""
        ctx = _base_ctx(
            source_jurisdiction="FI",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"
        assert not report.is_compliant

    def test_fi_to_no_intra_eea_approved_report(self):
        """FI→NO intra-EEA transfer produces fully APPROVED report."""
        ctx = _base_ctx(
            source_jurisdiction="FI",
            destination_jurisdiction="NO",
            has_transfer_safeguards=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "APPROVED"
        assert report.is_compliant is True
