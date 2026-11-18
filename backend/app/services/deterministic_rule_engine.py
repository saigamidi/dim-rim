"""Deterministic Rule Engine for BR-01 VIN validation rules."""
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of VIN validation."""

    def __init__(
        self,
        is_valid: bool,
        failure_reason_code: str | None = None,
        failure_reason_detail: str | None = None,
        checksum_passed: bool = False,
    ):
        self.is_valid = is_valid
        self.failure_reason_code = failure_reason_code
        self.failure_reason_detail = failure_reason_detail
        self.checksum_passed = checksum_passed


class DeterministicRuleEngine:
    """
    Deterministic Rule Engine implementing BR-01 VIN Validation Rules.
    
    Rules:
    1. Normalize to uppercase and remove whitespace/control characters
    2. Reject empty values
    3. Enforce exact length 17
    4. Reject characters I, O, Q and any non-alphanumeric character
    5. Compute ISO 3779 check digit (position 9)
    6. Persist one validation outcome per VIN record
    """

    # Transliteration map for check digit calculation (ISO 3779)
    TRANSLITERATION = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
    }

    # Position weights for check digit calculation
    WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

    # Invalid characters that are explicitly forbidden
    FORBIDDEN_CHARS = {'I', 'O', 'Q'}

    @staticmethod
    def normalize_vin(vin: str) -> str:
        """
        Normalize VIN: uppercase and remove whitespace/control characters.
        
        Args:
            vin: Raw VIN string
            
        Returns:
            Normalized VIN string
        """
        if not vin:
            return ""
        
        # Remove whitespace and control characters, convert to uppercase
        normalized = ''.join(c for c in vin if c.isprintable() and not c.isspace()).upper()
        return normalized

    @classmethod
    def validate_vin(cls, normalized_vin: str) -> ValidationResult:
        """
        Validate a normalized VIN against BR-01 rules.
        
        Args:
            normalized_vin: Normalized VIN string (uppercase, no whitespace)
            
        Returns:
            ValidationResult with is_valid flag and failure details
        """
        # Rule 2: Reject empty values
        if not normalized_vin:
            return ValidationResult(
                is_valid=False,
                failure_reason_code="empty_value",
                failure_reason_detail="VIN is empty or contains only whitespace",
                checksum_passed=False,
            )

        # Rule 3: Enforce exact length 17
        if len(normalized_vin) != 17:
            return ValidationResult(
                is_valid=False,
                failure_reason_code="wrong_length",
                failure_reason_detail=f"VIN length is {len(normalized_vin)}, expected 17",
                checksum_passed=False,
            )

        # Rule 4: Reject I, O, Q and any non-alphanumeric character
        for i, char in enumerate(normalized_vin):
            if char in cls.FORBIDDEN_CHARS:
                return ValidationResult(
                    is_valid=False,
                    failure_reason_code="invalid_character",
                    failure_reason_detail=f"VIN contains forbidden character '{char}' at position {i + 1}",
                    checksum_passed=False,
                )
            
            if not char.isalnum():
                return ValidationResult(
                    is_valid=False,
                    failure_reason_code="invalid_character",
                    failure_reason_detail=f"VIN contains non-alphanumeric character '{char}' at position {i + 1}",
                    checksum_passed=False,
                )

        # Rule 5: Compute ISO 3779 check digit (position 9, index 8)
        checksum_passed, checksum_detail = cls.validate_checksum(normalized_vin)
        
        if not checksum_passed:
            return ValidationResult(
                is_valid=False,
                failure_reason_code="checksum_failure",
                failure_reason_detail=checksum_detail,
                checksum_passed=False,
            )

        # All checks passed
        return ValidationResult(
            is_valid=True,
            failure_reason_code=None,
            failure_reason_detail=None,
            checksum_passed=True,
        )

    @classmethod
    def validate_checksum(cls, vin: str) -> tuple[bool, str]:
        """
        Validate ISO 3779 check digit at position 9 (index 8).
        
        Args:
            vin: Normalized 17-character VIN
            
        Returns:
            Tuple of (is_valid, detail_message)
        """
        if len(vin) != 17:
            return False, "VIN must be 17 characters for checksum validation"

        try:
            # Calculate weighted sum
            weighted_sum = 0
            for i, char in enumerate(vin):
                if i == 8:  # Skip check digit position
                    continue
                
                if char not in cls.TRANSLITERATION:
                    return False, f"Character '{char}' at position {i + 1} cannot be transliterated"
                
                value = cls.TRANSLITERATION[char]
                weight = cls.WEIGHTS[i]
                weighted_sum += value * weight

            # Compute check digit: remainder of sum divided by 11
            check_digit = weighted_sum % 11
            
            # Check digit 10 is represented as 'X'
            expected_check_char = 'X' if check_digit == 10 else str(check_digit)
            actual_check_char = vin[8]

            if actual_check_char != expected_check_char:
                return False, (
                    f"Check digit mismatch: expected '{expected_check_char}', "
                    f"found '{actual_check_char}' at position 9"
                )

            return True, "Checksum valid"

        except Exception as e:
            logger.error(f"Checksum validation error for VIN {vin}: {str(e)}")
            return False, f"Checksum calculation error: {str(e)}"

    @classmethod
    def get_check_digit(cls, vin: str) -> str | None:
        """
        Calculate what the check digit should be for a VIN.
        
        Args:
            vin: 17-character VIN
            
        Returns:
            Expected check digit character, or None if calculation fails
        """
        if len(vin) != 17:
            return None

        try:
            weighted_sum = 0
            for i, char in enumerate(vin):
                if i == 8:  # Skip check digit position
                    continue
                
                if char not in cls.TRANSLITERATION:
                    return None
                
                value = cls.TRANSLITERATION[char]
                weight = cls.WEIGHTS[i]
                weighted_sum += value * weight

            check_digit = weighted_sum % 11
            return 'X' if check_digit == 10 else str(check_digit)

        except Exception:
            return None
