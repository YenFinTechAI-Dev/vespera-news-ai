ALTER TABLE news_summaries ADD COLUMN IF NOT EXISTS key_points jsonb NOT NULL DEFAULT '[]'::jsonb;
CREATE TABLE IF NOT EXISTS news_ai_jobs (
 article_id uuid PRIMARY KEY REFERENCES news_articles(id) ON DELETE CASCADE,
 status text NOT NULL DEFAULT 'pending', attempts integer NOT NULL DEFAULT 0,
 next_attempt timestamptz NOT NULL DEFAULT now(), priority_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS news_ai_usage (day date PRIMARY KEY, attempts integer NOT NULL);
CREATE TABLE IF NOT EXISTS news_pipeline_state (
 id integer PRIMARY KEY CHECK(id=1), last_refresh timestamptz,
 last_success timestamptz, last_result jsonb NOT NULL DEFAULT '{}'
);
