from backend.app.apps.core.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    address: Mapped[str] = mapped_column(nullable=True)
    
    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")