import ai_provider
"""Durable, bounded AI summarization queue. No model calls on the read path."""
import asyncio
import json
import logging
import os
from database import connection
import ai_writer
from news_provider_guard import provider_state

log=logging.getLogger(__name__)
DAILY_LIMIT=48
REFRESH_SECONDS=max(300,int(os.getenv('NEWS_REFRESH_SECONDS','900')))

def enqueue():
    with connection() as conn:
        conn.execute("""INSERT INTO news_ai_jobs(article_id,priority_at)
          SELECT a.id,a.published_at FROM news_articles a JOIN news_summaries s ON s.article_id=a.id AND s.language=a.source_language
          WHERE a.status='published' AND a.published_at<=now() AND NOT s.ai_generated
          ORDER BY a.published_at DESC LIMIT 200 ON CONFLICT(article_id) DO NOTHING""")

def process_one():
    if not ai_writer._available():return 'unconfigured'
    provider=provider_state()
    if provider and provider['blocked']:return 'provider_paused'
    with connection() as conn:
        row=conn.execute("""SELECT j.article_id,a.original_title,a.source_url,a.category,s.summary
          FROM news_ai_jobs j JOIN news_articles a ON a.id=j.article_id
          JOIN news_summaries s ON s.article_id=a.id AND s.language=a.source_language
          WHERE a.status='published' AND a.published_at<=now() AND j.attempts<3
          AND ((j.status IN ('pending','failed') AND j.next_attempt<=now())
          OR (j.status='processing' AND j.updated_at<now()-INTERVAL '10 minutes'))
          ORDER BY j.priority_at DESC FOR UPDATE OF j SKIP LOCKED LIMIT 1""").fetchone()
        if not row:return 'idle'
        budget=conn.execute("""INSERT INTO news_ai_usage(day,attempts) VALUES ((CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok')::date,1)
          ON CONFLICT(day) DO UPDATE SET attempts=news_ai_usage.attempts+1 WHERE news_ai_usage.attempts<%s RETURNING attempts""",[DAILY_LIMIT]).fetchone()
        if not budget:return 'daily_limit'
        conn.execute("UPDATE news_ai_jobs SET status='processing',attempts=attempts+1,updated_at=now() WHERE article_id=%s",[row['article_id']])
    # Release DB transaction while waiting for provider.
    result=ai_writer.rewrite(row['original_title'],row['summary'],row['category'],row['source_url'])
    with connection() as conn:
        if not result:
            conn.execute("UPDATE news_ai_jobs SET status='failed',next_attempt=now()+INTERVAL '30 minutes',updated_at=now() WHERE article_id=%s",[row['article_id']])
            return 'failed'
        for lang in ('vi','en'):
            data=result[lang]
            conn.execute("""INSERT INTO news_summaries(article_id,language,title,summary,ai_generated,key_points,model_name)
              VALUES (%s,%s,%s,%s,true,%s::jsonb,%s) ON CONFLICT(article_id,language)
              DO UPDATE SET title=EXCLUDED.title,summary=EXCLUDED.summary,ai_generated=true,
              key_points=EXCLUDED.key_points,model_name=EXCLUDED.model_name,generated_at=now()""",
              [row['article_id'],lang,data['title'],data['summary'],json.dumps(data['key_points']),ai_provider.model()])
        conn.execute("UPDATE news_ai_jobs SET status='ready',updated_at=now() WHERE article_id=%s",[row['article_id']])
    return 'ready'

async def automation_loop():
    from rss_importer import ingest_news
    loop=asyncio.get_running_loop();next_feed=0
    while True:
        try:
            if loop.time()>=next_feed:
                result=await asyncio.to_thread(ingest_news)
                with connection() as conn:
                    conn.execute("""INSERT INTO news_pipeline_state(id,last_refresh,last_success,last_result)
                      VALUES (1,now(),CASE WHEN %s THEN now() ELSE NULL END,%s::jsonb)
                      ON CONFLICT(id) DO UPDATE SET last_refresh=now(),last_result=EXCLUDED.last_result,
                      last_success=COALESCE(EXCLUDED.last_success,news_pipeline_state.last_success)""",[result.get('failed_sources',0)==0,json.dumps(result)])
                next_feed=loop.time()+REFRESH_SECONDS
            await asyncio.to_thread(enqueue)
            for _ in range(2):
                state=await asyncio.to_thread(process_one)
                if state in ('idle','daily_limit','unconfigured','provider_paused'):break
        except Exception:
            log.warning('News automation failed; retrying, existing articles retained')
            next_feed=max(next_feed,loop.time()+60)
        await asyncio.sleep(60)
