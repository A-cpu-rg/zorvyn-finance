from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    UserListResponse,
    UserResponse,
    UserUpdate,
)


def get_all_users(db: Session, page: int = 1, page_size: int = 20) -> UserListResponse:
    query = db.query(User).filter(User.is_deleted == False)  # noqa: E712
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        users=[UserResponse.model_validate(u) for u in users],
    )


def get_user_by_id(user_id: int, db: Session) -> UserResponse:
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,  # noqa: E712
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


def update_user(user_id: int, payload: UserUpdate, db: Session) -> UserResponse:
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,  # noqa: E712
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def delete_user(user_id: int, requesting_user_id: int, db: Session) -> dict:
    """Soft delete — cannot delete yourself."""
    if user_id == requesting_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,  # noqa: E712
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_deleted = True
    user.is_active = False
    db.commit()
    return {"message": f"User '{user.name}' has been deleted"}


def change_password(user: User, payload: PasswordChange, db: Session) -> dict:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
