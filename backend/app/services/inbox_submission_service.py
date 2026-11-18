"""Inbox submission service with AGN1 orchestration logic."""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.adapters.inbox_connector_adapter import InboxConnectorAdapter
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.repositories.email_attachment_repository import EmailAttachmentRepository
from app.repositories.intake_case_repository import IntakeCaseRepository
from app.schemas.intake_schemas import InboxSubmissionIn, IntakeCaseOut
from app.services.audit_service import AuditService


class InboxSubmissionService:
    """Service for inbox submission with AGN1 Intake & Triage Agent orchestration.
    
    AGN1 orchestration logic:
    1. Fetch email from TOL1 Inbox Connector
    2. Distinguish disruption candidates from non-cases
    3. Create intake case with received status
    4. Record audit event
    5. Progress status: received → parsed (when attachments parsed)
    """

    def __init__(self, session: Session, correlation_id: str):
        self.session = session
        self.correlation_id = correlation_id
        self.intake_repo = IntakeCaseRepository(session)
        self.attachment_repo = EmailAttachmentRepository(session)
        self.audit_service = AuditService(session)
        self.inbox_adapter = InboxConnectorAdapter()

    def submit_inbox_email(
        self, submission: InboxSubmissionIn, actor_id: str
    ) -> IntakeCaseOut:
        """Submit an inbox email for disruption case creation.
        
        AGN1 Intake & Triage orchestration:
        - Fetch email metadata from TOL1
        - Classify as disruption candidate vs. non-case
        - Create intake case with received status
        - Create placeholder attachments if present
        - Record audit event
        """
        # AGN1 Step 1: Fetch email from TOL1 (mocked - uses submission data)
        # In MVP, we create synthetic email from submission data
        # Future: Will call live TOL1 API
        from app.adapters.inbox_connector_adapter import InboxEmail
        
        email = InboxEmail(
            email_id=submission.source_email_id,
            from_address=submission.source_address,
            received_at=submission.received_at_utc,
            subject=submission.subject,
            has_attachments=submission.has_attachments,
            is_disruption_candidate=False,  # Will be determined below
        )
        
        # AGN1 Step 2: Distinguish disruption candidates from non-cases
        is_candidate = self.inbox_adapter.classify_as_disruption_candidate(email)
        
        if not is_candidate:
            # Non-case: Do not create loadable artifact, raise error immediately
            # Note: Audit event for non-candidates is not recorded to database
            # since there's no intake_case to reference (by design per FR-001)
            raise ValueError("Email is not a disruption candidate")
        
        # Check for duplicate submission
        existing = self.intake_repo.get_by_source_email_id(submission.source_email_id)
        if existing:
            return IntakeCaseOut.model_validate(existing)
        
        # AGN1 Step 3: Create intake case with received status
        case_id = str(uuid.uuid4())
        case_key = f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{case_id[:8]}"
        
        intake_case = IntakeCase(
            id=case_id,
            case_key=case_key,
            source_email_id=submission.source_email_id,
            source_address=submission.source_address,
            received_at_utc=submission.received_at_utc,
            subject=submission.subject,
            intake_status="received",
            correlation_id=self.correlation_id,
        )
        
        created_case = self.intake_repo.create(intake_case)
        
        # Create placeholder attachments if present
        if submission.has_attachments:
            attachment = EmailAttachment(
                id=str(uuid.uuid4()),
                intake_case_id=case_id,
                filename="pending_attachment.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                byte_size=0,
                storage_ref=f"inbox/{submission.source_email_id}/pending",
                parse_status="pending",
            )
            self.attachment_repo.create(attachment)
        
        # AGN1 Step 4: Record audit event
        self.audit_service.record_event(
            intake_case_id=case_id,
            correlation_id=self.correlation_id,
            actor_type="user",
            actor_id=actor_id,
            action_type="intake_submission",
            entity_type="intake_case",
            entity_id=case_id,
            outcome="success",
            metadata={
                "case_key": case_key,
                "source_email_id": submission.source_email_id,
                "source_address": submission.source_address,
                "subject": submission.subject,
                "has_attachments": submission.has_attachments,
            },
        )
        
        return IntakeCaseOut.model_validate(created_case)

    def get_case(self, case_id: str) -> IntakeCaseOut | None:
        """Get intake case by ID."""
        case = self.intake_repo.get_by_id(case_id)
        if not case:
            return None
        return IntakeCaseOut.model_validate(case)
