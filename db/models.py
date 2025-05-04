from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID
Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column('id', Integer, primary_key=True)
    username = Column(String(length=80), unique=True)
    email = Column(String(length=120), unique=True)
    password_hash = Column(String(length=256))


class Genre(Base):
    __tablename__ = "genres"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)


class Book(Base):
    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(length=100))
    author = Column(String(length=80))
    price = Column(Float)
    genre = Column(String)
    cover = Column(String)
    description = Column(String)
    rating = Column(Float)
    year = Column(Integer)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_book = Column(String)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer)


class CartItem(Base):
    __tablename__ = "cartitems"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    count = Column(Integer, default=1)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    status = Column(String, default='Новый')
    user_id = Column(Integer, ForeignKey('users.id'))
    address = Column(String)
    price = Column(Float)


class OrderItem(Base):
    __tablename__ = "orderitems"
    id = Column(Integer, primary_key=True)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))
    count = Column(Integer)
    price = Column(Float)