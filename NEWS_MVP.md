# News MVP — backend only

No visual changes. Frontend server routes expose `/api/news/mvp/*` using the existing session cookie. Backend routes also appear in `/docs`, under News MVP; private endpoints require gateway and session headers (never put gateway secrets in browser code).

## Available

- GET `sources`: curated source registry with primary/editorial/preprint/community/unreviewed provenance. This labels origin, not truth. arXiv is not automatically peer reviewed.
- GET `stories?language=vi&days=7`: groups recent articles conservatively by title similarity, category, date and numbers. Each story carries all constituent source links and timestamps. This heuristic misses cross-language stories and requires review; it does not verify events.
- GET/POST/DELETE `interests`: authenticated, user-owned topics, companies and industries. POST/DELETE body: `{"kind":"company","term":"OpenAI"}`. Maximum 30 interests.
- GET `digest?language=vi`: personalized preview from followed terms, up to 10 stories; excludes unreviewed/community sources. Source excerpts are explicitly distinguished from AI summaries.
- GET/PUT `email`: subscription configuration; PUT `{"enabled":true,"language":"vi"}`. Local MVP only sends to the account email explicitly approved in the server configuration.
- POST `ask`: `{"question":"What changed in machine learning?","language":"en"}`. Retrieves up to 8 matching collected articles, then uses the existing authenticated AI synthesis, citation validation, language checks and usage limits. Refuses when fewer than two sources have enough evidence.

## Email configuration — disabled by default

Set these privately in `backend/.env`, then restart backend:

```
NEWS_SMTP_HOST=
NEWS_SMTP_PORT=587
NEWS_SMTP_USER=
NEWS_SMTP_PASSWORD=
NEWS_SMTP_FROM=
NEWS_EMAIL_ALLOWED_RECIPIENT=
NEWS_EMAIL_DELIVERY_ENABLED=false
```

Preview with GET digest first. After the recipient is approved and subscribed, explicitly set DELIVERY_ENABLED=true to send. No emails are sent by installing this feature. The worker checks every 15 minutes while backend is running and sends at most once per local day (UTC+7), when matching news exists. Use a dedicated SMTP credential and STARTTLS. Keep secrets out of Git.

The outbox prevents duplicate daily sends. Ambiguous delivery failures are marked uncertain and are not retried automatically. Disable subscription via PUT email enabled=false. This local implementation is not a public bulk mailing service; verified signup and public unsubscribe links remain necessary before opening subscriptions to arbitrary recipients.

## Limits

Stories and personalized matching inspect at most 500 recent dated articles. Q&A searches the last 30 days; unknown dates are excluded. Matching uses normalized keywords and is not a semantic search engine. AI works from excerpts/abstracts, not every full article. Email previews reuse available summaries and do not guarantee immediate translations.
