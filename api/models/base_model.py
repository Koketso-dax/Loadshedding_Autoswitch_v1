"""
    Module for common base class
"""
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
    """ Common class inheriting from declarative base """
    pass
