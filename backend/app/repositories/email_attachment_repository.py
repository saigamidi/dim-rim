"""Repository for email attachment data access."""
from sqlalchemy.orm import Session

from app.models.email_attachment import EmailAttachment


class EmailAttachmentRepository:
    """Repository for email attachment CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, attachment: EmailAttachment) -> EmailAttachment:
        """Create a new email attachment."""
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment

    def get_by_id(self, attachment_id: str) -> EmailAttachment | None:
        """Get email attachment by ID."""
        return (
            self.session.query(EmailAttachment)
            .filter(EmailAttachment.id == attachment_id)
            .first()
        )

    def get_by_case_id(self, case_id: str) -> list[EmailAttachment]:
        """Get all attachments for a case."""
        return (
            self.session.query(EmailAttachment)
            .filter(EmailAttachment.intake_case_id == case_id)
            .all()
        )
