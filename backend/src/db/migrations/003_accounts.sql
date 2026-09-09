CREATE TABLE IF NOT EXISTS app_users (
 id uuid PRIMARY KEY, name varchar(100) NOT NULL, email varchar(254) UNIQUE NOT NULL,
 password_hash text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS app_sessions (
 token_hash text PRIMARY KEY, user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
 expires_at timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS app_conversations (
 id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
 title text NOT NULL, messages jsonb NOT NULL DEFAULT '[]', updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS app_conversations_owner ON app_conversations(user_id,updated_at DESC);
CREATE TABLE IF NOT EXISTS app_usage (
 user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE, day date NOT NULL,
 requests integer NOT NULL DEFAULT 0, PRIMARY KEY(user_id,day)
);
CREATE TABLE IF NOT EXISTS app_auth_limits (
 key text PRIMARY KEY, window_start timestamptz NOT NULL, attempts integer NOT NULL
);
