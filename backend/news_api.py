import ai_provider
"""Published news, searchable feed, cached AI summaries, and automation health."""
from enum import Enum
from uuid import UUID
from fastapi import APIRouter,HTTPException,Query
from database import connection,DatabaseUnavailable
router=APIRouter()
class Category(str,Enum):
    economy='economy'
    technology='technology'
    ai='ai'
    research='research'
    tools='tools'
    ai_tools='ai_tools'
    web='web'
    financial_crime='financial_crime'
class Language(str,Enum):
    vi='vi'
    en='en'
def unavailable():return HTTPException(503,'Cơ sở dữ liệu chưa sẵn sàng. Vui lòng thử lại.')
@router.get('/health')
def health():
    try:
        with connection() as conn:conn.execute('SELECT 1 FROM news_articles LIMIT 1')
        return {'status':'ok','database':'ready'}
    except DatabaseUnavailable:raise unavailable() from None

@router.get('/news/status')
def news_status():
    from news_worker import DAILY_LIMIT
    from news_provider_guard import provider_state
    import ai_writer
    from news_sources import public_sources
    with connection() as conn:
        state=conn.execute('SELECT last_refresh,last_success,last_result FROM news_pipeline_state WHERE id=1').fetchone()
        counts=conn.execute("SELECT category,count(*) AS count FROM news_articles WHERE status='published' AND published_at<=now() GROUP BY category").fetchall()
        summary=conn.execute("SELECT count(*) AS count FROM news_summaries WHERE language='vi' AND ai_generated=true").fetchone()['count']
        usage=conn.execute("SELECT attempts FROM news_ai_usage WHERE day=(CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok')::date").fetchone()
        resets=conn.execute("SELECT (date_trunc('day',now() AT TIME ZONE 'Asia/Bangkok')+INTERVAL '1 day') AT TIME ZONE 'Asia/Bangkok' AS at").fetchone()['at']
    return {'ai_provider':ai_provider.provider(),'ai_model':ai_provider.model(),'provider':provider_state(),'ai_resets_at':resets,'sources':public_sources(),'pipeline':state,'categories':counts,'ai_ready':summary,'refresh_minutes':15,'ai_configured':ai_writer._available(),
            'ai_daily_limit':DAILY_LIMIT,'ai_attempts_today':usage['attempts'] if usage else 0}

@router.get('/news')
def list_news(category:Category|None=None,language:Language=Language.vi,
              limit:int=Query(default=20,ge=1,le=100),offset:int=Query(default=0,ge=0,le=10000),
              q:str|None=None,period:str='all',source:str|None=None):
    conditions="a.status = 'published' AND a.published_at <= CURRENT_TIMESTAMP"
    params=[language.value]
    if category is not None:conditions+=' AND a.category = %s';params.append(category.value)
    if source:
        if len(source)>100:raise HTTPException(422,'Source too long')
        conditions+=' AND a.source_name = %s';params.append(source)
    if period not in ('all','week','today'):raise HTTPException(422,'Invalid period')
    if period in ('today','week'):conditions+=' AND NOT a.publication_date_unknown'
    if period=='today':conditions+=" AND (a.published_at AT TIME ZONE 'Asia/Bangkok')::date=(CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok')::date"
    if q:
        if len(q)>200:raise HTTPException(422,'Từ khóa tối đa 200 ký tự.')
        conditions+=' AND (s.title ILIKE %s OR s.summary ILIKE %s)';params.extend(['%'+q+'%']*2)
    if period=='week':conditions+=" AND a.published_at>=CURRENT_TIMESTAMP-INTERVAL '7 days'"
    try:
        with connection() as conn:
            conn.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            total=conn.execute('SELECT count(*) AS count FROM news_articles a JOIN LATERAL (SELECT * FROM news_summaries ns WHERE ns.article_id=a.id AND ns.language=%s LIMIT 1) s ON true WHERE '+conditions,params).fetchone()['count']
            items=conn.execute('''SELECT a.id,a.source_name,a.source_url,a.category,CASE WHEN a.publication_date_unknown THEN NULL ELSE a.published_at END AS published_at,
                s.language,s.title,s.summary,s.ai_generated,s.model_name,s.key_points,s.generated_at,
                CASE WHEN s.ai_generated THEN 'ready' ELSE COALESCE(j.status,'pending') END AS ai_status
                FROM news_articles a JOIN LATERAL (SELECT * FROM news_summaries ns WHERE ns.article_id=a.id AND ns.language=%s LIMIT 1) s ON true
                LEFT JOIN news_ai_jobs j ON j.article_id=a.id WHERE '''+conditions+
                ' ORDER BY a.published_at DESC, a.id DESC LIMIT %s OFFSET %s',[*params,limit,offset]).fetchall()
        return {'total':total,'limit':limit,'offset':offset,'items':items}
    except DatabaseUnavailable:raise unavailable() from None

@router.get('/news/{article_id}')
def get_news(article_id:UUID,language:Language=Language.vi):
    try:
        with connection() as conn:
            article=conn.execute('''SELECT a.id,a.source_name,a.source_url,a.category,CASE WHEN a.publication_date_unknown THEN NULL ELSE a.published_at END AS published_at,
              s.language,s.title,s.summary,s.ai_generated,s.model_name,s.key_points,s.generated_at,s.model_name,COALESCE(j.attempts,0) AS ai_attempts,
              CASE WHEN s.ai_generated THEN 'ready' ELSE COALESCE(j.status,'pending') END AS ai_status
              FROM news_articles a JOIN LATERAL (SELECT * FROM news_summaries ns WHERE ns.article_id=a.id ORDER BY (ns.language=%s) DESC LIMIT 1) s ON true
              LEFT JOIN news_ai_jobs j ON j.article_id=a.id
              WHERE a.id=%s AND a.status='published' AND a.published_at<=CURRENT_TIMESTAMP''',[language.value,article_id]).fetchone()
            if article is None:raise HTTPException(404,'Không tìm thấy bài viết ở ngôn ngữ đã chọn.')
            # Reading cannot trigger unbounded paid calls; it only prioritizes a pre-existing bounded queue.
            if not article['ai_generated']:
                conn.execute("INSERT INTO news_ai_jobs(article_id,priority_at) VALUES (%s,now()) ON CONFLICT(article_id) DO UPDATE SET priority_at=now() WHERE news_ai_jobs.status IN ('pending','failed') AND news_ai_jobs.attempts<3",[article_id])
        if article['language'] != language.value:
            article=dict(article,language=language.value,translation_pending=True,ai_generated=False,key_points=[],
              title='Bài viết đang chờ bản dịch tiếng Việt' if language.value=='vi' else 'Article awaiting English translation',
              summary='Bản dịch chưa sẵn sàng. Bạn có thể đọc nội dung gốc tại nguồn.' if language.value=='vi' else 'Translation is not ready. You can read the original at the source.')
        return article
    except DatabaseUnavailable:raise unavailable() from None

