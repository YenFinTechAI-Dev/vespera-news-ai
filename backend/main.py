"""News-only application: no stock models or market background tasks."""
import asyncio
import os
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI
from database import initialize_database
from news_api import router as news
from research_api import router as research
from web_discovery import router as discovery
from news_feedback import router as feedback
from news_mvp import router as mvp, newsletter_loop
from system_api import router as accounts
from social_auth import router as social
from news_worker import automation_loop

@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(initialize_database)
    tasks = []
    if os.getenv('NEWS_AUTOMATION_ENABLED', 'true').lower() == 'true':
        tasks.append(asyncio.create_task(automation_loop()))
    if os.getenv('NEWS_EMAIL_DELIVERY_ENABLED', 'false').lower() == 'true':
        tasks.append(asyncio.create_task(newsletter_loop()))
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            with suppress(asyncio.CancelledError):
                await task

app = FastAPI(title='VesperSignal News API', lifespan=lifespan)
for router in (news, research, discovery, feedback, mvp, accounts, social):
    app.include_router(router)
