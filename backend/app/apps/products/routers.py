import httpx
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory='templates')

async def get_user(request: Request) -> dict:
    access_token = request.cookies.get('access_token')
    if not access_token:
        return {}
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        try:
            response = await client.get('http://backend:8000/users/my-info', headers=headers, timeout=3.0)
            return response.json() if response.status_code == 200 else {}
        except Exception:
            return {}


@router.post("/cart/add")
async def add_to_cart_action(
        request: Request,
        product_id: int = Form(...),
        quantity: int = Form(1),
        user: dict = Depends(get_user)
):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)

    access_token = request.cookies.get('access_token')

    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}

        payload = {
            "product_id": str(product_id),
            "quantity": str(quantity)
        }

        response = await client.post(
            'http://backend:8000/products/cart/add',
            headers=headers,
            data=payload
        )

        print(f"DEBUG: Backend Status {response.status_code}, Body: {response.text}")

    referer = request.headers.get('referer')
    if referer:
        return RedirectResponse(referer, status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)