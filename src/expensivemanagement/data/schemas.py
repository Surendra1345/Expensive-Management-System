from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid
import enum



# ============================================================
# ENUMS — FIX: schemas.py previously typed status/approval_level
# fields as plain `str`, which accepts any string. Using the real
# enums here means Pydantic rejects invalid values automatically
# instead of silently accepting typos.
# ============================================================

class ClaimStatus(str, enum.Enum):
    Submitted = "Submitted"
    Under_Review = "Under_Review"
    Sent_Back_For_Revision = "Sent_Back_For_Revision"
    Manager_Approved = "Manager_Approved"
    Finance_Approved = "Finance_Approved"
    Partially_Approved = "Partially_Approved"
    Rejected = "Rejected"
    Reimbursed = "Reimbursed"
    Partially_Reimbursed = "Partially_Reimbursed"


class ApprovalLevel(str, enum.Enum):
    Manager = "Manager"
    Finance_Admin = "Finance_Admin"


class ApprovalAction(str, enum.Enum):
    Approved = "Approved"
    Rejected = "Rejected"
    Partially_Approved = "Partially_Approved"
    Send_Back = "Send_Back"


class BudgetRequestStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class PartialOfferStatus(str, enum.Enum):
    Pending = "Pending"
    Accepted = "Accepted"
    Declined = "Declined"
    Cancelled = "Cancelled"


# ============================================================
# Role schemas
# ============================================================

class RoleCreate(BaseModel):
    role_name: str


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_name: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Department schemas
# ============================================================

class DepartmentCreate(BaseModel):
    name: str
    manager_id: Optional[uuid.UUID] = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    manager_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Employee schemas
# ============================================================

class EmployeeCreate(BaseModel):
    name: str
    email: str
    role_id: uuid.UUID
    department_id: uuid.UUID


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role_id: uuid.UUID
    department_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    # NOTE: password / password_hash intentionally never included
    # here — this response is what gets sent back over the API.


# ============================================================
# Finance Admin schemas
# ============================================================

class FinanceAdminCreate(BaseModel):
    employee_id: uuid.UUID
    department_id: uuid.UUID


class FinanceAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    department_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Category schemas
# FIX: max_amount is now Optional[int] on both Create and
# Response — Category.max_amount is nullable in models.py, and
# Miscellaneous is expected to have no cap (max_amount = None).
# The old required `int` type would raise a validation error the
# moment a Miscellaneous category was returned through the API.
# ============================================================

class CategoryCreate(BaseModel):
    category_name: str
    max_amount: Optional[int] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_name: str
    max_amount: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Expense Claim schemas
# ============================================================

class ExpenseClaimCreate(BaseModel):
    purpose: str
    requested_amount: float
    employee_id: uuid.UUID


class ExpenseClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    purpose: str
    requested_amount: float
    status: ClaimStatus
    revision_count: int
    employee_id: uuid.UUID
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    reimbursed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Expense Line Item schemas
# ============================================================

class ExpenseLineItemCreate(BaseModel):
    claim_id: uuid.UUID
    category_id: uuid.UUID
    amount: float
    description: str
    receipt_url: str


class ExpenseLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    category_id: uuid.UUID
    amount: float
    description: str
    receipt_url: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Status History schemas
# (insert-only in intended usage — no Update schema provided;
# a new decision should always be a new row, not an edit)
# ============================================================


class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    approver_id: uuid.UUID
    requested_amount: float
    approved_amount: float
    remaining_amount: float
    approval_level: ApprovalLevel
    status: ApprovalAction
    remarks: str
    action_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Budget Request schemas
# ============================================================

class BudgetRequestCreate(BaseModel):
    claim_id: uuid.UUID
    department_id: uuid.UUID
    requested_by: uuid.UUID
    requested_amount: float


class BudgetRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    department_id: uuid.UUID
    requested_by: uuid.UUID
    requested_amount: float
    status: BudgetRequestStatus
    approved_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Reimbursement Payment schemas
# FIX: transaction_reference is now Optional — matches models.py
# change allowing cash payments with no reference number.
# (insert-only — no Update schema; a new payment is always a
# new row, never an edit to an existing one)
# ============================================================

class ReimbursementPaymentCreate(BaseModel):
    claim_id: uuid.UUID
    paid_amount: float
    payment_mode: str


class ReimbursementPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    paid_amount: float
    payment_date: Optional[datetime] = None
    payment_mode: str
    transaction_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Partial Reimbursement Offer schemas
# ============================================================

class PartialReimbursementOfferCreate(BaseModel):
    claim_id: uuid.UUID
    approved_by: uuid.UUID
    approved_amount: float
    reason: str

class PartialReimbursementOfferUpdate(BaseModel):
    status: PartialOfferStatus

class PartialReimbursementOfferVerify(BaseModel):
    offer_id: uuid.UUID
    accept: bool


class PartialReimbursementOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    approved_by: uuid.UUID
    approved_amount: float
    reason: str
    status: PartialOfferStatus
    responded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None


# ============================================================
# Audit Log
# Read-only — no Create schema. Written internally by the
# backend whenever another action happens, never by a client.
# ============================================================

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    action: str
    table_name: str
    record_id: uuid.UUID
    created_at: datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    employee_id: uuid.UUID
    name: str
    email: str
    role: str
    department_id: uuid.UUID