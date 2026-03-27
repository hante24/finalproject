from apps.core.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Float, Text


class Category(Base):
    __tablename__ = 'categories'
    
    title: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(default='')
    icon: Mapped[str] = mapped_column(default='🏃')
    
    products = relationship("Product", back_populates="category")


class Product(Base):
    title: Mapped[str] = mapped_column(unique=True)
    price: Mapped[int]
    description: Mapped[str] = mapped_column(Text, default='')
    main_image: Mapped[str]
    stock: Mapped[int] = mapped_column(default=0)
    discount_price: Mapped[int] = mapped_column(nullable=True, default=None)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=True)
    
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class Cart(Base):
    __tablename__ = 'carts'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = 'cart_items'
    
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(default=1)
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = 'orders'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    total_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(default='pending')
    delivery_address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(20))
    customer_name: Mapped[str] = mapped_column(String(100))
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int]
    price: Mapped[float] = mapped_column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
