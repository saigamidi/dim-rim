import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ValidationOutcomeCard } from '../components/vin/ValidationOutcomeCard';

describe('ValidationOutcomeCard', () => {
  it('renders validation summary with valid and invalid counts', () => {
    render(
      <ValidationOutcomeCard
        validCount={3892}
        invalidCount={13}
        totalCount={3905}
        failureBreakdown={{
          wrong_length: 3,
          invalid_character: 2,
          checksum_failure: 8
        }}
      />
    );

    expect(screen.getByText(/3,905 unique VIN records/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /outcome and failure reasons/i })).toBeInTheDocument();
  });

  it('renders failure breakdown table', () => {
    render(
      <ValidationOutcomeCard
        validCount={10}
        invalidCount={3}
        totalCount={13}
        failureBreakdown={{
          wrong_length: 1,
          invalid_character: 1,
          checksum_failure: 1
        }}
      />
    );

    expect(screen.getByText('wrong_length')).toBeInTheDocument();
    expect(screen.getByText('invalid_character')).toBeInTheDocument();
    expect(screen.getByText('checksum_failure')).toBeInTheDocument();
    expect(screen.getByText('Length is not 17')).toBeInTheDocument();
  });
});
