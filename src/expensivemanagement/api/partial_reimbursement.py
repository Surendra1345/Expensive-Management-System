from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from model.models import PartialReimbursementOffer,ExpenseClaim
from data.schemas import PartialReimbursementOfferCreate,PartialReimbursementOfferResponse,PartialReimbursementOfferUpdate
import uuid
from datetime import datetime

router=APIRouter(
    prefix="/partialreimbushment",
    tags=["PartialReimbushment"]
)

@router.post("/", response_model=PartialReimbursementOfferResponse)
def create_partial_offer(
    payload: PartialReimbursementOfferCreate,
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

    offer = PartialReimbursementOffer(
        claim_id=payload.claim_id,
        approved_by=payload.approved_by,
        approved_amount=payload.approved_amount,
        reason=payload.reason
    )

    db.add(offer)
    db.commit()
    db.refresh(offer)

    return offer

@router.get("/", response_model=list[PartialReimbursementOfferResponse])
def get_all_partial_offers(
    db: Session = Depends(get_db)
):
    return db.query(PartialReimbursementOffer).all()

@router.get("/{offer_id}", response_model=PartialReimbursementOfferResponse)
def get_partial_offer_by_id(
    offer_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    offer = (
        db.query(PartialReimbursementOffer)
        .filter(PartialReimbursementOffer.id == offer_id)
        .first()
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found"
        )

    return offer

@router.get("/claim/{claim_id}")
def get_partial_offers_by_claim(
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

    offers = (
        db.query(PartialReimbursementOffer)
        .filter(PartialReimbursementOffer.claim_id == claim_id)
        .all()
    )

    return {
        "claim_id": claim.id,
        "purpose": claim.purpose,
        "offers": offers
    }




@router.put("/{offer_id}", response_model=PartialReimbursementOfferResponse)
def update_partial_offer(
    offer_id: uuid.UUID,
    payload:PartialReimbursementOfferUpdate,
    db: Session = Depends(get_db)
):
    offer = (
        db.query(PartialReimbursementOffer)
        .filter(PartialReimbursementOffer.id == offer_id)
        .first()
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found"
        )

    offer.status = payload.status
    offer.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(offer)

    return offer