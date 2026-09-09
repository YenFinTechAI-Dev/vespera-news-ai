'use client';
import Script from 'next/script';
import { useEffect, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { useLocale } from '@/components/ui/Language';

type GoogleSDK = { accounts: { id: {
  initialize: (options: { client_id: string; nonce: string; callback: (result: { credential: string }) => void }) => void;
  renderButton: (element: HTMLElement, options: Record<string, string | number>) => void;
} } };
declare global { interface Window { google?: GoogleSDK } }
export function SocialLogin() {
  const locale = useLocale();
  const vi = locale === 'vi';
  const [config, setConfig] = useState<Record<string, boolean> | null>(null);
  const [sdk, setSdk] = useState(false);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const googleButton = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const queryError = new URLSearchParams(window.location.search).get('auth_error');
    if (queryError) { setError(queryError); window.history.replaceState(null, '', window.location.pathname); }
    fetch('/api/auth/config').then(async r => { if (!r.ok) throw new Error(); setConfig(await r.json()); }).catch(() => setError(vi ? 'Chưa kết nối được dịch vụ đăng nhập.' : 'Sign-in service is unavailable.'));
  }, [retry, vi]);
  useEffect(() => {
    if (!sdk || !config?.google || !googleButton.current) return;
    let active = true;
    fetch('/api/auth/google/start', { method: 'POST' }).then(async r => {
      const data = await r.json(); if (!r.ok) throw new Error(data.detail);
      if (!active || !googleButton.current || !window.google) return;
      window.google.accounts.id.initialize({ client_id: data.client_id, nonce: data.nonce, callback: async ({ credential }) => {
        setBusy('google'); setError('');
        try {
          const response = await fetch('/api/auth/google/complete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ credential }) });
          const result = await response.json(); if (!response.ok) throw new Error(result.detail);
          window.location.assign('/news');
        } catch (e) { setError(e instanceof Error ? e.message : 'Sign-in failed'); setBusy(''); }
      } });
      googleButton.current.innerHTML = '';
      window.google.accounts.id.renderButton(googleButton.current, { type: 'standard', theme: 'outline', size: 'large', shape: 'pill', text: 'continue_with', width: Math.min(400, googleButton.current.clientWidth || 320), locale });
    }).catch(e => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [sdk, config?.google, locale, retry]);
  async function start(provider: string) {
    setBusy(provider); setError('');
    try {
      const response = await fetch(`/api/auth/${provider}/start`, { method: 'POST' });
      const data = await response.json(); if (!response.ok) throw new Error(data.detail);
      window.location.assign(data.url);
    } catch (e) { setError(e instanceof Error ? e.message : 'Sign-in failed'); setBusy(''); }
  }
  return <div className="flex flex-col gap-3">
    <Script src="https://accounts.google.com/gsi/client" onReady={() => setSdk(true)} onError={() => setError(vi ? 'Không tải được Google. Kiểm tra kết nối rồi thử lại.' : 'Could not load Google Sign-In.')} />
    <div className={busy ? 'pointer-events-none opacity-60' : ''} aria-busy={!!busy}>
      <div ref={googleButton} className="flex min-h-10 w-full justify-center" />
    </div>
    {!config && <p className="text-center text-xs text-ink-muted">{vi ? 'Đang tải các cách đăng nhập…' : 'Loading sign-in options…'}</p>}
    <div className="grid grid-cols-2 gap-3">
      {([['facebook', 'Facebook'], ['github', 'GitHub']] as const).map(([provider, label]) => <button key={provider} type="button" onClick={() => start(provider)} disabled={!config?.[provider] || !!busy} className="flex min-h-12 items-center justify-center gap-2 rounded-xl border border-stroke px-3 py-2 text-sm text-ink transition-colors hover:bg-surface disabled:cursor-not-allowed disabled:opacity-45">
        {busy === provider ? <Loader2 size={17} className="animate-spin" /> : <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d={provider === 'facebook' ? 'M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073c0 6.026 4.388 11.021 10.125 11.927v-8.437H7.078v-3.49h3.047V9.413c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.973H15.83c-1.491 0-1.956.931-1.956 1.887v2.261h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.099 24 12.073z' : 'M12 .297a12 12 0 0 0-3.793 23.385c.6.111.82-.261.82-.577v-2.234c-3.338.726-4.043-1.416-4.043-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.729.083-.729 1.205.085 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.108-.775.419-1.305.762-1.605-2.665-.303-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23a11.5 11.5 0 0 1 6.006 0c2.291-1.552 3.297-1.23 3.297-1.23.654 1.652.243 2.873.119 3.176.769.84 1.235 1.91 1.235 3.221 0 4.609-2.807 5.625-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.216.694.825.576A12 12 0 0 0 12 .297z'} /></svg>}<span>{label}{config && !config[provider] && <small className="block text-[10px] text-ink-muted">{vi ? 'Chưa cấu hình' : 'Not configured'}</small>}</span>
      </button>)}
    </div>
    {busy === 'google' && <p className="text-center text-xs text-ink-muted">{vi ? 'Đang xác minh Google…' : 'Verifying Google…'}</p>}
    {error && <div role="alert" className="rounded-lg border border-risk-critical/30 bg-risk-critical/10 p-3 text-xs text-risk-critical">{error}<button type="button" className="ml-2 underline" onClick={() => { setError(''); setRetry(n => n + 1); }}>{vi ? 'Thử lại' : 'Retry'}</button></div>}
    <div className="my-1 flex items-center gap-3 text-xs text-ink-muted"><span className="h-px flex-1 bg-stroke" />{vi ? 'hoặc đăng nhập bằng email' : 'or sign in with email'}<span className="h-px flex-1 bg-stroke" /></div>
  </div>;
}
