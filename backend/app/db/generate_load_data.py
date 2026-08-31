import asyncio
import random
import sys
import uuid
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User

CATEGORIES = [
    "Laptops",
    "Smartphones",
    "Monitors",
    "Keyboards",
    "Storage",
    "Audio",
    "Networking",
    "Components",
]
ADJECTIVES = [
    "Ultra",
    "Pro",
    "Gaming",
    "Wireless",
    "Compact",
    "Ergonomic",
    "High-Speed",
    "Extreme",
    "Silent",
    "RGB",
]
NOUNS = [
    "Master",
    "Extreme",
    "V2",
    "Edition",
    "Series X",
    "Prime",
    "Elite",
    "Max",
    "Plus",
    "Studio",
]

BATCH_SIZE = 5000  # Commit in chunks of 5000 to maximize throughput


async def generate_load_data(
    num_users: int = 10000, num_products: int = 50000, num_orders: int = 100000
):
    print("[INFO] Starting high-speed dataset generation:")
    print(f"   - Users: {num_users:,}")
    print(f"   - Products: {num_products:,}")
    print(f"   - Orders: {num_orders:,}")
    print(f"   - Approx Order Items: {num_orders * 3:,}")
    print("--------------------------------------------------")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Bulk Create Users
        print(f"[PROGRESS] Generating {num_users:,} users...")
        pwd_hash = hash_password("Password123!")
        user_ids = []
        user_batch = []
        run_id = str(uuid.uuid4())[:8]

        for i in range(num_users):
            u_id = uuid.uuid4()
            user_ids.append(u_id)
            user = User(
                id=u_id, email=f"user_{run_id}_{i + 1}@benchmark.com", password_hash=pwd_hash
            )
            user_batch.append(user)

            if len(user_batch) >= BATCH_SIZE:
                db.add_all(user_batch)
                await db.commit()
                user_batch = []
                print(f"   Progress: {i + 1:,} / {num_users:,} users committed.")

        if user_batch:
            db.add_all(user_batch)
            await db.commit()

        print("[SUCCESS] Users completed.")

        # 2. Bulk Create Products
        print(f"[PROGRESS] Generating {num_products:,} products...")
        product_ids = []
        product_prices = {}
        product_batch = []

        for i in range(num_products):
            p_id = uuid.uuid4()
            product_ids.append(p_id)
            price = Decimal(str(round(random.uniform(9.99, 1999.99), 2)))
            product_prices[p_id] = price

            cat = random.choice(CATEGORIES)
            adj = random.choice(ADJECTIVES)
            noun = random.choice(NOUNS)
            name = f"{adj} {cat} {noun} #{i + 1}"
            stock = random.randint(10, 500)

            product = Product(
                id=p_id,
                name=name,
                description=f"Performance laboratory benchmark item {i + 1} in {cat}.",
                price=price,
                stock=stock,
            )
            product_batch.append(product)

            if len(product_batch) >= BATCH_SIZE:
                db.add_all(product_batch)
                await db.commit()
                product_batch = []
                print(f"   Progress: {i + 1:,} / {num_products:,} products committed.")

        if product_batch:
            db.add_all(product_batch)
            await db.commit()

        print("[SUCCESS] Products completed.")

        # 3. Bulk Create Orders & OrderItems
        print(f"[PROGRESS] Generating {num_orders:,} orders with order items...")
        order_batch = []
        item_batch = []
        total_items_created = 0

        for i in range(num_orders):
            order_id = uuid.uuid4()
            user_id = random.choice(user_ids)
            selected_p_ids = random.sample(product_ids, k=random.randint(1, 4))
            total_amt = Decimal("0.00")

            for p_id in selected_p_ids:
                p_price = product_prices[p_id]
                qty = random.randint(1, 3)
                total_amt += p_price * Decimal(str(qty))

                item = OrderItem(
                    id=uuid.uuid4(), order_id=order_id, product_id=p_id, quantity=qty, price=p_price
                )
                item_batch.append(item)
                total_items_created += 1

            order = Order(
                id=order_id,
                user_id=user_id,
                status="CONFIRMED",
                total_amount=total_amt,
                idempotency_key=f"load_key_{i + 1}",
            )
            order_batch.append(order)

            if len(order_batch) >= BATCH_SIZE:
                db.add_all(order_batch)
                db.add_all(item_batch)
                await db.commit()
                order_batch = []
                item_batch = []
                print(
                    f"   Progress: {i + 1:,} / {num_orders:,} orders committed ({total_items_created:,} items)."
                )

        if order_batch:
            db.add_all(order_batch)
            db.add_all(item_batch)
            await db.commit()

        print("[SUCCESS] High-speed load data generation complete!")
        print(f"   Total Users: {num_users:,}")
        print(f"   Total Products: {num_products:,}")
        print(f"   Total Orders: {num_orders:,}")
        print(f"   Total Order Items: {total_items_created:,}")


def main():
    users = 10000
    products = 50000
    orders = 100000

    if len(sys.argv) > 1:
        users = int(sys.argv[1])
    if len(sys.argv) > 2:
        products = int(sys.argv[2])
    if len(sys.argv) > 3:
        orders = int(sys.argv[3])

    asyncio.run(generate_load_data(num_users=users, num_products=products, num_orders=orders))


if __name__ == "__main__":
    main()
