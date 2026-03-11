-- Create the application database objects inside RicashDB.
-- This file is mounted into the official postgres image and executed on first boot.

CREATE TABLE IF NOT EXISTS "Bookmakers" (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    link TEXT,
    min_dep NUMERIC(5, 2),
    cpa NUMERIC(5, 2),
    rev NUMERIC(5, 2),
    priority INTEGER NOT NULL DEFAULT 0,
    avoid_with TEXT,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    type TEXT,
    opening_time TIME,
    closing_time TIME
);

INSERT INTO "Bookmakers" (
    id,
    name,
    link,
    min_dep,
    cpa,
    rev,
    priority,
    avoid_with,
    active,
    type,
    opening_time,
    closing_time
)
VALUES
    ('SISAL', 'SISAL', 'https://google.it/sisal', 20, 65, 2, 1, 'LOTTOMATICA, SNAI', TRUE, 'IT', '09:01', '18:00'),
    ('GOLDBET', 'GOLDBET', 'https://google.it/goldbet', 1000, 1000, 0, 2, NULL, TRUE, 'IT', '09:01', '18:00'),
    ('LOTTOMATICA', 'LOTTOMATICA', 'https://google.it/lottomatica', 1000, 1000, 0, 3, NULL, FALSE, 'IT', '09:01', '18:00'),
    ('SNAI', 'SNAI', 'https://google.it/snai', 1000, 1000, 0, 0, NULL, TRUE, 'IT', '09:01', '18:00'),
    ('EUROBET', 'EUROBET', 'https://google.it/eurobet', 1000, 1000, 0, 0, NULL, FALSE, 'IT', '09:01', '18:00'),
    ('LEOVEGAS_LOW', 'LEOVEGAS', 'https://google.it/leovegas_low', 50, 50, 0, 3, 'LEOVEGAS_MID, LEOVEGAS_HIGH', FALSE, 'IT', '09:01', '18:00'),
    ('LEOVEGAS_MID', 'LEOVEGAS', 'https://google.it/leovegas_mid', 100, 100, 0, 2, 'LEOVEGAS_LOW, LEOVEGAS_HIGH', FALSE, 'IT', '09:01', '18:00'),
    ('LEOVEGAS_HIGH', 'LEOVEGAS', 'https://google.it/leovegas_high', 150, 150, 0, 1, 'LEOVEGAS_LOW, LEOVEGAS_MID', FALSE, 'IT', '09:01', '18:00'),
    ('POKERSTAR', 'POKERSTAR', 'https://google.it/pokerstars', 1000, 1000, 0, 0, 'SISAL', FALSE, 'IT', '09:01', '18:00'),
    ('PLANETWIN', 'PLANETWIN', 'https://google.it/planetwin', 1000, 1000, 0, 0, NULL, FALSE, 'IT', '09:01', '18:00'),
    ('Spinnigranny', 'Spinnigranny', 'https://google.it/spinnigranny', 50, 100, 0, 0, NULL, FALSE, 'COM', '18:01', '09:00'),
    ('Vincispin', 'Vincispin', 'https://google.it/vincispion', 50, 100, 0, 0, NULL, TRUE, 'COM', '18:01', '09:00'),
    ('Spinmama', 'Spinmama', 'https://google.it/spinmama', 50, 100, 0, 0, NULL, FALSE, 'COM', '18:01', '09:00'),
    ('Needforslot', 'Needforslot', 'https://google.it/needforslot', 20, 50, 0, 1, NULL, FALSE, 'COM', '18:01', '09:00'),
    ('Mystake', 'Mystake', 'https://google.it/mystake', 30, 60, 0, 2, NULL, FALSE, 'COM', '18:01', '09:00')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    link = EXCLUDED.link,
    min_dep = EXCLUDED.min_dep,
    cpa = EXCLUDED.cpa,
    rev = EXCLUDED.rev,
    priority = EXCLUDED.priority,
    avoid_with = EXCLUDED.avoid_with,
    active = EXCLUDED.active,
    type = EXCLUDED.type,
    opening_time = EXCLUDED.opening_time,
    closing_time = EXCLUDED.closing_time;

