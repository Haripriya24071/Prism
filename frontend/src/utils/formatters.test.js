import { describe, it, expect } from 'vitest';
import { formatScore, getScoreColor } from './formatters';

describe('formatters', () => {
  it('formats numeric scores to percentages', () => {
    expect(formatScore(0.85)).toBe('85%');
    expect(formatScore(1)).toBe('100%');
    expect(formatScore(null)).toBe('N/A');
  });

  it('returns high score color class', () => {
    expect(getScoreColor(0.9)).toContain('emerald');
    expect(getScoreColor(0.5)).toContain('rose');
  });
});
