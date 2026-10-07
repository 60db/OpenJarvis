import { Cloud, ExternalLink } from 'lucide-react';
import { useAppStore } from '../../lib/store';

export function CostComparison() {
  const usage = useAppStore((s) => s.savings);
  return (
    <section className="hud-panel p-4">
      <h3 className="hud-label flex items-center gap-2 mb-3">
        <Cloud size={14} style={{ color: 'var(--color-accent)' }} />
        60db Usage
      </h3>
      <p className="text-xs mb-3" style={{ color: 'var(--color-text-secondary)' }}>
        Chat, speech, and Judge powered by 60db.
      </p>
      <dl className="grid grid-cols-2 gap-2 text-xs" style={{ color: 'var(--color-text)' }}>
        <dt>Requests</dt><dd className="text-right">{(usage?.total_calls ?? 0).toLocaleString()}</dd>
        <dt>Input tokens</dt><dd className="text-right">{(usage?.total_prompt_tokens ?? 0).toLocaleString()}</dd>
        <dt>Output tokens</dt><dd className="text-right">{(usage?.total_completion_tokens ?? 0).toLocaleString()}</dd>
      </dl>
      <a href="https://app.60db.ai" target="_blank" rel="noopener noreferrer"
        className="flex items-center gap-1.5 mt-4 text-xs" style={{ color: 'var(--color-accent)' }}>
        <ExternalLink size={12} /> View 60db billing
      </a>
    </section>
  );
}
