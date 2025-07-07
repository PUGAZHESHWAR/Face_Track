from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from models.base import Base

class Login(Base):
    __tablename__ = "login"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)