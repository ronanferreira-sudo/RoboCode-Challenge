import bcrypt
import unicodedata
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def _normalize_identifier(value: str) -> str:
    """Normaliza login para comparar ignorando acentos, maiusculas e espacos extras."""
    decomposed = unicodedata.normalize("NFKD", value.strip().casefold())
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(without_accents.split())


def find_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """Busca usuario por username ou email, ignorando acentos e caixa."""
    if not identifier:
        return None

    exact = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if exact:
        return exact

    target = _normalize_identifier(identifier)
    candidates = db.query(User).filter(
        (User.username.isnot(None)) | (User.email.isnot(None))
    ).all()
    matches = [
        user for user in candidates
        if _normalize_identifier(user.username or "") == target
        or _normalize_identifier(user.email or "") == target
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou sessão expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = find_user_by_identifier(db, username)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas o Administrador pode realizar esta ação!"
        )
    return current_user
