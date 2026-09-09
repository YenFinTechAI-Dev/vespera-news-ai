import json
"""Topic search across Google News publishers. Feed previews only; no full-text claim."""
import time
import threading
import xml.etree.ElementTree as ET
from collections import OrderedDict
from datetime import datetime,timezone
from urllib.parse import urlsplit,urlunsplit
import requests
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from typing import Literal
from database import connection,DatabaseUnavailable
from discovery_sources import aggregate,search_text
from rss_importer import plain,parse_date

router=APIRouter(prefix='/news')
cache=OrderedDict();lock=threading.Lock();semaphore=threading.BoundedSemaphore(2);attempts=[]
class Search(BaseModel):
    query:str=Field(min_length=2,max_length=120)
    language:Literal['vi','en']='vi'
    mode:Literal['all','news','web','research']='all'

def parse_results(content):
    if len(content)>2_000_000 or b'<!ENTITY' in content.upper():raise ValueError('Invalid feed')
    root=ET.fromstring(content)
    if root.tag!='rss':raise ValueError('Invalid feed')
    result=[];seen=set()
    for item in root.findall('./channel/item')[:30]:
        try:
            url=urlsplit(item.findtext('link',''))
            if url.scheme!='https' or url.hostname!='news.google.com' or url.username or url.password:continue
            link=urlunsplit(('https','news.google.com',url.path,'',''))
            title=plain(item.findtext('title',''))[:400]
            published=parse_date(item.findtext('pubDate',''))
            if not title or link in seen or published>datetime.now(timezone.utc):continue
            seen.add(link)
            publisher=plain(item.findtext('source','Publisher'))[:100]
            # Google News descriptions frequently repeat the title and do not contain an abstract.
            result.append(dict(url=link,title=title,summary=plain(item.findtext('description',''))[:900] or title,publisher=publisher,published=published))
        except (ValueError,TypeError,OverflowError):continue
    return result

def fetch_results(query,language):
    topic=search_text(query)
    params={'q':topic,'hl':'vi' if language=='vi' else 'en-US','gl':'VN' if language=='vi' else 'US','ceid':'VN:vi' if language=='vi' else 'US:en'}
    with requests.get('https://news.google.com/rss/search',params=params,timeout=(5,15),stream=True) as response:
        response.raise_for_status();chunks=[];size=0
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>2_000_000:raise ValueError('Feed too large')
            chunks.append(chunk)
    return parse_results(b''.join(chunks))

def search_topic(body):
    query=' '.join(body.query.split())
    if len(query)<2:raise HTTPException(422,'Nhập ít nhất 2 ký tự.')
    key=(query.casefold(),body.language,body.mode);now=time.monotonic()
    with lock:
        hit=cache.get(key)
        while attempts and attempts[0]<now-60:attempts.pop(0)
        if not hit or now-hit['at']>900:
            if len(attempts)>=12:raise HTTPException(429,'Vui lòng chờ một phút trước khi tìm tiếp.')
            attempts.append(now);hit=None
    if not hit:
        if not semaphore.acquire(blocking=False):raise HTTPException(429,'Đang xử lý tìm kiếm khác, hãy thử lại sau.')
        try:
            entries,source_status=aggregate(query,body.language,body.mode,fetch_results)
            if all(value=='unavailable' for value in source_status.values()):raise HTTPException(502,'Các nguồn tìm kiếm đang không phản hồi. Hãy thử lại.')
            ids=[]
            with connection() as conn:
                for item in entries:
                    row=conn.execute("INSERT INTO news_articles(source_name,source_url,original_title,category,published_at,status,source_language) VALUES(%s,%s,%s,'web',%s,'published',%s) ON CONFLICT(source_url) DO UPDATE SET source_url=EXCLUDED.source_url RETURNING id",
                        [item['publisher']+(' · Google News' if item['kind']=='news' else ''),item['url'],item['title'],item['published'] or datetime.now(timezone.utc),body.language]).fetchone()
                    ids.append(row['id'])
                    conn.execute('UPDATE news_articles SET discovery_kind=%s,publication_date_unknown=%s,discovery_evidence=%s::jsonb WHERE id=%s',[item['kind'],item['published'] is None,json.dumps({'excerpt':item['summary'],'authors':item.get('authors',[])}),row['id']])
                    conn.execute('''INSERT INTO news_summaries(article_id,language,title,summary,ai_generated) VALUES(%s,%s,%s,%s,false) ON CONFLICT(article_id,language) DO NOTHING''',[row['id'],body.language,item['title'],item['summary']])
                    conn.execute('INSERT INTO news_ai_jobs(article_id,priority_at) VALUES(%s,%s) ON CONFLICT(article_id) DO NOTHING',[row['id'],item['published'] or datetime.now(timezone.utc)])
            hit=dict(at=now,ids=ids,source_status=source_status,checked=datetime.now(timezone.utc).isoformat())
            with lock:
                cache[key]=hit;cache.move_to_end(key)
                while len(cache)>100:cache.popitem(last=False)
        except (requests.RequestException,ET.ParseError,ValueError):raise HTTPException(502,'Nguồn tìm kiếm tạm không phản hồi. Hãy thử lại.') from None
        finally:semaphore.release()
    with connection() as conn:
        items=conn.execute('''SELECT a.id,a.source_name,a.source_url,CASE WHEN a.publication_date_unknown THEN NULL ELSE a.published_at END AS published_at,a.discovery_kind,COALESCE(a.discovery_evidence->'authors','[]'::jsonb) AS authors,s.title,s.summary,s.ai_generated,s.language
          FROM news_articles a JOIN LATERAL(SELECT * FROM news_summaries ns WHERE ns.article_id=a.id ORDER BY(ns.language=%s) DESC LIMIT 1)s ON true
          WHERE a.id=ANY(%s) AND a.status='published' ORDER BY array_position(%s::uuid[],a.id)''',[body.language,hit['ids'],hit['ids']]).fetchall()
    return dict(query=query,items=items,checked_at=hit['checked'],refresh_seconds=900,source_status=hit['source_status'],mode=body.mode)

@router.post('/discover')
def discover(body:Search):
    try:return search_topic(body)
    except DatabaseUnavailable:raise HTTPException(503,'Chưa kết nối được kho tin.') from None
