import ai_provider
"""Shared provider backoff; never reset or bypass the daily attempt budget."""
from database import connection

def provider_state():
    if ai_provider.local():return None
    with connection() as conn:
        return conn.execute("SELECT reason,retry_at,http_status,(reason='insufficient_balance' OR retry_at>now()) AS blocked FROM news_provider_state WHERE id=1").fetchone()

def record_failure(status, code=None):
    if ai_provider.local():return
    reason='insufficient_balance' if str(code)=='1113' else 'rate_limited' if status==429 else 'authorization' if status in (401,403) else 'temporary'
    minutes=360 if reason=='authorization' else 30 if reason=='rate_limited' else 5
    with connection() as conn:
        conn.execute("INSERT INTO news_provider_state(id,reason,http_status,retry_at) VALUES(1,%s,%s,now()+%s*INTERVAL '1 minute') ON CONFLICT(id) DO UPDATE SET reason=EXCLUDED.reason,http_status=EXCLUDED.http_status,retry_at=EXCLUDED.retry_at",[reason,status,minutes])

def record_success():
    if ai_provider.local():return
    with connection() as conn:
        conn.execute("UPDATE news_provider_state SET reason='ready',http_status=200,retry_at=now() WHERE id=1")


def record_response_failure(response):
    try:
        error=response.json().get('error',{})
        code=error.get('code') if isinstance(error,dict) else None
    except (ValueError,AttributeError):
        code=None
    record_failure(response.status_code,code)
