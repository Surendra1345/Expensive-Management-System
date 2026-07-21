from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import EmployeeCreate,EmployeeResponse
from model.models import Employee,ExpenseClaim,Department,Role
import uuid

router=APIRouter(
    prefix="/employee",
    tags=["Employee"]
)

@router.post("/", response_model=EmployeeResponse)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db)
):
    employee = Employee(
        name=payload.name,
        email=payload.email,
        role_id=payload.role_id,
        department_id=payload.department_id
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee

@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee

@router.get("/{employee_id}/details")
def get_employee_details(
    employee_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    department = db.query(Department).filter(
        Department.id == employee.department_id
    ).first()

    role = db.query(Role).filter(
        Role.id == employee.role_id
    ).first()

    manager = None
    if department and department.manager_id:
        manager = db.query(Employee).filter(
            Employee.id == department.manager_id
        ).first()

    claims = db.query(ExpenseClaim).filter(
        ExpenseClaim.employee_id == employee.id
    ).all()

    return {
        "employee": employee,
        "role": role,
        "department": department,
        "manager": manager,
        "claims": claims
    }

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: uuid.UUID,
    payload: EmployeeCreate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee.name = payload.name
    employee.email = payload.email
    employee.role_id = payload.role_id
    employee.department_id = payload.department_id

    db.commit()
    db.refresh(employee)

    return employee

