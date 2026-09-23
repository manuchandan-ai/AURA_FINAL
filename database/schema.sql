-- ============================================
-- AURA — Adaptive Unified Reasoning Assistant
-- Database Schema (SQLite)
-- ============================================
-- Designed for SQLite with clean structure
-- allowing future migration to MySQL/PostgreSQL.
-- ============================================

-- Users: Core authentication table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    -- Status: pending, approved, rejected, waitlisted, banned, removed
    status TEXT NOT NULL DEFAULT 'pending',
    -- Role: user, admin
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Profiles: Extended user information
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    country TEXT DEFAULT 'India',
    profile_photo TEXT,  -- File path to stored photo
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Analysis History: Records of all analyses performed
CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    input_type TEXT NOT NULL DEFAULT 'text',  -- text, image, url, document, audio, mixed
    input_summary TEXT,                        -- Brief summary of what was analyzed
    detected_module TEXT,                      -- trust, verify, find, life, investigate, heritage
    intent TEXT,                               -- Detected intent
    confidence REAL,                           -- Overall confidence (0.0 to 1.0)
    status TEXT NOT NULL DEFAULT 'completed',  -- processing, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Analysis Results: Detailed structured results
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    result_type TEXT NOT NULL DEFAULT 'general',  -- general, signals, correlation, decision, explanation
    result_data TEXT,         -- JSON string with structured result data
    signals TEXT,             -- JSON string with detected signals
    correlation_data TEXT,    -- JSON string with correlation information
    decision TEXT,            -- Decision/recommendation text
    explanation TEXT,         -- Human-readable explanation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
);

-- Uploaded Files: Track all file uploads
CREATE TABLE IF NOT EXISTS uploaded_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    analysis_id INTEGER,     -- NULL if not yet associated with an analysis
    filename TEXT NOT NULL,   -- Stored filename (sanitized/UUID)
    original_filename TEXT NOT NULL,
    file_type TEXT,           -- MIME type or extension
    file_size INTEGER,        -- Size in bytes
    upload_path TEXT NOT NULL, -- Relative path to stored file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE SET NULL
);

-- Modules: Available AURA intelligence modules
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,  -- URL-friendly identifier
    description TEXT,
    icon TEXT,                   -- Bootstrap Icon class name
    is_active INTEGER NOT NULL DEFAULT 1,  -- 1=active, 0=inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports: User-submitted reports or system-generated reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    analysis_id INTEGER,
    report_type TEXT NOT NULL DEFAULT 'general',  -- general, suspicious, feedback, bug
    title TEXT,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, reviewed, resolved, dismissed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE SET NULL
);

-- Admin Actions: Audit log for all admin operations
CREATE TABLE IF NOT EXISTS admin_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,  -- approve_user, reject_user, ban_user, waitlist_user, remove_user, review_report, etc.
    target_user_id INTEGER,     -- The user affected by the action (if applicable)
    details TEXT,               -- Additional details or reason
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Re-registration Requests: For banned/removed users requesting access again
CREATE TABLE IF NOT EXISTS reregistration_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reason TEXT NOT NULL,         -- Why the user wants to re-register
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by INTEGER,          -- Admin who reviewed the request
    review_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- V2 Conversational & Goal Tracking Tables
-- ============================================

-- Conversations: Multi-turn chat sessions
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages: Individual messages within a conversation
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender TEXT NOT NULL, -- 'user' or 'aura'
    content TEXT NOT NULL,
    metadata TEXT, -- JSON for modules used, signals, confidence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Goals: User goals and roadmaps
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    progress INTEGER DEFAULT 0, -- 0 to 100
    status TEXT NOT NULL DEFAULT 'active', -- active, completed, abandoned
    roadmap TEXT, -- JSON array of steps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Reminders: Time-based user reminders
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    priority TEXT DEFAULT 'medium', -- low, medium, high
    due_date TIMESTAMP,
    is_completed INTEGER DEFAULT 0, -- 0=false, 1=true
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- Seed Data: Default modules
-- ============================================
INSERT OR IGNORE INTO modules (name, slug, description, icon) VALUES
    ('AURA Trust', 'trust', 'Digital Safety & Suspicious Content Analysis', 'bi-shield-check'),
    ('AURA Verify', 'verify', 'Document & Information Verification', 'bi-file-earmark-check'),
    ('AURA Find', 'find', 'Lost & Found Object Matching', 'bi-search'),
    ('AURA Life', 'life', 'Student & Career Intelligence', 'bi-mortarboard'),
    ('AURA Investigate', 'investigate', 'Evidence & Event Analysis', 'bi-clipboard-data'),
    ('AURA Heritage', 'heritage', 'Historical & Heritage Object Analysis', 'bi-building'),
    ('AURA Access', 'access', 'Accessibility Layer', 'bi-universal-access'),
    ('AURA Create', 'create', 'Generative Design & Content', 'bi-palette'),
    ('AURA Money', 'money', 'Financial Planning & Guidance', 'bi-cash-stack'),
    ('AURA Travel', 'travel', 'Itineraries & Exploration', 'bi-airplane'),
    ('AURA Health', 'health', 'Wellness & Fitness Tracking', 'bi-heart-pulse'),
    ('AURA Learn', 'learn', 'Study Plans & Skill Growth', 'bi-book'),
    ('AURA Shop', 'shop', 'Smart Purchases & Comparisons', 'bi-cart'),
    ('AURA Project', 'project', 'Build & Develop', 'bi-code-slash'),
    ('AURA Future', 'future', 'Scenario Planning & Logic', 'bi-compass');

-- ============================================
-- Indexes for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_module ON analysis_history(detected_module);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_id ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX IF NOT EXISTS idx_reregistration_requests_user_id ON reregistration_requests(user_id);
