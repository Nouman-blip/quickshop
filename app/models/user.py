from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    """User Model for storing user related details
    This model represents a user in the system with essential fields for authentication and user management
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Email is used as the primary way to identify/authenticate users
    email = Column(String, unique=True, index=True, nullable=False)
    # Hashed password is stored for security
    hashed_password = Column(String, nullable=False)
    # Full name of the user for display purposes
    full_name = Column(String, index=True)
    # Flag to indicate if the user is active (can login) or not
    is_active = Column(Boolean(), default=True)
    # Flag to identify admin users who have special privileges
    is_superuser = Column(Boolean(), default=False)
    # Automatically track when the user was created
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Automatically track when the user was last updated
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())