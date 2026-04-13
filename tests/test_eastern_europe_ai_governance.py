"""
Tests for 29_eastern_europe_ai_governance.py — Eastern Europe AI Governance
framework covering Poland (UODO AI Guidelines 2023 + GDPR Act Dz.U. 2018),
Czech Republic (ÚOOÚ AI Guidance 2023 + Act 110/2019 Coll.), Hungary (NAIH AI
Guidelines 2023 + Privacy Act CXII/2011), and the Eastern Europe cross-border
transfer framework.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

import pytest


# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load():
    _name = "eastern_europe_ai_governance_29"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "29_eastern_europe_ai_governance.py",
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
    """Return a fully-compliant Polish minimal-risk general-sector context."""
    defaults = dict(
        user_id="u1",
        jurisdiction="PL",
        sector="general",
        ai_risk_level="minimal",
        is_public_authority=False,
        has_gdpr_basis=True,
        has_dpia=True,
        is_automated_decision=False,
        has_human_oversight=True,
        involves_sensitive_data=False,
        has_explicit_consent=True,
        has_transparency_notice=True,
        is_biometric_processing=False,
        has_supervisory_approval=False,
        source_jurisdiction="PL",
        destination_jurisdiction="PL",
        has_transfer_safeguards=False,
    )
    defaults.update(overrides)
    return mod.EasternEuropeAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal document."""
    defaults = dict(
        content="test document content",
        document_id="d1",
        doc_type="ai_decision_record",
    )
    defaults.update(overrides)
    return mod.EasternEuropeAIDocument(**defaults)


# ===========================================================================
# TestPolandAIFilter
# ===========================================================================


