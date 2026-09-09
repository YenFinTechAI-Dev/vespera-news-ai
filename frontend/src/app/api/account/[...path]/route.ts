import { NextRequest, NextResponse } from 'next/server';
export const dynamic='force-dynamic';
async function proxy(req:NextRequest,{params}:{params:{path:string[]}}){
 const path=params.path.join('/');
 const allowed=(req.method==='GET'&&path==='me')||(req.method==='POST'&&['register','login','logout'].includes(path));
 if(!allowed)return NextResponse.json({detail:'Not found'},{status:404});
 if(req.method!=='GET'&&req.headers.get('origin')&&req.headers.get('origin')!==req.nextUrl.origin)return NextResponse.json({detail:'Invalid origin'},{status:403});
 const token=process.env.CHAT_PROXY_TOKEN;
 if(!token)return NextResponse.json({detail:'Gateway unavailable'},{status:503});
 try{
  const body=req.method==='POST'?await req.text():undefined;
  if(body&&body.length>4000)return NextResponse.json({detail:'Request too large'},{status:413});
  const result=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/account/${path}`,{method:req.method,headers:{'Content-Type':'application/json','X-Chat-Token':token,'X-Session-Token':req.cookies.get('vesper_session')?.value||'','X-Client-Key':req.headers.get('x-forwarded-for')?.split(',')[0]||'local'},body,cache:'no-store',signal:AbortSignal.timeout(20000)});
  const data=await result.json();const session=data.session_token;delete data.session_token;
  const response=NextResponse.json(data,{status:result.status});
  if(session)response.cookies.set('vesper_session',session,{httpOnly:true,sameSite:'lax',secure:req.nextUrl.protocol==='https:',path:'/',maxAge:7*86400});
  if(path==='logout'&&result.ok)response.cookies.set('vesper_session','',{httpOnly:true,sameSite:'lax',path:'/',maxAge:0});
  return response;
 }catch{return NextResponse.json({detail:'Không kết nối được dịch vụ tài khoản.'},{status:503})}
}
export {proxy as GET,proxy as POST,proxy as DELETE};
