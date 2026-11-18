"""TOL1 Inbox Connector Adapter - Mocked implementation for MVP."""
from datetime import datetime, timezone


class InboxEmail:
    """Email from inbox connector."""

    def __init__(
        self,
        email_id: str,
        from_address: str,
        received_at: datetime,
        subject: str,
        has_attachments: bool,
        is_disruption_candidate: bool,
    ):
        self.email_id = email_id
        self.from_address = from_address
        self.received_at = received_at
        self.subject = subject
        self.has_attachments = has_attachments
        self.is_disruption_candidate = is_disruption_candidate


class InboxConnectorAdapter:
    """Mocked inbox connector adapter for retrieving candidate disruption emails.
    
    Future live integration will replace this implementation while keeping the same interface.
    """

    def fetch_email(self, source_email_id: str) -> InboxEmail | None:
        """Fetch email by ID from inbox.
        
        MVP: Mocked implementation returns synthetic email data.
        Future: Will call live TOL1 inbox API.
        """
        # Mock: Return a synthetic email (classification will be determined by classify method)
        return InboxEmail(
            email_id=source_email_id,
            from_address="supplier@example.com",
            received_at=datetime.now(timezone.utc),
            subject="Email fetched from inbox",
            has_attachments=True,
            is_disruption_candidate=False,  # Will be determined by classify method
        )

    def classify_as_disruption_candidate(self, email: InboxEmail) -> bool:
        """Determine if email is a disruption candidate vs. non-case.
        
        MVP: Simple heuristic based on subject keywords.
        Future: Will integrate with AGN1 classification logic.
        """
        keywords = ["disruption", "vin list", "production", "supply", "delay"]
        subject_lower = email.subject.lower()
        return any(keyword in subject_lower for keyword in keywords)
