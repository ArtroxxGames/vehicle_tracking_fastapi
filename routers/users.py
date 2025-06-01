from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from auth_utils import verify_token, get_current_user

router = APIRouter()
security = HTTPBearer()

@router.get("/profile", response_model=UserResponse)
async def get_profile(db: Session = Depends(get_db), token: str = Depends(security)):
    """Obtener perfil del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Actualizar perfil del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Actualizar campos si se proporcionan
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/profile")
async def delete_account(db: Session = Depends(get_db), token: str = Depends(security)):
    """Eliminar cuenta del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Marcar como inactivo en lugar de eliminar por completo
    current_user.is_active = False
    db.commit()
    
    return {"message": "Cuenta desactivada exitosamente"}
