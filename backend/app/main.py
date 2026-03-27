from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.users.routers import users_router
from apps.products.routers import product_router


app = FastAPI(title="SportShop API", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix='/users', tags=['Users'])
app.include_router(product_router, prefix='/products', tags=['Products'])


@app.get("/")
async def root():
    return {"message": "SportShop API is running"}
