-- Full Election Reset (preserves voters, candidates, admins, RSA keys)

BEGIN;

-- 1. Clear vote-related tables
DELETE FROM vote_receipts;
DELETE FROM votes;
DELETE FROM blockchain;
DELETE FROM audit_log;
DELETE FROM admin_sessions;

-- 2. Reset voters (mark all as not voted)
UPDATE voters SET has_voted = FALSE;

-- 3. Reset election status
UPDATE elections SET status = 'PRELIMINARY' WHERE status IS NOT NULL;

-- 4. Reset auto-increment sequences
ALTER SEQUENCE IF EXISTS blockchain_block_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS votes_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS vote_receipts_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS audit_log_id_seq RESTART WITH 1;

COMMIT;

-- Verification
SELECT 'votes' AS table_name, COUNT(*) AS count FROM votes
UNION ALL SELECT 'blockchain', COUNT(*) FROM blockchain
UNION ALL SELECT 'vote_receipts', COUNT(*) FROM vote_receipts
UNION ALL SELECT 'audit_log', COUNT(*) FROM audit_log
UNION ALL SELECT 'voters_voted', COUNT(*) FROM voters WHERE has_voted = TRUE
UNION ALL SELECT 'voters_total', COUNT(*) FROM voters
UNION ALL SELECT 'candidates', COUNT(*) FROM candidates;
