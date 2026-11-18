import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ExtractionSummaryTiles } from '../components/vin/ExtractionSummaryTiles';

describe('ExtractionSummaryTiles', () => {
  it('renders all four summary tiles with correct counts', () => {
    render(
      <ExtractionSummaryTiles
        rowsParsed={3931}
        extracted={3919}
        deduplicated={14}
        rejected={12}
        attachmentFilename="test_file.xlsx"
      />
    );

    expect(screen.getByText('3,931')).toBeInTheDocument();
    expect(screen.getByText('3,919')).toBeInTheDocument();
    expect(screen.getByText('14')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('Rows parsed')).toBeInTheDocument();
    expect(screen.getByText('Extracted candidates')).toBeInTheDocument();
    expect(screen.getByText('Deduplicated (duplicates removed)')).toBeInTheDocument();
    expect(screen.getByText('Rejected as empty')).toBeInTheDocument();
  });

  it('displays reconciliation calculation', () => {
    render(
      <ExtractionSummaryTiles
        rowsParsed={100}
        extracted={95}
        deduplicated={5}
        rejected={5}
      />
    );

    expect(screen.getByText(/95 − 5 = 90/)).toBeInTheDocument();
  });
});
