from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import httpx

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

async def get_cart_count(request: Request) -> int:
    access_token = request.cookies.get('access_token')
    if not access_token:
        return 0
    try:
        async with httpx.AsyncClient() as client:
            headers = {'Authorization': f"Bearer {access_token}"}
            response = await client.get('http://backend:8000/products/cart/my', headers=headers, timeout=2.0)
            if response.status_code == 200:
                cart_data = response.json()
                items = cart_data.get('items', [])
                return sum(item['quantity'] for item in items)
    except Exception:
        pass
    return 0


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="pages/login.html", context={})

@router.post("/login")
async def login_action(request: Request, username: str = Form(), password: str = Form()):
    async with httpx.AsyncClient() as client:
        login_data = {"username": username, "password": password}
        response = await client.post("http://backend:8000/users/login", data=login_data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        redirect = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="access_token", value=token, httponly=True, max_age=86400, path="/")
        return redirect
    return RedirectResponse("/login?error=1", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/sign-up")
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="pages/sign-up.html", context={})

@router.post("/sign-up")
async def signup_action(request: Request, full_name: str = Form(), email: str = Form(), password: str = Form()):
    async with httpx.AsyncClient() as client:
        payload = {"name": full_name, "email": email, "password": password}
        response = await client.post("http://backend:8000/users/create", json=payload)
    if response.status_code == 201:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/sign-up?error=1", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout_action():
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@router.get("/")
async def index(request: Request, user: dict = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        try:
            cat_res = await client.get('http://backend:8000/products/categories', timeout=3.0)
            prod_res = await client.get('http://backend:8000/products/', timeout=3.0)
            categories = cat_res.json() if cat_res.status_code == 200 else []
            products = prod_res.json() if prod_res.status_code == 200 else []
        except Exception:
            categories, products = [], []

    context = {
        "request": request, "user": user, "categories": categories,
        "products": products, "cart_count": await get_cart_count(request)
    }
    return templates.TemplateResponse(request=request, name="pages/index.html", context=context)

@router.get("/catalog")
async def catalog(request: Request, q: str = "", category_id: str = None, user: dict = Depends(get_user)):
    valid_cat_id = int(category_id) if category_id and category_id.isdigit() else None
    async with httpx.AsyncClient() as client:
        categories_res = await client.get('http://backend:8000/products/categories')
        categories = categories_res.json() if categories_res.status_code == 200 else []
        params = {'q': q}
        if valid_cat_id: params['category_id'] = valid_cat_id
        products_res = await client.get('http://backend:8000/products/', params=params)
        products = products_res.json() if products_res.status_code == 200 else []

    context = {
        "request": request, "user": user, "categories": categories,
        "products": products, "cart_count": await get_cart_count(request),
        "search_query": q, "selected_category": valid_cat_id
    }
    return templates.TemplateResponse(request=request, name='pages/catalog.html', context=context)

@router.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int, user: dict = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        res = await client.get(f'http://backend:8000/products/{product_id}')
        if res.status_code != 200: return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)
        product = res.json()
    context = {"request": request, "user": user, "product": product, "cart_count": await get_cart_count(request)}
    return templates.TemplateResponse(request=request, name='pages/product.html', context=context)


@router.get("/cart")
async def cart_page(request: Request, user: dict = Depends(get_user)):
    if not user: return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = request.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        res = await client.get('http://backend:8000/products/cart/my', headers=headers)
        cart = res.json() if res.status_code == 200 else {'items': []}

    items = cart.get('items', [])
    total = sum((item['product'].get('discount_price') or item['product'].get('price', 0)) * item['quantity'] for item in items)

    context = {
        "request": request,
        "user": user,
        "cart_items": items,
        "total_price": total,
        "cart_count": sum(i['quantity'] for i in items)
    }
    return templates.TemplateResponse(request=request, name='pages/cart.html', context=context)


@router.post("/cart/add")
async def add_to_cart_action(request: Request, product_id: int = Form(...), quantity: int = Form(default=1),
                             user: dict = Depends(get_user)):
    if not user: return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)

    access_token = request.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}

        payload = {
            "product_id": int(product_id),
            "quantity": int(quantity)
        }

        response = await client.post(
            'http://backend:8000/products/cart/add',
            headers=headers,
            json=payload
        )

    print(f"СТАТУС: {response.status_code}, ВІДПОВІДЬ: {response.text}")

    referer = request.headers.get('referer', '/')
    return RedirectResponse(referer, status_code=status.HTTP_303_SEE_OTHER)

@router.post("/cart/remove/{cart_item_id}")
async def remove_from_cart_action(request: Request, cart_item_id: int, user: dict = Depends(get_user)):
    access_token = request.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        await client.delete(f'http://backend:8000/products/cart/remove/{cart_item_id}', headers=headers)
    return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)

@router.get("/checkout")
async def checkout_page(request: Request, user: dict = Depends(get_user)):
    if not user: return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = request.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        res = await client.get('http://backend:8000/products/cart/my', headers=headers)
        cart = res.json() if res.status_code == 200 else {'items': []}

    items = cart.get('items', [])
    total = sum((item['product'].get('discount_price') or item['product'].get('price', 0)) * item['quantity'] for item in items)
    context = {
        "request": request, "user": user, "cart_items": items,
        "total_price": total, "cart_count": len(items)
    }
    return templates.TemplateResponse(request=request, name='pages/checkout.html', context=context)

@router.post("/checkout")
async def checkout_action(request: Request, delivery_address: str = Form(), phone: str = Form(), customer_name: str = Form(), user: dict = Depends(get_user)):
    access_token = request.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        payload = {'delivery_address': delivery_address, 'phone': phone, 'customer_name': customer_name}
        await client.post('http://backend:8000/products/orders/create', headers=headers, json=payload)
    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


