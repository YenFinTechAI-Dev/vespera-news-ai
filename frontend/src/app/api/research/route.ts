import {isAllowedOrigin} from '@/lib/request-origin';
import {NextRequest,NextResponse} from 'next/server';
import {createHmac,randomBytes} from 'node:crypto';
export const dynamic='force-dynamic';
export async function POST(req:NextRequest){
 if(!isAllowedOrigin(req))return NextResponse.json({detail:'Invalid origin'},{status:403});
 const key=process.env.CHAT_PROXY_TOKEN;
 if(!key)return NextResponse.json({detail:'Dịch vụ chưa cấu hình.'},{status:503});
 const hash=(value:string)=>createHmac('sha256',key).update(value).digest('hex');
 const cookie=req.cookies.get('vesper_guest')?.value||'';
 const [oldId,signature]=cookie.split('.');
 const valid=/^[a-f0-9]{64}$/.test(oldId||'')&&/^[a-f0-9]{64}$/.test(signature||'')&&signature===hash('cookie:'+oldId);
 const id=valid?oldId:randomBytes(32).toString('hex');
 const finish=(data:unknown,status:number)=>{
   const response=NextResponse.json(data,{status,headers:{'Cache-Control':'no-store'}});
   if(!valid)response.cookies.set('vesper_guest',id+'.'+hash('cookie:'+id),{httpOnly:true,secure:process.env.NODE_ENV==='production',sameSite:'lax',path:'/',maxAge:31536000});
   return response;
 };
 try{
  const body=await req.text();if(body.length>5000)return finish({detail:'Request too large'},413);
  const r=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/research/synthesize`,{method:'POST',headers:{'Content-Type':'application/json','X-Chat-Token':key,'X-Session-Token':req.cookies.get('vesper_session')?.value||'','X-Guest-Key':hash('guest:'+id),'X-Client-Key':hash('ip:'+(req.headers.get('x-forwarded-for')?.split(',').pop()?.trim()||'unknown'))},body,cache:'no-store',signal:AbortSignal.timeout(240000)});
  return finish(await r.json(),r.status);
 }catch{return finish({detail:'Kết nối bị gián đoạn. Nguồn đã tìm vẫn được giữ; hãy thử lại.'},503)}
}
