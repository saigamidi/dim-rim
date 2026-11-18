/**
 * Unit tests for CaseQueueList component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CaseQueueList } from '../components/intake/CaseQueueList';
import { IntakeCaseOut } from '../types/intake';

const mockCases: IntakeCaseOut[] = [
  {
    id: 'case-1',
    case_key: 'CASE-2026-001',
    source_email_id: 'email-1',
    source_address: 'test@example.com',
    received_at_utc: '2026-11-18T13:42:07Z',
    subject: 'Test disruption case',
    intake_status: 'parsed',
    correlation_id: 'corr-1',
    created_at: '2026-11-18T13:42:07Z',
    updated_at: '2026-11-18T13:42:07Z',
    attachments: [],
  },
];

describe('CaseQueueList', () => {
  it('renders case list items', () => {
    const onSelectCase = vi.fn();
    render(<CaseQueueList cases={mockCases} selectedCaseId={null} onSelectCase={onSelectCase} />);
    
    expect(screen.getByText('CASE-2026-001')).toBeInTheDocument();
    expect(screen.getByText('Test disruption case')).toBeInTheDocument();
  });

  it('highlights selected case', () => {
    const onSelectCase = vi.fn();
    const { container } = render(
      <CaseQueueList cases={mockCases} selectedCaseId="case-1" onSelectCase={onSelectCase} />
    );
    
    const selectedItem = container.querySelector('[aria-current="true"]');
    expect(selectedItem).toBeInTheDocument();
    expect(selectedItem).toHaveClass('bg-accent-soft');
  });

  it('displays case status chip', () => {
    const onSelectCase = vi.fn();
    render(<CaseQueueList cases={mockCases} selectedCaseId={null} onSelectCase={onSelectCase} />);
    
    expect(screen.getByText('parsed')).toBeInTheDocument();
  });
});
