ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS source_language TEXT NOT NULL DEFAULT 'vi'
    CHECK (source_language IN ('vi','en'));
ALTER TABLE news_articles DROP CONSTRAINT IF EXISTS news_articles_category_check;
ALTER TABLE news_articles ADD CONSTRAINT news_articles_category_check
    CHECK (category IN ('economy','technology','ai','research','tools','ai_tools','financial_crime'));
