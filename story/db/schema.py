from __future__ import annotations

import duckdb

TABLES = """
CREATE TABLE IF NOT EXISTS config (
    id INTEGER DEFAULT 1 PRIMARY KEY,
    harness VARCHAR DEFAULT 'claude-code',
    provider VARCHAR,
    supported_scenes JSON DEFAULT '["api"]',
    max_concurrent_runs INTEGER DEFAULT 3
);

CREATE TABLE IF NOT EXISTS providers (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    type VARCHAR NOT NULL,
    config JSON NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS harnesses (
    name VARCHAR PRIMARY KEY,
    provider_name VARCHAR,
    config JSON DEFAULT '{"timeout_seconds": 300}'
);

CREATE TABLE IF NOT EXISTS collections (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    target VARCHAR,
    harness VARCHAR,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS stories (
    id VARCHAR PRIMARY KEY,
    collection_id VARCHAR,
    title VARCHAR NOT NULL,
    scene VARCHAR NOT NULL,
    target VARCHAR,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS runs (
    id VARCHAR PRIMARY KEY,
    story_id VARCHAR NOT NULL,
    batch_id VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'queued',
    harness VARCHAR NOT NULL,
    target VARCHAR,
    env JSON,
    step_summary JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS steps (
    run_id VARCHAR NOT NULL,
    idx INTEGER NOT NULL,
    chapter VARCHAR,
    description VARCHAR,
    narrative TEXT,
    status VARCHAR NOT NULL DEFAULT 'pending',
    actual JSON,
    assertions JSON,
    duration_ms INTEGER,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    PRIMARY KEY (run_id, idx)
);
"""

SEED_HARNESSES = [
    ("claude-code", '{"timeout_seconds": 300}'),
    ("claude-agent-sdk", '{"timeout_seconds": 300}'),
    ("opencode", '{"timeout_seconds": 300}'),
]


def init_db(conn: duckdb.DuckDBPyConnection) -> None:
    for stmt in TABLES.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)

    # Seed config
    row = conn.execute("SELECT count(*) FROM config").fetchone()
    if row and row[0] == 0:
        conn.execute("INSERT INTO config (id) VALUES (1)")

    # Seed harnesses
    for name, cfg in SEED_HARNESSES:
        conn.execute(
            "INSERT OR IGNORE INTO harnesses (name, config) VALUES (?, ?)",
            [name, cfg],
        )
