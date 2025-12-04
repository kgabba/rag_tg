DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS users;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(1536)
    -- потом сюда можно добавить: source, filename, page, created_at и т.п.
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_tg_id TEXT NOT NULL UNIQUE,  -- один юзер = один tg_id
    credits INT NOT NULL DEFAULT 0    -- удобнее, чтобы не было NULL
);