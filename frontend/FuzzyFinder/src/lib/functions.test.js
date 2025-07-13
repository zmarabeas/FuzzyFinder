import { describe, it, expect } from 'vitest';
import { FuzzyAPI } from './functions.js';

describe('FuzzyAPI', () => {
  it('should default to localhost route', () => {
    const api = new FuzzyAPI();
    expect(api.serverRoute).toBe('http://localhost:5005');
  });

  it('should allow overriding the server route', () => {
    const api = new FuzzyAPI('https://example.com');
    expect(api.serverRoute).toBe('https://example.com');
  });
});