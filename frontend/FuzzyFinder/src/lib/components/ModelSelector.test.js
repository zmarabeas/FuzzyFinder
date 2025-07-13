import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import ModelSelector from './ModelSelector.svelte';

describe('ModelSelector', () => {
  it('reflects bound value when changed', async () => {
    const { getByLabelText } = render(ModelSelector, { selectedModel: 'yolo' });
    const select = getByLabelText(/Animal Detection Model/i);
    expect(select.value).toBe('yolo');
    await fireEvent.change(select, { target: { value: 'mobilenet' } });
    expect(select.value).toBe('mobilenet');
  });
});