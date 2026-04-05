from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user import (
    change_password,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me/password")
def update_my_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change your own password. Requires the current password for verification."""
    return change_password(current_user, payload, db)


# ── Admin-only endpoints ─────────────────────────────────────────────────────

@router.get("/", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """[Admin only] List all users with pagination."""
    return get_all_users(db, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """[Admin only] Get a specific user by ID."""
    return get_user_by_id(user_id, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_id(
    user_id: int,
    payload: UserUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """[Admin only] Update a user's name, role, or active status."""
    return update_user(user_id, payload, db)


@router.delete("/{user_id}")
def delete_user_by_id(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """[Admin only] Soft-delete a user. Cannot delete yourself."""
    return delete_user(user_id, requesting_user_id=current_user.id, db=db)
