"""
Create db engine instance
"""
from models.base_model import Base
from flask_sqlalchemy import SQLAlchemy

# create db engine using sqlalchemy inheriting from declarative mapped base
db = SQLAlchemy(model_class=Base)
