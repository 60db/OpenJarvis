import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it, vi } from 'vitest';
import { InferenceRecoveryButton } from './InferenceSourceSetup';

it('offers 60db setup recovery and disables it while stopping', () => {
  const ready = renderToStaticMarkup(<InferenceRecoveryButton recovering={false} onChange={vi.fn()} />);
  const busy = renderToStaticMarkup(<InferenceRecoveryButton recovering onChange={vi.fn()} />);
  expect(ready).toContain('Reset 60db setup');
  expect(ready).not.toMatch(/ disabled(?:=""|>)/);
  expect(busy).toContain('Stopping setup...');
  expect(busy).toMatch(/ disabled(?:=""|>)/);
});
