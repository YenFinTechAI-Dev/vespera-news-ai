# Render with Hugging Face

Deploy backend and frontend as separate Web Services using the commands in README.md.

Backend environment:

```env
AI_PROVIDER=huggingface
HF_MODEL=Qwen/Qwen3-4B-Instruct-2507:nscale
HF_TOKEN=<enter privately in Render>
DATABASE_URL=<your Neon connection string>
CHAT_PROXY_TOKEN=<long random secret>
NEWS_AUTOMATION_ENABLED=true
NEWS_EMAIL_DELIVERY_ENABLED=false
```

Frontend environment:

```env
BACKEND_URL=https://<your-backend-service>.onrender.com
CHAT_PROXY_TOKEN=<same backend secret>
```

Never use NEXT_PUBLIC_ for these secrets. The HF router is called only by Python. Ollama is not required for this configuration. HF inference is metered, not unlimited free AI; account credits and provider availability apply. Existing daily limits and cached summaries remain enabled. Set NEWS_AUTOMATION_ENABLED=false to pause background RSS/summary jobs.

The default model returned HTTP 200 with JSON during integration testing. This does not guarantee future availability. Provider errors stop synthesis instead of presenting fabricated summaries. Migration 015 scopes provider backoff so old Z.ai failures do not block Hugging Face.

After deployment, check backend /health, open frontend /news, then test an authenticated synthesis. Do not mark deployment complete merely because the build passed.
