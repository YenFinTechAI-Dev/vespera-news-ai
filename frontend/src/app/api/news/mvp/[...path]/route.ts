import {isAllowedOrigin} from '@/lib/request-origin';
import {NextRequest,NextResponse} from 'next/server';
export const dynamic='force-dynamic';
async function proxy(req:NextRequest,{params}:{params:{path:string[]}}){
 const path=params.path.join('/');
 const allowed:Record<string,string[]>={sources:['GET'],stories:['GET'],interests:['GET','POST','DELETE'],digest:['GET'],email:['GET','PUT'],ask:['POST']};
 if(!allowed[path]?.includes(req.method))return NextResponse.json({detail:'Not found'},{status:404});
 if(req.method!=='GET'&&!isAllowedOrigin(req))return NextResponse.json({detail:'Invalid origin'},{status:403});
 const publicRoute=path==='sources'||path==='stories';
 const session=req.cookies.get('vesper_session')?.value;
 if(!publicRoute&&!session)return NextResponse.json({detail:'Sign in required'},{status:401});
 if(!publicRoute&&!process.env.CHAT_PROXY_TOKEN)return NextResponse.json({detail:'Gateway unavailable'},{status:503});
 try{
  const body=req.method==='GET'?undefined:await req.text();
  if(body&&body.length>5000)return NextResponse.json({detail:'Request too large'},{status:413});
  const r=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/news/mvp/${path}${req.nextUrl.search}`,{method:req.method,headers:{'Content-Type':'application/json',...(!publicRoute?{'X-Chat-Token':process.env.CHAT_PROXY_TOKEN!,'X-Session-Token':session!}:{})},body,cache:'no-store',signal:AbortSignal.timeout(240000)});
  return NextResponse.json(await r.json(),{status:r.status,headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({detail:'News service unavailable'},{status:503})}
}
export {proxy as GET,proxy as POST,proxy as PUT,proxy as DELETE};

