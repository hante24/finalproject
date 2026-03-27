from apps.auth.password_handler import password_handler
from apps.users.models import User
from apps.users.schemas import RegisterUserSchema
from sqlalchemy import select
from fastapi import HTTPException, status


class UserManager:
    async def create(self, session, user_data: RegisterUserSchema) -> User:
        query = select(User).filter(User.email == user_data.email)
        result = await session.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                detail=f'User with email {user_data.email} already exists',
                status_code=status.HTTP_409_CONFLICT
            )
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=password_handler.get_password_hash(user_data.password)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def get(self, session, user_id: int) -> User | None:
        query = select(User).filter(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, session, email: str) -> User | None:
        query = select(User).filter(User.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()


user_manager = UserManager()
