"""Database seed data for development and testing."""
import json
import uuid
from datetime import datetime, timezone

import bcrypt

from app.database import SessionLocal
from app.models import (
    AuditEvent,
    CandidateRow,
    EmailAttachment,
    IntakeCase,
    User,
    VinRecord,
    VinValidationResult,
)


def seed_database():
    """Seed the database with demo users and sample cases."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_user = db.query(User).filter(User.email == "disruption.mgr@tmna.com").first()
        if existing_user:
            print("Seed data already exists, skipping...")
            return
        
        print("Seeding database...")
        
        # Seed demo users with bcrypt-hashed passwords (cost factor 12)
        users = [
            User(
                email="disruption.mgr@tmna.com",
                hashed_password=bcrypt.hashpw("Manager123!".encode(), bcrypt.gensalt(12)).decode(),
                full_name="Disruption Manager",
                role="Disruption Manager",
                is_active=True,
            ),
            User(
                email="event.reviewer@tmna.com",
                hashed_password=bcrypt.hashpw("Reviewer123!".encode(), bcrypt.gensalt(12)).decode(),
                full_name="Event Approval Reviewer",
                role="Event Approval Reviewer",
                is_active=True,
            ),
            User(
                email="vip.comms@tmna.com",
                hashed_password=bcrypt.hashpw("Comms123!".encode(), bcrypt.gensalt(12)).decode(),
                full_name="VIP Communication Reviewer",
                role="VIP Communication Reviewer",
                is_active=True,
            ),
        ]
        
        for user in users:
            db.add(user)
        
        db.flush()  # Get IDs assigned
        
        # Sample intake cases
        case1_id = str(uuid.uuid4())
        case1 = IntakeCase(
            id=case1_id,
            case_key="CASE-2026-001",
            source_email_id="email-001@disruptions.tmna.com",
            source_address="supplier-alerts@supplier.com",
            received_at_utc=datetime(2026, 11, 15, 14, 30, 0, tzinfo=timezone.utc),
            subject="Part Shortage - VIN List Attached",
            intake_status="parsed",
            correlation_id=str(uuid.uuid4()),
        )
        
        case2_id = str(uuid.uuid4())
        case2 = IntakeCase(
            id=case2_id,
            case_key="CASE-2026-002",
            source_email_id="email-002@disruptions.tmna.com",
            source_address="logistics-team@tmna.com",
            received_at_utc=datetime(2026, 11, 16, 9, 15, 0, tzinfo=timezone.utc),
            subject="Logistics Delay - Production Impact",
            intake_status="classification_pending_review",
            correlation_id=str(uuid.uuid4()),
        )
        
        db.add(case1)
        db.add(case2)
        db.flush()
        
        # Sample attachment for case1
        attachment1_id = str(uuid.uuid4())
        attachment1 = EmailAttachment(
            id=attachment1_id,
            intake_case_id=case1_id,
            filename="affected_vins.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            byte_size=45678,
            storage_ref=f"attachments/{attachment1_id}/affected_vins.xlsx",
            parse_status="parsed",
        )
        
        db.add(attachment1)
        db.flush()
        
        # Sample candidate rows with diverse VIN validation outcomes
        # 8 valid VINs + 4 invalid VINs for different failure reasons
        test_vins = [
            # Valid VINs (8) - with correct ISO 3779 checksums
            "1HGBH41J70N109186",  # Valid checksum (check digit 7)
            "2HGBH41J60N109187",  # Valid checksum (check digit 6)
            "3HGBH41J50N109188",  # Valid checksum (check digit 5)
            "4HGBH41J40N109189",  # Valid checksum (check digit 4)
            "5HGBH41J70N10918A",  # Valid checksum (check digit 7)
            "1G1ZT538906109186",  # Valid checksum (check digit 9)
            "2G1WH52K809109187",  # Valid checksum (check digit 8)
            "3GNDA13D20S109188",  # Valid checksum (check digit 2)
            # Invalid VINs (4)
            "1HGBH41JX",           # Wrong length (9 chars)
            "1HGBH41JXMN109I86",  # Invalid character (I)
            "1HGBH41J00N109186",  # Checksum failure (wrong check digit, should be 7)
            "",                   # Empty value
        ]
        
        candidate_rows = []
        for i, vin in enumerate(test_vins):
            row_id = str(uuid.uuid4())
            candidate_rows.append(CandidateRow(
                id=row_id,
                attachment_id=attachment1_id,
                source_row_number=i + 1,
                canonical_vin_candidate=vin if vin else None,
                raw_row_json=json.dumps({
                    "row": i + 1,
                    "vin": vin if vin else "",
                    "model": "Camry" if i < 8 else "Unknown",
                    "year": 2024
                }),
                row_status="extracted",
                lineage_ref=f"lin-{case1_id}/att-{attachment1_id}/r{i+1}",
            ))
        
        for row in candidate_rows:
            db.add(row)
        
        db.flush()
        
        # Sample VIN records with extraction status
        vin_records = []
        for i, row in enumerate(candidate_rows):
            vin_id = str(uuid.uuid4())
            raw_vin = row.canonical_vin_candidate
            
            # Handle empty VIN (rejected during extraction)
            if not raw_vin:
                vin_records.append(VinRecord(
                    id=vin_id,
                    intake_case_id=case1_id,
                    candidate_row_id=row.id,
                    raw_vin=raw_vin,
                    normalized_vin=None,
                    extraction_status="rejected_empty",
                    is_duplicate_within_case=False,
                ))
            else:
                # Normalize: uppercase, trim
                normalized_vin = raw_vin.strip().upper()
                vin_records.append(VinRecord(
                    id=vin_id,
                    intake_case_id=case1_id,
                    candidate_row_id=row.id,
                    raw_vin=raw_vin,
                    normalized_vin=normalized_vin,
                    extraction_status="extracted",
                    is_duplicate_within_case=False,
                ))
        
        for vin_rec in vin_records:
            db.add(vin_rec)
        
        db.flush()
        
        # Sample VIN validation results (12 total: 8 valid, 4 invalid with different reasons)
        validation_results = []
        validated_at = datetime(2026, 11, 15, 14, 40, 0, tzinfo=timezone.utc)
        
        # Validation outcomes matching the test VINs
        validation_outcomes = [
            # Valid VINs (8)
            ("valid", None, None, True),
            ("valid", None, None, True),
            ("valid", None, None, True),
            ("valid", None, None, True),
            ("valid", None, None, True),
            ("valid", None, None, True),
            ("valid", None, None, True),
            ("valid", None, None, True),
            # Invalid VINs (4)
            ("invalid", "wrong_length", "VIN length is 9, expected 17", False),
            ("invalid", "invalid_character", "VIN contains forbidden character 'I' at position 14", False),
            ("invalid", "checksum_failure", "Check digit mismatch: expected '8', found '9' at position 9", False),
            ("invalid", "empty_value", "VIN is empty or contains only whitespace", False),
        ]
        
        for i, vin_rec in enumerate(vin_records):
            # Only create validation results for extracted VINs (not rejected_empty during extraction)
            if vin_rec.extraction_status == "extracted":
                status, reason_code, reason_detail, checksum_passed = validation_outcomes[i]
                
                validation_results.append(VinValidationResult(
                    id=str(uuid.uuid4()),
                    vin_record_id=vin_rec.id,
                    validation_status=status,
                    failure_reason_code=reason_code,
                    failure_reason_detail=reason_detail,
                    checksum_passed=checksum_passed,
                    validated_at_utc=validated_at,
                ))
        
        for val_result in validation_results:
            db.add(val_result)
        
        db.flush()
        
        # Sample audit events
        audit_events = [
            AuditEvent(
                intake_case_id=case1_id,
                correlation_id=case1.correlation_id,
                actor_type="system",
                actor_id="inbox_connector",
                action_type="intake_registered",
                entity_type="intake_case",
                entity_id=case1_id,
                outcome="success",
                metadata_json=json.dumps({"source": "TOL1", "case_key": case1.case_key}),
                occurred_at_utc=case1.received_at_utc,
            ),
            AuditEvent(
                intake_case_id=case1_id,
                correlation_id=case1.correlation_id,
                actor_type="system",
                actor_id="attachment_parser",
                action_type="parsing_completed",
                entity_type="email_attachment",
                entity_id=attachment1_id,
                outcome="success",
                metadata_json=json.dumps({"row_count": 12, "filename": "affected_vins.xlsx"}),
                occurred_at_utc=datetime(2026, 11, 15, 14, 35, 0, tzinfo=timezone.utc),
            ),
            AuditEvent(
                intake_case_id=case1_id,
                correlation_id=case1.correlation_id,
                actor_type="system",
                actor_id="vin_processor",
                action_type="vins_validated",
                entity_type="intake_case",
                entity_id=case1_id,
                outcome="success",
                metadata_json=json.dumps({
                    "valid_count": 8,
                    "invalid_count": 3,
                    "failure_breakdown": {
                        "wrong_length": 1,
                        "invalid_character": 1,
                        "checksum_failure": 1,
                    }
                }),
                occurred_at_utc=validated_at,
            ),
            AuditEvent(
                intake_case_id=case2_id,
                correlation_id=case2.correlation_id,
                actor_type="system",
                actor_id="inbox_connector",
                action_type="intake_registered",
                entity_type="intake_case",
                entity_id=case2_id,
                outcome="success",
                metadata_json=json.dumps({"source": "TOL1", "case_key": case2.case_key}),
                occurred_at_utc=case2.received_at_utc,
            ),
        ]
        
        for event in audit_events:
            db.add(event)
        
        db.commit()
        print("Database seeded successfully!")
        print("\nDemo credentials:")
        print("  Disruption Manager: disruption.mgr@tmna.com / Manager123!")
        print("  Event Reviewer: event.reviewer@tmna.com / Reviewer123!")
        print("  VIP Comms: vip.comms@tmna.com / Comms123!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
