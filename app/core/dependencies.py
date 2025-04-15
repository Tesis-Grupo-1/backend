# app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from app.core.security import verify_token
from fastapi.security import OAuth2PasswordBearer

# El OAuth2PasswordBearer obtiene el token de la cabecera 'Authorization'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependencia para extraer y verificar el token JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verifica el token y devuelve el payload decodificado (usualmente, el email o ID del usuario)
    payload = verify_token(token)
    return payload  # Esto puede devolver la información del usuario decodificada desde el token
