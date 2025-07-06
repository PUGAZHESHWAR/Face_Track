from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.student import Student
from models.staff import Staff
from models.department import Department
from models.class_model import Class
from models.organization import Organization
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Access individual variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Check for missing values
if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("One or more environment variables are missing")

# Build the DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()