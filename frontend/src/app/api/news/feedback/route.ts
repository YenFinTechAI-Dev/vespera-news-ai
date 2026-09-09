import {NextRequest,NextResponse} from 'next/server';
import {createHash} from 'node:crypto';
export async function POST(req:NextRequest){
 if(req.headers.get('origin')!==req.nextUrl.origin)return NextResponse.json({detail:'Invalid origin'},{status:403});
 const key=process.env.CHAT_PROXY_TOKEN;
 if(!key)return NextResponse.json({detail:'Unavailable'},{status:503});
 try{const body=await req.text();if(body.length>12000)return NextResponse.json({detail:'Too large'},{status:413});
 const client=createHash('sha256').update(key+'|'+(req.headers.get('x-forwarded-for')?.split(',')[0]||'local')).digest('hex');
 const r=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/news/feedback`,{method:'POST',headers:{'Content-Type':'application/json','X-Chat-Token':key,'X-Client-Key':client},body,signal:AbortSignal.timeout(15000),cache:'no-store'});
 return NextResponse.json(await r.json(),{status:r.status});
 }catch{return NextResponse.json({detail:'Unavailable'},{status:503})}
}
