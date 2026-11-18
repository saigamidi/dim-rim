/**
 * Unit tests for Chip component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Chip } from '../components/shared/Chip';

describe('Chip', () => {
  it('renders children text', () => {
    render(<Chip variant="ok">Test Chip</Chip>);
    expect(screen.getByText('Test Chip')).toBeInTheDocument();
  });

  it('applies correct variant classes', () => {
    const { container } = render(<Chip variant="ok">Success</Chip>);
    const chip = container.firstChild as HTMLElement;
    expect(chip).toHaveClass('bg-ok-bg');
    expect(chip).toHaveClass('text-ok');
  });

  it('renders with icon when provided', () => {
    const { container } = render(
      <Chip variant="warn" icon="TriangleAlert">
        Warning
      </Chip>
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <Chip variant="info" className="custom-class">
        Info
      </Chip>
    );
    const chip = container.firstChild as HTMLElement;
    expect(chip).toHaveClass('custom-class');
  });
});
