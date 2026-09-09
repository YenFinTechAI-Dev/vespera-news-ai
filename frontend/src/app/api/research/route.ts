import {NextRequest,NextResponse} from 'next/server';
export const dynamic='force-dynamic';
export async function POST(req:NextRequest){
 if(req.headers.get('origin')!==req.nextUrl.origin)return NextResponse.json({detail:'Invalid origin'},{status:403});
 const session=req.cookies.get('vesper_session')?.value;
 if(!session)return NextResponse.json({detail:'Đăng nhập để tổng hợp AI và dùng hạn mức tài khoản.'},{status:401});
 if(!process.env.CHAT_PROXY_TOKEN)return NextResponse.json({detail:'Dịch vụ chưa cấu hình.'},{status:503});
 try{
  const body=await req.text();if(body.length>5000)return NextResponse.json({detail:'Request too large'},{status:413});
  const r=await fetch(`${process.env.BACKEND_URL||'http://127.0.0.1:8001'}/research/synthesize`,{method:'POST',headers:{'Content-Type':'application/json','X-Chat-Token':process.env.CHAT_PROXY_TOKEN,'X-Session-Token':session},body,cache:'no-store',signal:AbortSignal.timeout(240000)});
  return NextResponse.json(await r.json(),{status:r.status,headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({detail:'Kết nối bị gián đoạn. Nguồn đã tìm vẫn được giữ; hãy thử lại.'},{status:503})}
}
