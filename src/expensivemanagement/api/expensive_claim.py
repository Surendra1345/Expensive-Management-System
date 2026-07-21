from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from model.models import ExpenseClaim,ClaimStatus,Employee,ExpenseLineItem,ApprovalLevel,ApprovalAction,StatusHistory
from data.schemas import ExpenseClaimCreate,ExpenseClaimResponse
import uuid
import datetime

router=APIRouter(
    prefix="/expensiveclaims",
    tags=["ExpensiveClaim"]
)

@router.post("/", response_model=ExpenseClaimResponse)
def create_expense_claim(
    payload: ExpenseClaimCreate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == payload.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    claim = ExpenseClaim(
        employee_id=payload.employee_id,
        purpose=payload.purpose,
        requested_amount=payload.requested_amount,
        status=ClaimStatus.Submitted
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    return claim

@router.put("/{claim_id}/manager-approve")
def manager_approve_claim(
    claim_id: uuid.UUID,
    approver_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    # Check claim
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

    # Check manager
    manager = (
        db.query(Employee)
        .filter(Employee.id == approver_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found"
        )

    # Already approved?
    if claim.status != ClaimStatus.Submitted:
        raise HTTPException(
            status_code=400,
            detail="Only submitted claims can be approved"
        )

    # Update claim
    claim.status = ClaimStatus.Manager_Approved
    claim.approved_at = datetime.utcnow()

    # Create status history
    history = StatusHistory(
        claim_id=claim.id,
        approver_id=manager.id,
        requested_amount=claim.requested_amount,
        approved_amount=claim.requested_amount,
        remaining_amount=0,
        approval_level=ApprovalLevel.Manager,
        status=ApprovalAction.Approved,
        remarks="Approved by Manager"
    )

    db.add(history)

    db.commit()

    return {
        "message": "Claim approved successfully by Manager",
        "claim_id": claim.id,
        "status": claim.status
    }

@router.put("/{claim_id}/reject")
def reject_claim(
    claim_id: uuid.UUID,
    approver_id: uuid.UUID,
    remarks: str,
    db: Session = Depends(get_db)
):
    # Check claim
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

    # Check approver
    approver = (
        db.query(Employee)
        .filter(Employee.id == approver_id)
        .first()
    )

    if not approver:
        raise HTTPException(
            status_code=404,
            detail="Approver not found"
        )

    # Cannot reject an already completed claim
    if claim.status in [
        ClaimStatus.Rejected,
        ClaimStatus.Reimbursed
    ]:
        raise HTTPException(
            status_code=400,
            detail="Claim cannot be rejected"
        )

    # Update claim
    claim.status = ClaimStatus.Rejected
    claim.approved_at = datetime.utcnow()

    # Store history
    history = StatusHistory(
        claim_id=claim.id,
        approver_id=approver.id,
        requested_amount=claim.requested_amount,
        approved_amount=0,
        remaining_amount=claim.requested_amount,
        approval_level=ApprovalLevel.Manager,
        status=ApprovalAction.Rejected,
        remarks=remarks
    )

    db.add(history)

    db.commit()

    return {
        "message": "Expense claim rejected successfully",
        "claim_id": claim.id,
        "status": claim.status
    }

@router.put("/{claim_id}/finance-approve")
def finance_approve_claim(
    claim_id: uuid.UUID,
    approver_id: uuid.UUID,
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

    approver = (
        db.query(Employee)
        .filter(Employee.id == approver_id)
        .first()
    )

    if not approver:
        raise HTTPException(
            status_code=404,
            detail="Finance Admin not found"
        )

    if claim.status != ClaimStatus.Manager_Approved:
        raise HTTPException(
            status_code=400,
            detail="Only manager approved claims can be finance approved"
        )

    claim.status = ClaimStatus.Finance_Approved
    claim.approved_at = datetime.utcnow()

    history = StatusHistory(
        claim_id=claim.id,
        approver_id=approver.id,
        requested_amount=claim.requested_amount,
        approved_amount=claim.requested_amount,
        remaining_amount=0,
        approval_level=ApprovalLevel.Finance_Admin,
        status=ApprovalAction.Approved,
        remarks="Approved by Finance Admin"
    )

    db.add(history)

    db.commit()

    return {
        "message": "Claim approved by Finance Admin",
        "claim_id": claim.id,
        "status": claim.status
    }


@router.put("/{claim_id}/finance-reject")
def finance_reject_claim(
    claim_id: uuid.UUID,
    approver_id: uuid.UUID,
    remarks: str,
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

    approver = (
        db.query(Employee)
        .filter(Employee.id == approver_id)
        .first()
    )

    if not approver:
        raise HTTPException(
            status_code=404,
            detail="Finance Admin not found"
        )

    if claim.status != ClaimStatus.Manager_Approved:
        raise HTTPException(
            status_code=400,
            detail="Only manager approved claims can be rejected by Finance"
        )

    claim.status = ClaimStatus.Rejected
    claim.approved_at = datetime.utcnow()

    history = StatusHistory(
        claim_id=claim.id,
        approver_id=approver.id,
        requested_amount=claim.requested_amount,
        approved_amount=0,
        remaining_amount=claim.requested_amount,
        approval_level=ApprovalLevel.Finance_Admin,
        status=ApprovalAction.Rejected,
        remarks=remarks
    )

    db.add(history)

    db.commit()

    return {
        "message": "Claim rejected by Finance Admin",
        "claim_id": claim.id,
        "status": claim.status
    }




@router.get("/", response_model=list[ExpenseClaimResponse])
def get_all_claims(
    db: Session = Depends(get_db)
):
    return db.query(ExpenseClaim).all()

@router.get("/{claim_id}", response_model=ExpenseClaimResponse)
def get_claim(
    claim_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    claim = db.query(ExpenseClaim).filter(
        ExpenseClaim.id == claim_id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Expense claim not found"
        )

    return claim

@router.get("/{claim_id}/line-items")
def get_claim_line_items(
    claim_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    claim = db.query(ExpenseClaim).filter(
        ExpenseClaim.id == claim_id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Expense claim not found"
        )

    line_items = db.query(ExpenseLineItem).filter(
        ExpenseLineItem.claim_id == claim_id
    ).all()

    return {
        "claim_id": claim.id,
        "purpose": claim.purpose,
        "line_items": line_items
    }


@router.put("/{claim_id}", response_model=ExpenseClaimResponse)
def update_claim(
    claim_id: uuid.UUID,
    payload: ExpenseClaimCreate,
    db: Session = Depends(get_db)
):
    claim = db.query(ExpenseClaim).filter(
        ExpenseClaim.id == claim_id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Expense claim not found"
        )

    claim.purpose = payload.purpose
    claim.requested_amount = payload.requested_amount
    claim.employee_id = payload.employee_id

    db.commit()
    db.refresh(claim)

    return claim

