import enum
import uuid
import bcrypt
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from config.database import Base
 
 
# ==========================================================
# ENUMS
# ==========================================================
 
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
 
 
class BudgetRequestStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
 
 
class PartialOfferStatus(str, enum.Enum):
    Pending = "Pending"
    Accepted = "Accepted"
    Declined = "Declined"
    Cancelled = "Cancelled"
 
 
# ==========================================================
# ROLES
# ==========================================================
 
class Role(Base):
    __tablename__ = "roles"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="role", foreign_keys="Employee.role_id"
    )
 
 
# ==========================================================
# DEPARTMENTS
# ==========================================================
 
class Department(Base):
    __tablename__ = "departments"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    manager_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    manager: Mapped["Employee"] = relationship(
        foreign_keys=[manager_id], post_update=True
    )
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department", foreign_keys="Employee.department_id"
    )
    finance_admins: Mapped[list["FinanceAdmin"]] = relationship(back_populates="department")
    budget_requests: Mapped[list["BudgetRequest"]] = relationship(back_populates="department")
 
 
# ==========================================================
# EMPLOYEES
# ==========================================================
 
class Employee(Base):
    __tablename__ = "employees"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    role: Mapped["Role"] = relationship(back_populates="employees", foreign_keys=[role_id])
    department: Mapped["Department"] = relationship(back_populates="employees", foreign_keys=[department_id])
 
    # Reverse side of business relationships (all FKs pinned to avoid ambiguity
    # since multiple tables have more than one FK pointing at employees.id)
    finance_admin_profile: Mapped["FinanceAdmin"] = relationship(
        back_populates="employee", foreign_keys="FinanceAdmin.employee_id", uselist=False
    )
    claims: Mapped[list["ExpenseClaim"]] = relationship(
        back_populates="employee", foreign_keys="ExpenseClaim.employee_id"
    )
    approvals: Mapped[list["StatusHistory"]] = relationship(
        back_populates="approver", foreign_keys="StatusHistory.approver_id"
    )
    budget_requests_made: Mapped[list["BudgetRequest"]] = relationship(
        back_populates="requester", foreign_keys="BudgetRequest.requested_by"
    )
    budget_requests_approved: Mapped[list["BudgetRequest"]] = relationship(
        back_populates="approver", foreign_keys="BudgetRequest.approved_by"
    )
    partial_offers_approved: Mapped[list["PartialReimbursementOffer"]] = relationship(
        back_populates="approver", foreign_keys="PartialReimbursementOffer.approved_by"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="employee", foreign_keys="AuditLog.employee_id"
    )
 
 
# ==========================================================
# FINANCE ADMIN
# ==========================================================
 
class FinanceAdmin(Base):
    __tablename__ = "finance_admins"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    employee: Mapped["Employee"] = relationship(
        back_populates="finance_admin_profile", foreign_keys=[employee_id]
    )
    department: Mapped["Department"] = relationship(back_populates="finance_admins")
 
 
# ==========================================================
# CATEGORY
# ==========================================================
 
class Category(Base):
    __tablename__ = "categories"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_amount: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    line_items: Mapped[list["ExpenseLineItem"]] = relationship(back_populates="category")
 
 
# ==========================================================
# EXPENSE CLAIM
# ==========================================================
 
class ExpenseClaim(Base):
    __tablename__ = "expense_claims"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=True)
    requested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus, name="claim_status"), default=ClaimStatus.Submitted, nullable=False)
    revision_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    last_resubmitted_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    reimbursed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    employee: Mapped["Employee"] = relationship(back_populates="claims", foreign_keys=[employee_id])
 
    line_items: Mapped[list["ExpenseLineItem"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["StatusHistory"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    budget_requests: Mapped[list["BudgetRequest"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    reimbursement_payments: Mapped[list["ReimbursementPayment"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    partial_offers: Mapped[list["PartialReimbursementOffer"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
 
 
# ==========================================================
# EXPENSE LINE ITEMS
# ==========================================================
 
class ExpenseLineItem(Base):
    __tablename__ = "expense_line_items"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_claims.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    claim: Mapped["ExpenseClaim"] = relationship(back_populates="line_items")
    category: Mapped["Category"] = relationship(back_populates="line_items")
 
 
# ==========================================================
# STATUS HISTORY
# ==========================================================
 
class StatusHistory(Base):
    __tablename__ = "status_history"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_claims.id"), nullable=False)
    approver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    requested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    approved_amount: Mapped[float] = mapped_column(Float, nullable=False)
    remaining_amount: Mapped[float] = mapped_column(Float, nullable=False)
    approval_level: Mapped[ApprovalLevel] = mapped_column(Enum(ApprovalLevel, name="approval_level"), nullable=False)
    status: Mapped[ApprovalAction] = mapped_column(Enum(ApprovalAction, name="approval_action"), nullable=False)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    action_time: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    claim: Mapped["ExpenseClaim"] = relationship(back_populates="status_history")
    approver: Mapped["Employee"] = relationship(back_populates="approvals", foreign_keys=[approver_id])
 
 
# ==========================================================
# BUDGET REQUESTS
# ==========================================================
 
class BudgetRequest(Base):
    __tablename__ = "budget_requests"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_claims.id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    requested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[BudgetRequestStatus] = mapped_column(Enum(BudgetRequestStatus, name="budget_request_status"), default=BudgetRequestStatus.Pending, nullable=False)
    approved_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    approved_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    claim: Mapped["ExpenseClaim"] = relationship(back_populates="budget_requests")
    department: Mapped["Department"] = relationship(back_populates="budget_requests")
    requester: Mapped["Employee"] = relationship(
        back_populates="budget_requests_made", foreign_keys=[requested_by]
    )
    approver: Mapped["Employee"] = relationship(
        back_populates="budget_requests_approved", foreign_keys=[approved_by]
    )
 
 
# ==========================================================
# REIMBURSEMENT PAYMENTS
# ==========================================================
 
class ReimbursementPayment(Base):
    __tablename__ = "reimbursement_payments"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_claims.id"), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    payment_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)

    claim: Mapped["ExpenseClaim"] = relationship(back_populates="reimbursement_payments")
 
 
# ==========================================================
# AUDIT LOGS
# ==========================================================
 
class AuditLog(Base):
    __tablename__ = "audit_logs"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
 
    employee: Mapped["Employee"] = relationship(back_populates="audit_logs", foreign_keys=[employee_id])
 
 
# ==========================================================
# PARTIAL REIMBURSEMENT OFFERS
# ==========================================================
 
class PartialReimbursementOffer(Base):
    __tablename__ = "partial_reimbursement_offers"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_claims.id"), nullable=False)
    approved_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    approved_amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[PartialOfferStatus] = mapped_column(Enum(PartialOfferStatus, name="partial_offer_status"), default=PartialOfferStatus.Pending, nullable=False)
    responded_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
 
    claim: Mapped["ExpenseClaim"] = relationship(back_populates="partial_offers")
    approver: Mapped["Employee"] = relationship(
        back_populates="partial_offers_approved", foreign_keys=[approved_by]
    )
 
 
# ==========================================================
# ACCOUNT (auth, not part of the ORM relationship graph)
# ==========================================================
 
class Account(Base):
    __tablename__ = "accounts"
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
 
    @staticmethod
    def encrypt(password: str) -> str:
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")
 
    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )