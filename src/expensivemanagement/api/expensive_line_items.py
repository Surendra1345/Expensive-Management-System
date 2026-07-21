from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import ExpenseLineItemCreate,ExpenseLineItemResponse
from model.models import ExpenseLineItem,Category,ExpenseClaim
import uuid

router=APIRouter(
    prefix="/expensicelineitems",
    tags=["ExpensiveLineItems"]
)

@router.post("/", response_model=ExpenseLineItemResponse)
def create_line_item(
    payload: ExpenseLineItemCreate,
    db: Session = Depends(get_db)
):
    claim = db.query(ExpenseClaim).filter(
        ExpenseClaim.id == payload.claim_id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Expense claim not found"
        )

    category = db.query(Category).filter(
        Category.id == payload.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    line_item = ExpenseLineItem(
        claim_id=payload.claim_id,
        category_id=payload.category_id,
        amount=payload.amount,
        description=payload.description,
        receipt_url=payload.receipt_url
    )

    db.add(line_item)
    db.commit()
    db.refresh(line_item)

    return line_item

@router.get("/", response_model=list[ExpenseLineItemResponse])
def get_all_line_items(
    db: Session = Depends(get_db)
):
    return db.query(ExpenseLineItem).all()

@router.get("/{line_item_id}", response_model=ExpenseLineItemResponse)
def get_line_item(
    line_item_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    line_item = db.query(ExpenseLineItem).filter(
        ExpenseLineItem.id == line_item_id
    ).first()

    if not line_item:
        raise HTTPException(
            status_code=404,
            detail="Expense line item not found"
        )

    return line_item

@router.get("/claim/{claim_id}")
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
        "total_line_items": len(line_items),
        "line_items": line_items
    }

@router.put("/{line_item_id}", response_model=ExpenseLineItemResponse)
def update_line_item(
    line_item_id: uuid.UUID,
    payload: ExpenseLineItemCreate,
    db: Session = Depends(get_db)
):
    line_item = db.query(ExpenseLineItem).filter(
        ExpenseLineItem.id == line_item_id
    ).first()

    if not line_item:
        raise HTTPException(
            status_code=404,
            detail="Expense line item not found"
        )

    line_item.claim_id = payload.claim_id
    line_item.category_id = payload.category_id
    line_item.amount = payload.amount
    line_item.description = payload.description
    line_item.receipt_url = payload.receipt_url

    db.commit()
    db.refresh(line_item)

    return line_item

