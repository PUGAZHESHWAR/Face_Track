from sqlalchemy import Column, String, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from models.base import Base

class Department(Base):
    __tablename__ = 'departments'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    code = Column(Text, unique=True)
    description = Column(Text)
    head_of_department = Column(Text)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey('organizations.id'))
    created_at = Column(Date)