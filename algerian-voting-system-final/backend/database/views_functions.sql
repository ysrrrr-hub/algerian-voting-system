-- ============================================================
-- Views & Stored Procedures
-- ============================================================

-- ==================== View: إحصائيات التصويت ====================
CREATE OR REPLACE VIEW voting_statistics AS
SELECT
    (SELECT COUNT(*) FROM voters) AS total_voters,
    (SELECT COUNT(*) FROM voters WHERE has_voted = TRUE) AS voted_count,
    (SELECT COUNT(*) FROM voters WHERE has_voted = FALSE) AS remaining_count,
    (SELECT ROUND(
        (COUNT(*) FILTER (WHERE has_voted = TRUE) * 100.0) / NULLIF(COUNT(*), 0), 2
    ) FROM voters) AS turnout_percentage,
    (SELECT COUNT(*) FROM blockchain) AS blockchain_length,
    (SELECT MAX(timestamp) FROM blockchain) AS last_vote_time;

-- ==================== دالة: التحقق من أهلية الناخب ====================
CREATE OR REPLACE FUNCTION check_voter_eligibility(p_nfc_uid VARCHAR)
RETURNS TABLE(
    eligible      BOOLEAN,
    message       TEXT,
    voter_name_ar VARCHAR,
    voter_name_fr VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        CASE
            WHEN v.voter_id IS NULL THEN FALSE
            WHEN v.has_voted = TRUE  THEN FALSE
            ELSE TRUE
        END AS eligible,
        CASE
            WHEN v.voter_id IS NULL THEN 'بطاقة غير مسجلة / Carte non enregistrée'
            WHEN v.has_voted = TRUE  THEN 'تم التصويت مسبقاً / Déjà voté'
            ELSE                          'مؤهل للتصويت / Éligible'
        END AS message,
        v.full_name_ar,
        v.full_name_fr
    FROM voters v
    WHERE v.nfc_uid = p_nfc_uid;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE,
            'بطاقة غير مسجلة / Carte non enregistrée'::TEXT,
            NULL::VARCHAR, NULL::VARCHAR;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ==================== دالة: تسجيل إجراء ====================
CREATE OR REPLACE FUNCTION log_vote_attempt(
    p_nfc_uid     VARCHAR,
    p_ip_address  VARCHAR,
    p_success     BOOLEAN,
    p_error_msg   TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_log (action_type, nfc_uid, ip_address, success, error_message)
    VALUES ('VOTE_ATTEMPT', p_nfc_uid, p_ip_address, p_success, p_error_msg);
END;
$$ LANGUAGE plpgsql;

-- ==================== دالة: إحصائيات حسب الولاية ====================
CREATE OR REPLACE FUNCTION get_stats_by_wilaya()
RETURNS TABLE(
    wilaya       VARCHAR,
    total_voters BIGINT,
    voted_count  BIGINT,
    turnout_pct  NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.wilaya,
        COUNT(*)::BIGINT AS total_voters,
        COUNT(*) FILTER (WHERE v.has_voted = TRUE)::BIGINT AS voted_count,
        ROUND(
            (COUNT(*) FILTER (WHERE v.has_voted = TRUE) * 100.0)
            / NULLIF(COUNT(*), 0), 2
        ) AS turnout_pct
    FROM voters v
    GROUP BY v.wilaya
    ORDER BY v.wilaya;
END;
$$ LANGUAGE plpgsql;
