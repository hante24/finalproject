from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import router

app = FastAPI(title="SportShop", debug=True)

app.mount('/static', StaticFiles(directory="static"), name='static')
app.include_router(router)

templates = Jinja2Templates(directory='templates')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
