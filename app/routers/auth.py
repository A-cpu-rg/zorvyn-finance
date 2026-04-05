from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - The **first** registered user is automatically granted the ADMIN role.
    - Subsequent users receive the role specified in the request body (default: viewer).
    - Only admins should call this in production to control who gets what role.
    """
    return register_user(payload, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate and receive a Bearer token.
    Use the token in the `Authorization: Bearer <token>` header for all protected routes.
    """
    return login_user(payload, db)
