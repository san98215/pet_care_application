from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(primary_key=True)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="pets")
    # uselist=False: one-to-one with PetState rather than a list
    state: Mapped["PetState"] = relationship(back_populates="pet", uselist=False, cascade="all, delete-orphan")


class PetState(Base):
    __tablename__ = "pet_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True enforces the one-to-one relationship with Pet at the DB level
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"), unique=True, nullable=False)
    mood: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    vitality: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    rolling_score_7d: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    pet: Mapped["Pet"] = relationship(back_populates="state")
