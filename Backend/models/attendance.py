from sqlalchemy import Column, String, Text, Date, ForeignKey, UUID, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from models.base import Base
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(PGUUID(as_uuid=True), ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # Present / Absent