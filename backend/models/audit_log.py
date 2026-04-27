from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_audit_log_user_id", "user_id"),
        Index("ix_audit_log_timestamp", "timestamp"),
    )
