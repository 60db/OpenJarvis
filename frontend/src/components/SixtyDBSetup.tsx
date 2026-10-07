import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { configureSixtyDB, getSixtyDBStatus, getSixtyDBVoices, type SixtyDBVoice } from '../lib/api';
import { useAppStore } from '../lib/store';

export function SixtyDBSetup({ onReady, embedded = false }: {
  onReady?: () => void;
  embedded?: boolean;
}) {
  const [key, setKey] = useState('');
  const [hasKey, setHasKey] = useState(false);
  const [voices, setVoices] = useState<SixtyDBVoice[]>([]);
  const [voiceId, setVoiceId] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getSixtyDBStatus().then(async (status) => {
      if (cancelled) return;
      setHasKey(status.key_configured);
      setVoiceId(status.voice_id);
      if (status.key_configured && status.voice_id && !embedded) {
        useAppStore.getState().setSelectedModel('60db-tiny');
        onReady?.();
        return;
      }
      if (status.key_configured) {
        const catalog = await getSixtyDBVoices();
        if (!cancelled) setVoices(catalog);
      }
    }).catch((err) => {
      if (!cancelled) setError(err instanceof Error ? err.message : String(err));
    }).finally(() => { if (!cancelled) setChecked(true); });
    return () => { cancelled = true; };
  }, [embedded, onReady]);

  const loadVoices = async () => {
    setBusy(true);
    setError('');
    setSaved(false);
    try {
      const catalog = await getSixtyDBVoices(key.trim());
      setVoices(catalog);
      if (!catalog.some((v) => v.voice_id === voiceId)) setVoiceId(catalog[0]?.voice_id || '');
      if (!catalog.length) setError('No voices are available for this 60db workspace.');
    } catch (err) {
      setVoices([]);
      setError(err instanceof Error ? err.message : String(err));
    } finally { setBusy(false); }
  };

  const save = async () => {
    setBusy(true);
    setError('');
    try {
      await configureSixtyDB(key.trim(), voiceId);
      setKey('');
      setHasKey(true);
      setSaved(true);
      const store = useAppStore.getState();
      store.setSelectedModel('60db-tiny');
      store.updateSettings({ speechEnabled: true, voiceOutputEnabled: true });
      onReady?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally { setBusy(false); }
  };

  const fieldStyle = { background: 'var(--color-bg-secondary)', color: 'var(--color-text)', border: '1px solid var(--color-border)' };
  const form = (
    <div className="w-full max-w-lg space-y-5">
      <div>
        <h1 className="text-2xl font-semibold" style={{ color: 'var(--color-text)' }}>Jarvis with 60db</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary)' }}>
          One key for chat, voice input, spoken answers, and Judge.
        </p>
      </div>
      {!checked && <p role="status">Checking your saved setup…</p>}
      <label className="block text-sm" style={{ color: 'var(--color-text)' }}>
        60db API key
        <input type="password" autoComplete="off" value={key} disabled={busy}
          placeholder={hasKey ? 'Key saved — leave blank to keep it' : 'Paste your 60db API key'}
          onChange={(event) => { setKey(event.target.value); setVoices([]); setSaved(false); }}
          className="block w-full mt-2 px-3 py-2 rounded-lg" style={fieldStyle} />
      </label>
      <a href="https://app.60db.ai" target="_blank" rel="noreferrer" className="text-sm underline"
        style={{ color: 'var(--color-accent)' }}>Get a 60db API key</a>
      <button type="button" onClick={() => void loadVoices()} disabled={busy || (!key.trim() && !hasKey)}
        className="block px-4 py-2 rounded-lg text-sm disabled:opacity-50" style={fieldStyle}>
        {busy ? 'Connecting…' : 'Load voices'}
      </button>
      {voices.length > 0 && <label className="block text-sm" style={{ color: 'var(--color-text)' }}>
        Choose your voice
        <select value={voiceId} disabled={busy} onChange={(event) => { setVoiceId(event.target.value); setSaved(false); }}
          className="block w-full mt-2 px-3 py-2 rounded-lg" style={fieldStyle}>
          {voices.map((voice) => <option key={voice.voice_id} value={voice.voice_id}>
            {voice.name}{voice.labels?.language_name ? ` · ${voice.labels.language_name}` : ''}
          </option>)}
        </select>
      </label>}
      {voices.find((voice) => voice.voice_id === voiceId)?.preview_url &&
        <audio controls src={voices.find((voice) => voice.voice_id === voiceId)?.preview_url} aria-label="Voice preview" />}
      {error && <p role="alert" className="text-sm" style={{ color: 'var(--color-error)' }}>{error}</p>}
      {saved && <p role="status" className="text-sm" style={{ color: 'var(--color-success)' }}>60db settings saved.</p>}
      <button type="button" onClick={() => void save()} disabled={busy || !voices.some((v) => v.voice_id === voiceId)}
        className="w-full py-3 px-4 rounded-lg font-medium flex justify-center gap-2 disabled:opacity-50"
        style={{ background: 'var(--color-accent)', color: 'white' }}>
        {busy && <Loader2 size={18} className="animate-spin" />}
        {embedded ? 'Save voice and key' : 'Start using Jarvis'}
      </button>
    </div>
  );
  return embedded ? form : <div className="fixed inset-0 flex items-center justify-center p-6"
    style={{ background: 'var(--color-bg)' }}>{form}</div>;
}
