CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name TEXT NOT NULL CHECK (length(trim(source_name)) > 0),
    source_url TEXT NOT NULL UNIQUE CHECK (source_url ~ '^https?://'),
    original_title TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('economy', 'technology')),
    published_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'rejected'))
);

CREATE TABLE IF NOT EXISTS news_summaries (
    article_id UUID NOT NULL REFERENCES news_articles(id) ON DELETE CASCADE,
    language TEXT NOT NULL CHECK (language IN ('vi', 'en')),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    summary TEXT NOT NULL CHECK (length(trim(summary)) > 0),
    ai_generated BOOLEAN NOT NULL DEFAULT TRUE,
    model_name TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (article_id, language)
);

CREATE INDEX IF NOT EXISTS news_published_date_idx
    ON news_articles (published_at DESC, id DESC) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS news_category_date_idx
    ON news_articles (category, published_at DESC) WHERE status = 'published';
