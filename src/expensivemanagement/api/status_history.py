from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import StatusHistoryResponse
from model.models import StatusHistory,ExpenseClaim,Employee
import uuid

router=APIRouter(
    prefix="/statushistory",
    tags=["StatusHistory"]
)


@router.get("/", response_model=list[StatusHistoryResponse])
def get_all_status_history(
    db: Session = Depends(get_db)
):
    return db.query(StatusHistory).all()


@router.get("/{history_id}", response_model=StatusHistoryResponse)
def get_status_history_by_id(
    history_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    history = (
        db.query(StatusHistory)
        .filter(StatusHistory.id == history_id)
        .first()
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Status history not found"
        )

    return history

@router.get("/claim/{claim_id}")
def get_claim_status_history(
    claim_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    claim = (
        db.query(ExpenseClaim)
        .filter(ExpenseClaim.id == claim_id)
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Expense claim not found"
        )

    history = (
        db.query(StatusHistory)
        .filter(StatusHistory.claim_id == claim_id)
        .order_by(StatusHistory.action_time)
        .all()
    )

    return {
        "claim_id": claim.id,
        "purpose": claim.purpose,
        "current_status": claim.status,
        "history": history
    }

@router.get("/approver/{employee_id}")
def get_approvals_by_employee(
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

    approvals = (
        db.query(StatusHistory)
        .filter(StatusHistory.approver_id == employee_id)
        .all()
    )

    return {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "total_actions": len(approvals),
        "approvals": approvals
    }