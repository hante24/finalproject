import asyncio
from apps.core.base_model import async_session_maker
from apps.products.crud import category_manager, product_manager
from apps.users.models import User


async def init_database():
    print(" Початок ініціалізації бази даних...")
    
    async with async_session_maker() as session:
        categories_data = [
            {"title": "Футбол", "slug": "football", "description": "М'ячі, бутси, форма", "icon": "⚽"},
            {"title": "Баскетбол", "slug": "basketball", "description": "Все для баскетболу", "icon": "🏀"},
            {"title": "Теніс", "slug": "tennis", "description": "Ракетки та м'ячі", "icon": "🎾"},
            {"title": "Біг", "slug": "running", "description": "Кросівки для бігу", "icon": "🏃"},
            {"title": "Фітнес", "slug": "fitness", "description": "Тренажери та аксесуари", "icon": "💪"},
            {"title": "Плавання", "slug": "swimming", "description": "Спорядження для плавання", "icon": "🏊"}
        ]
        
        for cat_data in categories_data:
            try:
                await category_manager.create_category(session, **cat_data)
                print(f" Категорія: {cat_data['title']}")
            except:
                print(f"  Категорія {cat_data['title']} вже існує")

        football_products = [
            {"title": "М'яч Nike Premier League", "price": 1500, "discount_price": 1299, "stock": 20, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1614632537197-38a17061c2bd?w=800", "description": "Офіційний м'яч Прем'єр Ліги"},
            {"title": "Бутси Adidas Predator", "price": 4500, "discount_price": 3999, "stock": 15, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1628253747716-5cf2b23c9ea9?w=800", "description": "Професійні бутси"},
            {"title": "Футбольна форма Barcelona", "price": 2500, "discount_price": None, "stock": 30, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800", "description": "Оригінальна форма"},
            {"title": "Щитки Nike Mercurial", "price": 800, "discount_price": 699, "stock": 50, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1551958219-acbc608c6377?w=800", "description": "Захист для гомілок"},
            {"title": "Воротарські рукавички", "price": 1200, "discount_price": None, "stock": 25, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=800", "description": "Професійні рукавички"},
            {"title": "Футбольні гетри Pro", "price": 350, "discount_price": 299, "stock": 100, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=800", "description": "Компресійні гетри"},
            {"title": "Тренувальний м'яч Puma", "price": 900, "discount_price": None, "stock": 40, "category_id": 1, "main_image": "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=800", "description": "Для тренувань"},
        ]

        basketball_products = [
            {"title": "М'яч Spalding NBA", "price": 1800, "discount_price": 1599, "stock": 25, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1519861531473-9200262188bf?w=800", "description": "Офіційний м'яч NBA"},
            {"title": "Кросівки Nike Air Jordan 1", "price": 6000, "discount_price": 5499, "stock": 10, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", "description": "Легендарні кросівки"},
            {"title": "Баскетбольна форма Lakers", "price": 2800, "discount_price": None, "stock": 20, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1515523110800-9415d13b84a8?w=800", "description": "Форма команди Lakers"},
            {"title": "Кросівки Under Armour Curry", "price": 5500, "discount_price": 4999, "stock": 12, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800", "description": "Signature взуття Curry"},
            {"title": "Баскетбольний м'яч Wilson", "price": 1400, "discount_price": None, "stock": 30, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800", "description": "Професійний м'яч"},
            {"title": "Компресійні тайтси Nike Pro", "price": 1100, "discount_price": 999, "stock": 35, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=800", "description": "Компресійний одяг"},
            {"title": "Баскетбольні наколінники", "price": 650, "discount_price": None, "stock": 45, "category_id": 2, "main_image": "https://images.unsplash.com/photo-1577212017308-894e5bb8ee49?w=800", "description": "Захист колін"},
        ]

        tennis_products = [
            {"title": "Ракетка Wilson Pro Staff", "price": 5500, "discount_price": 4999, "stock": 15, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=800", "description": "Професійна ракетка"},
            {"title": "М'ячі для тенісу Head ATP", "price": 450, "discount_price": 399, "stock": 80, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1545161398-1d79a0a96db4?w=800", "description": "Набір з 3 м'ячів"},
            {"title": "Ракетка Babolat Pure Drive", "price": 6000, "discount_price": None, "stock": 12, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1617083278895-c2f8e25c5da1?w=800", "description": "Топова ракетка"},
            {"title": "Тенісні кросівки Asics Gel", "price": 3200, "discount_price": 2899, "stock": 20, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=800", "description": "Професійне взуття"},
            {"title": "Сумка для ракеток Wilson", "price": 1800, "discount_price": None, "stock": 18, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800", "description": "На 6 ракеток"},
            {"title": "Тенісний одяг Adidas", "price": 1600, "discount_price": 1399, "stock": 25, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1622630998477-20aa696ecb05?w=800", "description": "Комплект форми"},
            {"title": "Намотка Wilson Pro", "price": 250, "discount_price": None, "stock": 60, "category_id": 3, "main_image": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800", "description": "Професійна намотка"},
        ]

        running_products = [
            {"title": "Кросівки Nike ZoomX", "price": 4800, "discount_price": 4299, "stock": 18, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", "description": "Для марафону"},
            {"title": "Кросівки Asics Gel-Kayano", "price": 4200, "discount_price": None, "stock": 22, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800", "description": "Максимальна амортизація"},
            {"title": "Спортивні годинники Garmin", "price": 8500, "discount_price": 7999, "stock": 10, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800", "description": "GPS трекер"},
            {"title": "Компресійні гетри 2XU", "price": 1200, "discount_price": 1099, "stock": 30, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800", "description": "Для відновлення"},
            {"title": "Спортивна футболка Nike Dri-FIT", "price": 1100, "discount_price": None, "stock": 40, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800", "description": "Вологовідвідна тканина"},
            {"title": "Біговий пояс FlipBelt", "price": 850, "discount_price": 749, "stock": 35, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=800", "description": "Для телефону та ключів"},
            {"title": "Кросівки Adidas Ultraboost", "price": 5200, "discount_price": None, "stock": 15, "category_id": 4, "main_image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800", "description": "Boost технологія"},
        ]

        fitness_products = [
            {"title": "Гантелі розбірні 20кг", "price": 2200, "discount_price": 1999, "stock": 25, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800", "description": "Набір гантелей"},
            {"title": "Коврик для йоги Manduka", "price": 1800, "discount_price": None, "stock": 40, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=800", "description": "Преміум якість"},
            {"title": "Фітнес-резинки набір", "price": 650, "discount_price": 549, "stock": 60, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=800", "description": "5 рівнів опору"},
            {"title": "Гиря 16кг", "price": 1400, "discount_price": None, "stock": 30, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800", "description": "Чавунна гиря"},
            {"title": "Штанга 50кг", "price": 4500, "discount_price": 3999, "stock": 12, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800", "description": "З набором блінів"},
            {"title": "Скакалка швидкісна", "price": 450, "discount_price": 399, "stock": 50, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800", "description": "Для кросфіту"},
            {"title": "М'яч медичний 5кг", "price": 1100, "discount_price": None, "stock": 28, "category_id": 5, "main_image": "https://images.unsplash.com/photo-1584380931214-dbb5b72e7fd0?w=800", "description": "Для функціоналу"},
        ]

        swimming_products = [
            {"title": "Окуляри Speedo Fastskin", "price": 1200, "discount_price": 1099, "stock": 35, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800", "description": "Професійні окуляри"},
            {"title": "Купальник Arena Carbon", "price": 3500, "discount_price": 2999, "stock": 15, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1576610616656-d3aa5d1f4534?w=800", "description": "Для змагань"},
            {"title": "Плавки Speedo Endurance", "price": 850, "discount_price": None, "stock": 40, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1576610616656-d3aa5d1f4534?w=800", "description": "Хлоростійкі"},
            {"title": "Шапочка силіконова TYR", "price": 350, "discount_price": 299, "stock": 60, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1519827551626-2c1157d4d0af?w=800", "description": "Не ковзає"},
            {"title": "Дошка для плавання", "price": 550, "discount_price": None, "stock": 30, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1519827551626-2c1157d4d0af?w=800", "description": "Для тренувань"},
            {"title": "Ласти короткі Speedo", "price": 1400, "discount_price": 1199, "stock": 25, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1519827551626-2c1157d4d0af?w=800", "description": "Тренувальні ласти"},
            {"title": "Рушник з мікрофібри", "price": 650, "discount_price": None, "stock": 45, "category_id": 6, "main_image": "https://images.unsplash.com/photo-1582735689330-9e8b0c0e5d0b?w=800", "description": "Швидко сохне"},
        ]
        
        all_products = (football_products + basketball_products + tennis_products + 
                       running_products + fitness_products + swimming_products)
        
        for prod_data in all_products:
            try:
                await product_manager.create_product(session=session, **prod_data)
                print(f" Товар: {prod_data['title']}")
            except Exception as e:
                print(f"  Помилка: {prod_data['title']} - {e}")
        
        print(f"\n Ініціалізація завершена!")
        print(f" Категорій: {len(categories_data)}")
        print(f" Товарів: {len(all_products)}")


if __name__ == "__main__":
    asyncio.run(init_database())
