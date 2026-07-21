from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from model.models import AuditLog,Employee
from data.schemas import AuditLogResponse
import uuid

router=APIRouter(
    prefix="/auditlog",
    tags=["AuditLog"]
)

@router.get("/", response_model=list[AuditLogResponse])
def get_all_audit_logs(
    db: Session = Depends(get_db)
):
    return db.query(AuditLog).all()

@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log_by_id(
    log_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    log = (
        db.query(AuditLog)
        .filter(AuditLog.id == log_id)
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found"
        )

    return log

@router.get("/employee/{employee_id}")
def get_employee_logs(
    employee_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.employee_id == employee_id)
        .all()
    )

    return {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "total_logs": len(logs),
        "logs": logs
    }