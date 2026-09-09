"""Local application accounts, sessions, conversation storage and daily request quota."""
import hashlib
import hmac
import json
import os
import re
import secrets
from pathlib import Path
from uuid import UUID, uuid4
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from database import connection

router = APIRouter(prefix='/account', tags=['Accounts'])
DAILY_LIMIT = 50

def initialize_accounts():
    with connection() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(736521906)')
        conn.execute((Path(__file__).parent/'src/db/migrations/003_accounts.sql').read_text(encoding='utf-8'), prepare=False)

def gateway(token):
    expected=os.getenv('CHAT_PROXY_TOKEN','')
    if not expected or not hmac.compare_digest(token or '',expected):
        raise HTTPException(401,'Gateway authorization required')

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def password_hash(password, salt=None):
    salt=salt or secrets.token_hex(16)
    return salt+':'+hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()

def identity(session):
    if not session: raise HTTPException(401,'Vui lòng đăng nhập để sử dụng AI.')
    with connection() as conn:
        row=conn.execute('SELECT u.id,u.name,u.email FROM app_sessions s JOIN app_users u ON u.id=s.user_id WHERE s.token_hash=%s AND s.expires_at>CURRENT_TIMESTAMP',[digest(session)]).fetchone()
    if not row: raise HTTPException(401,'Phiên đăng nhập đã hết hạn.')
    return row

def throttle(key):
    # Persistent, shared across backend processes. Never store raw email/IP.
    with connection() as conn:
        row=conn.execute('''INSERT INTO app_auth_limits (key,window_start,attempts) VALUES (%s,CURRENT_TIMESTAMP,1)
          ON CONFLICT (key) DO UPDATE SET attempts=CASE WHEN app_auth_limits.window_start<CURRENT_TIMESTAMP-INTERVAL '15 minutes' THEN 1 ELSE app_auth_limits.attempts+1 END,
          window_start=CASE WHEN app_auth_limits.window_start<CURRENT_TIMESTAMP-INTERVAL '15 minutes' THEN CURRENT_TIMESTAMP ELSE app_auth_limits.window_start END RETURNING attempts''',[digest(key)]).fetchone()
    if row['attempts']>15: raise HTTPException(429,'Thử quá nhiều lần. Vui lòng chờ 15 phút.')

class Credentials(BaseModel):
    email:str=Field(min_length=3,max_length=254)
    password:str=Field(min_length=8,max_length=128)
    name:str=Field(default='',max_length=100)

def session_for(conn,user):
    token=secrets.token_urlsafe(32)
    conn.execute("INSERT INTO app_sessions(token_hash,user_id,expires_at) VALUES (%s,%s,CURRENT_TIMESTAMP+INTERVAL '7 days')",[digest(token),user['id']])
    return {'user':{k:user[k] for k in ('id','name','email')},'session_token':token}

@router.post('/register')
def register(body:Credentials,x_chat_token:str|None=Header(None),x_client_key:str|None=Header(None)):
    gateway(x_chat_token);throttle('register:'+str(x_client_key))
    email=body.email.strip().lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or not body.name.strip(): raise HTTPException(422,'Nhập tên và email hợp lệ.')
    with connection() as conn:
        user=conn.execute('INSERT INTO app_users(id,name,email,password_hash) VALUES (%s,%s,%s,%s) ON CONFLICT(email) DO NOTHING RETURNING id,name,email',[uuid4(),body.name.strip(),email,password_hash(body.password)]).fetchone()
        if not user: raise HTTPException(409,'Không thể tạo tài khoản với email này.')
        return session_for(conn,user)

@router.post('/login')
def login(body:Credentials,x_chat_token:str|None=Header(None),x_client_key:str|None=Header(None)):
    gateway(x_chat_token);throttle('ip:'+str(x_client_key));throttle('email:'+body.email.strip().lower())
    with connection() as conn:
        user=conn.execute('SELECT id,name,email,password_hash FROM app_users WHERE email=%s',[body.email.strip().lower()]).fetchone()
        encoded=user['password_hash'] if user else '00'*16+':'+ '00'*64
        valid=hmac.compare_digest(password_hash(body.password,encoded.split(':')[0]),encoded)
        if not user or not valid: raise HTTPException(401,'Email hoặc mật khẩu không đúng.')
        return session_for(conn,user)

@router.get('/me')
def me(x_chat_token:str|None=Header(None),x_session_token:str|None=Header(None)):
    gateway(x_chat_token);user=identity(x_session_token)
    with connection() as conn:
        usage=conn.execute("SELECT requests FROM app_usage WHERE user_id=%s AND day=(CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok')::date",[user['id']]).fetchone()
    return {'user':user,'usage':{'used':usage['requests'] if usage else 0,'limit':DAILY_LIMIT,'unit':'requests','reset_timezone':'Asia/Bangkok'}}

@router.post('/logout')
def logout(x_chat_token:str|None=Header(None),x_session_token:str|None=Header(None)):
    gateway(x_chat_token)
    with connection() as conn: conn.execute('DELETE FROM app_sessions WHERE token_hash=%s',[digest(x_session_token or '')])
    return {'ok':True}
