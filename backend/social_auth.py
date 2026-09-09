"""Provider-verified identities. OAuth secrets and tokens stay server-side."""
import base64
import hashlib
import hmac
import os
import secrets
from urllib.parse import urlencode
from uuid import uuid4

import requests
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from database import connection
from system_api import gateway, throttle, digest, password_hash, session_for

router = APIRouter(prefix='/account/social', tags=['Social login'])
PROVIDERS = ('google', 'github', 'facebook')

def config(provider):
    if provider not in PROVIDERS:
        raise HTTPException(404, 'Unknown provider')
    client = os.getenv(provider.upper() + '_CLIENT_ID', '').strip()
    secret = os.getenv(provider.upper() + '_CLIENT_SECRET', '').strip()
    return client, secret

def enabled(provider):
    client, secret = config(provider)
    return bool(client and (provider == 'google' or secret))

def callback(provider):
    return os.getenv('AUTH_APP_URL', 'http://localhost:3003').rstrip('/') + '/api/auth/' + provider + '/callback'

@router.get('/config')
def configuration(x_chat_token: str | None = Header(None)):
    gateway(x_chat_token)
    return {p: enabled(p) for p in PROVIDERS}

@router.post('/{provider}/start')
def start(provider: str, x_chat_token: str | None = Header(None), x_client_key: str | None = Header(None)):
    gateway(x_chat_token)
    if not enabled(provider):
        raise HTTPException(503, 'Nhà cung cấp chưa được cấu hình.')
    throttle('oauth-start:' + str(x_client_key))
    state, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(3))
    with connection() as conn:
        conn.execute('DELETE FROM app_oauth_attempts WHERE expires_at < now()')
        conn.execute("INSERT INTO app_oauth_attempts VALUES (%s,%s,%s,%s,now()+interval '10 minutes')", [digest(state), provider, nonce, verifier])
    client, _ = config(provider)
    if provider == 'google':
        return {'state': state, 'nonce': nonce, 'client_id': client}
    params = dict(client_id=client, redirect_uri=callback(provider), state=state, response_type='code')
    if provider == 'github':
        params.update(scope='read:user user:email', code_challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode(), code_challenge_method='S256')
        url = 'https://github.com/login/oauth/authorize'
    else:
        params.update(scope='email,public_profile')
        url = 'https://www.facebook.com/' + os.getenv('FACEBOOK_GRAPH_VERSION', 'v23.0') + '/dialog/oauth'
    return {'state': state, 'url': url + '?' + urlencode(params)}

class Completion(BaseModel):
    state: str = Field(min_length=20, max_length=200)
    credential: str = Field(default='', max_length=10000)
    code: str = Field(default='', max_length=2000)

def consume(provider, state):
    # Commit deletion before contacting provider: every attempt is single use.
    with connection() as conn:
        row = conn.execute('DELETE FROM app_oauth_attempts WHERE state_hash=%s AND provider=%s AND expires_at>now() RETURNING nonce,verifier', [digest(state), provider]).fetchone()
    if not row:
        raise HTTPException(401, 'Phiên đăng nhập đã hết hạn. Vui lòng thử lại.')
    return row

def google_profile(credential, nonce):
    claims = id_token.verify_oauth2_token(credential, Request(), config('google')[0])
    if not hmac.compare_digest(str(claims.get('nonce', '')), nonce) or claims.get('email_verified') is not True:
        raise ValueError('Invalid identity')
    return str(claims['sub']), claims['email'], claims.get('name', '')

def json_request(method, url, **kwargs):
    response = requests.request(method, url, timeout=(5, 15), **kwargs)
    response.raise_for_status()
    return response.json()

def code_profile(provider, code, verifier):
    client, secret = config(provider)
    payload = dict(client_id=client, client_secret=secret, code=code, redirect_uri=callback(provider))
    if provider == 'github':
        payload['code_verifier'] = verifier
        token = json_request('POST', 'https://github.com/login/oauth/access_token', data=payload, headers={'Accept': 'application/json'})['access_token']
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'}
        profile = json_request('GET', 'https://api.github.com/user', headers=headers)
        emails = json_request('GET', 'https://api.github.com/user/emails', headers=headers)
        email = next((e['email'] for e in emails if e.get('verified') and e.get('primary')), None)
        if not email:
            raise ValueError('Verified email required')
        return str(profile['id']), email, profile.get('name') or profile['login']
    root = 'https://graph.facebook.com/' + os.getenv('FACEBOOK_GRAPH_VERSION', 'v23.0')
    token = json_request('POST', root + '/oauth/access_token', data=payload)['access_token']
    proof = hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()
    profile = json_request('GET', root + '/me', headers={'Authorization': 'Bearer ' + token}, params={'fields': 'id,name,email', 'appsecret_proof': proof})
    return str(profile['id']), profile['email'], profile.get('name', '')

def social_session(provider, subject, email, name):
    email = email.strip().lower()
    if not subject or not email or len(email) > 254:
        raise HTTPException(401, 'Không nhận được email từ nhà cung cấp.')
    with connection() as conn:
        # Serialize creation, including concurrent providers using the same email.
        conn.execute('SELECT pg_advisory_xact_lock(736521907)')
        user = conn.execute('SELECT u.id,u.name,u.email FROM app_social_identities i JOIN app_users u ON u.id=i.user_id WHERE i.provider=%s AND i.subject=%s', [provider, subject]).fetchone()
        if not user:
            if conn.execute('SELECT id FROM app_users WHERE email=%s', [email]).fetchone():
                raise HTTPException(409, 'Email đã có tài khoản. Hãy đăng nhập bằng phương thức đã dùng trước đó; hệ thống không tự liên kết tài khoản.')
            user = conn.execute('INSERT INTO app_users(id,name,email,password_hash) VALUES (%s,%s,%s,%s) RETURNING id,name,email', [uuid4(), (name or email.split('@')[0])[:100], email, password_hash(secrets.token_urlsafe(64))]).fetchone()
            conn.execute('INSERT INTO app_social_identities(provider,subject,user_id) VALUES (%s,%s,%s)', [provider, subject, user['id']])
        return session_for(conn, user)

@router.post('/{provider}/complete')
def complete(provider: str, body: Completion, x_chat_token: str | None = Header(None), x_client_key: str | None = Header(None)):
    gateway(x_chat_token)
    if not enabled(provider):
        raise HTTPException(503, 'Nhà cung cấp chưa được cấu hình.')
    throttle('oauth-complete:' + str(x_client_key))
    attempt = consume(provider, body.state)
    try:
        profile = google_profile(body.credential, attempt['nonce']) if provider == 'google' else code_profile(provider, body.code, attempt['verifier'])
    except (ValueError, KeyError, TypeError, requests.RequestException, GoogleAuthError):
        raise HTTPException(401, 'Không xác minh được đăng nhập. Hãy thử lại và cho phép chia sẻ email.') from None
    return social_session(provider, *profile)
