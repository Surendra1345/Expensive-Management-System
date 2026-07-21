import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from data.schemas import RoleCreate, RoleResponse
from model.models import Role, Employee

router=APIRouter(
    prefix="/roles",
    tags=["Role"]
)



@router.post("/", response_model=RoleResponse)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db)
):
    existing_role = (
        db.query(Role)
        .filter(Role.role_name == payload.role_name)
        .first()
    )

    if existing_role:
        raise HTTPException(
            status_code=400,
            detail="Role already exists"
        )

    role = Role(role_name=payload.role_name)

    db.add(role)
    db.commit()
    db.refresh(role)

    return role

@router.get("/", response_model=list[RoleResponse])
def get_all_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.get("/{role_id}", response_model=RoleResponse)
def get_role_by_id(
    role_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    role = (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    return role

@router.get("/{role_id}/employees")
def get_employees_by_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    role = (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    employees = (
        db.query(Employee)
        .filter(Employee.role_id == role_id)
        .all()
    )

    return {
        "role_id": role.id,
        "role_name": role.role_name,
        "total_employees": len(employees),
        "employees": employees
    }

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: uuid.UUID,
    payload: RoleCreate,
    db: Session = Depends(get_db)
):
    role = (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    role.role_name = payload.role_name

    db.commit()
    db.refresh(role)

    return role