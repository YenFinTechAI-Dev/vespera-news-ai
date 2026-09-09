CREATE TABLE IF NOT EXISTS news_interests (
 user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
 kind text NOT NULL CHECK(kind IN ('topic','company','industry')),
 term text NOT NULL CHECK(length(term) BETWEEN 2 AND 100),
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(user_id,kind,term)
);
CREATE TABLE IF NOT EXISTS news_digest_preferences (
 user_id uuid PRIMARY KEY REFERENCES app_users(id) ON DELETE CASCADE,
 language text NOT NULL DEFAULT 'vi' CHECK(language IN ('vi','en')),
 enabled boolean NOT NULL DEFAULT false,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS news_email_outbox (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
 day date NOT NULL,
 status text NOT NULL CHECK(status IN ('pending','sending','sent','failed','uncertain')),
 subject text NOT NULL, body text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), sent_at timestamptz,
 UNIQUE(user_id,day)
);
