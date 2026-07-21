from config.database import SessionLocal
from model.models import Employee, Department

db = SessionLocal()
try:
    # ---------------- Fetch existing departments ----------------
    it_department = db.query(Department).filter(Department.name == "IT").first()
    hr_department = db.query(Department).filter(Department.name == "HR").first()
    sales_department = db.query(Department).filter(Department.name == "Sales").first()
    finance_department = db.query(Department).filter(Department.name == "Finance").first()

    # ---------------- Fetch existing managers ----------------
    walter = db.query(Employee).filter(Employee.email == "walter@gmail.com").first()
    rajesh = db.query(Employee).filter(Employee.email == "rajesh@gmail.com").first()
    bala = db.query(Employee).filter(Employee.email == "bala@gmail.com").first()
    ajay = db.query(Employee).filter(Employee.email == "ajay@gmail.com").first()

    # ---------------- Safety check before updating ----------------
    missing = []
    for label, obj in [
        ("IT department", it_department), ("HR department", hr_department),
        ("Sales department", sales_department), ("Finance department", finance_department),
        ("Walter", walter), ("Rajesh", rajesh), ("Bala", bala), ("Ajay", ajay),
    ]:
        if obj is None:
            missing.append(label)

    if missing:
        raise ValueError(f"Could not find: {', '.join(missing)} — check they exist in the DB first")

    # ---------------- Assign managers ----------------
    it_department.manager_id = walter.id
    hr_department.manager_id = rajesh.id
    sales_department.manager_id = bala.id
    finance_department.manager_id = ajay.id

    db.commit()
    print("manager_id updated successfully for all 4 departments.")
except Exception as e:
    db.rollback()
    print(e)
finally:
    db.close()