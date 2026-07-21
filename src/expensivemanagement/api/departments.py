from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from data.schemas import DepartmentCreate,DepartmentResponse
from model.models import Department,Employee,FinanceAdmin
import uuid

router=APIRouter(
    prefix="/department",
    tags=["Departments"]
)

@router.post("/", response_model=DepartmentResponse)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db)
):
    department = Department(
        name=payload.name,
        manager_id=payload.manager_id
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department

@router.get("/", response_model=list[DepartmentResponse])
def get_all_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department

@router.get("/{department_id}/employees")
def get_department_employees(
    department_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    employees = db.query(Employee).filter(
        Employee.department_id == department_id
    ).all()

    return {
        "department": department.name,
        "total_employees": len(employees),
        "employees": employees
    }

@router.get("/{department_id}/manager")
def get_department_manager(
    department_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    manager = db.query(Employee).filter(
        Employee.id == department.manager_id
    ).first()

    return manager

@router.get("/{department_id}/details")
def get_department_details(
    department_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    manager = db.query(Employee).filter(
        Employee.id == department.manager_id
    ).first()

    employees = db.query(Employee).filter(
        Employee.department_id == department_id
    ).all()

    finance_admins = db.query(FinanceAdmin).filter(
        FinanceAdmin.department_id == department_id
    ).all()

    return {
        "department": department,
        "manager": manager,
        "employees": employees,
        "finance_admins": finance_admins
    }

@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: uuid.UUID,
    payload: DepartmentCreate,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    department.name = payload.name
    department.manager_id = payload.manager_id

    db.commit()
    db.refresh(department)

    return department

