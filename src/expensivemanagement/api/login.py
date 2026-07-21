from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import LoginResponse,LoginRequest
from model.models import Account,Employee,Role

router=APIRouter(prefix="/accounts",
                 tags=["Account"])


@router.post("/api/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    # Check username
    account = (
        db.query(Account)
        .filter(Account.username == payload.username)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    if not Account.verify(payload.password, account.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Get employee details
    employee = (
        db.query(Employee)
        .filter(Employee.name == account.username)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Get role
    role = (
        db.query(Role)
        .filter(Role.id == employee.role_id)
        .first()
    )

    # Temporary token (replace with JWT later)
    access_token = str(employee.id)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        employee_id=employee.id,
        name=employee.name,
        email=employee.email,
        role=role.role_name,
        department_id=employee.department_id,
    )


