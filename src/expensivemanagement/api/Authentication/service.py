from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.Authentication.models import Account, Employee
from security import create_access_token


def authenticate_account(db: Session, username: str, password: str) -> Account:
    """Verify credentials against the accounts table. Raises 401 if invalid."""
    account = db.query(Account).filter(Account.username == username).first()
    if not account or not Account.verify(password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return account


def get_employee_for_account(db: Session, account: Account) -> Employee:
    """Look up the employee linked to this account by name.

    Relies on the convention that Account.username == Employee.name.
    Raises 404 if no matching employee exists.
    """
    employee = db.query(Employee).filter(Employee.name == account.username).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee record found for this account",
        )
    return employee


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    print("grant_type =", repr(form_data.grant_type))
    print("username   =", repr(form_data.username))
    print("password   =", repr(form_data.password))

    # 1. Verify the account credentials
    account = db.query(Account).filter(
        Account.username == form_data.username
    ).first()

    if not account or not Account.verify(form_data.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


    

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(employee.id),
    }