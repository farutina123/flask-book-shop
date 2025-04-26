from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float
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


class Genre(Base):
    __tablename__ = "genres"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)