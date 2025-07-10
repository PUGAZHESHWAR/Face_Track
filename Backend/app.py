from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from models.base import SessionLocal, engine, Base
from models.login import Login
from models.class_model import Class
from models.student import Student
from models.organization import Organization
from models.department import Department
from models.staff import Staff
from typing import List
from datetime import date
from typing import Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from auth import hash_password, verify_password, create_access_token

app = FastAPI(title="Auth API")
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "https://nill.com",
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Allowed origins
    allow_credentials=True,             # Send cookies/auth headers
    allow_methods=["*"],                # Allow all HTTP methods
    allow_headers=["*"],                # Allow all headers
)

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DepartmentData(BaseModel):
    name: str
    students: int

class DashboardResponse(BaseModel):
    totalStudents: int
    totalStaff: int
    totalDepartments: int
    totalClasses: int
    departmentData: List[DepartmentData]

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    address: str | None = None
    contact: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True
class OrganizationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    contact: Optional[str] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    created_at: Optional[date] = None
    
class StudentCreate(BaseModel):
    roll_number: str
    full_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    course: Optional[str]
    semester: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]
    department_id: UUID
    class_id: UUID
    organization_id: UUID

class StudentUpdate(BaseModel):
    roll_number: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    department_id: Optional[UUID]
    class_id: Optional[UUID]
    semester: Optional[str]
    course: Optional[str]
    address: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    organization_id: Optional[UUID]

    class Config:
        orm_mode = True

class StudentOut(BaseModel):
    id: UUID
    roll_number: str
    full_name: str
    email: str
    phone: Optional[str]
    department_id: Optional[UUID]
    class_id: Optional[UUID]
    semester: Optional[str]
    course: Optional[str]
    address: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    created_at: Optional[date]
    organization_id: UUID

    # # Nested relationships
    # departments: Optional[DepartmentOut]
    # classes: Optional[ClassOut]

    class Config:
        orm_mode = True
        
class DepartmentOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class ClassOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
        
class StaffBase(BaseModel):
    employee_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[UUID] = None
    role: Optional[str] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[float] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    joining_date: Optional[date] = None
    organization_id: UUID

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[UUID] = None
    role: Optional[str] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[float] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    joining_date: Optional[date] = None

class StaffOut(StaffBase):
    id: UUID
    class Config:
        orm_mode = True
        
class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    head_of_department: Optional[str] = None
    organization_id: UUID

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: UUID
    created_at: Optional[date]

    class Config:
        orm_mode = True

# REGISTER
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Login).filter(Login.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = Login(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# LOGIN
@app.post("/login", response_model=Token)
def login(payload:UserLogin, db: Session = Depends(get_db)):
    user = db.query(Login).filter(Login.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# PROTECTED ROUTE
@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    return {"message": "Access granted", "token": token}

@app.get("/api/dashboard/{org_id}", response_model=DashboardResponse)
def get_dashboard_data(org_id: UUID, db: Session = Depends(get_db)):
    total_students = db.query(Student).filter_by(organization_id=org_id).count()
    total_staff = db.query(Staff).filter_by(organization_id=org_id).count()
    total_departments = db.query(Department).filter_by(organization_id=org_id).count()
    total_classes = db.query(Class).filter_by(organization_id=org_id).count()
    departments = db.query(Department).filter_by(organization_id=org_id).all()

    department_data = []
    for dept in departments:
        student_count = db.query(Student).filter_by(department_id=dept.id).count()
        department_data.append({"name": dept.name, "students": student_count})

    return {
        "totalStudents": total_students,
        "totalStaff": total_staff,
        "totalDepartments": total_departments,
        "totalClasses": total_classes,
        "departmentData": department_data,
    }

@app.get("/organizations", response_model=List[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()
    return orgs

@app.post("/organizations", response_model=OrganizationResponse)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    org = Organization(**payload.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@app.put("/organizations/{org_id}", response_model=OrganizationResponse)
def update_organization(org_id: UUID, payload: OrganizationUpdate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(org, key, value)

    db.commit()
    db.refresh(org)
    return org

@app.delete("/organizations/{org_id}")
def delete_organization(org_id: UUID, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    db.delete(org)
    db.commit()
    return {"detail": "Organization deleted successfully"}

@app.get("/api/students/{organization_id}", response_model=List[StudentOut])
def get_students_by_org(organization_id: UUID, db: Session = Depends(get_db)):
    return db.query(Student).filter(Student.organization_id == organization_id).all()

@app.post("/api/students", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    student_dict = student.dict()
    student_dict["created_at"] = datetime.utcnow().date()
    db_student = Student(**student_dict)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.put("/api/students/{student_id}", response_model=StudentOut)
def update_student(student_id: UUID, update: StudentUpdate, db: Session = Depends(get_db)):
    print(f"Updating student with ID: {student_id} with data: {update.dict()}")
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/api/students/{student_id}")
def delete_student(student_id: UUID, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted"}

@app.get("/api/departments/{organization_id}", response_model=List[DepartmentOut])
def get_departments(organization_id: UUID, db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.organization_id == organization_id).all()

@app.get("/api/classes/{organization_id}", response_model=List[ClassOut])
def get_classes(organization_id: UUID, db: Session = Depends(get_db)):
    return db.query(Class).filter(Class.organization_id == organization_id).all()
@app.get("/api/staff/{organization_id}", response_model=List[StaffOut])
def get_staff(organization_id: UUID, db: Session = Depends(get_db)):
    return db.query(Staff).filter(Staff.organization_id == organization_id).all()

@app.post("/api/staff", response_model=StaffOut)
def create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    db_staff = Staff(**staff.dict())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@app.put("/api/staff/{staff_id}", response_model=StaffOut)
def update_staff(staff_id: UUID, update: StaffUpdate, db: Session = Depends(get_db)):
    db_staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(db_staff, key, value)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@app.delete("/api/staff/{staff_id}")
def delete_staff(staff_id: UUID, db: Session = Depends(get_db)):
    db_staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    db.delete(db_staff)
    db.commit()
    return {"message": "Deleted successfully"}

@app.get("{organization_id}", response_model=List[DepartmentOut])
def get_departments(organization_id: UUID, db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.organization_id == organization_id).all()

@app.post("/api/departments/", response_model=DepartmentOut)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    new_dept = Department(**dept.dict())
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

@app.put("/api/departments/{department_id}", response_model=DepartmentOut)
def update_department(department_id: UUID, dept_data: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    for key, value in dept_data.dict(exclude_unset=True).items():
        setattr(dept, key, value)

    db.commit()
    db.refresh(dept)
    return dept

@app.delete("/api/departments/{department_id}")
def delete_department(department_id: UUID, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    try:
        db.delete(department)
        db.commit()
        return {"message": "Department deleted successfully"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Department is still referenced by other records (e.g., classes)."
        )