CREATE TABLE IF NOT EXISTS news_feedback (
 id uuid PRIMARY KEY,
 rating integer NOT NULL CHECK(rating BETWEEN 1 AND 5),
 comment text NOT NULL DEFAULT '' CHECK(length(comment)<=2000),
 language text NOT NULL CHECK(language IN ('vi','en')),
 created_at timestamptz NOT NULL DEFAULT now()
);
