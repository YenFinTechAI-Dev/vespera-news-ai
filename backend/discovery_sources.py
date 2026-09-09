"""Public web search and scholarly metadata; never fetch arbitrary result URLs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlsplit, quote
import ipaddress
import json
import xml.etree.ElementTree as ET
import requests
import re
from rss_importer import plain
from search_relevance import relevant

def read(url, params):
    with requests.get(url, params=params, timeout=(4, 10), stream=True, headers={'User-Agent': 'VesperSignal/1.0 (public search)'}) as r:
        r.raise_for_status()
        data = bytearray()
        for chunk in r.iter_content(65536):
            data.extend(chunk)
            if len(data) > 2_000_000: raise ValueError('Response too large')
    return bytes(data)

def safe_url(value):
    try:
        url = urlsplit(value)
        if url.scheme not in ('http','https') or not url.hostname or url.username or url.password: return False
        if url.hostname in ('localhost','x.com','twitter.com') or url.hostname.endswith(('.localhost','.local','.x.com','.twitter.com')): return False
        try: return ipaddress.ip_address(url.hostname).is_global
        except ValueError: return '.' in url.hostname
    except ValueError: return False

def search_text(query):
    """Extract the work title from a citation while retaining ordinary queries."""
    value=' '.join(query.split()).strip()
    citation=re.search(r'\)\.\s*(.+?)(?:[,.]\s*(?:Tạp chí|Journal|Proceedings|Conference)\b|\.$)',value,flags=re.I)
    if citation and len(citation.group(1).split())>=4:
        return citation.group(1).strip(' .')
    return value

def citation_author(query):
    """Return the leading author from a conventional academic citation."""
    value=' '.join(query.split()).strip()
    match=re.match(r'(.+?)\s*\.\s*\(\d{4}\)\.', value)
    return match.group(1).strip() if match else ''

def web(query, language):
    topic=search_text(query)
    author=citation_author(query)
    search_query = (chr(34)+topic+chr(34)+' '+chr(34)+author+chr(34)) if author else (chr(34)+topic+chr(34) if len(topic.split())>=4 else topic)
    raw = read('https://www.bing.com/search', {'q':search_query,'format':'rss','setlang':language})
    if b'<!ENTITY' in raw.upper(): raise ValueError('Invalid feed')
    root = ET.fromstring(raw)
    if root.tag != 'rss': raise ValueError('Search feed unavailable')
    results = []
    for item in root.findall('./channel/item')[:10]:
        url = item.findtext('link','')
        title = plain(item.findtext('title',''))[:400]
        if safe_url(url) and title:
            results.append(dict(url=url,title=title,summary=plain(item.findtext('description',''))[:900],publisher=urlsplit(url).hostname,kind='web',published=None))
    return results

def research(query, language):
    data = json.loads(read('https://api.crossref.org/works', {'query.bibliographic':search_text(query),'rows':20,'sort':'relevance','select':'DOI,title,publisher,abstract,published,author'}))
    results=[]
    for item in data['message']['items']:
        title=plain(' '.join(item.get('title',[])))[:400]
        doi=item.get('DOI','')
        if not title or not doi: continue
        published=None
        try:
            parts=item['published']['date-parts'][0]
            published=datetime(*(parts+[1]*(3-len(parts))),tzinfo=timezone.utc)
            if published>datetime.now(timezone.utc): continue
        except (KeyError,TypeError,ValueError): pass
        authors=[' '.join(filter(None,[a.get('given'),a.get('family')])) for a in item.get('author',[])[:8]]
        results.append(dict(url='https://doi.org/'+quote(doi,safe='/'),title=title,summary=plain(item.get('abstract',''))[:900],publisher=item.get('publisher','Crossref'),kind='research',published=published,authors=authors))
    return results

def aggregate(query, language, mode, news_fetch):
    funcs={'news':news_fetch,'web':web,'research':research}
    names=(['research','news','web'] if mode=='all' and citation_author(query) else (list(funcs) if mode=='all' else [mode]))
    result=[];status={};seen=set()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={name:pool.submit(funcs[name],query,language) for name in names}
        groups={}
        for name,future in futures.items():
            try:
                groups[name]=future.result()
                status[name]='ok'
            except (requests.RequestException,ValueError,KeyError,TypeError,ET.ParseError):
                groups[name]=[];status[name]='unavailable'
    # Interleave provider-ranked results so newer news cannot bury relevant research.
    for i in range(30):
        for name in names:
            if i>=len(groups[name]):continue
            item=groups[name][i]
            # Match the work title for citation-shaped queries; author metadata
            # is used to narrow provider requests but should not hide the paper.
            if item['url'] in seen or not safe_url(item['url']) or not relevant(search_text(query),item['title'],item.get('summary','')):continue
            seen.add(item['url']);item.setdefault('kind',name)
            item['summary']=item.get('summary') or item['title']
            item['publisher']=item.get('publisher') or name
            result.append(item)
    return result,status
