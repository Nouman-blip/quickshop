from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine using connection settings from config
# The pool_pre_ping option enables connection health checks
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    # Echo SQL statements for debugging (disable in production)
    echo=False
)

# Create a session factory that will be used to create database sessions
# The factory ensures each request gets its own session
SessionLocal = sessionmaker(
    # Bind the session to our database engine
    bind=engine,
    # Enable automatic transaction handling
    autocommit=False,
    # Enable automatic object expiration after commit
    autoflush=True
)

# Dependency function to get a database session
def get_db():
    """Get a fresh database session for each request
    This function creates a new session, handles the request,
    and ensures the session is properly closed afterward
    """
    db = SessionLocal()
    try:
        # Return the session for use in the request
        yield db
    finally:
        # Ensure the session is closed even if there's an error
        db.close()