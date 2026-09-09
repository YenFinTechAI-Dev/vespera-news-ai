"""Bounded published news context, obtained from the same API query as the website."""
from datetime import date
from news_api import list_news, Language

def build_news_context(language):
    try:
        data=list_news(language=Language(language),limit=5,offset=0)
        return {'status':'ok','retrieved_on':date.today().isoformat(),'total':data['total'],
                'scope':'Five most recent published summaries in selected language; not necessarily today.',
                'articles':[{**{k:str(a[k]) for k in ('id','published_at','source_name','source_url','title')},
                             'summary':a['summary'][:2000], 'url':'/news/'+str(a['id'])} for a in data['items']]}
    except Exception:
        return {'status':'unavailable','articles':[]}
