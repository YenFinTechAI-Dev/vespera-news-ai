'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {useLocale} from '@/components/ui/Language';
type Note={query:string;content:string;saved_at:string};
type Article={id:string;title:string;summary?:string;source_name?:string;source_url?:string};
export default function Notes(){
 const vi=useLocale()==='vi';const [notes,setNotes]=useState<Note[]>([]);const [articles,setArticles]=useState<Article[]>([]);const [ready,setReady]=useState(false);const [failed,setFailed]=useState(false);
 useEffect(()=>{
  function load(){let error=false;
   try{const value=JSON.parse(localStorage.getItem('vesper-research-notes')||'[]');setNotes(Array.isArray(value)?value.filter(x=>typeof x?.query==='string'&&typeof x?.content==='string'&&typeof x?.saved_at==='string'):[])}catch{error=true}
   try{const value=JSON.parse(localStorage.getItem('vesper-news-saved')||'[]');setArticles(Array.isArray(value)?value.filter(x=>typeof x?.id==='string'&&typeof x?.title==='string'):[])}catch{error=true}
   setFailed(error);setReady(true);
  }
  load();window.addEventListener('storage',load);window.addEventListener('focus',load);
  return()=>{window.removeEventListener('storage',load);window.removeEventListener('focus',load)};
 },[]);
 function download(content:string){const url=URL.createObjectURL(new Blob([content],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='vespersignal-research.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
 function sourceUrl(value?:string){try{const url=new URL(value||'');return ['https:','http:'].includes(url.protocol)?url.href:null}catch{return null}}
 return <main className="min-h-screen bg-base px-6 py-12 text-ink"><div className="mx-auto max-w-3xl">
  <Link href="/news">← {vi?'Trở về tìm kiếm':'Back to search'}</Link>
  <h1 className="my-6 text-3xl font-semibold">{vi?'Thư viện đã lưu':'Saved library'}</h1>
  <p className="mb-8 leading-relaxed text-ink-muted">{vi?'Bài báo bạn bấm “Lưu bài” và ghi chú nghiên cứu đều nằm ở đây. Dữ liệu lưu trên trình duyệt này; bạn có thể xuất file để giữ một bản riêng.':'Your bookmarked articles and research notes live here. Data is stored in this browser; export a file to keep a separate copy.'}</p>
  {failed&&<p role="alert" className="mb-6">{vi?'Không đọc được một phần dữ liệu đã lưu trên trình duyệt.':'Some browser data could not be read.'}</p>}
  {!ready&&<p role="status">{vi?'Đang đọc thư viện…':'Loading library…'}</p>}
  {ready&&!failed&&!articles.length&&!notes.length&&<div className="mb-8 rounded-2xl border border-stroke p-6"><p>{vi?'Trình duyệt này chưa có bài hoặc ghi chú đã lưu.':'No saved articles or notes in this browser yet.'}</p><p className="mt-3 text-sm text-ink-muted">{vi?'Nếu đã lưu ở Edge/Chrome, hãy mở trang này trong đúng trình duyệt đó và cùng địa chỉ localhost:3003. Dữ liệu chưa đồng bộ giữa các trình duyệt.':'If you saved in Edge or Chrome, open this page in that browser at the same localhost:3003 address. Data does not sync across browsers.'}</p><Link href="/news" className="mt-4 inline-block underline">{vi?'Tìm bài để lưu':'Find an article to save'} →</Link></div>}
  <section aria-labelledby="saved-articles"><h2 id="saved-articles" className="mb-5 text-xl font-semibold">{vi?'Bài báo đã lưu':'Saved articles'} ({articles.length})</h2>
   {ready&&!articles.length&&<p className="mb-8 text-sm text-ink-muted">{vi?'Bấm biểu tượng đánh dấu hoặc “Lưu bài” trong bài báo để thêm vào đây.':'Bookmark an article to add it here.'}</p>}
   {articles.map(a=><article key={a.id} className="mb-5 rounded-2xl border border-stroke p-6"><p className="mb-3 text-xs text-ink-muted">{a.source_name}</p><Link href={'/news/'+encodeURIComponent(a.id)}><h3 className="text-xl font-semibold hover:underline">{a.title}</h3></Link>{a.summary&&<p className="mt-4 text-sm leading-relaxed text-ink-muted">{a.summary}</p>}<div className="mt-5 flex flex-wrap items-center gap-4 text-sm"><Link className="underline" href={'/news/'+encodeURIComponent(a.id)}>{vi?'Mở bài':'Read article'}</Link>{sourceUrl(a.source_url)&&<a className="underline" href={sourceUrl(a.source_url)!} target="_blank" rel="noopener noreferrer">{vi?'Nguồn gốc':'Original source'} ↗</a>}<button className="rounded-lg border border-stroke px-4 py-2" onClick={()=>download(`# ${a.title}\n\n${a.summary||''}\n\n${a.source_name||''}\n${sourceUrl(a.source_url)||''}`)}>{vi?'Tải Markdown':'Download Markdown'}</button></div></article>)}
  </section>
  <section aria-labelledby="saved-notes" className="mt-10"><h2 id="saved-notes" className="mb-5 text-xl font-semibold">{vi?'Ghi chú nghiên cứu':'Research notes'} ({notes.length})</h2>
   {ready&&!notes.length&&<p className="mb-8 text-sm text-ink-muted">{vi?'Chưa có ghi chú tổng hợp. Các bài đã đánh dấu hiển thị ở phần Bài báo đã lưu phía trên.':'No research notes yet. Bookmarked articles appear above.'}</p>}
   {notes.map((n,i)=><article key={n.saved_at+i} className="mb-5 rounded-2xl border border-stroke p-6"><h3 className="text-xl font-semibold">{n.query}</h3><p className="my-3 text-xs text-ink-muted">{new Date(n.saved_at).toLocaleString()}</p><details><summary className="cursor-pointer">{vi?'Xem ghi chú và nguồn':'View note and references'}</summary><pre className="mt-4 whitespace-pre-wrap break-words font-sans text-sm leading-relaxed">{n.content}</pre></details><button onClick={()=>download(n.content)} className="mt-5 rounded-lg border border-stroke px-4 py-2 text-sm">{vi?'Tải Markdown':'Download Markdown'}</button></article>)}
  </section>
 </div></main>;
}
