import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router';
import { expect, it, vi } from 'vitest';

it('shows only 60db even when old provider comparisons and models are present', async () => {
  vi.stubGlobal('localStorage', { getItem: () => null });
  try {
    const { useAppStore } = await import('../lib/store');
    const { SystemPanel } = await import('./Chat/SystemPanel');
    const { CostComparison } = await import('./Dashboard/CostComparison');
    const { CommandPalette } = await import('./CommandPalette');
    const { DashboardPage } = await import('../pages/DashboardPage');
    const { GetStartedPage } = await import('../pages/GetStartedPage');
    const { XRayFooter } = await import('./Chat/XRayFooter');
    const providers = ['GPT-5.6 Sol', 'Claude Fable 5', 'Gemini 3.1 Pro'];
    useAppStore.setState({
      models: providers.map((id) => ({ id, object: 'model', created: 0, owned_by: 'old-provider' })),
      selectedModel: '60db-tiny',
      savings: {
        total_calls: 2, total_prompt_tokens: 100, total_completion_tokens: 200,
        total_tokens: 300, local_cost: 0,
        per_provider: providers.map((label) => ({
          provider: label, label, input_cost: 1, output_cost: 2, total_cost: 3,
          energy_wh: 0, energy_joules: 0, flops: 0,
        })),
      },
    });
    const surfaces = [
      <SystemPanel />, <CostComparison />, <CommandPalette />, <DashboardPage />,
      <MemoryRouter><GetStartedPage /></MemoryRouter>,
    ];
    for (const surface of surfaces) {
      const html = renderToStaticMarkup(surface);
      expect(html).toContain('60db');
      expect(html).not.toMatch(/GPT|Claude|Gemini|Ollama|Qwen|electricity only|Cost Comparison|\$0\.0000/i);
    }
    const legacyFooter = renderToStaticMarkup(<XRayFooter telemetry={{ engine: 'old-provider', model_id: providers[0], total_ms: 100 }} />);
    expect(legacyFooter).not.toContain(providers[0]);
    const footer = renderToStaticMarkup(<XRayFooter telemetry={{ engine: 'sixtydb', model_id: '60db-tiny' }} />);
    expect(footer).toContain('60db');
  } finally {
    vi.unstubAllGlobals();
  }
});
