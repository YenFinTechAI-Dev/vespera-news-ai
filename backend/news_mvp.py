"""News MVP services. Source provenance is explicit; clustering is a heuristic."""
import asyncio
import logging
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Literal
from urllib.parse import urlsplit
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from database import connection
from news_sources import SOURCES
from system_api import gateway, identity, throttle
from search_relevance import words, STOP

router=APIRouter(prefix='/news/mvp',tags=['News MVP'])
log=logging.getLogger(__name__)

def current_user(x_chat_token:str|None=Header(None),x_session_token:str|None=Header(None)):
    gateway(x_chat_token)
    return identity(x_session_token)

def provenance(url):
    host=(urlsplit(url).hostname or '').lower()
    for source in SOURCES:
        if host in source['hosts'] or (source.get('subdomains') and any(host.endswith('.'+h) for h in source['hosts'])):
            kind='community' if 'medium' in host else 'preprint' if host=='arxiv.org' else 'primary' if source['id'] in ('sec','ftc','openai','google-ai','deepmind','huggingface','transformers','vllm','ollama') else 'editorial'
            return {'tier':kind,'curated':True,'source_id':source['id'],'verified_claims':False}
    return {'tier':'unreviewed','curated':False,'verified_claims':False}

def load_articles(language,days=7):
    with connection() as conn:
        rows=conn.execute('''SELECT a.id,a.original_title,a.source_name,a.source_url,a.category,
          a.published_at,s.title,s.summary,s.language,s.ai_generated,s.generated_at
          FROM news_articles a JOIN LATERAL(SELECT * FROM news_summaries ns WHERE ns.article_id=a.id
            ORDER BY (ns.language=%s) DESC,ns.ai_generated DESC LIMIT 1)s ON true
          WHERE a.status='published' AND NOT a.publication_date_unknown
          AND a.published_at<=now() AND a.published_at>=now()-(%s * interval '1 day')
          ORDER BY a.published_at DESC,a.id DESC LIMIT 500''',[language,days]).fetchall()
    for row in rows:
        row['provenance']=provenance(row['source_url'])
        row['translation_ready']=row['language']==language and row['ai_generated']
    return rows

def cluster(rows):
    # Same narrow title, same dates, compatible numbers. Avoid transitive merging.
    groups=[]
    for row in rows:
        tokens=words(row['original_title'])-STOP
        numbers={t for t in tokens if t.isdigit()}
        match=None
        for group in groups:
            seed=group['articles'][0]
            seed_tokens=words(seed['original_title'])-STOP
            if abs((row['published_at']-seed['published_at']).total_seconds())>172800:continue
            if row['category']!=seed['category']:continue
            if numbers!={t for t in seed_tokens if t.isdigit()}:continue
            if len(tokens&seed_tokens)>=4 and len(tokens&seed_tokens)/max(1,len(tokens|seed_tokens))>=0.65:
                match=group;break
        if match is None:
            match={'id':str(row['id']),'title':row['title'],'updated_at':row['published_at'],'articles':[],
                   'grouping':'title_similarity_v1','needs_editorial_review':True}
            groups.append(match)
        match['articles'].append(row)
        match['source_count']=len({urlsplit(a['source_url']).hostname for a in match['articles']})
    return groups

@router.get('/sources')
def source_registry():
    return {'sources':[{**s,'provenance':provenance('https://'+s['hosts'][0])} for s in SOURCES],
            'policy':'Curated provenance, not a guarantee of correctness. Preprints and community posts are labeled separately.'}

@router.get('/stories')
def stories(language:Literal['vi','en']='vi',days:int=Query(7,ge=1,le=30),limit:int=Query(30,ge=1,le=100)):
    groups=cluster([r for r in load_articles(language,days) if r['provenance']['tier']!='unreviewed'])
    return {'items':groups[:limit],'total':len(groups),'retrieved_at':datetime.now(timezone.utc),
            'scope':'Up to 500 recent articles. Conservative same-language title grouping; not semantic event verification.'}

