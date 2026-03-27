from apps.products.models import Product, Category, Cart, CartItem, Order, OrderItem
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status


class ProductManager:
    async def create_product(self, session, **data):
        product = Product(**data)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    async def get_product(self, session, product_id: int):
        query = select(Product).filter(Product.id == product_id).options(selectinload(Product.category))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_products(self, session, q: str = '', category_id: int = None):
        query = select(Product).options(selectinload(Product.category))
        
        if q := q.strip():
            words = [word for word in q.replace(',', ' ').split() if len(word) > 1]
            search_fields_condition = or_(
                and_(*(search_field.icontains(word) for word in words))
                for search_field in (Product.title, Product.description)
            )
            query = query.filter(search_fields_condition)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
            
        result = await session.execute(query)
        return list(result.scalars())


class CategoryManager:
    async def create_category(self, session, title, slug, description='', icon='🏃'):
        category = Category(title=title, slug=slug, description=description, icon=icon)
        session.add(category)
        await session.commit()
        return category
    
    async def get_categories(self, session):
        query = select(Category)
        result = await session.execute(query)
        return list(result.scalars())


class CartManager:
    async def get_or_create_cart(self, session, user_id):
        query = select(Cart).where(Cart.user_id == user_id).options(
            selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.category)
        )
        result = await session.execute(query)
        cart = result.scalar()
        
        if not cart:
            cart = Cart(user_id=user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        return cart
    
    async def add_to_cart(self, session, user_id, product_id, quantity=1):
        cart = await self.get_or_create_cart(session, user_id)
        
        query = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        result = await session.execute(query)
        existing_item = result.scalar()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(cart_item)
        
        await session.commit()
        return await self.get_or_create_cart(session, user_id)
    
    async def update_cart_item(self, session, user_id, cart_item_id, quantity):
        cart = await self.get_or_create_cart(session, user_id)
        
        query = select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id
        )
        result = await session.execute(query)
        cart_item = result.scalar()
        
        if cart_item:
            if quantity <= 0:
                await session.delete(cart_item)
            else:
                cart_item.quantity = quantity
            await session.commit()
        
        return await self.get_or_create_cart(session, user_id)
    
    async def remove_from_cart(self, session, user_id, cart_item_id):
        cart = await self.get_or_create_cart(session, user_id)
        
        query = select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id
        )
        result = await session.execute(query)
        cart_item = result.scalar()
        
        if cart_item:
            await session.delete(cart_item)
            await session.commit()
        
        return await self.get_or_create_cart(session, user_id)
    
    async def clear_cart(self, session, user_id):
        cart = await self.get_or_create_cart(session, user_id)
        
        query = select(CartItem).where(CartItem.cart_id == cart.id)
        result = await session.execute(query)
        items = result.scalars().all()
        
        for item in items:
            await session.delete(item)
        
        await session.commit()


class OrderManager:
    async def create_order(self, session, user_id, delivery_address, phone, customer_name):
        cart_mgr = CartManager()
        cart = await cart_mgr.get_or_create_cart(session, user_id)
        
        if not cart.items:
            return None
        
        total_amount = 0
        for item in cart.items:
            price = item.product.discount_price if item.product.discount_price else item.product.price
            total_amount += price * item.quantity
        
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            delivery_address=delivery_address,
            phone=phone,
            customer_name=customer_name
        )
        session.add(order)
        await session.flush()
        
        for item in cart.items:
            price = item.product.discount_price if item.product.discount_price else item.product.price
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=price
            )
            session.add(order_item)
        
        await cart_mgr.clear_cart(session, user_id)
        
        await session.commit()
        await session.refresh(order)
        return order
    
    async def get_user_orders(self, session, user_id):
        query = select(Order).where(Order.user_id == user_id).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).order_by(Order.created_at.desc())
        result = await session.execute(query)
        return list(result.scalars())


product_manager = ProductManager()
category_manager = CategoryManager()
cart_manager = CartManager()
order_manager = OrderManager()
