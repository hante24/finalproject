from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from apps.core.dependencies import get_session, get_current_user
from apps.users.crud import user_manager
from apps.users.schemas import RegisterUserSchema, UserResponse
from apps.auth.password_handler import password_handler
from apps.auth.auth_handler import auth_handler

users_router = APIRouter()


@users_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: RegisterUserSchema,
    session=Depends(get_session)
):
    user = await user_manager.create(session, user_data)
    return {"id": user.id, "email": user.email, "name": user.name}


@users_router.post('/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session)
):
    user = await user_manager.get_by_email(session, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not password_handler.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    access_token = auth_handler.encode_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get('/my-info', response_model=UserResponse)
async def get_my_info(
    current_user=Depends(get_current_user)
):
    return current_user
