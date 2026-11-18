"""TOL3 VIN Validation Adapter for BR-01 utility.

This adapter provides the interface contract for VIN validation services.
The DeterministicRuleEngine implements BR-01 rules directly as a
service-internal utility. This adapter is preserved as a seam for
potential future external validation services.
"""
import logging
from typing import Protocol

from app.services.deterministic_rule_engine import DeterministicRuleEngine, ValidationResult

logger = logging.getLogger(__name__)


class VinValidationAdapterProtocol(Protocol):
    """Protocol for VIN validation adapters."""

    def validate_vin(self, normalized_vin: str) -> ValidationResult:
        """
        Validate a normalized VIN.
        
        Args:
            normalized_vin: Normalized VIN string (uppercase, no whitespace)
            
        Returns:
            ValidationResult with is_valid flag and failure details
        """
        ...


class VinValidationAdapter:
    """
    TOL3 VIN Validation Adapter.
    
    Wraps the DeterministicRuleEngine to provide the adapter interface.
    This allows the service layer to interact with validation through
    a consistent adapter pattern, while the actual BR-01 logic is
    implemented in the rule engine.
    """

    def __init__(self):
        self.rule_engine = DeterministicRuleEngine()

    def validate_vin(self, normalized_vin: str) -> ValidationResult:
        """
        Validate a normalized VIN using BR-01 rules.
        
        Args:
            normalized_vin: Normalized VIN string (uppercase, no whitespace)
            
        Returns:
            ValidationResult with is_valid flag and failure details
        """
        logger.debug(f"TOL3 VIN Validation: validating VIN {normalized_vin}")
        
        # Delegate to deterministic rule engine
        result: ValidationResult = self.rule_engine.validate_vin(normalized_vin)
        
        logger.debug(
            f"TOL3 VIN Validation: VIN {normalized_vin} -> "
            f"valid={result.is_valid}, reason={result.failure_reason_code}"
        )
        
        return result

    def normalize_vin(self, raw_vin: str) -> str:
        """
        Normalize a raw VIN string.
        
        Args:
            raw_vin: Raw VIN string
            
        Returns:
            Normalized VIN string (uppercase, no whitespace)
        """
        normalized: str = self.rule_engine.normalize_vin(raw_vin)
        return normalized

    def get_check_digit(self, vin: str) -> str | None:
        """
        Calculate what the check digit should be for a VIN.
        
        Args:
            vin: 17-character VIN
            
        Returns:
            Expected check digit character, or None if calculation fails
        """
        check_digit: str | None = self.rule_engine.get_check_digit(vin)
        return check_digit
