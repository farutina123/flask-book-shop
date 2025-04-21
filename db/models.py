from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(length=80), unique=True)
    email = Column(String(length=120), unique=True)
    password_hash = Column(String(length=256))