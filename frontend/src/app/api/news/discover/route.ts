import {NextRequest,NextResponse} from 'next/server';
export const dynamic='force-dynamic';
export async function POST(req:NextRequest){
 if(req.headers.get('origin')&&req.headers.get('origin')!==req.nextUrl.origin)return NextResponse.json({detail:'Invalid origin'},{status:403});
 try{const text=await req.text();if(text.length>1000)return NextResponse.json({detail:'Query too long'},{status:413});JSON.parse(text);
 const r=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/news/discover`,{method:'POST',headers:{'Content-Type':'application/json'},body:text,cache:'no-store',signal:AbortSignal.timeout(25000)});
 return NextResponse.json(await r.json(),{status:r.status});
 }catch{return NextResponse.json({detail:'Chưa kết nối được tìm kiếm. Hãy thử lại.'},{status:503})}
}
