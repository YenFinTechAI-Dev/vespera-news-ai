CREATE TABLE IF NOT EXISTS research_guest_ip_usage (
 key text NOT NULL, day date NOT NULL, requests integer NOT NULL DEFAULT 0,
 PRIMARY KEY(key,day)
);
