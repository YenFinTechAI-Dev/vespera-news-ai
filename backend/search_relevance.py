"""Conservative lexical screening, not a claim of semantic verification."""
import re
import unicodedata

STOP=set('the a an and or of in on to for with is are how what does do can it as by from about this that dang duoc nhu the nao trong va cua la ve mot nhung cac voi cho khi thi de co gi toi minh ban hay tim'.split())
def words(value):
    text=''.join(c for c in unicodedata.normalize('NFD',value.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')
    return set(re.findall(r'[a-z0-9]+',text))

def normalized_tokens(value):
    text=''.join(c for c in unicodedata.normalize('NFD',value.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')
    return re.findall(r'[a-z0-9]+',text)

def relevant(query,title,excerpt):
    query_tokens=[token for token in normalized_tokens(query) if token not in STOP]
    # Long title-like searches need phrase continuity. This prevents a paper
    # sharing a few generic words from being presented as the requested work.
    anchors={token for token in query_tokens if len(token)<=3}
    if len(query_tokens)>=6 and not anchors:
        content_tokens=normalized_tokens(title+' '+excerpt)
        query_bigrams=list(zip(query_tokens,query_tokens[1:]))
        content_bigrams=set(zip(content_tokens,content_tokens[1:]))
        if query_bigrams and sum(pair in content_bigrams for pair in query_bigrams)/len(query_bigrams)<0.5:
            return False
    required=words(query)-STOP
    if not required:return True
    found=words(title+' '+excerpt)
    # Preserve named entities and ticker-like anchors. A broad word such as
    # “ngân hàng” must not make an unrelated banking paper match “MB Bank”.
    anchors={token for token in required if len(token)<=3}
    if len(required)>=3 and anchors and not anchors.issubset(found):
        return False
    # Reject single-word dictionary matches for multi-keyword topics.
    threshold=1 if len(required)==1 else max(2,(len(required)+1)//2)
    return len(required & found)>=threshold
