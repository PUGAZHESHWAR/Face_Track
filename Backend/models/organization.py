from sqlalchemy import Column, Text, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime, timezone
import uuid
from models.base import Base

class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    address = Column(Text)
    contact = Column(Text)
    created_at = Column(
        DateTime(timezone=True),  # includes both date and time, with timezone info
        default=lambda: datetime.now(timezone.utc)  # timezone-aware UTC datetime
    )