# TASK-5 Handoff: Backend Feature B3 - VIN Validation

## Endpoints

### POST /api/v1/vins/cases/{case_id}/validate
Run BR-01 deterministic validation on extracted VINs.

**Authentication:** Required (JWT Bearer token)

**Path Parameters:**
- `case_id` (string, UUID): Intake case ID

**Request Body:** None

**Response 200 OK:**
```json
{
  "case_id": "uuid",
  "valid_count": 8,
  "invalid_count": 3,
  "failure_breakdown": {
    "wrong_length": 1,
    "invalid_character": 1,
    "checksum_failure": 1,
    "empty_value": 0
  },
  "validated_at_utc": "2026-11-15T14:40:00Z"
}
```

**Error Responses:**
- 400: Extraction required first (no extracted VINs found)
- 401: Authentication required
- 404: Case not found
- 500: Internal server error

**Behavior:**
- Validates length=17, checks for forbidden characters (I, O, Q), validates ISO 3779 checksum
- Persists validation results with explicit failure reason codes
- Idempotent: can be rerun (replaces previous validation results)
- Records audit event with validation counts

---

### GET /api/v1/vins/cases/{case_id}/summary
Get full VIN summary including extraction and validation counts.

**Authentication:** Required (JWT Bearer token)

**Path Parameters:**
- `case_id` (string, UUID): Intake case ID

**Response 200 OK:**
```json
{
  "case_id": "uuid",
  "extracted": 11,
  "deduplicated": 0,
  "rejected": 1,
  "valid": 8,
  "invalid": 3,
  "failure_reason_breakdown": {
    "wrong_length": 1,
    "invalid_character": 1,
    "checksum_failure": 1,
    "empty_value": 0
  }
}
```

**Note:** This endpoint was extended from TASK-4 to include validation counts.

**Error Responses:**
- 401: Authentication required
- 404: Case not found
- 500: Internal server error

---

## BR-01 VIN Validation Rules

The Deterministic Rule Engine enforces these rules in order:

1. **Normalize:** Uppercase and remove whitespace/control characters
2. **Reject empty values:** VINs that are null, empty, or only whitespace
3. **Enforce length:** Exactly 17 characters required
4. **Check characters:** 
   - No forbidden characters: I, O, Q
   - Only alphanumeric characters allowed
5. **Validate checksum:** ISO 3779 check digit at position 9
   - Transliteration map converts letters to numbers
   - Weighted sum calculation with position weights
   - Modulo 11 produces check digit (0-9 or X for 10)

---

## Failure Reason Codes

- `wrong_length`: VIN is not exactly 17 characters
- `invalid_character`: VIN contains I, O, Q, or non-alphanumeric character
- `checksum_failure`: ISO 3779 check digit does not match calculated value
- `empty_value`: VIN is empty, null, or only whitespace

---

## Seed Data

### Case CASE-2026-001 VIN Records

12 VIN records total (11 extracted + 1 rejected during extraction):

**Valid VINs (8):**
1. `1HGBH41J70N109186` - Valid checksum (check digit 7)
2. `2HGBH41J60N109187` - Valid checksum (check digit 6)
3. `3HGBH41J50N109188` - Valid checksum (check digit 5)
4. `4HGBH41J40N109189` - Valid checksum (check digit 4)
5. `5HGBH41J70N10918A` - Valid checksum (check digit 7)
6. `1G1ZT538906109186` - Valid checksum (check digit 9)
7. `2G1WH52K809109187` - Valid checksum (check digit 8)
8. `3GNDA13D20S109188` - Valid checksum (check digit 2)

**Invalid VINs (3 validated as invalid):**
9. `1HGBH41JX` - Wrong length (9 chars) - `failure_reason_code: "wrong_length"`
10. `1HGBH41JXMN109I86` - Invalid character (I) - `failure_reason_code: "invalid_character"`
11. `1HGBH41J00N109186` - Checksum failure (check digit should be 7, but is 0) - `failure_reason_code: "checksum_failure"`

**Rejected During Extraction (1):**
12. Empty VIN - `extraction_status: "rejected_empty"` (no validation result created)

---

## Backend Flows

### Validation Flow (POST /api/v1/vins/cases/{case_id}/validate)

1. Verify case exists (404 if not found)
2. Retrieve extracted VIN records (status = "extracted")
3. If no extracted VINs, return 400 error
4. Delete existing validation results for idempotent rerun
5. For each extracted VIN:
   - Normalize VIN (uppercase, trim)
   - Run BR-01 validation via DeterministicRuleEngine
   - Determine status (valid/invalid)
   - Track failure reason if invalid
   - Create VinValidationResult record
