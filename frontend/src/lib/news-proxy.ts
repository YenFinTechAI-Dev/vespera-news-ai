import { NextRequest, NextResponse } from "next/server";
export const dynamic = "force-dynamic";
export async function proxyNews(request:NextRequest, id?:string) {
 if(id&&!/^[0-9a-f-]{36}$/i.test(id))return NextResponse.json({detail:"Invalid article ID"},{status:400});
 const base=process.env.BACKEND_URL||"http://127.0.0.1:8001";
 const url=new URL(`/news${id?'/'+id:''}`,base);
 for(const key of ['language','category','limit','offset','q','period','source']){const value=request.nextUrl.searchParams.get(key);if(value!==null)url.searchParams.set(key,value)}
 try{const response=await fetch(url,{cache:'no-store',signal:AbortSignal.timeout(15000)});const data=await response.json();return NextResponse.json(data,{status:response.status});}
 catch{return NextResponse.json({detail:"News service unavailable"},{status:503})}
}
