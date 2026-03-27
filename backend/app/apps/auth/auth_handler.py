from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from settings import settings

class AuthHandler:
    secret = settings.SECRET_KEY
    algorithm = settings.ALGORITHM

    def encode_token(self, user_id: int) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'sub': str(user_id)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

auth_handler = AuthHandler()