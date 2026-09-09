CREATE TABLE IF NOT EXISTS app_social_identities (
 provider text NOT NULL CHECK (provider IN ('google','github','facebook')),
 subject text NOT NULL, user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
 PRIMARY KEY(provider, subject)
);
CREATE TABLE IF NOT EXISTS app_oauth_attempts (
 state_hash text PRIMARY KEY, provider text NOT NULL, nonce text NOT NULL,
 verifier text NOT NULL, expires_at timestamptz NOT NULL
);
