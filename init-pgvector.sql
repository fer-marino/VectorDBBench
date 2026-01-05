-- Initializes the pgvector extension in the target database on first cluster init
-- This script is executed by the Postgres Docker entrypoint when the data dir is empty
CREATE EXTENSION IF NOT EXISTS vector;
