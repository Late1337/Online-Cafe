from sqlalchemy import create_engine, String, Float, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import List
from flask_login import UserMixin
import bcrypt
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

PGUSER = "postgres"
PGPASSWORD = "your_password"

engine = create_engine(f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@localhost:5432/Online-Coffee-Shop", echo=True)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)

    def drop_db(self):
        Base.metadata.drop_all(engine)
        
class Users(Base, UserMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50), unique=True)

    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="user")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')    

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    weight: Mapped[str] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    ingredients: Mapped[str] = mapped_column(String(100))
    file_name: Mapped[str] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="item")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="item")


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["Users"] = relationship("Users", back_populates="cart_items")
    item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    order_time: Mapped[datetime] = mapped_column()
    order_list: Mapped[dict] = mapped_column(JSON)

    user: Mapped["Users"] = relationship("Users", back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_items")
    
base = Base()
base.create_db()
