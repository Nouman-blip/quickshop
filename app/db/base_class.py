from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """Base class for all database models
    This class provides common functionality and configuration for all models in the system
    """
    # Make the id attribute available to all models
    id: Any
    
    # Automatically generate table name from class name
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case for table names
        # e.g., UserProfile becomes user_profile
        return cls.__name__.lower()
    
    # Add a string representation for easier debugging
    def __repr__(self):
        attrs = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        return f"<{self.__class__.__name__}({attrs})>"