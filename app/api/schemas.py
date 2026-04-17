from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


ORM_CONFIG = ConfigDict(from_attributes=True, populate_by_name=True)
STRIP_CONFIG = ConfigDict(str_strip_whitespace=True)

APIId = UUID | int | str


class APIBaseModel(BaseModel):
    model_config = STRIP_CONFIG


class ORMBaseModel(BaseModel):
    model_config = ORM_CONFIG


class HealthResponse(BaseModel):
    status: str = "ok"


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str | list[dict[str, Any]] | dict[str, Any]


class StatusResponse(BaseModel):
    status: str
    message: str | None = None


class PaginatedResponse(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0


class LoginRequest(APIBaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(ORMBaseModel):
    id: APIId
    email: EmailStr
    full_name: str | None = None
    role: str
    department: str | None = None
    department_id: APIId | None = None
    is_active: bool = True


class MeResponse(UserResponse):
    pass


class LoginResponse(ORMBaseModel):
    access_token: str
    token_type: str = "bearer"
    user: MeResponse


class ScheduleBase(APIBaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    department: str | None = None
    notes: str | None = None
    recurrence_rule: str | None = None


class ScheduleCreate(ScheduleBase):
    assigned_to: str = Field(..., min_length=1, max_length=255)
    assigned_user_id: APIId | None = None


class ScheduleUpdate(APIBaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    assigned_to: str | None = Field(default=None, min_length=1, max_length=255)
    assigned_user_id: APIId | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    department: str | None = None
    notes: str | None = None
    recurrence_rule: str | None = None
    status: str | None = None


class ScheduleResponse(ORMBaseModel):
    id: APIId
    title: str
    assigned_to: str
    start_time: datetime
    end_time: datetime
    department: str | None = None
    notes: str | None = None
    status: str | None = None
    assigned_user_id: APIId | None = None
    created_by_user_id: APIId | None = None
    cancelled_by_user_id: APIId | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    submitted_at: datetime | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    cancelled_at: datetime | None = None
    rejection_reason: str | None = None
    recurrence_rule: str | None = None


class ScheduleCreateResponse(BaseModel):
    schedule_id: APIId
    schedule: ScheduleResponse
    message: str = "Schedule created"


class ScheduleCancelResponse(BaseModel):
    schedule_id: APIId
    schedule: ScheduleResponse
    message: str = "Schedule cancelled"


class AuditLogResponse(ORMBaseModel):
    id: APIId
    action: str
    entity_type: str
    entity_id: APIId | None = None
    actor_user_id: APIId | None = None
    created_at: datetime | None = None
    meta_json: dict[str, Any] | str | list[Any] | None = None


class DepartmentResponse(ORMBaseModel):
    id: APIId
    code: str
    name: str
    description: str | None = None
    is_active: bool = True


class OperationalSummaryResponse(BaseModel):
    totals: dict[str, Any] = Field(default_factory=dict)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)


class WorkflowActorContext(BaseModel):
    id: APIId | None = None
    email: str | None = None
    role: str | None = None
    department: str | None = None


class WorkflowStepDefinitionResponse(ORMBaseModel):
    id: APIId
    workflow_definition_id: APIId
    name: str
    step_key: str
    step_order: int
    next_step_id: APIId | None = None
    is_terminal: bool = False
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkflowDefinitionResponse(ORMBaseModel):
    id: APIId
    name: str
    version: str
    description: str | None = None
    status: str
    entry_step_id: APIId | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    steps: list[WorkflowStepDefinitionResponse] = Field(default_factory=list)


class WorkflowStepExecutionResponse(ORMBaseModel):
    id: APIId
    workflow_instance_id: APIId
    workflow_step_id: APIId
    status: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    executed_at: datetime | None = None


class WorkflowInstanceResponse(ORMBaseModel):
    id: APIId
    workflow_definition_id: APIId
    workflow_name: str | None = None
    workflow_version: str | None = None
    entity_type: str | None = None
    entity_id: APIId | None = None
    status: str
    current_step_id: APIId | None = None
    current_step_name: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    last_error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    executions: list[WorkflowStepExecutionResponse] = Field(default_factory=list)


class WorkflowInstanceEnvelope(BaseModel):
    workflow_instance: WorkflowInstanceResponse


class WorkflowHandlerListResponse(BaseModel):
    handlers: list[str] = Field(default_factory=list)


class WorkflowStartRequest(APIBaseModel):
    workflow_name: str = Field(..., min_length=1, max_length=255)
    context: dict[str, Any] = Field(default_factory=dict)
    entity_type: str | None = None
    entity_id: APIId | None = None
    version: str | None = None
    auto_run: bool = True


class WorkflowResumeRequest(APIBaseModel):
    context_updates: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequestResponse(ORMBaseModel):
    id: APIId
    workflow_instance_id: APIId
    entity_type: str | None = None
    entity_id: APIId | None = None
    required_role: str
    status: str
    department: str | None = None
    requested_by_user_id: APIId | None = None
    resolved_by_user_id: APIId | None = None
    context_json: dict[str, Any] | str | None = None
    decision_reason: str | None = None
    decision_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApprovalResolveRequest(APIBaseModel):
    approved: bool
    reason: str | None = Field(default=None, max_length=2000)


class ApprovalResolveResponse(BaseModel):
    approval: ApprovalRequestResponse
    workflow_instance: WorkflowInstanceResponse | None = None
    message: str = "Approval resolved"


class ClarificationRequestResponse(ORMBaseModel):
    id: APIId
    workflow_instance_id: APIId
    entity_type: str | None = None
    entity_id: APIId | None = None
    status: str
    department: str | None = None
    requested_by_user_id: APIId | None = None
    resolved_by_user_id: APIId | None = None
    prompt: str
    fields_json: list[str] | str | None = None
    context_json: dict[str, Any] | str | None = None
    response_json: dict[str, Any] | str | None = None
    resolution_note: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ClarificationResolveRequest(APIBaseModel):
    response: dict[str, Any] = Field(default_factory=dict)
    resolution_note: str | None = Field(default=None, max_length=2000)


class ClarificationResolveResponse(BaseModel):
    clarification: ClarificationRequestResponse
    workflow_instance: WorkflowInstanceResponse | None = None
    message: str = "Clarification resolved"


class MaloneDeliveryResponse(BaseModel):
    answer: str | None = None
    mode: str | None = None
    sources: list[dict[str, Any]] = Field(default_factory=list)


class MaloneRequestResponse(BaseModel):
    mode: str
    intent: dict[str, Any] = Field(default_factory=dict)
    status: str
    result: dict[str, Any] | None = None
    deterministic_execution: dict[str, Any] | None = None
    workflow_instance: WorkflowInstanceResponse | None = None
    delivery: MaloneDeliveryResponse
    proposal_record: dict[str, Any] = Field(default_factory=dict)
    truth_packet: dict[str, Any] = Field(default_factory=dict)
    rendered_output: dict[str, Any] = Field(default_factory=dict)
    verification: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[dict[str, Any]] | list[str] = Field(default_factory=list)