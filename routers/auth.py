from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User
from schemas import UserCreate, LoginRequest, Token, UserResponse
from auth_utils import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    # Verificar si el email ya existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el username ya existe
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(db: Session = Depends(get_db), token: str = Depends(security)):
    """Obtener información del usuario actual"""
    from auth_utils import verify_token, get_current_user
    
    email = verify_token(token)
    current_user = get_current_user(db, email)
    return current_user
