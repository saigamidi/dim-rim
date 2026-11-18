import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    // Login page should be visible initially (unauthenticated)
    const heading = screen.getByRole('heading', { name: /Disruption Manager RIM/i });
    expect(heading).toBeDefined();
  });
});
