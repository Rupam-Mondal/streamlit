from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Gym(Base):
    __tablename__ = "gyms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    owner_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(250))

    branches: Mapped[list["Branch"]] = relationship(
        back_populates="gym", cascade="all, delete-orphan"
    )


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(250))
    city: Mapped[str] = mapped_column(String(80))
    gym_id: Mapped[int] = mapped_column(ForeignKey("gyms.id"))

    gym: Mapped[Gym] = relationship(back_populates="branches")