class Interest(BaseModel):
    kind:Literal['topic','company','industry']
    term:str=Field(min_length=2,max_length=100)

@router.get('/interests')
def interests(user=Depends(current_user)):
    with connection() as conn:
        return {'items':conn.execute('SELECT kind,term,created_at FROM news_interests WHERE user_id=%s ORDER BY created_at',[user['id']]).fetchall()}

@router.post('/interests')
def follow(body:Interest,user=Depends(current_user)):
    term=' '.join(body.term.split()).lower()
    if len(term)<2:raise HTTPException(422,'Topic must have at least two characters')
    with connection() as conn:
        conn.execute('SELECT id FROM app_users WHERE id=%s FOR UPDATE',[user['id']])
        count=conn.execute('SELECT count(*) AS n FROM news_interests WHERE user_id=%s',[user['id']]).fetchone()['n']
        if count>=30:raise HTTPException(409,'Maximum 30 interests')
        conn.execute('INSERT INTO news_interests(user_id,kind,term) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING',[user['id'],body.kind,term])
    return {'status':'following','kind':body.kind,'term':term}

@router.delete('/interests')
def unfollow(body:Interest,user=Depends(current_user)):
    with connection() as conn:
        conn.execute('DELETE FROM news_interests WHERE user_id=%s AND kind=%s AND term=%s',[user['id'],body.kind,' '.join(body.term.split()).lower()])
    return {'status':'removed'}

def match_interest(row,interest):
    needle=words(interest['term'])-STOP
    if not needle:return False
    haystack=words(row['original_title']+' '+row['title']+' '+row['summary']+' '+row['category'])
    return needle<=haystack

def build_digest(user,language):
    tracked=interests(user)['items']
    rows=[r for r in load_articles(language) if r['provenance']['tier'] in ('primary','editorial','preprint')
          and any(match_interest(r,t) for t in tracked)]
    groups=cluster(rows)[:10]
    lines=['Bản tin VesperSignal' if language=='vi' else 'VesperSignal briefing']
    for group in groups:
        item=group['articles'][0]
        lines.extend(['',item['title'],item['summary'][:900],
            ('Tóm tắt AI' if language=='vi' else 'AI summary') if item['ai_generated'] else ('Trích đoạn nguồn' if language=='vi' else 'Source excerpt'),
            str(item['published_at']),item['source_name'],item['source_url']])
    return {'stories':groups,'text':'\n'.join(lines),'generated_at':datetime.now(timezone.utc),
            'language':language,'interest_count':len(tracked),'status':'ready' if groups else 'no_matching_news'}

@router.get('/digest')
def digest(language:Literal['vi','en']='vi',user=Depends(current_user)):
    return build_digest(user,language)

class Subscription(BaseModel):
    enabled:bool=False
    language:Literal['vi','en']='vi'

def email_configured():
    return bool(os.getenv('NEWS_SMTP_HOST') and os.getenv('NEWS_SMTP_FROM') and os.getenv('NEWS_SMTP_USER') and os.getenv('NEWS_SMTP_PASSWORD'))

@router.get('/email')
def email_preferences(user=Depends(current_user)):
    with connection() as conn:
        row=conn.execute('SELECT enabled,language FROM news_digest_preferences WHERE user_id=%s',[user['id']]).fetchone()
    return {'subscription':row or {'enabled':False,'language':'vi'},'configured':email_configured(),
            'delivery_enabled':os.getenv('NEWS_EMAIL_DELIVERY_ENABLED')=='true','recipient':user['email']}

