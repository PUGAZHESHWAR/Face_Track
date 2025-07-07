from sqlalchemy import Column, Text, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from db import Base

class Class(Base):
    __tablename__ = 'classes'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text)
    code = Column(Text, unique=True)
    department_id = Column(PGUUID(as_uuid=True), ForeignKey('departments.id'))
    semester = Column(Text)
    section = Column(Text)
    academic_year = Column(Text)
    capacity = Column(Integer)
    description = Column(Text)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey('organizations.id'))
    created_at = Column(Date)