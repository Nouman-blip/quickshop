from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.crud.user import user as crud_user
from app.api.deps import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[UserInDB])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_superuser)
) -> Any:
    """Retrieve users. Only superusers can access this endpoint."""
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserInDB)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """Create new user."""
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
    user = crud_user.create(db, obj_in=user_in)
    return user

@router.get("/me", response_model=UserInDB)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Get current user."""
    return current_user

@router.put("/me", response_model=UserInDB)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Update own user."""
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=UserInDB)
def read_user_by_id(
    user_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific user by id."""
    user = crud_user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user