class TestPolandAIFilter:
    """Layer 1: Poland — UODO AI Guidelines 2023 + GDPR Act Dz.U. 2018."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.PolandAIFilter().evaluate(ctx, doc)

    # --- UODO AI Guideline §3 — public authority automated decision without oversight ---

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

    def test_public_authority_automated_no_oversight_cites_uodo_3(self):
        """DENIED for public authority without oversight cites UODO §3."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "UODO" in combined and "§3" in combined

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
        """Non-public-authority automated decision without oversight → APPROVED (§3 not triggered)."""
        ctx = _base_ctx(
            is_public_authority=False,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_public_authority_non_automated_no_oversight_approved(self):
        """Public authority + NOT automated decision + no oversight → APPROVED (§3 not triggered)."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=False,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Polish GDPR Act Art. 9 — sensitive data without consent or GDPR basis ---

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

    def test_sensitive_data_no_consent_no_basis_cites_gdpr_act(self):
        """DENIED for sensitive data without consent/basis cites Polish GDPR Act."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Dz.U. 2018" in combined or "GDPR" in combined

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
        """No sensitive data + no consent + no basis → APPROVED (Art. 9 not triggered)."""
        ctx = _base_ctx(
            involves_sensitive_data=False,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- UODO AI Guideline §5 — biometric processing without supervisory approval ---

    def test_biometric_no_supervisory_approval_requires_review(self):
        """Biometric processing + no supervisory approval → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_biometric_processing=True,
            has_supervisory_approval=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_biometric_no_supervisory_approval_cites_uodo_5(self):
        """REQUIRES_HUMAN_REVIEW for biometric without approval cites UODO §5."""
        ctx = _base_ctx(
            is_biometric_processing=True,
            has_supervisory_approval=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "UODO" in combined and "§5" in combined

    def test_biometric_with_supervisory_approval_approved(self):
        """Biometric processing WITH supervisory approval → APPROVED."""
        ctx = _base_ctx(
            is_biometric_processing=True,
            has_supervisory_approval=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_no_biometric_no_supervisory_approval_approved(self):
        """Non-biometric processing without supervisory approval → APPROVED (§5 not triggered)."""
        ctx = _base_ctx(
            is_biometric_processing=False,
            has_supervisory_approval=False,
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

    def test_compliant_cites_uodo_and_gdpr(self):
        """Compliant approval cites UODO Guidelines and GDPR Act."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "UODO" in combined or "GDPR" in combined

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
# TestCzechRepublicAIFilter
# ===========================================================================


class TestCzechRepublicAIFilter:
    """Layer 2: Czech Republic — ÚOOÚ AI Guidance 2023 + Act 110/2019 Coll."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.CzechRepublicAIFilter().evaluate(ctx, doc)

    # --- Act 110/2019 §16 — high-risk + sensitive data + no DPIA: denied ---

    def test_high_risk_sensitive_no_dpia_denied(self):
        """High-risk + sensitive data + no DPIA → DENIED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=False,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_sensitive_no_dpia_cites_act_110_2019(self):
        """DENIED for high-risk sensitive data without DPIA cites Act 110/2019 §16."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=False,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "110/2019" in combined and "16" in combined

    def test_high_risk_sensitive_with_dpia_approved(self):
        """High-risk + sensitive data WITH DPIA (and transparency notice) → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=True,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_limited_risk_sensitive_no_dpia_not_denied(self):
        """Limited-risk + sensitive data + no DPIA → NOT DENIED (§16 only for high-risk)."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            involves_sensitive_data=True,
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision != "DENIED"

    # --- ÚOOÚ AI Guidance §2.1 — limited/high automated decision without oversight ---

    def test_limited_risk_automated_no_oversight_requires_review(self):
        """Limited-risk automated decision without oversight → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_automated_no_oversight_but_sensitive_no_dpia_denied(self):
        """High-risk automated without oversight but also sensitive without DPIA → DENIED (§16 first)."""
        ctx = _base_ctx(
            ai_risk_level="high",
            is_automated_decision=True,
            has_human_oversight=False,
            involves_sensitive_data=True,
            has_dpia=False,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"

    def test_limited_risk_automated_no_oversight_cites_uooú_21(self):
        """REQUIRES_HUMAN_REVIEW for limited-risk automated without oversight cites ÚOOÚ §2.1."""
        ctx = _base_ctx(
            ai_risk_level="limited",
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "2.1" in combined

    def test_high_risk_automated_with_oversight_and_transparency_approved(self):
        """High-risk automated WITH oversight and transparency notice → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            is_automated_decision=True,
            has_human_oversight=True,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_minimal_risk_automated_no_oversight_approved(self):
        """Minimal-risk automated decision without oversight → APPROVED (§2.1 not triggered)."""
        ctx = _base_ctx(
            ai_risk_level="minimal",
            is_automated_decision=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- ÚOOÚ AI Guidance §4.2 — high-risk AI without transparency notice ---

    def test_high_risk_no_transparency_notice_requires_review(self):
        """High-risk AI + no transparency notice → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_transparency_notice_cites_uooú_42(self):
        """REQUIRES_HUMAN_REVIEW for missing transparency notice cites ÚOOÚ §4.2."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "4.2" in combined

    def test_high_risk_with_transparency_notice_approved(self):
        """High-risk AI WITH transparency notice → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level="high",
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_limited_risk_no_transparency_notice_approved(self):
        """Limited-risk AI + no transparency notice → APPROVED (§4.2 not triggered)."""
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

    def test_compliant_cites_uooú_and_act_110(self):
        """Compliant approval cites ÚOOÚ Guidance and Act 110/2019."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "110/2019" in combined or "ÚOOÚ" in combined

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_denied_requires_logging(self):
        """DENIED result sets requires_logging=True."""
        ctx = _base_ctx(
            ai_risk_level="high",
            involves_sensitive_data=True,
            has_dpia=False,
            has_transparency_notice=True,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestHungaryAIFilter
# ===========================================================================


class TestHungaryAIFilter:
    """Layer 3: Hungary — NAIH AI Guidelines 2023 + Privacy Act CXII/2011."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.HungaryAIFilter().evaluate(ctx, doc)

    # --- NAIH AI Guideline §3.2 — public authority automated decision without oversight ---

    def test_public_authority_automated_no_oversight_denied(self):
        """Public authority + automated decision + no oversight → DENIED."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_public_authority=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_public_authority_automated_no_oversight_cites_naih_32(self):
        """DENIED for public authority without oversight cites NAIH §3.2."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_public_authority=True,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "NAIH" in combined and "3.2" in combined

    def test_public_authority_automated_with_oversight_approved(self):
        """Public authority + automated decision WITH oversight → APPROVED."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_public_authority=True,
            has_human_oversight=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_public_authority_automated_no_oversight_approved(self):
        """Non-public-authority automated without oversight → APPROVED (§3.2 not triggered)."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_public_authority=False,
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Privacy Act CXII/2011 §5 — sensitive data without consent or GDPR basis ---

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

    def test_sensitive_data_no_consent_no_basis_cites_privacy_act(self):
        """DENIED for sensitive data without consent/basis cites Privacy Act CXII/2011 §5."""
        ctx = _base_ctx(
            involves_sensitive_data=True,
            has_explicit_consent=False,
            has_gdpr_basis=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "CXII" in combined and "§5" in combined

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

    # --- NAIH AI Guideline §5.1 — high-risk healthcare AI without DPIA ---

    def test_healthcare_high_risk_no_dpia_requires_review(self):
        """Healthcare sector + high-risk AI + no DPIA → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector="healthcare",
            ai_risk_level="high",
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_healthcare_high_risk_no_dpia_cites_naih_51(self):
        """REQUIRES_HUMAN_REVIEW for healthcare without DPIA cites NAIH §5.1."""
        ctx = _base_ctx(
            sector="healthcare",
            ai_risk_level="high",
            has_dpia=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "NAIH" in combined and "5.1" in combined

    def test_healthcare_high_risk_with_dpia_approved(self):
        """Healthcare sector + high-risk AI WITH DPIA → APPROVED."""
        ctx = _base_ctx(
            sector="healthcare",
            ai_risk_level="high",
            has_dpia=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_general_sector_high_risk_no_dpia_approved(self):
        """General sector + high-risk AI + no DPIA → APPROVED (§5.1 not triggered)."""
        ctx = _base_ctx(
            sector="general",
            ai_risk_level="high",
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_healthcare_limited_risk_no_dpia_approved(self):
        """Healthcare sector + limited-risk AI + no DPIA → APPROVED (§5.1 not triggered)."""
        ctx = _base_ctx(
            sector="healthcare",
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

    def test_compliant_cites_naih_and_privacy_act(self):
        """Compliant approval cites NAIH Guidelines and Privacy Act CXII/2011."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "NAIH" in combined or "CXII" in combined

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False


# ===========================================================================
# TestEasternEuropeCrossBorderFilter
# ===========================================================================


class TestEasternEuropeCrossBorderFilter:
    """Layer 4: Eastern Europe + EEA cross-border data transfer framework."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.EasternEuropeCrossBorderFilter().evaluate(ctx, doc)

    # --- Intra-EEA transfers ---

    def test_intra_eea_pl_to_de_approved(self):
        """PL → DE (intra-EEA) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="PL", destination_jurisdiction="DE")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_cz_to_fr_approved(self):
        """CZ → FR (intra-EEA) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="CZ", destination_jurisdiction="FR")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_hu_to_pl_approved(self):
        """HU → PL (intra-EEA) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="HU", destination_jurisdiction="PL")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_pl_to_no_approved(self):
        """PL → NO (EEA non-EU) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="PL", destination_jurisdiction="NO")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_pl_to_is_approved(self):
        """PL → IS (EEA non-EU) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="PL", destination_jurisdiction="IS")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_pl_to_li_approved(self):
        """PL → LI (EEA non-EU) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="PL", destination_jurisdiction="LI")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_intra_eea_not_requires_logging(self):
        """Intra-EEA transfer sets requires_logging=False."""
        ctx = _base_ctx(source_jurisdiction="PL", destination_jurisdiction="SE")
        result = self._eval(ctx)
        assert result.requires_logging is False

    # --- GDPR Art. 46 safeguards ---

    def test_non_eea_with_sccs_approved(self):
        """Non-EEA destination + SCCs/BCRs → APPROVED."""
        ctx = _base_ctx(
            source_jurisdiction="PL",
            destination_jurisdiction="US",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_non_eea_with_sccs_cites_gdpr_46(self):
        """APPROVED with SCCs cites GDPR Article 46."""
        ctx = _base_ctx(
            source_jurisdiction="CZ",
            destination_jurisdiction="IN",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "46" in combined

    def test_non_eea_with_sccs_requires_logging(self):
        """APPROVED with SCCs sets requires_logging=True."""
        ctx = _base_ctx(
            source_jurisdiction="HU",
            destination_jurisdiction="SG",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True

    # --- Non-EEA without safeguards — jurisdiction-specific denials ---

    def test_pl_non_eea_no_safeguards_denied(self):
        """PL source → non-EEA without safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="PL",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_pl_non_eea_no_safeguards_cites_uodo(self):
        """PL denial message references UODO."""
        ctx = _base_ctx(
            source_jurisdiction="PL",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "UODO" in combined or "Poland" in combined

    def test_cz_non_eea_no_safeguards_denied(self):
        """CZ source → non-EEA without safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="CZ",
            destination_jurisdiction="JP",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_cz_non_eea_no_safeguards_cites_uooú(self):
        """CZ denial message references ÚOOÚ."""
        ctx = _base_ctx(
            source_jurisdiction="CZ",
            destination_jurisdiction="JP",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "ÚOOÚ" in combined or "Czech" in combined

    def test_hu_non_eea_no_safeguards_denied(self):
        """HU source → non-EEA without safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="HU",
            destination_jurisdiction="BR",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_hu_non_eea_no_safeguards_cites_naih(self):
        """HU denial message references NAIH."""
        ctx = _base_ctx(
            source_jurisdiction="HU",
            destination_jurisdiction="BR",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "NAIH" in combined or "Hungary" in combined

    def test_unknown_source_non_eea_no_safeguards_denied(self):
        """Unknown source → non-EEA without safeguards → DENIED (default message)."""
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
            source_jurisdiction="PL",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestEasternEuropeAIGovernanceOrchestrator
# ===========================================================================


class TestEasternEuropeAIGovernanceOrchestrator:
    """Four-filter orchestrator produces four results per call."""

    def _orchestrate(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.EasternEuropeAIGovernanceOrchestrator().evaluate(ctx, doc)

    def test_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        results = self._orchestrate(_base_ctx())
        assert len(results) == 4

    def test_result_order_matches_filters(self):
        """Orchestrator results are in filter order: Poland, Czech, Hungary, CrossBorder."""
        results = self._orchestrate(_base_ctx())
        assert results[0].filter_name == "POLAND_AI_FILTER"
        assert results[1].filter_name == "CZECH_REPUBLIC_AI_FILTER"
        assert results[2].filter_name == "HUNGARY_AI_FILTER"
        assert results[3].filter_name == "EASTERN_EUROPE_CROSS_BORDER_FILTER"

    def test_all_approved_compliant_baseline(self):
        """Fully compliant baseline yields four APPROVED results."""
        results = self._orchestrate(_base_ctx())
        for r in results:
            assert r.decision == "APPROVED"

    def test_all_filters_evaluated_on_deny(self):
        """Even when one filter denies, all four filters are evaluated."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        results = self._orchestrate(ctx)
        assert len(results) == 4


# ===========================================================================
# TestEasternEuropeAIGovernanceReport
# ===========================================================================


class TestEasternEuropeAIGovernanceReport:
    """Aggregated governance report aggregation and properties."""

    def _report(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.EasternEuropeAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.EasternEuropeAIGovernanceReport(
            context=ctx,
            document=doc,
            filter_results=results,
        )

    # --- overall_decision ---

    def test_all_approved_overall_approved(self):
        """All APPROVED filters → overall_decision APPROVED."""
        report = self._report(_base_ctx())
        assert report.overall_decision == "APPROVED"

    def test_one_denied_overall_denied(self):
        """One DENIED filter → overall_decision DENIED."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        report = self._report(ctx)
        assert report.overall_decision == "DENIED"

    def test_one_review_overall_requires_review(self):
        """One REQUIRES_HUMAN_REVIEW (no DENIED) → overall_decision REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_biometric_processing=True,
            has_supervisory_approval=False,
        )
        report = self._report(ctx)
        assert report.overall_decision in {"REQUIRES_HUMAN_REVIEW", "DENIED"}
        # Specifically no denial triggers (biometric triggers review only)
        # If only biometric fires, should be REQUIRES_HUMAN_REVIEW
        if not any(r.is_denied for r in report.filter_results):
            assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"

    # --- is_compliant ---

    def test_approved_is_compliant(self):
        """APPROVED overall → is_compliant True."""
        report = self._report(_base_ctx())
        assert report.is_compliant is True

    def test_denied_not_compliant(self):
        """DENIED overall → is_compliant False."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        report = self._report(ctx)
        assert report.is_compliant is False

    def test_requires_review_is_compliant(self):
        """REQUIRES_HUMAN_REVIEW overall → is_compliant True."""
        ctx = _base_ctx(
            is_biometric_processing=True,
            has_supervisory_approval=False,
        )
        report = self._report(ctx)
        # Only check if review (not denied)
        if not any(r.is_denied for r in report.filter_results):
            assert report.is_compliant is True

    # --- compliance_summary ---

    def test_compliance_summary_contains_user_id(self):
        """Compliance summary includes the user_id."""
        ctx = _base_ctx(user_id="test-user-42")
        report = self._report(ctx)
        assert "test-user-42" in report.compliance_summary

    def test_compliance_summary_contains_jurisdiction(self):
        """Compliance summary includes the jurisdiction code."""
        ctx = _base_ctx(jurisdiction="HU")
        report = self._report(ctx)
        assert "HU" in report.compliance_summary

    def test_compliance_summary_contains_overall_decision(self):
        """Compliance summary includes the overall decision."""
        report = self._report(_base_ctx())
        assert "APPROVED" in report.compliance_summary

    def test_compliance_summary_contains_filter_names(self):
        """Compliance summary lists all four filter names."""
        report = self._report(_base_ctx())
        summary = report.compliance_summary
        assert "POLAND_AI_FILTER" in summary
        assert "CZECH_REPUBLIC_AI_FILTER" in summary
        assert "HUNGARY_AI_FILTER" in summary
        assert "EASTERN_EUROPE_CROSS_BORDER_FILTER" in summary

    def test_compliance_summary_denied_scenario(self):
        """Compliance summary for DENIED scenario includes DENIED in text."""
        ctx = _base_ctx(
            is_public_authority=True,
            is_automated_decision=True,
            has_human_oversight=False,
        )
        report = self._report(ctx)
        assert "DENIED" in report.compliance_summary

    # --- FilterResult.is_denied ---

    def test_filter_result_is_denied_true_only_for_denied(self):
        """is_denied is True only when decision is 'DENIED'."""
        result_denied = mod.FilterResult(filter_name="test", decision="DENIED")
        result_review = mod.FilterResult(
            filter_name="test", decision="REQUIRES_HUMAN_REVIEW"
        )
        result_approved = mod.FilterResult(filter_name="test", decision="APPROVED")
        assert result_denied.is_denied is True
        assert result_review.is_denied is False
        assert result_approved.is_denied is False

    # --- Context is frozen ---

    def test_context_is_frozen(self):
        """EasternEuropeAIContext is a frozen dataclass — mutation raises."""
        ctx = _base_ctx()
        with pytest.raises((AttributeError, TypeError)):
            ctx.user_id = "mutated"  # type: ignore[misc]

    # --- Document is frozen ---

    def test_document_is_frozen(self):
        """EasternEuropeAIDocument is a frozen dataclass — mutation raises."""
        doc = _base_doc()
        with pytest.raises((AttributeError, TypeError)):
            doc.document_id = "mutated"  # type: ignore[misc]
