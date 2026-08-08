-- HomeHelp AI (V1) Supabase Database Schema

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'NEW', -- NEW, ACTIVE, INACTIVE
    source VARCHAR(50) NOT NULL DEFAULT 'WHATSAPP',
    activation_step VARCHAR(50) NOT NULL DEFAULT 'STARTED_CHAT' -- STARTED_CHAT, REGISTERED_FIRST_WORKER, LOGGED_FIRST_EVENT, GENERATED_FIRST_PAYMENT, RETURNING_USER
);

-- Index for phone number lookup
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);

-- 2. WORKERS TABLE
CREATE TABLE IF NOT EXISTS workers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL DEFAULT 'Domestic Worker',
    monthly_salary NUMERIC(10, 2) NOT NULL CHECK (monthly_salary >= 0),
    working_days_per_month INT NOT NULL DEFAULT 26 CHECK (working_days_per_month > 0),
    weekly_off VARCHAR(50) NOT NULL DEFAULT 'Sunday',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for user_id lookup
CREATE INDEX IF NOT EXISTS idx_workers_user_id ON workers(user_id);
CREATE INDEX IF NOT EXISTS idx_workers_user_name ON workers(user_id, lower(name));

-- 3. EVENTS TABLE (Immutable)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- ABSENT, HALF_DAY, PLANNED_LEAVE, ADVANCE, BONUS, PAYMENT
    event_date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount NUMERIC(10, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for worker and date range query
CREATE INDEX IF NOT EXISTS idx_events_worker_date ON events(worker_id, event_date);

-- 4. ANALYTICS EVENTS TABLE
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_name VARCHAR(100) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for user and event metrics
CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_name ON analytics_events(event_name);
