from __future__ import annotations
from typing import Final
WORKFLOW_ENTITY_TYPE: Final[str] = "workflow_instance"
DEFAULT_WORKFLOW_NAME: Final[str] = "malone_governed_execution"
DEFAULT_WORKFLOW_VERSION: Final[str] = "v1"
WORKFLOW_STATUS_PENDING: Final[str] = "pending"
WORKFLOW_STATUS_IN_PROGRESS: Final[str] = "in_progress"
WORKFLOW_STATUS_COMPLETED: Final[str] = "completed"
WORKFLOW_STATUS_FAILED: Final[str] = "failed"
WORKFLOW_STATUS_BLOCKED: Final[str] = "blocked"
WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL: Final[str] = "blocked_pending_approval"
WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION: Final[str] = "blocked_pending_clarification"
STEP_STATUS_PENDING: Final[str] = "pending"
STEP_STATUS_COMPLETED: Final[str] = "completed"
STEP_STATUS_BLOCKED: Final[str] = "blocked"
STEP_STATUS_FAILED: Final[str] = "failed"
APPROVAL_ENTITY_TYPE: Final[str] = "approval_request"
APPROVAL_STATUS_PENDING: Final[str] = "pending"
APPROVAL_STATUS_APPROVED: Final[str] = "approved"
APPROVAL_STATUS_REJECTED: Final[str] = "rejected"
CLARIFICATION_ENTITY_TYPE: Final[str] = "clarification_request"
CLARIFICATION_STATUS_PENDING: Final[str] = "pending"
CLARIFICATION_STATUS_RESOLVED: Final[str] = "resolved"
CLARIFICATION_STATUS_CANCELLED: Final[str] = "cancelled"
HANDLER_KEY_MALONE_VALIDATE_ACTION: Final[str] = "malone.validate_action"
HANDLER_KEY_MALONE_EXECUTE_ACTION: Final[str] = "malone.execute_action"
HANDLER_KEY_WORKFLOW_MARK_COMPLETE: Final[str] = "workflow.mark_complete"
REQUIRED_BUILTIN_HANDLER_KEYS: Final[tuple[str, ...]] = (
    HANDLER_KEY_MALONE_VALIDATE_ACTION,
    HANDLER_KEY_MALONE_EXECUTE_ACTION,
    HANDLER_KEY_WORKFLOW_MARK_COMPLETE,
)
WORKFLOW_ACTIVE_STATUSES: Final[set[str]] = {WORKFLOW_STATUS_PENDING, WORKFLOW_STATUS_IN_PROGRESS}
WORKFLOW_RESUMABLE_STATUSES: Final[set[str]] = {WORKFLOW_STATUS_PENDING, WORKFLOW_STATUS_IN_PROGRESS, WORKFLOW_STATUS_BLOCKED, WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL, WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION}
WORKFLOW_TERMINAL_STATUSES: Final[set[str]] = {WORKFLOW_STATUS_COMPLETED, WORKFLOW_STATUS_FAILED}
def get_required_builtin_handler_keys() -> list[str]:
    return list(REQUIRED_BUILTIN_HANDLER_KEYS)
