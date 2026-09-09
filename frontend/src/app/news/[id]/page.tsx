import NewsView from "@/components/news/NewsView";
export default function Page({params}:{params:{id:string}}){return <NewsView id={params.id}/>;}
