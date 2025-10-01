# backend/routes/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models.user_model import UserCreate, UserLogin, UserResponse, Token 
from ..models.database import get_user_by_username, get_user_by_id # Includes DB helpers
from ..services.utility_service import verify_password, create_access_token, hash_password

# --- Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/auth", tags=["auth"])

# --- Routes (THIS IS THE MISSING CONTENT) ---

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing = await get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = hash_password(user.password)
    # The database collection is accessible via the get_user_by_username helper
    from ..models.database import users_collection 
    new_user = {"username": user.username, "hashed_password": hashed_pw}
    result = await users_collection.insert_one(new_user)

    return {"id": str(result.inserted_id), "username": user.username}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await get_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user["_id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": str(user["_id"]), "username": user["username"]}