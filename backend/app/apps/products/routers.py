from fastapi import APIRouter, status, Depends, Form, UploadFile, File, HTTPException, Request
from apps.core.dependencies import get_session, get_current_user
from apps.products.crud import product_manager, category_manager, cart_manager, order_manager
from apps.products.s3 import s3_service
from typing import List
from starlette.templating import Jinja2Templates
import uuid

product_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@product_router.post('/categories/create', status_code=status.HTTP_201_CREATED)
async def create_category(
    title: str = Form(),
    slug: str = Form(),
    description: str = Form(default=""),
    icon: str = Form(default="🏃"),
    session=Depends(get_session)
):
    category = await category_manager.create_category(
        session=session,
        title=title,
        slug=slug,
        description=description,
        icon=icon
    )
    return category


@product_router.get('/categories')
async def get_categories(session=Depends(get_session)):
    categories = await category_manager.get_categories(session=session)
    return categories


@product_router.post('/create', status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_product(
    title: str = Form(),
    price: int = Form(gt=0),
    description: str = Form(default=""),
    stock: int = Form(default=0),
    discount_price: int = Form(default=None),
    category_id: int = Form(default=None),
    main_image: UploadFile = File(),
    image1: UploadFile = File(default=None),
    image2: UploadFile = File(default=None),
    session=Depends(get_session)
):
    product_uuid = uuid.uuid4()
    main_image_url = s3_service.upload_file(main_image, product_uuid=product_uuid)
    images = [s3_service.upload_file(i, product_uuid=product_uuid) for i in (image1, image2) if i]
    product = await product_manager.create_product(
        session=session,
        title=title, 
        price=price, 
        description=description, 
        uuid_id=product_uuid, 
        main_image=main_image_url, 
        images=images,
        category_id=category_id,
        stock=stock,
        discount_price=discount_price
    )
    return product


@product_router.get('/{product_uuid}')
async def get_product(
    product_uuid: uuid.UUID,
    session=Depends(get_session)
):
    product = await product_manager.get_product(
        session=session,
        product_uuid=product_uuid,
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    return product


@product_router.get('/')
async def get_products(
    q: str = '',
    category_id: int = None,
    session=Depends(get_session)
):
    products: list = await product_manager.get_products(
        session=session,
        q=q,
        category_id=category_id
    )
    return products


@product_router.get("/cart")
async def get_cart_page(
    request: Request,
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    if not user:
         raise HTTPException(status_code=401)

    cart = await cart_manager.get_or_create_cart(session, user.id)

    return templates.TemplateResponse("pages/cart.html", {
        "request": request,
        "cart": cart
    })


@product_router.post('/cart/add', status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def add_to_cart(
    product_id: int = Form(),
    quantity: int = Form(default=1),
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    cart = await cart_manager.add_to_cart(
        session=session,
        user_id=current_user.id,
        product_id=product_id,
        quantity=quantity
    )
    return cart


@product_router.put('/cart/update/{cart_item_id}', dependencies=[Depends(get_current_user)])
async def update_cart_item(
    cart_item_id: int,
    quantity: int = Form(),
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    cart = await cart_manager.update_cart_item(
        session=session,
        user_id=current_user.id,
        cart_item_id=cart_item_id,
        quantity=quantity
    )
    return cart


@product_router.delete('/cart/remove/{cart_item_id}', dependencies=[Depends(get_current_user)])
async def remove_from_cart(
    cart_item_id: int,
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    cart = await cart_manager.remove_from_cart(
        session=session,
        user_id=current_user.id,
        cart_item_id=cart_item_id
    )
    return {"message": "Товар видалено", "cart": cart}


@product_router.delete('/cart/clear', dependencies=[Depends(get_current_user)])
async def clear_cart(
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    await cart_manager.clear_cart(session=session, user_id=current_user.id)
    return {"message": "Кошик очищено"}


@product_router.post('/orders/create', status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_order(
    delivery_address: str = Form(),
    phone: str = Form(),
    customer_name: str = Form(),
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    order = await order_manager.create_order(
        session=session,
        user_id=current_user.id,
        delivery_address=delivery_address,
        phone=phone,
        customer_name=customer_name
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Кошик порожній')
    return order


@product_router.get('/orders/my', dependencies=[Depends(get_current_user)])
async def get_my_orders(
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    orders = await order_manager.get_user_orders(session=session, user_id=current_user.id)
    return orders


@product_router.get('/orders/{order_id}', dependencies=[Depends(get_current_user)])
async def get_order(
    order_id: int,
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    order = await order_manager.get_order(session=session, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Замовлення не знайдено')
    return order