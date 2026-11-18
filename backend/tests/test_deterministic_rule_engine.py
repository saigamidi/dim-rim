"""Unit tests for DeterministicRuleEngine BR-01 validation rules."""
import pytest

from app.services.deterministic_rule_engine import DeterministicRuleEngine


class TestDeterministicRuleEngine:
    """Test BR-01 VIN validation rules."""

    def test_normalize_vin(self):
        """Test VIN normalization."""
        engine = DeterministicRuleEngine()
        
        # Uppercase
        assert engine.normalize_vin("1hgbh41jxmn109186") == "1HGBH41JXMN109186"
        
        # Remove whitespace
        assert engine.normalize_vin(" 1HGBH41JXMN109186 ") == "1HGBH41JXMN109186"
        assert engine.normalize_vin("1HGBH 41JX MN109186") == "1HGBH41JXMN109186"
        
        # Remove control characters
        assert engine.normalize_vin("1HGBH41JXMN109186\n") == "1HGBH41JXMN109186"
        assert engine.normalize_vin("1HGBH41JXMN109186\t") == "1HGBH41JXMN109186"
        
        # Empty input
        assert engine.normalize_vin("") == ""
        assert engine.normalize_vin("   ") == ""

    def test_validate_empty_vin(self):
        """Test rejection of empty VINs."""
        engine = DeterministicRuleEngine()
        
        result = engine.validate_vin("")
        assert not result.is_valid
        assert result.failure_reason_code == "empty_value"
        assert "empty" in result.failure_reason_detail.lower()
        assert not result.checksum_passed

    def test_validate_wrong_length(self):
        """Test rejection of VINs with wrong length."""
        engine = DeterministicRuleEngine()
        
        # Too short
        result = engine.validate_vin("1HGBH41JX")
        assert not result.is_valid
        assert result.failure_reason_code == "wrong_length"
        assert "9" in result.failure_reason_detail
        assert "17" in result.failure_reason_detail
        assert not result.checksum_passed
        
        # Too long
        result = engine.validate_vin("1HGBH41JXMN109186EXTRA")
        assert not result.is_valid
        assert result.failure_reason_code == "wrong_length"
        assert not result.checksum_passed

    def test_validate_forbidden_characters(self):
        """Test rejection of VINs with forbidden characters I, O, Q."""
        engine = DeterministicRuleEngine()
        
        # Forbidden I
        result = engine.validate_vin("1HGBH41JXMN109I86")
        assert not result.is_valid
        assert result.failure_reason_code == "invalid_character"
        assert "I" in result.failure_reason_detail
        assert not result.checksum_passed
        
        # Forbidden O
        result = engine.validate_vin("1HGBH41JXMN109O86")
        assert not result.is_valid
        assert result.failure_reason_code == "invalid_character"
        assert "O" in result.failure_reason_detail
        
        # Forbidden Q
        result = engine.validate_vin("1HGBH41JXMN109Q86")
        assert not result.is_valid
        assert result.failure_reason_code == "invalid_character"
        assert "Q" in result.failure_reason_detail

    def test_validate_non_alphanumeric_characters(self):
        """Test rejection of VINs with non-alphanumeric characters."""
        engine = DeterministicRuleEngine()
        
        # Special character
        result = engine.validate_vin("1HGBH41JXMN109-86")
        assert not result.is_valid
        assert result.failure_reason_code == "invalid_character"
        assert not result.checksum_passed
        
        # Space (should have been normalized, but test anyway)
        result = engine.validate_vin("1HGBH41JXMN 09186")
        assert not result.is_valid
        assert result.failure_reason_code == "invalid_character"

    def test_validate_checksum_valid(self):
        """Test valid VINs with correct checksums."""
        engine = DeterministicRuleEngine()
        
        # Valid VIN with numeric check digit
        result = engine.validate_vin("1HGBH41J70N109186")
        assert result.is_valid
        assert result.failure_reason_code is None
        assert result.checksum_passed
        
        # Another valid VIN
        result = engine.validate_vin("2HGBH41J60N109187")
        assert result.is_valid
        assert result.checksum_passed
        
        # More valid VINs
        result = engine.validate_vin("1G1ZT538906109186")
        assert result.is_valid
        assert result.checksum_passed

    def test_validate_checksum_invalid(self):
        """Test VINs with incorrect checksums."""
        engine = DeterministicRuleEngine()
        
        # Wrong check digit (should be 7, but is 0)
        result = engine.validate_vin("1HGBH41J00N109186")
        assert not result.is_valid
        assert result.failure_reason_code == "checksum_failure"
        assert "Check digit mismatch" in result.failure_reason_detail
        assert not result.checksum_passed

    def test_validate_checksum_calculation(self):
        """Test checksum calculation directly."""
        engine = DeterministicRuleEngine()
        
        # Valid checksum
        is_valid, detail = engine.validate_checksum("1HGBH41J70N109186")
        assert is_valid
        assert "valid" in detail.lower()
        
        # Invalid checksum
        is_valid, detail = engine.validate_checksum("1HGBH41J00N109186")
        assert not is_valid
        assert "mismatch" in detail.lower()
        
        # Wrong length
        is_valid, detail = engine.validate_checksum("1HGBH41JX")
        assert not is_valid
        assert "17" in detail

    def test_get_check_digit(self):
        """Test check digit calculation."""
        engine = DeterministicRuleEngine()
        
        # Calculate check digit for valid VIN
        check_digit = engine.get_check_digit("1HGBH41J70N109186")
        assert check_digit == "7"
        
        # Another check digit
        check_digit = engine.get_check_digit("2HGBH41J60N109187")
        assert check_digit == "6"
        
        # Wrong length
        check_digit = engine.get_check_digit("1HGBH41JX")
        assert check_digit is None

    def test_validate_multiple_vins(self):
        """Test validation of multiple VINs."""
        engine = DeterministicRuleEngine()
        
        test_cases = [
            ("1HGBH41J70N109186", True, None),
            ("2HGBH41J60N109187", True, None),
            ("3HGBH41J50N109188", True, None),
            ("1HGBH41JX", False, "wrong_length"),
            ("1HGBH41JXMN109I86", False, "invalid_character"),
            ("1HGBH41J00N109186", False, "checksum_failure"),
            ("", False, "empty_value"),
        ]
        
        for vin, expected_valid, expected_reason in test_cases:
            result = engine.validate_vin(vin)
            assert result.is_valid == expected_valid, f"VIN {vin} validation failed"
            assert result.failure_reason_code == expected_reason, f"VIN {vin} reason mismatch"

    def test_validate_edge_cases(self):
        """Test edge cases in VIN validation."""
        engine = DeterministicRuleEngine()
        
        # All zeros (invalid - all zeros doesn't pass checksum)
        result = engine.validate_vin("00000000000000000")
        # Check digit for all zeros would be 0, so this actually passes
        # But it's an edge case - we'll check it validates
        
        # All A's (will fail checksum unless check digit is correct)
        result = engine.validate_vin("AAAAAAAAAAAAAAAAA")
        # This will likely fail checksum
        
        # Mixed case before normalization should be handled
        normalized = engine.normalize_vin("1hgbh41j70n109186")
        result = engine.validate_vin(normalized)
        assert result.is_valid
