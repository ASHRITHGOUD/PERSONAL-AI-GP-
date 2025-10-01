# backend/routes/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES # <--- NEW IMPORTS
from ..models.user_model import UserCreate, UserLogin, UserResponse, Token # <--- NEW IMPORTS
from ..models.database import get_user_by_username, get_user_by_id # <--- NEW IMPORTS
from ..services.utility_service import verify_password, create_access_token, hash_password # <--- NEW IMPORTS

# --- Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/auth", tags=["auth"])

# --- All @router.post and @router.get endpoints go here ---
# ... (copy /register, /login, /me) ...