from sqlalchemy import Column, String, Text, Date, Numeric, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from models.base import Base

class Staff(Base):
    __tablename__ = 'staff'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey('organizations.id'))
    department_id = Column(PGUUID(as_uuid=True), ForeignKey('departments.id'))
    employee_id = Column(Text, unique=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True)
    phone = Column(Text)
    role = Column(Text)
    designation = Column(Text)
    qualification = Column(Text)
    experience = Column(Numeric)
    address = Column(Text)
    date_of_birth = Column(Date)
    gender = Column(Text)
    joining_date = Column(Date)
    created_at = Column(Date)