from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from fastapi.responses import JSONResponse
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
import base64
import cv2
import numpy as np
import face_recognition
import json
import os
import logging
from PIL import Image
from io import BytesIO
import re

from auth import hash_password, verify_password, create_access_token

app = FastAPI(title="Auth API")
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "https://nill.com",
    "*" 
]
logger = logging.getLogger("uvicorn.error")
# Face images directory
images_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'face-images'))
os.makedirs(images_path, exist_ok=True)
face_registry_path = os.path.join(images_path, 'face_registry.json')

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
        
class ClassCreate(BaseModel):
    name: str
    code: Optional[str] = None
    department_id: UUID
    semester: Optional[str] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    organization_id: UUID


class ClassOut(ClassCreate):
    id: UUID
    created_at: Optional[date] = None

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

@app.get("/api/classes/{organization_id}", response_model=List[ClassOut])
def get_classes(organization_id: UUID, db: Session = Depends(get_db)):
    return db.query(Class).filter(Class.organization_id == organization_id).all()


@app.post("/api/classes/", response_model=ClassOut)
def create_class(data: ClassCreate, db: Session = Depends(get_db)):
    new_class = Class(**data.dict())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@app.put("/api/classes/{class_id}", response_model=ClassOut)
def update_class(class_id: UUID, data: ClassCreate, db: Session = Depends(get_db)):
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="Class not found")

    for key, value in data.dict().items():
        setattr(class_item, key, value)

    db.commit()
    db.refresh(class_item)
    return class_item


@app.delete("/api/classes/{class_id}")
def delete_class(class_id: UUID, db: Session = Depends(get_db)):
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="Class not found")

    try:
        db.delete(class_item)
        db.commit()
        return {"message": "Class deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to delete class. Possibly referenced elsewhere.")
    
@app.get("/students/by-roll/{roll_number}")
def get_student_by_roll(roll_number: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll_number == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": student.roll_number,
        "name": student.full_name,
        "type": "student",
        "department": student.course,
        "class": student.semester,
        "gender": student.gender,
        "email": student.email,
        "phone": student.phone,
        "dob": student.date_of_birth,
        "address": student.address,
    }
    
# Load known encodings from file (assumed format: { "stu_123": [[enc1], [enc2], ...], ... })
with open("face-images/face_registry.json", "r") as f:
    data_dict = json.load(f)

class FaceRequest(BaseModel):
    image: str  # base64 encoded

@app.post("/api/recognize-face")
async def recognize_face(request: FaceRequest):
    try:
        image_data = request.image

        # Remove base64 prefix if present
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]

        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JSONResponse(content={"error": "Invalid image data"}, status_code=400)

        # Convert to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect face
        face_locations = face_recognition.face_locations(rgb_img, model="hog")
        if not face_locations:
            return {"status": "no_face", "message": "No face detected"}

        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        if not face_encodings:
            return {"status": "no_encoding", "message": "Could not encode face"}

        input_encoding = face_encodings[0]

        # Compare with known faces
        tolerance = 0.5
        best_match = None
        best_distance = 1.0

        for registry_key, encodings in data_dict.items():
            known_encodings = [np.array(enc) for enc in encodings]
            distances = face_recognition.face_distance(known_encodings, input_encoding)
            min_distance = min(distances)

            if min_distance < best_distance:
                best_distance = min_distance
                best_match = registry_key

        if best_match and best_distance <= tolerance:
            if best_match.startswith("stu_"):
                reg_no = best_match[4:]
                return {
                    "status": "recognized",
                    "identifier": reg_no,
                    "confidence": float(f"{1 - best_distance:.2f}"),
                    "image_url": f"/face-images/{best_match}.jpg"
                }
            else:
                return {
                    "status": "recognized",
                    "identifier": best_match,
                    "confidence": float(f"{1 - best_distance:.2f}"),
                    "image_url": f"/face-images/{best_match}.jpg"
                }

        else:
            return {"status": "unrecognized", "message": "No matching face in registry"}

    except Exception as e:
        logger.error(f"Face recognition failed: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
def validate_roll_number(roll_number):
    """Validate roll number format"""
    if not roll_number:
        raise ValueError("Roll number is required")
    if not isinstance(roll_number, str):
        raise ValueError("Roll number must be a string")
    if not roll_number.strip():
        raise ValueError("Roll number cannot be blank")
    if not re.match(r'^[a-zA-Z0-9\-_]+$', roll_number):
        raise ValueError("Roll number contains invalid characters")
    return roll_number.strip()

def validate_employee_id(employee_id):
    """Validate employee ID format"""
    if not employee_id:
        raise ValueError("Employee ID is required")
    if not isinstance(employee_id, str):
        raise ValueError("Employee ID must be a string")
    if not employee_id.strip():
        raise ValueError("Employee ID cannot be blank")
    if not re.match(r'^[a-zA-Z0-9\-_]+$', employee_id):
        raise ValueError("Employee ID contains invalid characters")
    return employee_id.strip()

def save_face_data():
    try:
        with open(face_registry_path, 'w') as f:
            json.dump(data_dict, f)
    except Exception as e:
        logger.error(f"Error saving face data: {str(e)}")

def process_face_image(image_bytes, identifier):
    """Process and validate a face image"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image data")
        
        # Convert to RGB (face_recognition uses RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find face locations with multiple methods
        face_locations = face_recognition.face_locations(rgb_img, model="hog")
        if not face_locations:
            face_locations = face_recognition.face_locations(rgb_img, model="cnn")
        
        if not face_locations:
            raise ValueError("No face detected in image")
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        if not face_encodings:
            raise ValueError("Could not encode face")
        
        return face_encodings[0]
    except Exception as e:
        logger.error(f"Face processing failed: {str(e)}")
        raise

@app.post("/api/upload-face")
async def upload_face(
    face: UploadFile = File(...),
    identifier: str = Form(...),
    id_type: str = Form(...)
):
    try:
        if not face:
            raise HTTPException(status_code=400, detail="No file part")
        
        if id_type == 'student':
            identifier = validate_roll_number(identifier)
            prefix = 'stu_'
        elif id_type == 'staff':
            identifier = validate_employee_id(identifier)
            prefix = 'staff_'
        else:
            raise HTTPException(status_code=400, detail="Invalid ID type")

        if not identifier:
            raise HTTPException(status_code=400, detail="Identifier is required")

        contents = await face.read()
        if not contents:
            raise HTTPException(status_code=400, detail="No selected file")

        # Process face image
        face_encoding = process_face_image(contents, identifier)

        # Save with prefixed filename
        filename = f"{prefix}{identifier}.jpg"
        filepath = os.path.join(images_path, filename)

        img = Image.open(BytesIO(contents))
        img.save(filepath, 'JPEG', quality=85, optimize=True)

        # Update registry
        registry_key = f"{prefix}{identifier}"
        if registry_key not in data_dict:
            data_dict[registry_key] = []
        data_dict[registry_key].append(face_encoding.tolist())
        save_face_data()

        return {
            "success": True,
            "identifier": identifier,
            "id_type": id_type,
            "image_path": filename
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))