# News operations

The worker only queues articles from the last 30 days and uses `NEWS_AI_DAILY_LIMIT` (default 200) for background summaries. This prevents a first production boot from spending the entire daily budget on old imported articles. Search and source previews continue to work when the AI budget is exhausted.
