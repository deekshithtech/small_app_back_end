# app/__init__.py

# Package version
__version__ = "0.1.0"

# Import important modules to make them available when importing the package
from .main import app
from . import models, schemas, database

# Optional: You can define what gets imported with `from app import *`
__all__ = ['app', 'models', 'schemas', 'database']