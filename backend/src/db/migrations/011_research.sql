ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS discovery_evidence jsonb;
CREATE TABLE IF NOT EXISTS research_answers (
 user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
 request_hash text NOT NULL, status text NOT NULL, answer jsonb,
 updated_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(user_id,request_hash)
);
