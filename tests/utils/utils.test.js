import { toUiAmount, trim, getFormattedDate } from '../../src/utils/utils';

describe('toUiAmount', () => {
  it('formats thousands correctly', () => {
    expect(toUiAmount(1500)).toBe('1.5K');
    expect(toUiAmount(1000)).toBe('1K');
    expect(toUiAmount(999)).toBe('999');
  });

  it('formats millions and billions correctly', () => {
    expect(toUiAmount(2_000_000)).toBe('2M');
    expect(toUiAmount(2_500_000)).toBe('2.5M');
    expect(toUiAmount(1_000_000_000)).toBe('1B');
    expect(toUiAmount(2_500_000_000)).toBe('2.5B');
  });

  it('returns 0 for falsy/zero', () => {
    expect(toUiAmount(0)).toBe(0);
    expect(toUiAmount(undefined)).toBe(0);
    expect(toUiAmount(null)).toBe(0);
  });
});

describe('trim', () => {
  it('trims specified character from both ends', () => {
    expect(trim('--hello--', '-')).toBe('hello');
    expect(trim('***star***', '*')).toBe('star');
  });

  it('returns original string if char not found', () => {
    expect(trim('hello', '-')).toBe('hello');
  });

  it('handles empty strings', () => {
    expect(trim('', '-')).toBe('');
    expect(trim()).toBe('');
  });
});

describe('getFormattedDate', () => {
  it('formats a valid date', () => {
    const date = new Date('2024-01-15T00:00:00Z');
    expect(typeof getFormattedDate(date)).toBe('string');
    expect(getFormattedDate(date).length).toBeGreaterThan(0);
  });

  it('returns empty string for invalid/empty date', () => {
    expect(getFormattedDate(null)).toBe('');
    expect(getFormattedDate(undefined)).toBe('');
  });
});
