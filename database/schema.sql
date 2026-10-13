PRAGMA foreign_keys = ON;

-- =========================================
-- 1. Brand Profiles
-- =========================================

CREATE TABLE IF NOT EXISTS brand_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL,
    official_website TEXT,
    description TEXT,
    logo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- 2. Official Assets
-- =========================================

CREATE TABLE IF NOT EXISTS official_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    asset_type TEXT NOT NULL,
    platform TEXT,
    asset_name TEXT NOT NULL,
    asset_url TEXT,
    publisher TEXT,
    verified INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (brand_id)
        REFERENCES brand_profiles(id)
        ON DELETE CASCADE
);


-- =========================================
-- 3. Detection Results
-- =========================================

CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    target_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_url TEXT,
    publisher TEXT,
    description TEXT,
    name_similarity REAL DEFAULT 0,
    risk_score INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'Low',
    reasons TEXT,
    status TEXT DEFAULT 'Needs Review',
    is_official INTEGER DEFAULT 0,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (brand_id)
        REFERENCES brand_profiles(id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================
-- 4. Scan History
-- =========================================

CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER,
    scan_type TEXT NOT NULL,
    target_name TEXT,
    risk_score INTEGER DEFAULT 0,
    result_status TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (brand_id)
        REFERENCES brand_profiles(id)
        ON DELETE SET NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================
-- 5. Users
-- =========================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    password_reset_nonce TEXT,
    role TEXT DEFAULT 'analyst',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- 6. Useful Indexes
-- =========================================

CREATE INDEX IF NOT EXISTS idx_detections_brand
ON detections(brand_id);

CREATE INDEX IF NOT EXISTS idx_detections_risk
ON detections(risk_level);

CREATE INDEX IF NOT EXISTS idx_detections_status
ON detections(status);

CREATE INDEX IF NOT EXISTS idx_assets_brand
ON official_assets(brand_id);

CREATE INDEX IF NOT EXISTS idx_scan_history_brand
ON scan_history(brand_id);
