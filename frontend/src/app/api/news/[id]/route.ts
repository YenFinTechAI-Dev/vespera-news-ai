import {NextRequest} from "next/server";
import {proxyNews} from "@/lib/news-proxy";
export const dynamic="force-dynamic";
export function GET(req:NextRequest,{params}:{params:{id:string}}){return proxyNews(req,params.id);}
