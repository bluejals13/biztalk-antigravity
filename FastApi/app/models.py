# app/models.py
from app.database import Base
from sqlalchemy import Column, DateTime, String, Text, func


class HistoryRecord(Base):
  __tablename__ = "history_records"

  id = Column(String(36), primary_key=True)
  task_type = Column(String(50), nullable=False)
  provider = Column(String(50), nullable=False)
  input_data = Column(Text, nullable=True)
  result_data = Column(Text, nullable=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())