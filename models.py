from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import List
from database import Base
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint

import uuid

"""
    Define the database models. 
    (Note: Models not at state of newest migration but contain enough information to add new products 
    (other values are defaulted in DB). 
    As database connector will be changed to prisma)

"""

class Color(Base):
    __tablename__ = "colors"
    id: Mapped[UUID] = mapped_column(UUID,primary_key=True,default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(50))
    hex: Mapped[str] = mapped_column(String(9))
    display_hex: Mapped[str] = mapped_column(String(9))
    products: Mapped[List["Product"]] = relationship(back_populates="color")

    __table_args__ = (
        UniqueConstraint("hex"), 
    )

class Size(Base):
    __tablename__ = "sizes"
    id: Mapped[UUID] = mapped_column(UUID,primary_key=True,default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(50))
    width: Mapped[float] = mapped_column(Float)
    height: Mapped[float] = mapped_column(Float)
    products: Mapped[List["Product"]] = relationship(back_populates="size")


class Shape(Base):
    __tablename__ = "shapes"
    id: Mapped[UUID] = mapped_column(UUID,primary_key=True,default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(50))
    products: Mapped[List["Product"]] = relationship(back_populates="shape")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(UUID,primary_key=True,default=uuid.uuid4)

    color_id: Mapped[UUID] = mapped_column(ForeignKey("colors.id"))
    color: Mapped["Color"] = relationship(back_populates="products")

    size_id: Mapped[UUID] = mapped_column(ForeignKey("sizes.id"))
    size: Mapped["Size"] = relationship(back_populates="products")

    shape_id: Mapped[UUID] = mapped_column(ForeignKey("shapes.id"))
    shape: Mapped["Shape"] = relationship(back_populates="products")

    count: Mapped[Integer] = mapped_column(Integer, default=1)

    __table_args__ = (
        UniqueConstraint("color_id", "size_id", "shape_id"), 
    )