6. Batch insert validation results
7. Record audit event with counts
8. Commit transaction
9. Return validation summary

### Summary Flow (GET /api/v1/vins/cases/{case_id}/summary)

1. Verify case exists (404 if not found)
2. Count extraction statuses:
   - `extracted`: unique VINs kept
   - `duplicate`: duplicates within case
   - `rejected_empty`: empty/null values
3. Count validation statuses:
   - `valid`: passed all BR-01 checks
   - `invalid`: failed at least one check
4. Count failure reasons:
   - `wrong_length`, `invalid_character`, `checksum_failure`, `empty_value`
5. Return combined extraction + validation summary

---

## Database Schema

### vin_validation_result Table

- `id` (CHAR(36) PK): Validation result ID
- `vin_record_id` (CHAR(36) FK UNIQUE): Reference to vin_record
- `validation_status` (VARCHAR(32)): "valid" or "invalid"
- `failure_reason_code` (VARCHAR(64)): Failure reason code or NULL
- `failure_reason_detail` (VARCHAR(255)): Human-readable failure description
- `checksum_passed` (BOOLEAN): Whether ISO 3779 checksum passed
- `validated_at_utc` (TIMESTAMP): When validation was performed
- `created_at` (TIMESTAMP): Record creation timestamp

**Indexes:**
- Primary key on `id`
- Unique constraint on `vin_record_id`
- Index on `vin_record_id`, `validation_status`, `failure_reason_code`

---

## Services

### DeterministicRuleEngine
Service-internal utility implementing BR-01 validation rules.

**Methods:**
- `normalize_vin(vin: str) -> str`: Normalize VIN to uppercase, remove whitespace
- `validate_vin(normalized_vin: str) -> ValidationResult`: Run full BR-01 validation
- `validate_checksum(vin: str) -> tuple[bool, str]`: Validate ISO 3779 check digit
- `get_check_digit(vin: str) -> str | None`: Calculate expected check digit

### VinProcessingService
Extended with validation methods.

**New Methods:**
- `validate_vins(case_id: str) -> VinValidationRunOut`: Run validation on extracted VINs
- `get_validation_summary(case_id: str) -> VinValidationSummaryOut`: Get full summary with validation

---

## Adapters

### VinValidationAdapter (TOL3)
Adapter wrapping DeterministicRuleEngine for validation services.

**Purpose:** Provides adapter interface for VIN validation while BR-01 logic is implemented in the rule engine. Preserves seam for potential future external validation services.

**Methods:**
- `validate_vin(normalized_vin: str) -> ValidationResult`: Validate via BR-01 rules
- `normalize_vin(raw_vin: str) -> str`: Normalize VIN string
- `get_check_digit(vin: str) -> str | None`: Calculate check digit

---

## Test Coverage

### Unit Tests
- `test_deterministic_rule_engine.py`: BR-01 rule validation logic
- `test_vin_validation_service.py`: VinProcessingService validation methods

### Integration Tests
- `test_vin_validation_integration.py`: Repository operations and database persistence

### Acceptance Tests
- `test_vin_validation_acceptance.py`: Full validation endpoint flows, audit events, idempotent rerun

---

## Demo Usage

### Login
```bash
POST /api/v1/auth/login
{
  "email": "disruption.mgr@tmna.com",
  "password": "Manager123!"
}
```

### Validate VINs
```bash
POST /api/v1/vins/cases/{case_id}/validate
Authorization: Bearer {token}
```

### Get Full Summary
```bash
GET /api/v1/vins/cases/{case_id}/summary
Authorization: Bearer {token}
```

Expected summary for seeded CASE-2026-001:
```json
{
  "case_id": "...",
  "extracted": 11,
  "deduplicated": 0,
  "rejected": 1,
  "valid": 8,
  "invalid": 3,
  "failure_reason_breakdown": {
    "wrong_length": 1,
    "invalid_character": 1,
    "checksum_failure": 1,
    "empty_value": 0
  }
}
```

---

## Audit Events

Validation creates audit event:
```json
{
  "action_type": "vins_validated",
  "entity_type": "intake_case",
  "entity_id": "{case_id}",
  "outcome": "success",
  "metadata": {
    "valid_count": 8,
    "invalid_count": 3,
    "failure_breakdown": {
      "wrong_length": 1,
      "invalid_character": 1,
      "checksum_failure": 1,
      "empty_value": 0
    }
  }
}
```
