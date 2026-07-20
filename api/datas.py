from api.Authentication.database import SessionLocal
from api.Authentication.models import Account, Employee, Category, Role, Department

db = SessionLocal()


def get_or_create_role(role_name, created_by=None):
    role = db.query(Role).filter_by(role_name=role_name).first()
    if role is None:
        role = Role(role_name=role_name, created_by=created_by)
        db.add(role)
        db.flush()
    return role


def get_or_create_category(category_name, max_amount=None):
    category = db.query(Category).filter_by(category_name=category_name).first()
    if category is None:
        category = Category(category_name=category_name, max_amount=max_amount)
        db.add(category)
        db.flush()
    return category


def get_or_create_department(name):
    department = db.query(Department).filter_by(name=name).first()
    if department is None:
        department = Department(name=name)
        db.add(department)
        db.flush()
    return department


def get_or_create_employee(name, email, password, role_id, department_id, is_active=True):
    emp = db.query(Employee).filter_by(email=email).first()
    if emp is None:
        emp = Employee(
            name=name,
            email=email,
            password_hash=Account.encrypt(password),
            role_id=role_id,
            is_active=is_active,
            department_id=department_id,
        )
        db.add(emp)
        db.flush()
    return emp


def get_or_create_account(username, password):
    acc = db.query(Account).filter_by(username=username).first()
    if acc is None:
        acc = Account(username=username, password=Account.encrypt(password))
        db.add(acc)
    return acc


try:
    # 1. Roles
    Finance_head = get_or_create_role("Finance_Head")
    Finance_admin = get_or_create_role("Finance_admin")
    Manager = get_or_create_role("Manager")
    employee = get_or_create_role("Employee")

    # 2. Categories
    get_or_create_category("Food", max_amount=5000)
    get_or_create_category("Hotel", max_amount=10000)
    get_or_create_category("Travel", max_amount=15000)
    get_or_create_category("Miscellaneous", max_amount=3000)

    # 3. Departments (manager assigned later once employees exist)
    IT = get_or_create_department("IT")
    HR = get_or_create_department("HR")
    Sales = get_or_create_department("Sales")
    Finance = get_or_create_department("Finance")

    # 4. Employees
    ram = get_or_create_employee("Ram", "ram@gmail.com", "ram@123", employee.id, IT.id)
    mani = get_or_create_employee("Mani", "mani@gmail.com", "mani@123", employee.id, IT.id)
    siva = get_or_create_employee("Siva", "siva@gmail.com", "siva@123", employee.id, IT.id)
    raghul = get_or_create_employee("Raghul", "raghul@gmail.com", "raghul@123", employee.id, IT.id)
    swetha = get_or_create_employee("Swetha", "swetha@gmail.com", "swetha@123", employee.id, HR.id)
    mohan = get_or_create_employee("Mohan", "mohan@gmail.com", "mohan@123", employee.id, HR.id)
    david = get_or_create_employee("David", "david@gmail.com", "david@123", employee.id, HR.id)
    hari = get_or_create_employee("Hari", "hari@gmail.com", "hari@123", employee.id, HR.id)
    priya = get_or_create_employee("Priya", "priya@gmail.com", "priya@123", employee.id, Sales.id)
    lavanya = get_or_create_employee("Lavanya", "lavanya@gmail.com", "lavanya@123", employee.id, Sales.id)
    sathish = get_or_create_employee("Sathish", "sathish@gmail.com", "sathish@123", employee.id, Sales.id)
    gopal = get_or_create_employee("Gopal", "gopal@gmail.com", "gopal@123", employee.id, Sales.id)
    sam = get_or_create_employee("Sam", "sam@gmail.com", "sam@123", employee.id, Finance.id)
    albert = get_or_create_employee("Albert", "albert@gmail.com", "albert@123", employee.id, Finance.id)
    rohini = get_or_create_employee("Rohini", "rohini@gmail.com", "rohini@123", employee.id, Finance.id)
    alice = get_or_create_employee("Alice", "alice@gmail.com", "alice@123", employee.id, Finance.id)

    walter = get_or_create_employee("Walter", "walter@gmail.com", "walter@123", Manager.id, IT.id)
    rajesh = get_or_create_employee("Rajesh", "rajesh@gmail.com", "rajesh@123", Manager.id, HR.id)
    bala = get_or_create_employee("Bala", "bala@gmail.com", "bala@123", Manager.id, Sales.id)
    ajay = get_or_create_employee("Ajay", "ajay@gmail.com", "ajay@123", Manager.id, Finance.id)

    kumar = get_or_create_employee("Kumar", "kumar@gmail.com", "kumar@123", Finance_admin.id, IT.id)
    rohan = get_or_create_employee("Rohan", "rohan@gmail.com", "rohan@123", Finance_admin.id, HR.id)
    charlie = get_or_create_employee("Charlie", "charlie@gmail.com", "charlie@123", Finance_admin.id, Sales.id)
    vinoth = get_or_create_employee("Vinoth", "vinoth@gmail.com", "vinoth@123", Finance_admin.id, Finance.id)

    ganesh = get_or_create_employee("Ganesh", "ganesh@gmail.com", "ganesh@123", Finance_head.id, Finance.id)

    db.flush()

    # 5. Assign department managers now that employees exist
    IT.manager_id = walter.id
    HR.manager_id = rajesh.id
    Sales.manager_id = bala.id
    Finance.manager_id = ajay.id

    # 5b. Backfill created_by on the roles now that the Finance_Head employee exists
    Finance_admin.created_by = ganesh.id
    Manager.created_by = ganesh.id
    employee.created_by = ganesh.id
    db.flush()

    # 6. Accounts
    get_or_create_account("Ram", "ram@123")
    get_or_create_account("Mani", "mani@123")
    get_or_create_account("Siva", "siva@123")
    get_or_create_account("Raghul", "raghul@123")
    get_or_create_account("Swetha", "swetha@123")
    get_or_create_account("Mohan", "mohan@123")
    get_or_create_account("David", "david@123")
    get_or_create_account("Hari", "hari@123")
    get_or_create_account("Priya", "priya@123")
    get_or_create_account("Lavanya", "lavanya@123")
    get_or_create_account("Sathish", "sathish@123")
    get_or_create_account("Gopal", "gopal@123")
    get_or_create_account("Sam", "sam@123")
    get_or_create_account("Albert", "albert@123")
    get_or_create_account("Rohini", "rohini@123")
    get_or_create_account("Alice", "alice@123")
    get_or_create_account("Walter", "walter@123")
    get_or_create_account("Rajesh", "rajesh@123")
    get_or_create_account("Bala", "bala@123")
    get_or_create_account("Ajay", "ajay@123")
    get_or_create_account("Kumar", "kumar@123")
    get_or_create_account("Rohan", "rohan@123")
    get_or_create_account("Charlie", "charlie@123")
    get_or_create_account("Vinoth", "vinoth@123")
    get_or_create_account("Ganesh", "ganesh@123")

    db.commit()
    print("Seed data inserted successfully (existing records were skipped).")
except Exception as e:
    db.rollback()
    print("Seed failed:", e)
finally:
    db.close()