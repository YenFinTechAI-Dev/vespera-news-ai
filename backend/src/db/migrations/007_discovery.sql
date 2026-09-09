ALTER TABLE news_articles DROP CONSTRAINT IF EXISTS news_articles_category_check;
ALTER TABLE news_articles ADD CONSTRAINT news_articles_category_check CHECK(category IN ('economy','technology','research','ai_tools','ai','tools','financial_crime','web'));
