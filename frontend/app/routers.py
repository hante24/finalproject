from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import httpx
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory='templates')

async def get_user(requests: Request) -> dict:
    access_token = requests.cookies.get('access_token')
    if not access_token:
        return {}
    async with httpx.AsyncClient() as client_login:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {access_token}"
        }
        response_login = await client_login.get('http://backend:8000/users/my-info', headers=headers)
        if response_login.status_code == 200:
            return response_login.json()
        return {}

async def get_cart_count(requests: Request) -> int:
    access_token = requests.cookies.get('access_token')
    if not access_token:
        return 0
    try:
        async with httpx.AsyncClient() as client:
            headers = {'Authorization': f"Bearer {access_token}"}
            response = await client.get('http://backend:8000/products/cart/my', headers=headers)
            if response.status_code == 200:
                cart_data = response.json()
                return sum(item['quantity'] for item in cart_data.get('items', []))
    except:
        pass
    return 0

@router.get("/")
async def index(requests: Request, user: dict = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        categories_response = await client.get('http://backend:8000/products/categories')
        categories = categories_response.json() if categories_response.status_code == 200 else []
        products_response = await client.get('http://backend:8000/products/')
        products = products_response.json() if products_response.status_code == 200 else []
    cart_count = await get_cart_count(requests)
    context = {"user": user, 'request': requests, 'categories': categories, 'products': products, 'cart_count': cart_count}
    return templates.TemplateResponse(request=requests,name='pages/index.html',context=context)


@router.get("/catalog")
async def catalog(requests: Request,q: str = "",category_id: Optional[str] = None,user: dict = Depends(get_user)):
    valid_category_id = int(category_id) if category_id and category_id.isdigit() else None

    async with httpx.AsyncClient() as client:
        categories_response = await client.get('http://backend:8000/products/categories')
        categories = categories_response.json() if categories_response.status_code == 200 else []

        params = {'q': q}
        if valid_category_id:
            params['category_id'] = valid_category_id

        products_response = await client.get('http://backend:8000/products/', params=params)
        products = products_response.json() if products_response.status_code == 200 else []

    cart_count = await get_cart_count(requests)
    context = {
        "user": user,
        'request': requests,
        'categories': categories,
        'products': products,
        'cart_count': cart_count,
        'search_query': q,
        'selected_category': valid_category_id
    }
    return templates.TemplateResponse(request=requests, name='pages/catalog.html', context=context)

@router.get("/product/{product_uuid}")
async def product_detail(requests: Request, product_uuid: str, user: dict = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        product_response = await client.get(f'http://backend:8000/products/{product_uuid}')
        if product_response.status_code != 200:
            return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)
        product = product_response.json()
    cart_count = await get_cart_count(requests)
    context = {"user": user, 'request': requests, 'product': product, 'cart_count': cart_count}
    return templates.TemplateResponse(request=requests,name='pages/product.html', context=context)

@router.get("/cart")
async def cart_page(requests: Request, user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        cart_response = await client.get('http://backend:8000/products/cart/my', headers=headers)
        cart = cart_response.json() if cart_response.status_code == 200 else {'items': []}
    total = 0
    for item in cart.get('items', []):
        price = item['product'].get('discount_price') or item['product']['price']
        total += price * item['quantity']
    cart_count = sum(item['quantity'] for item in cart.get('items', []))
    context = {"user": user, 'request': requests, 'cart': cart, 'total': total, 'cart_count': cart_count}
    return templates.TemplateResponse(request=requests,name='pages/cart.html', context=context)

@router.post("/cart/add")
async def add_to_cart_action(requests: Request, product_id: int = Form(), quantity: int = Form(default=1), user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        data = {'product_id': product_id, 'quantity': quantity}
        await client.post('http://backend:8000/products/cart/add', headers=headers, data=data)
    referer = requests.headers.get('referer', '/')
    return RedirectResponse(referer, status_code=status.HTTP_303_SEE_OTHER)

@router.post("/cart/update/{cart_item_id}")
async def update_cart_action(requests: Request, cart_item_id: int, quantity: int = Form(), user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        data = {'quantity': quantity}
        await client.put(f'http://backend:8000/products/cart/update/{cart_item_id}', headers=headers, data=data)
    return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)

@router.post("/cart/remove/{cart_item_id}")
async def remove_from_cart_action(requests: Request, cart_item_id: int, user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        await client.delete(f'http://backend:8000/products/cart/remove/{cart_item_id}', headers=headers)
    return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)

@router.get("/checkout")
async def checkout_page(requests: Request, user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        cart_response = await client.get('http://backend:8000/products/cart/my', headers=headers)
        cart = cart_response.json() if cart_response.status_code == 200 else {'items': []}
    if not cart.get('items'):
        return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)
    total = 0
    for item in cart.get('items', []):
        price = item['product'].get('discount_price') or item['product']['price']
        total += price * item['quantity']
    cart_count = sum(item['quantity'] for item in cart.get('items', []))
    context = {"user": user, 'request': requests, 'cart': cart, 'total': total, 'cart_count': cart_count}
    return templates.TemplateResponse(request=requests,name='pages/checkout.html', context=context)

@router.post("/checkout")
async def checkout_action(requests: Request, delivery_address: str = Form(), phone: str = Form(), customer_name: str = Form(), user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        data = {'delivery_address': delivery_address, 'phone': phone, 'customer_name': customer_name}
        response = await client.post('http://backend:8000/products/orders/create', headers=headers, data=data)
        if response.status_code == 201:
            return RedirectResponse('/orders', status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse('/checkout', status_code=status.HTTP_303_SEE_OTHER)

@router.get("/orders")
async def orders_page(requests: Request, user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)
    access_token = requests.cookies.get('access_token')
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f"Bearer {access_token}"}
        orders_response = await client.get('http://backend:8000/products/orders/my', headers=headers)
        orders = orders_response.json() if orders_response.status_code == 200 else []
    cart_count = await get_cart_count(requests)
    context = {"user": user, 'request': requests, 'orders': orders, 'cart_count': cart_count}
    return templates.TemplateResponse(request=requests,name='pages/orders.html', context=context)

@router.get("/sign-up")
@router.post("/sign-up")
async def user_register(requests: Request, user: dict = Depends(get_user), username: str = Form(""), email: str = Form(""), password: str = Form("")):
    if user:
        return RedirectResponse(requests.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    context = {'request': requests}
    if requests.method == "GET":
        return templates.TemplateResponse(request=requests,name='pages/sign-up.html', context=context)
    async with httpx.AsyncClient() as client:
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        json_data = {'password': password, 'email': email, 'name': username}
        response = await client.post('http://backend:8000/users/create', json=json_data, headers=headers)
        if response.status_code == status.HTTP_201_CREATED:
            redirect_response = RedirectResponse(requests.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)
            async with httpx.AsyncClient() as client_login:
                headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
                json_data = {'password': password, 'username': email}
                response_login = await client_login.post('http://backend:8000/users/login', data=json_data, headers=headers)
            redirect_response.set_cookie('access_token', response_login.json()['access_token'], max_age=15*60)
            return redirect_response
        elif response.status_code == status.HTTP_409_CONFLICT:
            context['username'] = username
            context['email'] = email
            context['error'] = "Користувач з таким email вже існує"
            return templates.TemplateResponse(request=requests,name='pages/sign-up.html', context=context)

@router.get("/logout")
async def logout(requests: Request):
    redirect_response = RedirectResponse(requests.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.delete_cookie('access_token')
    return redirect_response

@router.get("/login")
@router.post("/login")
async def login(requests: Request, user: dict = Depends(get_user), email: str = Form(""), password: str = Form("")):
    redirect_response = RedirectResponse(requests.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    if user:
        return redirect_response
    context = {'request': requests, "email": email}
    if requests.method == "GET":
        return templates.TemplateResponse(request=requests,name='pages/login.html', context=context)
    async with httpx.AsyncClient() as client_login:
        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        json_data = {'password': password, 'username': email}
        response_login = await client_login.post('http://backend:8000/users/login', data=json_data, headers=headers)
    if response_login.status_code == status.HTTP_404_NOT_FOUND:
        context['error'] = "Користувач з таким email не знайдений"
        return templates.TemplateResponse(request=requests,name='pages/login.html', context=context)
    if response_login.status_code == status.HTTP_400_BAD_REQUEST:
        context['error'] = "перевірте введення паролю"
        return templates.TemplateResponse(request=requests,name='pages/login.html', context=context)
    redirect_response.set_cookie('access_token', response_login.json()['access_token'], max_age=15 * 60)
    return redirect_response
