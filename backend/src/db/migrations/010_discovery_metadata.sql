ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS discovery_kind text;
ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS publication_date_unknown boolean NOT NULL DEFAULT false;
