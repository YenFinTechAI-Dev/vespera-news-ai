CREATE TABLE IF NOT EXISTS news_provider_state (
 id INTEGER PRIMARY KEY CHECK(id=1),
 reason TEXT NOT NULL,
 http_status INTEGER,
 retry_at TIMESTAMPTZ NOT NULL
);
