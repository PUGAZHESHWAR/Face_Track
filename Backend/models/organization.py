from sqlalchemy import Column, Text, Date
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from db import Base

class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    address = Column(Text)
    contact = Column(Text)
    created_at = Column(Date)