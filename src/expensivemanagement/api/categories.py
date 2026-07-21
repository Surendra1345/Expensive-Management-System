from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import CategoryCreate,CategoryResponse
from model.models import Category,ExpenseLineItem
import uuid

router=APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=CategoryResponse)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(
        Category.category_name == payload.category_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = Category(
        category_name=payload.category_name,
        max_amount=payload.max_amount
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category

@router.get("/{category_id}/claims")
def get_category_claims(
    category_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    line_items = db.query(ExpenseLineItem).filter(
        ExpenseLineItem.category_id == category_id
    ).all()

    return {
        "category": category.category_name,
        "max_amount": category.max_amount,
        "total_records": len(line_items),
        "expense_line_items": line_items
    }

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryCreate,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.category_name = payload.category_name
    category.max_amount = payload.max_amount

    db.commit()
    db.refresh(category)

    return category

