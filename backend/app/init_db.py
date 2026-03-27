import asyncio
from apps.core.base_model import async_session_maker
from apps.products.crud import category_manager, product_manager
import uuid
from apps.users.models import User
from apps.products.models import Category, Product, Cart


async def init_database():
    
    async with async_session_maker() as session:
        print(" Починаємо ініціалізацію бази даних...")

        categories_data = [
            {
                "title": "Футбол",
                "slug": "football",
                "description": "Все для футболу: м'ячі, взуття, форма",
                "icon": "⚽"
            },
            {
                "title": "Баскетбол",
                "slug": "basketball",
                "description": "Баскетбольне спорядження",
                "icon": "🏀"
            },
            {
                "title": "Теніс",
                "slug": "tennis",
                "description": "Ракетки, м'ячі та аксесуари для тенісу",
                "icon": "🎾"
            },
            {
                "title": "Біг",
                "slug": "running",
                "description": "Кросівки та одяг для бігу",
                "icon": "🏃"
            },
            {
                "title": "Фітнес",
                "slug": "fitness",
                "description": "Обладнання для фітнесу та тренажерного залу",
                "icon": "💪"
            },
            {
                "title": "Плавання",
                "slug": "swimming",
                "description": "Купальники, окуляри, шапочки",
                "icon": "🏊"
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            try:
                category = await category_manager.create_category(session, **cat_data)
                categories.append(category)
                print(f" Створено категорію: {cat_data['title']}")
            except Exception as e:
                print(f"  Категорія {cat_data['title']} вже існує або помилка: {e}")

        products_data = [
            {
                "title": "М'яч футбольний Nike Strike",
                "price": 1200,
                "discount_price": 999,
                "description": "Професійний футбольний м'яч для тренувань та ігор",
                "stock": 15,
                "category_id": 1,
                "main_image": "https://images.unsplash.com/photo-1614632537197-38a17061c2bd?w=500",
                "images": []
            },
            {
                "title": "Бутси Nike Mercurial",
                "price": 3500,
                "discount_price": 2999,
                "description": "Професійні футбольні бутси з ідеальним зчепленням",
                "stock": 10,
                "category_id": 1,
                "main_image": "https://images.unsplash.com/photo-1628253747716-5cf2b23c9ea9?w=500",
                "images": []
            },
            {
                "title": "М'яч баскетбольний Spalding",
                "price": 1500,
                "discount_price": None,
                "description": "Офіційний ігровий баскетбольний м'яч",
                "stock": 20,
                "category_id": 2,
                "main_image": "https://images.unsplash.com/photo-1519861531473-9200262188bf?w=500",
                "images": []
            },
            {
                "title": "Кросівки Nike Air Jordan",
                "price": 5000,
                "discount_price": 4500,
                "description": "Легендарні баскетбольні кросівки",
                "stock": 8,
                "category_id": 2,
                "main_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                "images": []
            },
            {
                "title": "Ракетка Wilson Pro Staff",
                "price": 4500,
                "discount_price": None,
                "description": "Професійна тенісна ракетка для досвідчених гравців",
                "stock": 12,
                "category_id": 3,
                "main_image": "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=500",
                "images": []
            },
            {
                "title": "М'ячі для тенісу Head ATP",
                "price": 350,
                "discount_price": 299,
                "description": "Набір з 3 тенісних м'ячів",
                "stock": 50,
                "category_id": 3,
                "main_image": "https://images.unsplash.com/photo-1545161398-1d79a0a96db4?w=500",
                "images": []
            },
            {
                "title": "Кросівки для бігу Asics Gel",
                "price": 2800,
                "discount_price": 2499,
                "description": "Професійні кросівки для бігу з амортизацією",
                "stock": 15,
                "category_id": 4,
                "main_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                "images": []
            },
            {
                "title": "Фітнес-трекер Garmin",
                "price": 4000,
                "discount_price": None,
                "description": "Розумний годинник для відстеження тренувань",
                "stock": 10,
                "category_id": 4,
                "main_image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
                "images": []
            },
            {
                "title": "Гантелі розбірні 20кг",
                "price": 1500,
                "discount_price": 1299,
                "description": "Набір розбірних гантелей для домашніх тренувань",
                "stock": 25,
                "category_id": 5,
                "main_image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500",
                "images": []
            },
            {
                "title": "Коврик для йоги Premium",
                "price": 800,
                "discount_price": None,
                "description": "Нековзний коврик для йоги та пілатесу",
                "stock": 30,
                "category_id": 5,
                "main_image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500",
                "images": []
            },
            {
                "title": "Окуляри для плавання Speedo",
                "price": 600,
                "discount_price": 499,
                "description": "Професійні окуляри для плавання з захистом від UV",
                "stock": 40,
                "category_id": 6,
                "main_image": "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=500",
                "images": []
            },
            {
                "title": "Купальник Arena Carbon",
                "price": 2500,
                "discount_price": 1999,
                "description": "Професійний купальник для змагань",
                "stock": 15,
                "category_id": 6,
                "main_image": "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=500",
                "images": []
            }
        ]
        
        for prod_data in products_data:
            try:
                product = await product_manager.create_product(
                    session=session,
                    uuid_id=uuid.uuid4(),
                    **prod_data
                )
                print(f" Створено товар: {prod_data['title']}")
            except Exception as e:
                print(f"️  Товар {prod_data['title']} вже існує або помилка: {e}")
        
        print("\n Ініціалізація завершена успішно!")
        print(" Створено категорій:", len(categories_data))
        print(" Створено товарів:", len(products_data))


if __name__ == "__main__":
    asyncio.run(init_database())
