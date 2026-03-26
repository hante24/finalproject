from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from apps.auth.auth_handler import auth_handler
from apps.core.dependencies import get_session, get_current_user
from apps.users.crud import user_manager, User
from apps.auth.password_handler import PasswordHandler
from apps.users.schemas import RegisterUserSchema, UserBaseFieldsSchema

users_router = APIRouter()


@users_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(user_register_data: RegisterUserSchema, session=Depends(    get_session   )) -> UserBaseFieldsSchema:
    user = await user_manager.create_user(session=session, user_register_data=user_register_data)
    return user


@users_router.post('/login')
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(    get_session   )
):
    user: User = await user_manager.get(session, data.username)
    if not user:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    is_password_valid = await PasswordHandler.verify_password(data.password, user.hashed_password)
    if not is_password_valid:
        raise HTTPException(detail="incorrect password", status_code=status.HTTP_400_BAD_REQUEST)

    return await auth_handler.get_access_token(user)


@users_router.get('/my-info')
async def get_my_info(user: User = Depends(get_current_user)) -> UserBaseFieldsSchema:
    return user