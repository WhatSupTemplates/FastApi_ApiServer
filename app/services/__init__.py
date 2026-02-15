"""Services module initialization
Keep your business logic separate from API routes and data access.
"""
from app.services.user import UserService

__all__ = ["UserService"]
