import { useNavigate } from 'react-router';
import { KeyRound, Mic, MessageSquare, Volume2 } from 'lucide-react';

export function GetStartedPage() {
  const navigate = useNavigate();
  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6" style={{ color: 'var(--color-text)' }}>
      <div><h1 className="text-2xl font-semibold">Get started with 60db</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--color-text-secondary)' }}>One API key for your daily Jarvis assistant.</p></div>
      <section className="hud-panel p-6">
        <h2 className="flex items-center gap-2 font-medium mb-4"><KeyRound size={18} /> Connect 60db</h2>
        <ol className="list-decimal pl-5 space-y-3 text-sm">
          <li>Get your API key from <a href="https://app.60db.ai" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-accent)' }}>60db</a>.</li>
          <li>Open Settings and enter your key under “Jarvis with 60db”.</li>
          <li>Load voices, choose your voice, then save and connect.</li>
        </ol>
        <button className="mt-5 px-4 py-2 rounded-lg text-sm cursor-pointer" style={{ background: 'var(--color-accent)', color: 'var(--color-on-accent)' }} onClick={() => navigate('/settings')}>Open Settings</button>
      </section>
      <section className="hud-panel p-6 space-y-4">
        <h2 className="font-medium">Use Jarvis every day</h2>
        <p className="flex items-center gap-2 text-sm"><MessageSquare size={16} /> Send a message for a 60db answer.</p>
        <p className="flex items-center gap-2 text-sm"><Mic size={16} /> Use the microphone to dictate. Allow microphone access when prompted.</p>
        <p className="flex items-center gap-2 text-sm"><Volume2 size={16} /> Choose Read aloud to hear an answer in your selected 60db voice.</p>
        <p className="text-sm">Use Judge on an answer to evaluate it with 60db.</p>
        <button className="px-4 py-2 rounded-lg text-sm cursor-pointer" style={{ background: 'var(--color-accent)', color: 'var(--color-on-accent)' }} onClick={() => navigate('/')}>Start chatting</button>
      </section>
      <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>Your API key stays on this computer. 60db processes your prompts and audio.</p>
      <a href="https://docs.60db.ai/introduction" target="_blank" rel="noopener noreferrer" className="text-sm" style={{ color: 'var(--color-accent)' }}>60db documentation</a>
    </div>
  );
}
