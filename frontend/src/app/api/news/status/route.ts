import { NextResponse } from 'next/server';
export const dynamic='force-dynamic';
export async function GET(){try{const r=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/news/status`,{cache:'no-store',signal:AbortSignal.timeout(15000)});return NextResponse.json(await r.json(),{status:r.status})}catch{return NextResponse.json({detail:'News status unavailable'},{status:503})}}
