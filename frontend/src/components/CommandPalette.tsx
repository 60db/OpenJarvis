import { useEffect, useRef, useState } from 'react';
import { Cloud, Check, Search, X } from 'lucide-react';
import { useAppStore } from '../lib/store';

export function CommandPalette() {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const selectedModel = useAppStore((s) => s.selectedModel);
  const setSelectedModel = useAppStore((s) => s.setSelectedModel);
  const close = useAppStore((s) => s.setCommandPaletteOpen);
  const matches = '60db-tiny'.includes(query.trim().toLowerCase());
  const select = () => { setSelectedModel('60db-tiny'); close(false); };

  useEffect(() => {
    const previous = document.activeElement;
    inputRef.current?.focus();
    return () => { if (previous instanceof HTMLElement) previous.focus(); };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      style={{ background: 'rgba(0,0,0,0.5)' }} onClick={() => close(false)}>
      <div role="dialog" aria-modal="true" aria-label="60db model"
        className="w-full max-w-lg rounded-xl overflow-hidden"
        style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)' }}
        onClick={(e) => e.stopPropagation()} onKeyDown={(e) => {
          if (e.key === 'Escape') close(false);
          if (e.key === 'Tab') {
            const controls = e.currentTarget.querySelectorAll<HTMLElement>('input, button');
            const first = controls[0];
            const last = controls[controls.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
          }
        }}>
        <div className="flex items-center gap-3 px-4 py-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <Search size={18} />
          <input ref={inputRef} aria-label="Search 60db models" placeholder="Search 60db models..."
            className="flex-1 bg-transparent outline-none text-sm" value={query}
            onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => {
              if (e.key === 'Enter' && matches) { e.preventDefault(); select(); }
            }} />
          <button aria-label="Close model picker" className="p-1 cursor-pointer" onClick={() => close(false)}><X size={16} /></button>
        </div>
        {matches ? (
          <button className="flex items-center gap-3 w-full px-4 py-4 text-sm text-left cursor-pointer" onClick={select}>
            <Cloud size={16} style={{ color: 'var(--color-accent)' }} />
            <span className="flex-1">60db-tiny</span>
            {selectedModel === '60db-tiny' && <Check size={16} aria-label="Active" />}
          </button>
        ) : <p className="px-4 py-6 text-sm">No matching 60db models.</p>}
        <p className="px-4 pb-4 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>Manage your 60db API key and voice in Settings.</p>
      </div>
    </div>
  );
}
