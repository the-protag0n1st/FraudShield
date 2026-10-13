-- ============================================================================
-- FraudShield: Database Triggers
-- Enforces data integrity and immutable audit logging at the database tier
-- ============================================================================

DELIMITER $$

-- 1. Automatically manage resolved_at timestamp based on case_status
DROP TRIGGER IF EXISTS trg_case_resolved_at$$
CREATE TRIGGER trg_case_resolved_at
BEFORE UPDATE ON investigation_cases
FOR EACH ROW
BEGIN
    IF NEW.case_status IN ('resolved_fraud', 'resolved_legitimate') THEN
        IF OLD.case_status NOT IN ('resolved_fraud', 'resolved_legitimate') OR OLD.resolved_at IS NULL THEN
            SET NEW.resolved_at = CURRENT_TIMESTAMP;
        END IF;
    ELSE
        SET NEW.resolved_at = NULL;
    END IF;
END$$

-- 2. Prevent updates to audit log entries (tamper-evident audit trail)
DROP TRIGGER IF EXISTS trg_audit_logs_no_update$$
CREATE TRIGGER trg_audit_logs_no_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Security Policy Violation: Audit log records are immutable and cannot be modified.';
END$$

-- 3. Prevent deletions from audit log entries
DROP TRIGGER IF EXISTS trg_audit_logs_no_delete$$
CREATE TRIGGER trg_audit_logs_no_delete
BEFORE DELETE ON audit_logs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Security Policy Violation: Audit log records are immutable and cannot be deleted.';
END$$

DELIMITER ;
