from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import BudgetRequestCreate,BudgetRequestResponse
from model.models import BudgetRequest,ExpenseClaim,Department
import uuid

router=APIRouter(
    prefix="/budgetrequest",
    tags=["BudgetRequest"]
)

@router.post("/", response_model=BudgetRequestResponse)
def create_budget_request(
    payload: BudgetRequestCreate,
    db: Session = Depends(get_db)
):
    claim = (
        db.query(ExpenseClaim)
        .filter(ExpenseClaim.id == payload.claim_id)
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Expense claim not found"
        )

    request = BudgetRequest(
        claim_id=payload.claim_id,
        department_id=payload.department_id,
        requested_by=payload.requested_by,
        requested_amount=payload.requested_amount,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request

@router.get("/", response_model=list[BudgetRequestResponse])
def get_all_budget_requests(
    db: Session = Depends(get_db)
):
    return db.query(BudgetRequest).all()

@router.get("/{request_id}", response_model=BudgetRequestResponse)
def get_budget_request_by_id(
    request_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    request = (
        db.query(BudgetRequest)
        .filter(BudgetRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Budget request not found"
        )

    return request

@router.get("/department/{department_id}")
def get_budget_requests_by_department(
    department_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    requests = (
        db.query(BudgetRequest)
        .filter(BudgetRequest.department_id == department_id)
        .all()
    )

    return {
        "department_id": department.id,
        "department_name": department.name,
        "total_requests": len(requests),
        "requests": requests
    }

@router.get("/claim/{claim_id}")
def get_budget_requests_by_claim(
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

    requests = (
        db.query(BudgetRequest)
        .filter(BudgetRequest.claim_id == claim_id)
        .all()
    )

    return {
        "claim_id": claim.id,
        "purpose": claim.purpose,
        "budget_requests": requests
    }

