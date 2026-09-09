ALTER TABLE news_feedback ADD COLUMN IF NOT EXISTS discord_sent_at timestamptz;
ALTER TABLE news_feedback ADD COLUMN IF NOT EXISTS discord_attempts integer NOT NULL DEFAULT 0;
ALTER TABLE news_feedback ADD COLUMN IF NOT EXISTS discord_next_attempt timestamptz NOT NULL DEFAULT now();
