from fastapi import FastAPI

from apps.products.routers import product_router
from apps.users.routers import users_router
from settings import settings


def get_application() -> FastAPI:
    _app = FastAPI(
        debug=settings.DEBUG
    )
    _app.include_router(users_router, prefix='/users', tags=['Users'])
    _app.include_router(product_router, prefix='/products', tags=['Products'])
    return _app


app = get_application()