@router.put('/email')
def subscribe(body:Subscription,user=Depends(current_user)):
    # Delivery is additionally operator-gated; signup email alone is not proof of ownership.
    if body.enabled and user['email'].lower()!=os.getenv('NEWS_EMAIL_ALLOWED_RECIPIENT','').lower():
        raise HTTPException(409,'Recipient must first be approved in NEWS_EMAIL_ALLOWED_RECIPIENT for this local MVP')
    with connection() as conn:
        conn.execute('''INSERT INTO news_digest_preferences(user_id,enabled,language) VALUES(%s,%s,%s)
          ON CONFLICT(user_id) DO UPDATE SET enabled=EXCLUDED.enabled,language=EXCLUDED.language,updated_at=now()''',[user['id'],body.enabled,body.language])
    return email_preferences(user)

class NewsQuestion(BaseModel):
    question:str=Field(min_length=3,max_length=500)
    language:Literal['vi','en']='vi'

@router.post('/ask')
def ask(body:NewsQuestion,user=Depends(current_user)):
    from research_api import Question,run
    throttle('news-ask:'+str(user['id']))
    tokens=words(body.question)-STOP
    rows=load_articles(body.language,30)
    ranked=sorted([(len(tokens&(words(r['original_title']+' '+r['summary'])-STOP)),r) for r in rows
                   if r['provenance']['tier']!='unreviewed'],key=lambda item:item[0],reverse=True)
    ids=[r['id'] for score,r in ranked if score>=min(2,max(1,len(tokens)))][:8]
    if len(ids)<2:return {'status':'insufficient_sources','sources':[], 'detail':'Not enough relevant collected sources to answer.'}
    result=run(Question(query=body.question,language=body.language,source_ids=ids),user)
    result['retrieved_at']=datetime.now(timezone.utc)
    result['retrieval_scope']='500 most recent dated articles within 30 days'
    return result

def deliver_daily():
    if os.getenv('NEWS_EMAIL_DELIVERY_ENABLED')!='true' or not email_configured():return
    recipient=os.getenv('NEWS_EMAIL_ALLOWED_RECIPIENT','').lower()
    if not recipient:return
    with connection() as conn:
        users=conn.execute('''SELECT u.id,u.email,p.language FROM app_users u JOIN news_digest_preferences p ON p.user_id=u.id
          WHERE p.enabled AND lower(u.email)=%s''',[recipient]).fetchall()
    for user in users:
        digest=build_digest(user,user['language'])
        if not digest['stories']:continue
        with connection() as conn:
            row=conn.execute('''INSERT INTO news_email_outbox(user_id,day,status,subject,body)
              VALUES(%s,(now() AT TIME ZONE 'Asia/Bangkok')::date,'pending',%s,%s)
              ON CONFLICT(user_id,day) DO NOTHING RETURNING id''',[user['id'],'VesperSignal daily briefing',digest['text']]).fetchone()
            if not row:continue
            conn.execute("UPDATE news_email_outbox SET status='sending' WHERE id=%s",[row['id']])
        message=EmailMessage();message['Subject']='VesperSignal daily briefing'
        message['From']=os.environ['NEWS_SMTP_FROM'];message['To']=user['email']
        message['Message-ID']=f"<{row['id']}@vespersignal.local>"
        message.set_content(digest['text']+'\n\nDisable the subscription through your News email preferences.')
        outcome='uncertain'
        try:
            with smtplib.SMTP(os.environ['NEWS_SMTP_HOST'],int(os.getenv('NEWS_SMTP_PORT','587')),timeout=25) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(os.environ['NEWS_SMTP_USER'],os.environ['NEWS_SMTP_PASSWORD'])
                smtp.send_message(message)
            outcome='sent'
        except (OSError,smtplib.SMTPException):
            log.warning('News email delivery not confirmed; automatic retry disabled to avoid duplicates')
        finally:
            with connection() as conn:
                conn.execute("UPDATE news_email_outbox SET status=%s,sent_at=CASE WHEN %s='sent' THEN now() ELSE NULL END WHERE id=%s",[outcome,outcome,row['id']])

async def newsletter_loop():
    while True:
        try:await asyncio.to_thread(deliver_daily)
        except Exception:log.warning('News digest cycle unavailable')
        await asyncio.sleep(900)
