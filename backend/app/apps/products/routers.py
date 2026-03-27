from fastapi import APIRouter, status, Depends, Form
from apps.core.dependencies import get_session, get_current_user
from apps.products.crud import product_manager, category_manager, cart_manager, order_manager
from fastapi import HTTPException

product_router = APIRouter()



@product_router.get('/categories')
async def get_categories(session=Depends(get_session)):
    return await category_manager.get_categories(session=session)



@product_router.get('/')
async def get_products(
    q: str = '',
    category_id: int = None,
    session=Depends(get_session)
):
    return await product_manager.get_products(session=session, q=q, category_id=category_id)


# CART — обов'язково перед /{product_id}, інакше "cart" сприймається як product_id
@product_router.get('/cart/my', dependencies=[Depends(get_current_user)])
async def get_my_cart(
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    return await cart_manager.get_or_create_cart(session=session, user_id=current_user.id)


@product_router.post('/cart/add', status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def add_to_cart(
    product_id: int = Form(),
    quantity: int = Form(default=1),
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    return await cart_manager.add_to_cart(
        session=session,
        user_id=current_user.id,
        product_id=product_id,
        quantity=quantity
    )


@product_router.put('/cart/update/{cart_item_id}', dependencies=[Depends(get_current_user)])
async def update_cart_item(
    cart_item_id: int,
    quantity: int = Form(),
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    return await cart_manager.update_cart_item(
        session=session,
        user_id=current_user.id,
        cart_item_id=cart_item_id,
        quantity=quantity
    )


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
    return {"message": "Item removed", "cart": cart}


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cart is empty')
    return order


@product_router.get('/orders/my', dependencies=[Depends(get_current_user)])
async def get_my_orders(
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    return await order_manager.get_user_orders(session=session, user_id=current_user.id)



@product_router.get('/{product_id}')
async def get_product(
    product_id: int,
    session=Depends(get_session)
):
    product = await product_manager.get_product(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
    return product
