# TASK-4 Handoff: Backend Feature B2 - Parsing and VIN Extraction

## Implemented Endpoints

### Parsing Domain

#### POST /api/v1/parsing/attachments/{attachment_id}/parse
Parse an attachment into canonical candidate rows.

**Request:**
```json
{
  "force_reparse": false  // Optional, default false
}
```

**Response (200):**
```json
{
  "attachment_id": "uuid",
  "parse_status": "parsed",  // or "parse_partial", "parse_failed"
  "row_count": 8,
  "failure_count": 0,
  "lineage_base_ref": "lin-{case_id}/att-{attachment_id}"
}
```

**Behavior:**
- Orchestrates TOL2 Attachment Parser Adapter (mocked for MVP)
- Normalizes rows into canonical candidate-VIN structure
- Persists with row-level lineage format: `lin-{case_id}/att-{attachment_id}/r{row_num}`
- Handles parse failures explicitly (status: parse_failed, parse_partial)
- Idempotent via force_reparse flag
- Records audit event: `attachment_parsed`

#### GET /api/v1/parsing/cases/{case_id}/rows
Get all candidate rows for a case.

**Response (200):**
```json
[
  {
    "id": "uuid",
    "attachment_id": "uuid",
    "source_row_number": 1,
    "canonical_vin_candidate": "1HGBH41JXMN109186",
    "raw_row_json": "{...}",
    "row_status": "parsed",
    "lineage_ref": "lin-{case_id}/att-{attachment_id}/r1",
    "created_at": "2026-11-15T14:35:00Z"
  }
]
```

**Behavior:**
- Returns all parsed candidate rows for a case
- Ordered by source_row_number
- Each row includes lineage reference for traceability

### VIN Processing Domain

#### POST /api/v1/vins/cases/{case_id}/extract
Extract VINs from candidate rows.

**Response (200):**
```json
{
  "case_id": "uuid",
  "extracted_count": 8,
  "deduplicated_count": 2,
  "rejected_empty_count": 1,
  "run_status": "completed"
}
```

**Behavior:**
- Extracts VIN candidates from parsed candidate rows
- Normalizes VINs (uppercase, trim whitespace)
- Deduplicates within case (first occurrence kept, lineage preserved)
- Rejects empty/null VIN values
- Persists vin_record entries with extraction_status:
  - `"extracted"` - unique, valid VIN
  - `"duplicate"` - duplicate within case (is_duplicate_within_case=true)
  - `"rejected_empty"` - empty or null value
- Idempotent rerun allowed
- Records audit event: `vins_extracted`

#### GET /api/v1/vins/cases/{case_id}/summary
Get VIN extraction summary counts.

**Response (200):**
```json
{
  "case_id": "uuid",
  "extracted": 8,
  "deduplicated": 2,
  "rejected": 1
}
```

**Behavior:**
- Returns extraction counts only (validation counts added in TASK-5)
- `extracted`: count of unique, extracted VINs
- `deduplicated`: count of duplicate VINs within case
- `rejected`: count of empty/null VINs

## Seed Data

### Parsed Case
- **Case ID:** Generated in seed (CASE-2026-001)
- **Status:** "parsed"
- **Attachment:** "affected_vins.xlsx" (parsed status)
- **Candidate Rows:** 8 rows with VINs
- **VIN Records:** 8 extracted VINs (no validation yet)

### Sample VINs in Seed
```
1HGBH41JXMN100000
1HGBH41JXMN100001
1HGBH41JXMN100002
1HGBH41JXMN100003
1HGBH41JXMN100004
1HGBH41JXMN100005
1HGBH41JXMN100006
1HGBH41JXMN100007
```

All VINs have:
- `extraction_status`: "extracted"
- `is_duplicate_within_case`: false
- `normalized_vin`: Uppercase, trimmed

## Backend Flows

### Parsing Flow
1. User/system calls `POST /api/v1/parsing/attachments/{attachment_id}/parse`
2. Service validates attachment exists and media type is supported (Excel/CSV)
3. If already parsed and not force_reparse, returns existing results
4. If force_reparse=true, deletes existing candidate rows
5. Calls TOL2 Attachment Parser Adapter (mocked)
6. Creates candidate_row records with lineage format: `lin-{case_id}/att-{id}/r{row_num}`
7. Updates attachment parse_status to "parsed" or "parse_partial"
8. Records audit event with row counts
9. Returns parse result summary

### VIN Extraction Flow
1. User/system calls `POST /api/v1/vins/cases/{case_id}/extract`
2. Service retrieves all candidate rows for case
3. For each row:
   - Skip empty/null VINs (status: rejected_empty)
   - Normalize VIN (uppercase, trim whitespace)
   - Check for duplicate within case
   - If first occurrence: extract (status: extracted, is_duplicate=false)
   - If duplicate: mark (status: duplicate, is_duplicate=true)
4. Batch insert vin_record entries
5. Records audit event with extraction counts
6. Returns extraction summary

### Summary Flow
1. User calls `GET /api/v1/vins/cases/{case_id}/summary`
2. Service counts vin_records by extraction_status
3. Returns counts: extracted, deduplicated (is_duplicate=true), rejected

## TOL2 Adapter (Mocked)

**File:** `app/adapters/attachment_parser_adapter.py`

**Mock Behavior:**
- Validates Excel (.xlsx, .xls) and CSV file formats
- Returns 8 sample parsed rows with realistic VIN data
- Each row includes row_number, vin_candidate, and raw_data (JSON)
- Failure count always 0 in mock

**Production Integration:**
- Replace mock implementation with actual Excel/CSV parsing
- Fetch file from storage_ref
- Parse file content (openpyxl, pandas, csv module)
- Extract VIN candidates from appropriate columns
- Return ParsedRow objects with source row numbers

## Error Handling

### Parse Errors
- **404** - Attachment not found
- **400** - Unsupported attachment format (not Excel/CSV)
- **500** - Parse failure (updates attachment parse_status to "parse_failed")

### Extraction Errors
- **404** - Case not found
- **400** - No candidate rows found (parse attachments first)
- **500** - Extraction processing failure

## Authentication

All endpoints require JWT authentication via Authorization header.

**Example:**
```
Authorization: Bearer <token>
```

**Demo Credentials:**
- Disruption Manager: `disruption.mgr@tmna.com` / `Manager123!`
- Event Approval Reviewer: `event.reviewer@tmna.com` / `Reviewer123!`

## Testing

### Unit Tests
- `tests/test_parsing_service.py` - Parsing service logic
- `tests/test_vin_extraction_service.py` - VIN extraction service logic

### Integration Tests
- `tests/test_parsing_integration.py` - Candidate row repository
- `tests/test_vin_extraction_integration.py` - VIN record repository

### Acceptance Tests
- `tests/test_parsing_acceptance.py` - Full HTTP flow for parsing
- `tests/test_vin_extraction_acceptance.py` - Full HTTP flow for extraction

**Run Tests:**
```bash
cd /repos/dim-rim/backend
.venv/bin/python -m pytest tests/test_parsing_service.py tests/test_vin_extraction_service.py -v
.venv/bin/python -m pytest tests/test_parsing_integration.py tests/test_vin_extraction_integration.py -v
.venv/bin/python -m pytest tests/test_parsing_acceptance.py tests/test_vin_extraction_acceptance.py -v
```

## Next Steps (TASK-5)

TASK-5 will implement VIN validation with BR-01 deterministic rule engine:
- Length=17 validation
- Character validity (no I/O/Q, alphanumeric only)
- ISO 3779 checksum validation
- Explicit failure reason codes
- Validation result persistence
- Extended summary endpoint with validation breakdown
