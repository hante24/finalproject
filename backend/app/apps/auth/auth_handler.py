from jose import jwt, JWTError
from datetime import datetime, timedelta
from settings import settings


class AuthHandler:
    secret = settings.SECRET_KEY
    algorithm = settings.ALGORITHM

    def encode_token(self, user_id: int) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise Exception("Invalid token")


auth_handler = AuthHandler()