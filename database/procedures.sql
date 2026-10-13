-- ============================================================================
-- FraudShield: Stored Procedures
-- Encapsulates atomic transactional workflows at the database tier
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_update_case_status$$
CREATE PROCEDURE sp_update_case_status(
    IN p_case_id INT,
    IN p_user_id INT,
    IN p_new_status VARCHAR(30),
    IN p_notes TEXT
)
proc_label: BEGIN
    DECLARE v_old_status VARCHAR(30);
    DECLARE v_user_role VARCHAR(20);
    DECLARE v_case_exists INT DEFAULT 0;

    -- Validate target status parameter
    IF p_new_status NOT IN ('open', 'investigating', 'resolved_fraud', 'resolved_legitimate') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid case status provided.';
    END IF;

    -- Check case existence and lock record
    SELECT COUNT(*), case_status INTO v_case_exists, v_old_status
    FROM investigation_cases
    WHERE id = p_case_id
    GROUP BY case_status;

    IF v_case_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Case ID not found.';
    END IF;

    -- Check if user is reopening a resolved case
    IF v_old_status IN ('resolved_fraud', 'resolved_legitimate') AND p_new_status IN ('open', 'investigating') THEN
        SELECT role INTO v_user_role FROM users WHERE id = p_user_id;
        IF v_user_role IS NULL OR v_user_role != 'admin' THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Authorization Failure: Only administrators can reopen resolved investigation cases.';
        END IF;
    END IF;

    -- Update investigation case
    UPDATE investigation_cases
    SET case_status = p_new_status,
        resolution_notes = CASE 
            WHEN p_notes IS NOT NULL AND TRIM(p_notes) != '' THEN p_notes 
            ELSE resolution_notes 
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_case_id;

    -- If a note was provided, save to investigation notes
    IF p_notes IS NOT NULL AND TRIM(p_notes) != '' THEN
        INSERT INTO investigation_notes (case_id, user_id, note_text, created_at)
        VALUES (p_case_id, p_user_id, p_notes, CURRENT_TIMESTAMP);
    END IF;

    -- Record atomic audit log entry
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
    VALUES (
        p_user_id,
        'CASE_STATUS_UPDATED',
        'investigation_cases',
        p_case_id,
        JSON_OBJECT(
            'old_status', v_old_status,
            'new_status', p_new_status,
            'notes', p_notes
        ),
        CURRENT_TIMESTAMP
    );

END proc_label$$

DELIMITER ;
