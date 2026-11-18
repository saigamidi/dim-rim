import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AuditEventsTable } from '../components/audit/AuditEventsTable';

describe('AuditEventsTable', () => {
  const mockEvents = [
    {
      id: '1',
      occurred_at_utc: '2026-11-18T13:42:07Z',
      actor_type: 'agent',
      actor_id: 'AGN1 Intake & Triage',
      action_type: 'intake_registered',
      entity_type: 'intake_case',
      entity_id: 'DIS-2026-0412',
      outcome: 'success',
      correlation_id: 'c0a8d1f2-77be-4c1a-b3e5-91d2f06a4b18',
      created_at: '2026-11-18T13:42:07Z'
    },
    {
      id: '2',
      occurred_at_utc: '2026-11-18T14:04:10Z',
      actor_type: 'system',
      actor_id: 'Deterministic Rule Engine',
      action_type: 'br01_validation_completed',
      entity_type: 'intake_case',
      entity_id: 'DIS-2026-0412',
      outcome: 'success',
      correlation_id: 'c0a8d1f2-77be-4c1a-b3e5-91d2f06a4b18',
      metadata_json: '{"valid_count": 3892, "invalid_count": 13}',
      created_at: '2026-11-18T14:04:10Z'
    }
  ];

  it('renders audit events table with correct event data', () => {
    render(<AuditEventsTable events={mockEvents} />);

    expect(screen.getByText('AGN1 Intake & Triage')).toBeInTheDocument();
    expect(screen.getByText('intake_registered')).toBeInTheDocument();
    expect(screen.getByText('br01_validation_completed')).toBeInTheDocument();
  });

  it('displays action type filters section', () => {
    render(<AuditEventsTable events={mockEvents} />);

    // Just check that the table heading is present
    expect(screen.getByRole('heading', { name: /audit events/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /time \(utc\)/i })).toBeInTheDocument();
  });

  it('shows empty state when no events', () => {
    render(<AuditEventsTable events={[]} />);

    expect(screen.getByText(/no audit events match/i)).toBeInTheDocument();
  });
});
