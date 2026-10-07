import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useAppStore } from '../../lib/store';
import type { SavingsData } from '../../types';
import { CostComparison } from '../Dashboard/CostComparison';

export function SavingsDashboard({ apiUrl }: { apiUrl: string }) {
  const [error, setError] = useState('');
  useEffect(() => {
    let cancelled = false;
    const refresh = async () => {
      try {
        const usage = await invoke<SavingsData>('fetch_savings', { apiUrl });
        if (!cancelled) {
          useAppStore.getState().setSavings(usage);
          setError('');
        }
      } catch {
        if (!cancelled) setError('Unable to load 60db usage.');
      }
    };
    void refresh();
    const timer = setInterval(refresh, 5000);
    return () => { cancelled = true; clearInterval(timer); };
  }, [apiUrl]);
  return <div>{error && <p role="alert">{error}</p>}<CostComparison /></div>;
}
