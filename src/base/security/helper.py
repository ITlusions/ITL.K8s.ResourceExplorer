import logging

logger = logging.getLogger("audit")

def log_audit_event(user: str, action: str, details: str):
    """Logs an audit event."""
    logger.info(f"Audit Event | User: {user} | Action: {action} | Details: {details}")