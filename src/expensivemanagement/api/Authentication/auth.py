from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .models import Account, Employee
from .security import create_access_token, get_db
from .database import SessionLocal

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # 1. Verify the account credentials
    account = db.query(Account).filter(Account.username == form_data.username).first()
    if not account or not Account.verify(form_data.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Look up the matching employee by name
    #    (relies on the convention that Account.username == Employee.name)
    employee = db.query(Employee).filter(Employee.name == account.username).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee record found for this account",
        )

    # 3. Issue the token
    access_token = create_access_token(
        data={"sub": str(employee.id), "username": account.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(employee.id),
    }
