-- ============================================================
-- نظام التصويت الإلكتروني الجزائري - Database Schema v1.0
-- Algerian Blockchain-Based Electronic Voting System
-- ============================================================

DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS blockchain CASCADE;
DROP TABLE IF EXISTS admin_sessions CASCADE;
DROP TABLE IF EXISTS admin_users CASCADE;
DROP TABLE IF EXISTS encryption_keys CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS voters CASCADE;

-- ==================== جدول الناخبين ====================
CREATE TABLE voters (
    voter_id          SERIAL PRIMARY KEY,
    nfc_uid           VARCHAR(64) UNIQUE NOT NULL,
    full_name_ar      VARCHAR(255) NOT NULL,
    full_name_fr      VARCHAR(255) NOT NULL,
    date_of_birth     DATE NOT NULL,
    wilaya            VARCHAR(100) NOT NULL,
    has_voted         BOOLEAN DEFAULT FALSE,
    voted_at          TIMESTAMP,
    registration_date TIMESTAMP DEFAULT NOW(),
    CONSTRAINT chk_voter_age CHECK (
        EXTRACT(YEAR FROM AGE(date_of_birth)) >= 18
    )
);

-- ==================== جدول المرشحين ====================
CREATE TABLE candidates (
    candidate_id       SERIAL PRIMARY KEY,
    full_name_ar       VARCHAR(255) NOT NULL,
    full_name_fr       VARCHAR(255) NOT NULL,
    party_name_ar      VARCHAR(255),
    party_name_fr      VARCHAR(255),
    photo_url          VARCHAR(500),
    program_summary_ar TEXT,
    program_summary_fr TEXT,
    display_order      INT NOT NULL UNIQUE,
    is_active          BOOLEAN DEFAULT TRUE,
    created_at         TIMESTAMP DEFAULT NOW()
);

-- ==================== جدول البلوكشين ====================
CREATE TABLE blockchain (
    block_id       SERIAL PRIMARY KEY,
    block_index    INT NOT NULL UNIQUE,
    timestamp      TIMESTAMP DEFAULT NOW(),
    encrypted_vote TEXT NOT NULL,
    previous_hash  VARCHAR(64) NOT NULL,
    current_hash   VARCHAR(64) UNIQUE NOT NULL,
    nonce          INT DEFAULT 0,
    CONSTRAINT chk_hash_length CHECK (
        LENGTH(current_hash) = 64 AND LENGTH(previous_hash) = 64
    )
);

-- ==================== جدول سجل التدقيق ====================
CREATE TABLE audit_log (
    log_id        SERIAL PRIMARY KEY,
    action_type   VARCHAR(50) NOT NULL,
    nfc_uid       VARCHAR(64),
    ip_address    VARCHAR(45),
    user_agent    TEXT,
    success       BOOLEAN NOT NULL,
    error_message TEXT,
    timestamp     TIMESTAMP DEFAULT NOW()
);

-- ==================== جدول المفاتيح ====================
CREATE TABLE encryption_keys (
    key_id                SERIAL PRIMARY KEY,
    public_key            TEXT NOT NULL,
    private_key_encrypted TEXT NOT NULL,
    key_algorithm         VARCHAR(50) DEFAULT 'RSA-4096',
    created_at            TIMESTAMP DEFAULT NOW(),
    expires_at            TIMESTAMP,
    is_active             BOOLEAN DEFAULT TRUE
);

-- ==================== جدول المشرفين ====================
CREATE TABLE admin_users (
    admin_id      SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    role          VARCHAR(50) NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    last_login    TIMESTAMP,
    created_at    TIMESTAMP DEFAULT NOW(),
    CONSTRAINT chk_role CHECK (role IN ('SUPERVISOR', 'ADMIN'))
);

-- ==================== جدول الجلسات ====================
CREATE TABLE admin_sessions (
    session_id SERIAL PRIMARY KEY,
    admin_id   INT NOT NULL REFERENCES admin_users(admin_id) ON DELETE CASCADE,
    token      VARCHAR(128) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE
);

-- ==================== الفهارس ====================
CREATE INDEX idx_voters_nfc       ON voters(nfc_uid);
CREATE INDEX idx_voters_voted     ON voters(has_voted);
CREATE INDEX idx_voters_wilaya    ON voters(wilaya);
CREATE INDEX idx_blockchain_index ON blockchain(block_index);
CREATE INDEX idx_blockchain_hash  ON blockchain(current_hash);
CREATE INDEX idx_blockchain_prev  ON blockchain(previous_hash);
CREATE INDEX idx_audit_timestamp  ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_action     ON audit_log(action_type);
CREATE INDEX idx_audit_nfc        ON audit_log(nfc_uid);
CREATE INDEX idx_sessions_token   ON admin_sessions(token);
CREATE INDEX idx_sessions_expiry  ON admin_sessions(expires_at);

-- ==================== الأذونات ====================
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO voting_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO voting_admin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO voting_admin;
