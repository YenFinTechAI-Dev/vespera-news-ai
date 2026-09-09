/** Validate browser origins against the public deployment URL, not proxy headers. */
export function isAllowedOrigin(request: { headers: Headers; nextUrl: { origin: string } }, allowMissing = false): boolean {
  const origin = request.headers.get('origin');
  if (!origin) return allowMissing;
  const expected = process.env.APP_PUBLIC_URL || process.env.RENDER_EXTERNAL_URL || request.nextUrl.origin;
  try { return origin === new URL(expected).origin; } catch { return false; }
}
