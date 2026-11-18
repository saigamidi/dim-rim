"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-11-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # requirement: FR-001, FR-003 (user table for auth)
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=64), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    # requirement: FR-001, FR-003
    op.create_table('intake_case',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('case_key', sa.String(length=64), nullable=False),
    sa.Column('source_email_id', sa.String(length=255), nullable=False),
    sa.Column('source_address', sa.String(length=320), nullable=False),
    sa.Column('received_at_utc', sa.DateTime(), nullable=False),
    sa.Column('subject', sa.String(length=512), nullable=False),
    sa.Column('intake_status', sa.String(length=64), nullable=False),
    sa.Column('correlation_id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intake_case_case_key'), 'intake_case', ['case_key'], unique=True)
    op.create_index(op.f('ix_intake_case_source_email_id'), 'intake_case', ['source_email_id'], unique=True)
    op.create_index(op.f('ix_intake_case_received_at_utc'), 'intake_case', ['received_at_utc'], unique=False)
    op.create_index(op.f('ix_intake_case_intake_status'), 'intake_case', ['intake_status'], unique=False)

    # requirement: FR-001, FR-002
    op.create_table('email_attachment',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('intake_case_id', sa.String(length=36), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('media_type', sa.String(length=128), nullable=False),
    sa.Column('byte_size', sa.Integer(), nullable=False),
    sa.Column('storage_ref', sa.String(length=512), nullable=False),
    sa.Column('parse_status', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['intake_case_id'], ['intake_case.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_attachment_intake_case_id'), 'email_attachment', ['intake_case_id'], unique=False)
    op.create_index(op.f('ix_email_attachment_parse_status'), 'email_attachment', ['parse_status'], unique=False)

    # requirement: FR-002, FR-004
    op.create_table('candidate_row',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('attachment_id', sa.String(length=36), nullable=False),
    sa.Column('source_row_number', sa.Integer(), nullable=False),
    sa.Column('canonical_vin_candidate', sa.String(length=64), nullable=True),
    sa.Column('raw_row_json', sa.Text(), nullable=False),
    sa.Column('row_status', sa.String(length=64), nullable=False),
    sa.Column('lineage_ref', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['attachment_id'], ['email_attachment.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('attachment_id', 'source_row_number')
    )
    op.create_index(op.f('ix_candidate_row_attachment_id'), 'candidate_row', ['attachment_id'], unique=False)
    op.create_index(op.f('ix_candidate_row_row_status'), 'candidate_row', ['row_status'], unique=False)

    # requirement: FR-003
    op.create_table('classification_decision',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('intake_case_id', sa.String(length=36), nullable=False),
    sa.Column('suggested_disruption_type', sa.String(length=128), nullable=False),
    sa.Column('suggested_disruption_subtype', sa.String(length=128), nullable=True),
    sa.Column('suggested_event_ref', sa.String(length=128), nullable=True),
    sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=False),
    sa.Column('reviewer_decision', sa.String(length=32), nullable=False),
    sa.Column('final_disruption_type', sa.String(length=128), nullable=True),
    sa.Column('final_disruption_subtype', sa.String(length=128), nullable=True),
    sa.Column('final_event_ref', sa.String(length=128), nullable=True),
    sa.Column('reviewer_comment', sa.Text(), nullable=True),
    sa.Column('decided_by_user_id', sa.String(length=128), nullable=False),
    sa.Column('decided_at_utc', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['intake_case_id'], ['intake_case.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classification_decision_intake_case_id'), 'classification_decision', ['intake_case_id'], unique=False)
    op.create_index(op.f('ix_classification_decision_decided_at_utc'), 'classification_decision', ['decided_at_utc'], unique=False)

    # requirement: FR-004, FR-005
    op.create_table('vin_record',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('intake_case_id', sa.String(length=36), nullable=False),
    sa.Column('candidate_row_id', sa.String(length=36), nullable=False),
    sa.Column('raw_vin', sa.String(length=64), nullable=True),
    sa.Column('normalized_vin', sa.String(length=17), nullable=True),
    sa.Column('extraction_status', sa.String(length=64), nullable=False),
    sa.Column('is_duplicate_within_case', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['intake_case_id'], ['intake_case.id'], ),
    sa.ForeignKeyConstraint(['candidate_row_id'], ['candidate_row.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vin_record_intake_case_id'), 'vin_record', ['intake_case_id'], unique=False)
    op.create_index(op.f('ix_vin_record_candidate_row_id'), 'vin_record', ['candidate_row_id'], unique=False)
    op.create_index(op.f('ix_vin_record_normalized_vin'), 'vin_record', ['normalized_vin'], unique=False)

    # requirement: FR-005
    op.create_table('vin_validation_result',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('vin_record_id', sa.String(length=36), nullable=False),
    sa.Column('validation_status', sa.String(length=32), nullable=False),
    sa.Column('failure_reason_code', sa.String(length=64), nullable=True),
    sa.Column('failure_reason_detail', sa.String(length=255), nullable=True),
    sa.Column('checksum_passed', sa.Boolean(), nullable=False),
    sa.Column('validated_at_utc', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['vin_record_id'], ['vin_record.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('vin_record_id')
    )
    op.create_index(op.f('ix_vin_validation_result_vin_record_id'), 'vin_validation_result', ['vin_record_id'], unique=True)
    op.create_index(op.f('ix_vin_validation_result_validation_status'), 'vin_validation_result', ['validation_status'], unique=False)
    op.create_index(op.f('ix_vin_validation_result_failure_reason_code'), 'vin_validation_result', ['failure_reason_code'], unique=False)

    # requirement: FR-001, FR-002, FR-003, FR-004, FR-005
    op.create_table('audit_event',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('intake_case_id', sa.String(length=36), nullable=False),
    sa.Column('correlation_id', sa.String(length=36), nullable=False),
    sa.Column('actor_type', sa.String(length=64), nullable=False),
    sa.Column('actor_id', sa.String(length=128), nullable=False),
    sa.Column('action_type', sa.String(length=128), nullable=False),
    sa.Column('entity_type', sa.String(length=128), nullable=False),
    sa.Column('entity_id', sa.String(length=128), nullable=False),
    sa.Column('outcome', sa.String(length=64), nullable=False),
    sa.Column('metadata_json', sa.Text(), nullable=False),
    sa.Column('occurred_at_utc', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['intake_case_id'], ['intake_case.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_event_intake_case_id'), 'audit_event', ['intake_case_id'], unique=False)
    op.create_index(op.f('ix_audit_event_correlation_id'), 'audit_event', ['correlation_id'], unique=False)
    op.create_index(op.f('ix_audit_event_occurred_at_utc'), 'audit_event', ['occurred_at_utc'], unique=False)
    op.create_index(op.f('ix_audit_event_action_type'), 'audit_event', ['action_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_event_action_type'), table_name='audit_event')
    op.drop_index(op.f('ix_audit_event_occurred_at_utc'), table_name='audit_event')
    op.drop_index(op.f('ix_audit_event_correlation_id'), table_name='audit_event')
    op.drop_index(op.f('ix_audit_event_intake_case_id'), table_name='audit_event')
    op.drop_table('audit_event')
    
    op.drop_index(op.f('ix_vin_validation_result_failure_reason_code'), table_name='vin_validation_result')
    op.drop_index(op.f('ix_vin_validation_result_validation_status'), table_name='vin_validation_result')
    op.drop_index(op.f('ix_vin_validation_result_vin_record_id'), table_name='vin_validation_result')
    op.drop_table('vin_validation_result')
    
    op.drop_index(op.f('ix_vin_record_normalized_vin'), table_name='vin_record')
    op.drop_index(op.f('ix_vin_record_candidate_row_id'), table_name='vin_record')
    op.drop_index(op.f('ix_vin_record_intake_case_id'), table_name='vin_record')
    op.drop_table('vin_record')
    
    op.drop_index(op.f('ix_classification_decision_decided_at_utc'), table_name='classification_decision')
    op.drop_index(op.f('ix_classification_decision_intake_case_id'), table_name='classification_decision')
    op.drop_table('classification_decision')
    
    op.drop_index(op.f('ix_candidate_row_row_status'), table_name='candidate_row')
    op.drop_index(op.f('ix_candidate_row_attachment_id'), table_name='candidate_row')
    op.drop_table('candidate_row')
    
    op.drop_index(op.f('ix_email_attachment_parse_status'), table_name='email_attachment')
    op.drop_index(op.f('ix_email_attachment_intake_case_id'), table_name='email_attachment')
    op.drop_table('email_attachment')
    
    op.drop_index(op.f('ix_intake_case_intake_status'), table_name='intake_case')
    op.drop_index(op.f('ix_intake_case_received_at_utc'), table_name='intake_case')
    op.drop_index(op.f('ix_intake_case_source_email_id'), table_name='intake_case')
    op.drop_index(op.f('ix_intake_case_case_key'), table_name='intake_case')
    op.drop_table('intake_case')
    
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
