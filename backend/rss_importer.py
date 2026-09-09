"""Bounded RSS/Atom import with per-source diagnostics and canonical URL deduplication."""
import html
import logging

import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import requests
from database import connection, DatabaseUnavailable
from news_sources import SOURCES

log = logging.getLogger(__name__)
ATOM = '{http://www.w3.org/2005/Atom}'

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def plain(value):
    parser = PlainText(); parser.feed(value or '')
    return ' '.join(html.unescape(' '.join(parser.parts)).split())

def canonical_url(value, source):
    parts = urlsplit(value.strip())
    host = (parts.hostname or '').lower()
    if parts.scheme not in ('https', 'http') or parts.username or parts.password or parts.port not in (None, 80, 443):
        raise ValueError('Invalid source URL')
    if not any(host == h or (source.get('subdomains') and host.endswith('.' + h)) for h in source['hosts']):
        raise ValueError('Unexpected source host')
    path = parts.path
    if source['id'].startswith('arxiv'):
        path = re.sub(r'v\d+$', '', path)  # One article for revisions of the same paper.
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not k.startswith('utm_') and k not in ('source', 'ref', 'fbclid')])
    return urlunsplit(('https', host, path, query, ''))

def parse_date(value):
    try: result = parsedate_to_datetime(value)
    except (ValueError, TypeError): result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return result.replace(tzinfo=timezone.utc) if result.tzinfo is None else result

def parse_feed(content, source):
    if len(content) > 2_000_000 or b'<!ENTITY' in content.upper() or b'<!DOCTYPE' in content.upper():
        raise ValueError('Unsupported feed')
    root = ET.fromstring(content)
    atom = root.tag == ATOM + 'feed'
    if root.tag != 'rss' and not atom: raise ValueError('Not RSS or Atom')
    entries = root.findall(ATOM + 'entry') if atom else root.findall('./channel/item')
    items = []
    for entry in entries[:60]:
        try:
            if atom:
                links = [link for link in entry.findall(ATOM+'link') if link.get('rel', 'alternate') == 'alternate']
                link = links[0].get('href', '') if links else ''
                title = entry.findtext(ATOM+'title', '')
                excerpt = entry.findtext(ATOM+'summary') or entry.findtext(ATOM+'content', '')
                stamp = entry.findtext(ATOM+'published') or entry.findtext(ATOM+'updated', '')
            else:
                link = entry.findtext('link', '')
                title = entry.findtext('title', '')
                excerpt = entry.findtext('description') or entry.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', '')
                stamp = entry.findtext('pubDate') or entry.findtext('{http://purl.org/dc/elements/1.1/}date', '')
            published = parse_date(stamp)
            if published > datetime.now(timezone.utc): continue
            title = plain(title)[:400]; excerpt = plain(excerpt)[:1200] or title
            if not title or not excerpt: continue
            if source['category']=='financial_crime' and not re.search(r'fraud|scam|ponzi|launder|deceptive|defraud|charges|charged',title+' '+excerpt,re.I): continue
            items.append(dict(source_url=canonical_url(link, source), title=title, excerpt=excerpt,
                              published=published, category=source['category'], source_name=source['name'], language=source['language']))
        except (ValueError, TypeError, OverflowError): continue
    return items

def fetch_source(source):
    try:
        with requests.get(source['url'], timeout=(8, 20), stream=True, headers={'User-Agent':'VesperSignal/1.0 RSS Reader'}) as response:
            response.raise_for_status()
            chunks = []; size = 0
            for chunk in response.iter_content(65536):
                size += len(chunk)
                if size > 2_000_000: raise ValueError('Feed too large')
                chunks.append(chunk)
        items = parse_feed(b''.join(chunks), source)
        return items, dict(id=source['id'], status='ok', fetched=len(items))
    except (requests.RequestException, ET.ParseError, ValueError):
        log.warning('News source unavailable: %s', source['id'])
        return [], dict(id=source['id'], status='unavailable', fetched=0)

def collect():
    with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(fetch_source,SOURCES))

    return [item for items,_ in results for item in items], [state for _,state in results]

def ingest_news():
    items, states = collect(); inserted=0
    with connection() as conn:
        if not conn.execute('SELECT pg_try_advisory_xact_lock(736521905) AS acquired').fetchone()['acquired']:
            return {'inserted':0,'status':'another_run_active'}
        for item in items:
            article=conn.execute('''INSERT INTO news_articles(source_name,source_url,original_title,category,published_at,status,source_language)
                VALUES (%s,%s,%s,%s,%s,'published',%s) ON CONFLICT(source_url) DO NOTHING RETURNING id''',
                [item['source_name'],item['source_url'],item['title'],item['category'],item['published'],item['language']]).fetchone()
            if not article: continue
            inserted+=1
            conn.execute('''INSERT INTO news_summaries(article_id,language,title,summary,ai_generated)
                VALUES (%s,%s,%s,%s,FALSE)''',[article['id'],item['language'],item['title'],item['excerpt']])
    return dict(inserted=inserted, fetched=len(items), ai_generated=0,
                failed_sources=sum(s['status']=='unavailable' for s in states), sources=states)

if __name__=='__main__':
    try: print(ingest_news())
    except DatabaseUnavailable: print('Database unavailable'); raise SystemExit(1) from None
