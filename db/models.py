from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(__name_pos=Integer, primary_key=True)
    username = Column(__name_pos=String(length=80), unique=True)
    email = Column(__name_pos=String(length=120), unique=True)
    password_hash = Column(__name_pos=String(length=256))