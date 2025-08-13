# app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import ACCESS_TOKEN

bearer_scheme = HTTPBearer(auto_error=False)

def require_bearer(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Sin credenciales o esquema incorrecto
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not ACCESS_TOKEN:
        # Config del servidor incompleta
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfigured: ACCESS_TOKEN not set",
        )

    # Token inválido
    if credentials.credentials != ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True
