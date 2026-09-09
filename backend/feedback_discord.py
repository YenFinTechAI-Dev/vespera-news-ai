"""Deliver saved feedback; failures remain queued. Never log webhook credentials."""
import os
from urllib.parse import urlsplit
import requests
from database import connection

def deliver_feedback():
    url=os.getenv('DISCORD_FEEDBACK_WEBHOOK','').strip()
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname!='discord.com' or not parsed.path.startswith('/api/webhooks/') or parsed.username or parsed.password:return
    with connection() as conn:
        row=conn.execute("""SELECT id,rating,comment,language,created_at FROM news_feedback WHERE discord_sent_at IS NULL
          AND discord_next_attempt<=now() AND discord_attempts<10 ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1""").fetchone()
        if not row:return
        conn.execute("UPDATE news_feedback SET discord_attempts=discord_attempts+1,discord_next_attempt=now()+interval '5 minutes' WHERE id=%s",[row['id']])
    try:
        response=requests.post(url,params={'wait':'true'},json={'username':'Vespera News Feedback','allowed_mentions':{'parse':[]},'embeds':[{'title':'News feedback','description':row['comment'] or '(No comment)','fields':[{'name':'Rating','value':str(row['rating'])+'/5'},{'name':'Language','value':row['language']},{'name':'Feedback ID','value':str(row['id'])}],'timestamp':row['created_at'].isoformat()}]},timeout=(5,10),allow_redirects=False)
        if 200<=response.status_code<300:
            with connection() as conn:conn.execute('UPDATE news_feedback SET discord_sent_at=now() WHERE id=%s',[row['id']])
    except requests.RequestException:pass
