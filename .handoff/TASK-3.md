# TASK-3 Handoff: Backend Feature B1 - Intake and Classification

## Endpoints Implemented

### Intake Domain

#### POST /api/v1/intake/submissions
**Purpose**: Register disruption inbox submission (FR-001)

**Request**:
```json
{
  "source_email_id": "string (unique email ID)",
  "source_address": "string (max 320 chars)",
  "received_at_utc": "datetime (ISO 8601)",
  "subject": "string (max 512 chars)",
  "has_attachments": "boolean"
}
```

**Response** (201 Created):
```json
{
  "id": "string (UUID)",
  "case_key": "string (CASE-YYYYMMDD-{id[:8]})",
  "source_email_id": "string",
  "source_address": "string",
  "received_at_utc": "datetime",
  "subject": "string",
  "intake_status": "string (received|parsed|classification_pending_review|classification_decided)",
  "correlation_id": "string (UUID)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "attachments": [
    {
      "id": "string (UUID)",
      "intake_case_id": "string (UUID)",
      "filename": "string",
      "media_type": "string",
      "byte_size": "integer",
      "storage_ref": "string",
      "parse_status": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

**Workflow Triggered**:
- AGN1 Intake & Triage orchestration
- Fetch email from TOL1 Inbox Connector (mocked)
- Classify as disruption candidate vs. non-case
- Create intake_case with "received" status
- Create placeholder attachments if present
- Record audit event via TOL7 Audit Writer

#### GET /api/v1/intake/cases/{case_id}
**Purpose**: Read intake case summary

**Response** (200 OK): Same shape as POST /api/v1/intake/submissions response

---

### Classification Domain

#### POST /api/v1/classification/cases/{case_id}/recommendation
**Purpose**: Generate AI-assisted classification recommendation (FR-003)

**Response** (200 OK):
```json
{
  "id": "string (UUID)",
  "intake_case_id": "string (UUID)",
  "suggested_disruption_type": "string",
  "suggested_disruption_subtype": "string|null",
  "suggested_event_ref": "string|null",
  "confidence_score": "float (0.0-1.0)",
  "created_at": "datetime"
}
```

**Workflow Triggered**:
- AGN1 generates AI-assisted recommendation (mocked for MVP)
- Creates pending classification_decision record
- Updates intake_case status to "classification_pending_review"
- Records audit event

#### POST /api/v1/classification/cases/{case_id}/decision
**Purpose**: Record reviewer classification decision with BR-06 AMBER gate (FR-003)

**Request**:
```json
{
  "reviewer_decision": "string (confirm|revise|reject)",
  "final_disruption_type": "string|null (required for revise)",
  "final_disruption_subtype": "string|null (optional)",
  "final_event_ref": "string|null (optional)",
  "reviewer_comment": "string|null"
}
```

**Response** (200 OK):
```json
{
  "id": "string (UUID)",
  "intake_case_id": "string (UUID)",
  "suggested_disruption_type": "string",
  "suggested_disruption_subtype": "string|null",
  "suggested_event_ref": "string|null",
  "confidence_score": "float",
  "reviewer_decision": "string (confirm|revise|reject)",
  "final_disruption_type": "string|null",
  "final_disruption_subtype": "string|null",
  "final_event_ref": "string|null",
  "reviewer_comment": "string|null",
  "decided_by_user_id": "string",
  "decided_at_utc": "datetime",
  "created_at": "datetime"
}
```

**Authorization**: Requires "Event Approval Reviewer" role (403 if unauthorized)

**Workflow Triggered**:
- BR-06 AMBER gate: Role check (Event Approval Reviewer required)
- Update classification_decision with reviewer action
- confirm: Accept AGN1 recommendation
- revise: Override with reviewer values (requires final_disruption_type)
- reject: Clear binding, preserve history
- Update intake_case status to "classification_decided"
- Record audit event

---

### Audit Domain

#### GET /api/v1/audit/cases/{case_id}/events
**Purpose**: List case audit events

**Response** (200 OK) - Returns list:
```json
[
  {
    "id": "string (UUID)",
    "intake_case_id": "string (UUID)",
    "correlation_id": "string (UUID)",
    "actor_type": "string (user|system)",
    "actor_id": "string",
    "action_type": "string",
    "entity_type": "string",
    "entity_id": "string (UUID)",
    "outcome": "string",
    "metadata_json": "string (JSON)",
    "occurred_at_utc": "datetime",
    "created_at": "datetime"
  }
]
```

Note: Returns bare list, not `{items, total}` wrapper.

---

## Seed Data

### Demo Users

1. **Disruption Manager**
   - Email: `disruption.mgr@tmna.com`
   - Password: `Manager123!`
   - Role: `Disruption Manager`

2. **Event Approval Reviewer**
   - Email: `event.reviewer@tmna.com`
   - Password: `Reviewer123!`
   - Role: `Event Approval Reviewer`

3. **VIP Communication Reviewer**
   - Email: `vip.comms@tmna.com`
   - Password: `Comms123!`
   - Role: `VIP Communication Reviewer`

### Sample Intake Cases

1. **CASE-2026-001**
   - Status: `parsed`
   - Subject: "Part Shortage - VIN List Attached"
   - Has 1 attachment (affected_vins.xlsx)
   - Has 8 candidate rows
   - Has 8 VIN records (extracted)
   - Has 2 audit events

2. **CASE-2026-002**
   - Status: `classification_pending_review`
   - Subject: "Logistics Delay - Production Impact"
   - Ready for classification workflow
   - Has 1 audit event

### Audit Events (5 total)

- 2 events for CASE-2026-001: intake_registered, parsing_completed
- 1 event for CASE-2026-002: intake_registered
- Additional events created dynamically when using API endpoints

---

## Backend Flows

### Flow 1: Submit Inbox Email → Create Intake Case
**User Action**: POST /api/v1/intake/submissions

**Backend Steps**:
1. Fetch email from TOL1 Inbox Connector (mocked)
2. Classify as disruption candidate vs. non-case
3. If non-case: Record audit event, return error
4. If candidate: Create intake_case with "received" status
5. Create placeholder email_attachment if has_attachments=true
6. Record audit event via TOL7 Audit Writer
7. Return IntakeCaseOut

**Database Changes**:
- INSERT intake_case
- INSERT email_attachment (if attachments present)
- INSERT audit_event

---

### Flow 2: Generate Classification Recommendation
**User Action**: POST /api/v1/classification/cases/{case_id}/recommendation

**Backend Steps**:
1. Verify intake_case exists
2. AGN1 generates AI-assisted recommendation (mocked: infers from subject)
3. Create classification_decision with reviewer_decision="pending"
4. Update intake_case.intake_status to "classification_pending_review"
5. Record audit event
6. Return ClassificationRecommendationOut

**Database Changes**:
- INSERT classification_decision
- UPDATE intake_case (intake_status)
- INSERT audit_event

---

### Flow 3: Record Classification Decision (BR-06 AMBER Gate)
**User Action**: POST /api/v1/classification/cases/{case_id}/decision

**Backend Steps**:
1. Check user role = "Event Approval Reviewer" (403 if not)
2. Verify intake_case and pending classification_decision exist
3. Validate reviewer_decision (confirm|revise|reject)
4. If revise: Validate final_disruption_type provided
5. Update classification_decision with reviewer action:
   - confirm: Copy suggested_* to final_*
   - revise: Use provided final_* values
   - reject: Clear final_* (null)
6. Update intake_case.intake_status to "classification_decided"
7. Record audit event
8. Return ClassificationDecisionOut

**Database Changes**:
- UPDATE classification_decision
- UPDATE intake_case (intake_status)
- INSERT audit_event

---

### Flow 4: List Case Audit Events
**User Action**: GET /api/v1/audit/cases/{case_id}/events

**Backend Steps**:
1. Query audit_event WHERE intake_case_id = {case_id}
2. Order by occurred_at_utc ASC
3. Return list of AuditEventOut

**Database Changes**: None (read-only)

---

## State Progression

**Intake Case Status Flow**:
```
received → parsed → classification_pending_review → classification_decided
```

- `received`: Initial status after submission
- `parsed`: After attachment parsing (TASK-4)
- `classification_pending_review`: After AGN1 recommendation generated
- `classification_decided`: After reviewer confirms/revises/rejects

---

## Authentication & Authorization

- All endpoints require JWT Bearer token (Authorization: Bearer {token})
- Token obtained via POST /api/v1/auth/login (from TASK-2)
- Classification decision endpoint requires "Event Approval Reviewer" role (BR-06 AMBER gate)

---

## Adapters

### TOL1 Inbox Connector Adapter (Mocked)
**Location**: `app/adapters/inbox_connector_adapter.py`

**Purpose**: Fetch emails from inbox and classify disruption candidates

**Methods**:
- `fetch_email(source_email_id)`: Returns InboxEmail
- `classify_as_disruption_candidate(email)`: Returns bool

**MVP Behavior**: Returns synthetic email data, classifies based on subject keywords

### TOL7 Audit Writer Adapter (Active)
**Location**: `app/adapters/audit_writer_adapter.py`

**Purpose**: Write audit markers to external audit system

**Methods**:
- `write_audit_marker(...)`: Writes structured log entry
- `write_external_marker(...)`: Writes external event marker (future AGN5 seam)

**MVP Behavior**: Writes structured log entries for audit trail

---

## Middleware

### auth_middleware.py
- `get_current_user(credentials, db)`: JWT validation and user resolution
- `require_role(required_role)`: Role-based authorization dependency

### correlation_middleware.py
- Generates or reuses X-Correlation-ID header
- Stores correlation_id in request.state
- Returns X-Correlation-ID in response headers

### error_handling_middleware.py
- Global error handlers for consistent `{"detail": "..."}` responses
- ValueError → 400 Bad Request
- PermissionError → 403 Forbidden
- ValidationError → 422 Unprocessable Entity
- Exception → 500 Internal Server Error (no internals leaked)

### request_logging_middleware.py
- Structured logging for request/response with timing
- Includes correlation_id, method, path, status_code, duration_ms

---

## Testing

Run unit tests:
```bash
cd /repos/dim-rim/backend
python -m pytest tests/test_intake_service.py tests/test_classification_service.py tests/test_audit_service.py -v
```

Run integration tests:
```bash
python -m pytest tests/test_intake_integration.py tests/test_classification_integration.py -v
```

Run acceptance tests:
```bash
python -m pytest tests/test_intake_acceptance.py tests/test_classification_acceptance.py tests/test_audit_acceptance.py -v
```

---

## Screens That Can Use This Data

### Intake Case Workspace Screen (TASK-6)
- Can call: GET /api/v1/intake/cases/{case_id}
- Can call: POST /api/v1/intake/submissions
- Uses seed case: CASE-2026-001 (parsed status)
- Login as: Any user (disruption.mgr@tmna.com)

### Classification Review Screen (TASK-6)
- Can call: POST /api/v1/classification/cases/{case_id}/recommendation
- Can call: POST /api/v1/classification/cases/{case_id}/decision
- Uses seed case: CASE-2026-002 (classification_pending_review status)
- Login as: event.reviewer@tmna.com (Event Approval Reviewer role required for decision)

### Audit Trail Screen (TASK-7)
- Can call: GET /api/v1/audit/cases/{case_id}/events
- Uses seed case: CASE-2026-001 or CASE-2026-002
- Login as: Any user

---

## Notes

- All endpoints mounted under `/api/v1` prefix
- Correlation IDs threaded through request lifecycle
- Append-only audit trail for all in-scope actions
- BR-06 AMBER gate enforced on classification decision (role check)
- AGN1 Intake & Triage Agent implemented as orchestration logic in services
- Mocked integrations (TOL1, TOL7) follow adapter pattern for future live integration
