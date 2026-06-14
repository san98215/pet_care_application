from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # JSON array of {"category": str, "weight": float} representing auxiliary priorities
    priorities: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # cascade="all, delete-orphan": deleting a user removes their pets/logs/check-ins too
    pets: Mapped[list["Pet"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    task_logs: Mapped[list["TaskLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    check_ins: Mapped[list["CheckIn"]] = relationship(back_populates="user", cascade="all, delete-orphan")
