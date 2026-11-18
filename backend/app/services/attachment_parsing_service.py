"""Attachment parsing service orchestrating TOL2 seam and canonical row persistence."""
import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.adapters.attachment_parser_adapter import AttachmentParserAdapter
from app.models.candidate_row import CandidateRow
from app.repositories.candidate_row_repository import CandidateRowRepository
from app.repositories.email_attachment_repository import EmailAttachmentRepository
from app.schemas.parsing_schemas import AttachmentParseResultOut, CandidateRowOut

logger = logging.getLogger(__name__)


class AttachmentParsingService:
    """Service for attachment parsing operations."""

    def __init__(self, session: Session):
        self.session = session
        self.attachment_repo = EmailAttachmentRepository(session)
        self.candidate_row_repo = CandidateRowRepository(session)
        self.parser_adapter = AttachmentParserAdapter()

    def parse_attachment(
        self, attachment_id: str, force_reparse: bool = False
    ) -> AttachmentParseResultOut:
        """
        Parse an attachment into canonical candidate rows.
        
        Orchestrates TOL2 seam, normalizes rows, persists with row-level lineage.
        Handles parse failures explicitly. Idempotent via force_reparse flag.
        """
        # Get attachment
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail=f"Attachment {attachment_id} not found")

        # Check parse status
        if attachment.parse_status == "parsed" and not force_reparse:
            # Already parsed, return existing results
            existing_rows = self.candidate_row_repo.get_by_attachment_id(attachment_id)
            return AttachmentParseResultOut(
                attachment_id=attachment_id,
                parse_status="parsed",
                row_count=len(existing_rows),
                failure_count=0,
                lineage_base_ref=f"lin-{attachment.intake_case_id}/att-{attachment_id}",
            )

        # If reparse, delete existing rows
        if force_reparse and attachment.parse_status == "parsed":
            deleted_count = self.candidate_row_repo.delete_by_attachment_id(attachment_id)
            logger.info(f"Reparse requested: deleted {deleted_count} existing rows for attachment {attachment_id}")

        # Validate attachment format
        is_valid, error_message = self.parser_adapter.validate_attachment_format(
            attachment.filename, attachment.media_type
        )
        if not is_valid:
            # Update parse status to failed
            attachment.parse_status = "parse_failed"
            self.session.commit()
            raise HTTPException(status_code=400, detail=error_message)

        try:
            # Parse via TOL2 adapter
            parsed_rows, failure_count = self.parser_adapter.parse_attachment(
                attachment.filename, attachment.media_type, attachment.storage_ref
            )

            # Create candidate rows with row-level lineage
            lineage_base_ref = f"lin-{attachment.intake_case_id}/att-{attachment_id}"
            candidate_rows = []

            for parsed_row in parsed_rows:
                lineage_ref = f"{lineage_base_ref}/r{parsed_row.row_number}"
                
                candidate_row = CandidateRow(
                    id=str(uuid.uuid4()),
                    attachment_id=attachment_id,
                    source_row_number=parsed_row.row_number,
                    canonical_vin_candidate=parsed_row.vin_candidate,
                    raw_row_json=json.dumps(parsed_row.raw_data),
                    row_status="parsed",
                    lineage_ref=lineage_ref,
                    created_at=datetime.now(timezone.utc),
                )
                candidate_rows.append(candidate_row)

            # Batch insert candidate rows
            if candidate_rows:
                self.candidate_row_repo.create_many(candidate_rows)

            # Update attachment parse status
            attachment.parse_status = "parsed" if failure_count == 0 else "parse_partial"
            attachment.updated_at = datetime.now(timezone.utc)
            self.session.commit()

            logger.info(
                f"Attachment {attachment_id} parsed: {len(candidate_rows)} rows, {failure_count} failures"
            )

            return AttachmentParseResultOut(
                attachment_id=attachment_id,
                parse_status=attachment.parse_status,
                row_count=len(candidate_rows),
                failure_count=failure_count,
                lineage_base_ref=lineage_base_ref,
            )

        except Exception as e:
            # Mark parse as failed
            attachment.parse_status = "parse_failed"
            attachment.updated_at = datetime.now(timezone.utc)
            self.session.commit()
            
            logger.error(f"Parse failed for attachment {attachment_id}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Parse failed: {str(e)}"
            )

    def get_candidate_rows_by_case(self, case_id: str) -> list[CandidateRowOut]:
        """Get all candidate rows for a case."""
        rows = self.candidate_row_repo.get_by_case_id(case_id)
        return [CandidateRowOut.model_validate(row) for row in rows]

    def get_candidate_rows_by_attachment(self, attachment_id: str) -> list[CandidateRowOut]:
        """Get all candidate rows for an attachment."""
        rows = self.candidate_row_repo.get_by_attachment_id(attachment_id)
        return [CandidateRowOut.model_validate(row) for row in rows]
