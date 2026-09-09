"""Single provider configuration for chat, news and research."""
import os
import requests
from database import BACKEND_DIR

def json_format(kind):
    if not local():return {'type':'json_object'}
    text={'type':'string'}
    if kind=='summary':
        part={'type':'object','properties':{'title':text,'summary':text,'key_points':{'type':'array','items':text,'minItems':1,'maxItems':4}},'required':['title','summary','key_points'],'additionalProperties':False}
        schema={'type':'object','properties':{'vi':part,'en':part},'required':['vi','en'],'additionalProperties':False}
    else:
        part={'type':'object','properties':{'text':text,'sources':{'type':'array','items':{'type':'integer'},'minItems':1}},'required':['text','sources'],'additionalProperties':False}
        schema={'type':'object','properties':{'paragraphs':{'type':'array','items':part,'minItems':1,'maxItems':6},'limitations':text},'required':['paragraphs','limitations'],'additionalProperties':False}
    return {'type':'json_schema','json_schema':{'name':kind,'strict':True,'schema':schema}}

def provider():return os.getenv('AI_PROVIDER','huggingface').strip().lower()
def local():return provider()=='ollama'
def model():
    if local():return os.getenv('OLLAMA_MODEL','qwen2.5:3b')
    if provider()=='huggingface':return os.getenv('HF_MODEL','Qwen/Qwen3-4B-Instruct-2507:nscale')
    raise ValueError('Choose huggingface or ollama as AI_PROVIDER')
def available():
    if local():return True
    if provider()=='huggingface':return bool(os.getenv('HF_TOKEN','').strip())
    return False
def completion(payload,key='',stream=False,timeout=None):
    data=dict(payload);data['model']=model()
    if local():
        url=os.getenv('OLLAMA_BASE_URL','http://127.0.0.1:11434').rstrip('/')+'/v1/chat/completions'
        headers={'Content-Type':'application/json'}
        data.setdefault('temperature',0.2)
    elif provider()=='huggingface':
        token=os.getenv('HF_TOKEN','').strip()
        if not token:raise ValueError('Hugging Face is not configured')
        url='https://router.huggingface.co/v1/chat/completions'
        headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
        data.setdefault('temperature',0.2)
    else:raise ValueError('Unsupported AI provider')
    return requests.post(url,headers=headers,json=data,stream=stream,timeout=timeout or ((5,180) if local() else (10,90)),allow_redirects=False)


