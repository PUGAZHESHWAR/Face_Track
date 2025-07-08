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
    created_at: date

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

@app.get("/api/organizations", response_model=List[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()
    return orgs