import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import LoadingOverlay from './LoadingOverlay.svelte';

describe('LoadingOverlay', () => {
  it('renders when visible', () => {
    const { getByText } = render(LoadingOverlay, { visible: true, message: 'Testing...' });
    expect(getByText('Testing...')).toBeTruthy();
  });

  it('does not render when not visible', () => {
    const { queryByText } = render(LoadingOverlay, { visible: false, message: 'Hidden' });
    expect(queryByText('Hidden')).toBeNull();
  });
});