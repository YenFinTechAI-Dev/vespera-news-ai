"""Conservative lexical screening, not a claim of semantic verification."""
import re
import unicodedata

STOP=set('the a an and or of in on to for with is are how what does do can it as by from about this that dang duoc nhu the nao trong va cua la ve mot nhung cac voi cho khi thi de co gi toi minh ban hay tim'.split())
def words(value):
    text=''.join(c for c in unicodedata.normalize('NFD',value.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')
    return set(re.findall(r'[a-z0-9]+',text))

def relevant(query,title,excerpt):
    required=words(query)-STOP
    if not required:return True
    found=words(title+' '+excerpt)
    # Reject single-word dictionary matches for multi-keyword topics.
    threshold=1 if len(required)==1 else max(2,(len(required)+1)//2)
    return len(required & found)>=threshold
