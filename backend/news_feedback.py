"""Anonymous voluntary feedback; private reporting through server gateway only."""
from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from database import connection,DatabaseUnavailable
from system_api import gateway,throttle
router=APIRouter(prefix='/news/feedback',tags=['News feedback'])
class Feedback(BaseModel):
    id:UUID
    rating:int=Field(ge=1,le=5,strict=True)
    comment:str=Field(default='',max_length=2000)
    language:Literal['vi','en']='vi'
@router.post('')
def submit(body:Feedback,x_chat_token:str|None=Header(None),x_client_key:str|None=Header(None)):
    gateway(x_chat_token)
    if not x_client_key:raise HTTPException(400,'Client key missing')
    try:
        throttle('feedback:'+x_client_key)
        with connection() as conn:
            conn.execute('INSERT INTO news_feedback(id,rating,comment,language) VALUES(%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING',[body.id,body.rating,body.comment.strip(),body.language])
        return {'status':'received'}
    except DatabaseUnavailable:raise HTTPException(503,'Feedback storage unavailable') from None
@router.get('/report')
def report(x_chat_token:str|None=Header(None)):
    gateway(x_chat_token)
    with connection() as conn:
        stats=conn.execute('SELECT count(*) AS total,round(avg(rating),2) AS average_rating FROM news_feedback').fetchone()
        items=conn.execute('SELECT id,rating,comment,language,created_at FROM news_feedback ORDER BY created_at DESC LIMIT 200').fetchall()
    return {'stats':stats,'items':items}
