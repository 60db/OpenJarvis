import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';

describe('60db settings', () => {
  it('offers a single 60db key and voice setup', async () => {
    vi.stubGlobal('localStorage', { getItem: () => null });
    vi.stubGlobal('window', { __TAURI_INTERNALS__: {} });
    const { SettingsPage } = await import('./SettingsPage');
    const html = renderToStaticMarkup(<SettingsPage />);

    expect(html).toContain('Jarvis with 60db');
    expect(html).not.toContain('Atlas Cloud');
    const keyInput = html.match(/<input[^>]*type="password"[^>]*>/)?.[0];
    expect(keyInput).toBeDefined();
    expect(keyInput).not.toContain('disabled');
    vi.unstubAllGlobals();
  });
});
