import asyncio
import uuid
import random
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.core.security import hash_password

CATEGORIES = ["Laptops", "Smartphones", "Monitors", "Keyboards", "Storage", "Audio", "Networking", "Components"]
ADJECTIVES = ["Ultra", "Pro", "Gaming", "Wireless", "Compact", "Ergonomic", "High-Speed", "Extreme", "Silent", "RGB"]
NOUNS = ["Master", "Extreme", "V2", "Edition", "Series X", "Prime", "Elite", "Max", "Plus", "Studio"]

async def generate_load_data(num_users: int = 500, num_products: int = 2000, num_orders: int = 1500):
    print(f"🚀 Starting dataset generation: {num_users} users, {num_products} products, {num_orders} orders...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Bulk Create Users
        print("Creating users...")
        pwd_hash = hash_password("Password123!")
        users = []
        for i in range(num_users):
            user = User(
                email=f"load_user_{i+1}@benchmark.com",
                password_hash=pwd_hash
            )
            db.add(user)
            users.append(user)
        await db.commit()
        for u in users:
            await db.refresh(u)
        user_ids = [u.id for u in users]

        # 2. Bulk Create Products
        print("Creating products...")
        products = []
        for i in range(num_products):
            cat = random.choice(CATEGORIES)
            adj = random.choice(ADJECTIVES)
            noun = random.choice(NOUNS)
            name = f"{adj} {cat} {noun} #{i+1}"
            price = Decimal(str(round(random.uniform(9.99, 1999.99), 2)))
            stock = random.randint(10, 500)
            product = Product(
                name=name,
                description=f"Performance laboratory benchmark item {i+1} in {cat}.",
                price=price,
                stock=stock
            )
            db.add(product)
            products.append(product)
        await db.commit()
        for p in products:
            await db.refresh(p)
        product_map = {p.id: p for p in products}
        product_ids = list(product_map.keys())

        # 3. Bulk Create Orders & OrderItems
        print("Creating orders...")
        for i in range(num_orders):
            u_id = random.choice(user_ids)
            selected_p_ids = random.sample(product_ids, k=random.randint(1, 4))
            total_amt = Decimal("0.00")

            order = Order(
                user_id=u_id,
                status="CONFIRMED",
                total_amount=Decimal("0.00"),
                idempotency_key=f"load_key_{i+1}"
            )
            db.add(order)
            await db.flush()

            for p_id in selected_p_ids:
                p = product_map[p_id]
                qty = random.randint(1, 3)
                item_total = Decimal(str(p.price)) * Decimal(str(qty))
                total_amt += item_total

                item = OrderItem(
                    order_id=order.id,
                    product_id=p.id,
                    quantity=qty,
                    price=p.price
                )
                db.add(item)
            
            order.total_amount = total_amt
            if i % 100 == 0:
                await db.commit()

        await db.commit()
        print("✅ Load data generation complete!")

if __name__ == "__main__":
    asyncio.run(generate_load_data())
