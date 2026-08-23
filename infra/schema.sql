-- Phase 0: Infrastructure Schema for LifeKit SQLite Database

CREATE TABLE user_bios (
    bio_id TEXT PRIMARY KEY,
    goals JSON NOT NULL,
    primary_motivation TEXT,
    habits JSON[] null,
    preferred_checkin_time TEXT,
    weekly_time_budget_minutes INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE intents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(id),
    goal_id TEXT REFERENCES goals(id),
    type TEXT CHECK(type IN ('concept_check', 'habit_log', 'journal', 'content_digest')),
    invitation_text TEXT NOT NULL,
    context_snapshot JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exercise_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id TEXT REFERENCES goals(id),
    type TEXT CHECK(type IN ('journal', 'feynman', 'action_log', 'content_digest')),
    intent_id INTEGER,
    context_blob JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exercise_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER REFERENCES exercise_instances(id),
    response TEXT,
    metadata JSON,
    tone_analysis TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_title TEXT NOT NULL,
    section_reference TEXT,
    content_chunk TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE goals (
    goal_id TEXT PRIMARY KEY,
    user_bio_id TEXT REFERENCES user_bios(bio_id),
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'revival')) DEFAULT 'active',
    urgency_score REAL DEFAULT 0.5,
    current_interval_days INT DEFAULT 7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);