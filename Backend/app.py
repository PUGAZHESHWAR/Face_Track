from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.base import SessionLocal, engine, Base
from models.login import Login
from models.class_model import Class
from models.student import Student
from models.organization import Organization
from models.department import Department
from models.staff import Staff

from auth import hash_password, verify_password, create_access_token

app = FastAPI(title="Auth API")

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

class Token(BaseModel):
    access_token: str
    token_type: str

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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Login).filter(Login.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# PROTECTED ROUTE
@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    return {"message": "Access granted", "token": token}