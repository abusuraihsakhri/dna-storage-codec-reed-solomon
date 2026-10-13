"""
Security-focused tests for dna-storage-codec-reed-solomon.
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set secure audit key for tests
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-2026-secure")

import pytest
from agents.base import PHIGuard, AuditTrail, SecurityException


class TestPHIGuard:
    """Test PHI outbound guard functionality."""

    def test_mrn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_ssn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_email_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@example.com")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 and SSN 123-45-6789")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN" not in result
        assert "123-45-6789" not in result


class TestAuditTrail:
    """Test HMAC-SHA256 audit trail functionality."""

    def test_audit_trail_requires_secret_key(self):
        # Remove env var if present
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            with pytest.raises(SecurityException):
                AuditTrail(secret_key=None)
        finally:
            if original:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_audit_trail_rejects_short_key(self):
        with pytest.raises(SecurityException):
            AuditTrail(secret_key="short")

    def test_audit_trail_accepts_valid_key(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        assert len(trail.logs) == 0

    def test_audit_trail_logs_entry(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        entry = trail.log("test_actor", "test_tier", "TEST_EVENT", {"key": "value"})
        assert entry["audit_id"].startswith("AUDIT-")
        assert entry["current_hash"] != ""
        assert len(trail.logs) == 1

    def test_audit_trail_chain_integrity(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        trail.log("actor1", "tier1", "EVENT1", {"data": 1})
        trail.log("actor2", "tier2", "EVENT2", {"data": 2})
        assert trail.verify_integrity() is True

    def test_audit_trail_detects_tampering(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        trail.log("actor1", "tier1", "EVENT1", {"data": 1})
        trail.log("actor2", "tier2", "EVENT2", {"data": 2})
        # Tamper with the first entry
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False

    def test_audit_trail_blocks_phi_in_details(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        with pytest.raises(SecurityException):
            trail.log("actor", "tier", "EVENT", {"patient": "MRN-12345678"})

    def test_audit_detects_last_entry_signature_forgery(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        trail.log("actor", "tier", "EVENT", {"data": 1})
        trail.logs[-1]["current_hash"] = "0" * 64
        assert trail.verify_integrity() is False

    def test_audit_detects_metadata_change(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        trail.log("actor", "tier", "EVENT", {"data": 1})
        trail.logs[0]["event_type"] = "FORGED_EVENT"
        assert trail.verify_integrity() is False

    def test_get_trail_is_defensive_copy(self):
        trail = AuditTrail(secret_key="valid-secret-key-1234567890")
        trail.log("actor", "tier", "EVENT", {"data": 1})
        trail.get_trail()[0]["actor"] = "forged"
        assert trail.verify_integrity() is True
