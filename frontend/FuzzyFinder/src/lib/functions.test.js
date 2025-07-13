import { describe, it, expect, vi, afterEach } from 'vitest';
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

  it('should call correct endpoint when processing a YouTube video', async () => {
    const api = new FuzzyAPI('http://localhost:1234');

    const mockResponse = { message: 'YouTube processing not implemented yet', url: 'url', detector: 'yolo' };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    global.fetch = fetchMock;

    await api.processYouTubeVideo('url');

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:1234/process-youtube', expect.any(Object));
  });

  it('should fetch job status', async () => {
    const api = new FuzzyAPI('http://localhost');
    const mockResponse = { job_id: 1, status: 'completed' };
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(mockResponse) });

    const res = await api.getJobStatus(1);
    expect(res.status).toBe('completed');
  });

  afterEach(() => {
    // @ts-ignore
    delete global.fetch;
  });
});