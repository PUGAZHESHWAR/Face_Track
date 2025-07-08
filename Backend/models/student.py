from sqlalchemy import Column, String, Text, Date, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from models.base import Base

class Student(Base):
    __tablename__ = 'students'
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roll_number = Column(Text,nullable=False)
    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    phone = Column(Text)
    address = Column(Text)
    course = Column(Text)
    semester = Column(Text)
    gender = Column(Text)
    date_of_birth = Column(Date)
    department_id = Column(PGUUID(as_uuid=True), ForeignKey('departments.id'))
    class_id = Column(PGUUID(as_uuid=True), ForeignKey('classes.id'))
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey('organizations.id'))
    created_at = Column(Date)