from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from model.models import ReimbursementPayment,ExpenseClaim,ClaimStatus
from data.schemas import ReimbursementPaymentCreate,ReimbursementPaymentResponse
from datetime import datetime
import uuid
import string
import random

router=APIRouter(
    prefix="/reimbushmentpayment",
    tags=["ReimbushmentPayments"]
)

def generate_transaction_reference():
    return "TXN-" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=12)
    )

@router.post("/", response_model=ReimbursementPaymentResponse)
def create_reimbursement_payment(
    payload: ReimbursementPaymentCreate,
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

    payment = ReimbursementPayment(
        claim_id=payload.claim_id,
        paid_amount=payload.paid_amount,
        payment_mode=payload.payment_mode,
        transaction_reference=generate_transaction_reference()
    )

    db.add(payment)

    claim.reimbursed_at = datetime.utcnow()
    claim.status = ClaimStatus.Reimbursed

    db.commit()
    db.refresh(payment)

    return payment

@router.get("/", response_model=list[ReimbursementPaymentResponse])
def get_all_payments(
    db: Session = Depends(get_db)
):
    return db.query(ReimbursementPayment).all()

@router.get("/{payment_id}", response_model=ReimbursementPaymentResponse)
def get_payment_by_id(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    payment = (
        db.query(ReimbursementPayment)
        .filter(ReimbursementPayment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment

@router.get("/claim/{claim_id}")
def get_payments_by_claim(
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

    payments = (
        db.query(ReimbursementPayment)
        .filter(ReimbursementPayment.claim_id == claim_id)
        .all()
    )

    return {
        "claim_id": claim.id,
        "purpose": claim.purpose,
        "requested_amount": claim.requested_amount,
        "payments": payments
    }

