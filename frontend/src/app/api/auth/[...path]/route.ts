import { NextRequest, NextResponse } from 'next/server';
import { timingSafeEqual } from 'crypto';
export const dynamic = 'force-dynamic';
const providers = ['google', 'facebook', 'github'];
function same(a: string, b: string) { return !!a && a.length === b.length && timingSafeEqual(Buffer.from(a), Buffer.from(b)); }
export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) { return handle(req, params.path); }
export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) { return handle(req, params.path); }
async function handle(req: NextRequest, path: string[]) {
  const [provider, action] = path;
  const isConfig = path.length === 1 && provider === 'config' && req.method === 'GET';
  const isCallback = path.length === 2 && action === 'callback' && req.method === 'GET' && provider !== 'google';
  if (!isConfig && !(path.length === 2 && providers.includes(provider) && (isCallback || (req.method === 'POST' && ['start', 'complete'].includes(action))))) return NextResponse.json({ detail: 'Not found' }, { status: 404 });
  if (req.method === 'POST' && req.headers.get('origin') !== req.nextUrl.origin) return NextResponse.json({ detail: 'Invalid origin' }, { status: 403 });
  const cookieName = 'vesper_oauth_' + provider;
  const options = { httpOnly: true, sameSite: 'lax' as const, secure: req.nextUrl.protocol === 'https:', path: '/' };
  function failure(message: string, status = 400) {
    const response = isCallback ? NextResponse.redirect(new URL('/login?auth_error=' + encodeURIComponent(message), req.nextUrl.origin)) : NextResponse.json({ detail: message }, { status });
    if (action !== 'start') response.cookies.set(cookieName, '', { ...options, maxAge: 0 });
    return response;
  }
  try {
    if (!process.env.CHAT_PROXY_TOKEN) return failure('Dịch vụ đăng nhập chưa sẵn sàng.', 503);
    let body: Record<string, string> = {};
    if (action === 'complete' || isCallback) {
      if (isCallback) body = { state: req.nextUrl.searchParams.get('state') || '', code: req.nextUrl.searchParams.get('code') || '' };
      else {
        const raw = await req.text();
        if (raw.length > 12000) return failure('Request too large', 413);
        const input = JSON.parse(raw);
        body = { state: req.cookies.get(cookieName)?.value || '', credential: typeof input.credential === 'string' ? input.credential : '' };
      }
      if (!same(body.state, req.cookies.get(cookieName)?.value || '')) return failure('Phiên đăng nhập hết hạn. Vui lòng thử lại.', 401);
      if (isCallback && !body.code) return failure('Bạn đã hủy đăng nhập hoặc chưa cấp quyền.');
    }
    const endpoint = isConfig ? 'config' : provider + '/' + (isCallback ? 'complete' : action);
    const result = await fetch(`${process.env.BACKEND_URL || 'http://127.0.0.1:8001'}/account/social/${endpoint}`, {
      method: isConfig ? 'GET' : 'POST', cache: 'no-store', signal: AbortSignal.timeout(45000),
      headers: { 'Content-Type': 'application/json', 'X-Chat-Token': process.env.CHAT_PROXY_TOKEN, 'X-Client-Key': req.headers.get('x-forwarded-for')?.split(',')[0] || 'local' },
      body: isConfig ? undefined : JSON.stringify(body),
    });
    const data = await result.json();
    if (!result.ok) return failure(typeof data.detail === 'string' ? data.detail : 'Không thể đăng nhập.', result.status);
    const session = data.session_token; delete data.session_token;
    const state = data.state; delete data.state;
    const response = isCallback ? NextResponse.redirect(new URL('/news', req.nextUrl.origin)) : NextResponse.json(data);
    response.headers.set('Cache-Control', 'no-store');
    if (action === 'start') response.cookies.set(cookieName, state, { ...options, maxAge: 600 });
    if (session) {
      response.cookies.set('vesper_session', session, { ...options, maxAge: 7 * 86400 });
      response.cookies.set(cookieName, '', { ...options, maxAge: 0 });
    }
    return response;
  } catch { return failure('Không kết nối được dịch vụ đăng nhập. Vui lòng thử lại.', 503); }
}
