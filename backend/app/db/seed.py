import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base, User, Product, Cart, CartItem, Order, OrderItem
from app.core.security import hash_password

SEED_USERS = [
    {"email": "alice@example.com", "password": "Password123!"},
    {"email": "bob@example.com", "password": "Password123!"},
    {"email": "charlie@example.com", "password": "Password123!"},
]

SEED_PRODUCTS = [
    {"name": "Mechanical Keyboard", "description": "Tactile mechanical switches with RGB backlighting.", "price": Decimal("120.00"), "stock": 15},
    {"name": "Wireless Ergonomic Mouse", "description": "Ergonomic vertical design for wrist strain reduction.", "price": Decimal("65.50"), "stock": 30},
    {"name": "UltraWide Monitor 34\"", "description": "34-inch curved ultrawide monitor with 144Hz refresh rate.", "price": Decimal("499.99"), "stock": 8},
    {"name": "USB-C Multi-Port Hub", "description": "7-in-1 USB-C hub with 4K HDMI, USB 3.0, and PD charging.", "price": Decimal("45.00"), "stock": 50},
    {"name": "Noise-Cancelling Headphones", "description": "Active noise cancelling wireless over-ear headphones.", "price": Decimal("199.99"), "stock": 20},
    {"name": "Laptop Stand Aluminum", "description": "Adjustable aluminum ergonomic laptop riser.", "price": Decimal("39.95"), "stock": 40},
    {"name": "Desk Mat Large", "description": "Water-resistant large felt desk pad.", "price": Decimal("24.99"), "stock": 100},
    {"name": "HD Webcam 1080p", "description": "Full HD 1080p webcam with auto light correction and mic.", "price": Decimal("79.99"), "stock": 25},
    {"name": "Studio Condenser Microphone", "description": "Cardioid USB condenser mic with pop filter and boom arm.", "price": Decimal("110.00"), "stock": 12},
    {"name": "Smart LED Desk Lamp", "description": "Dimmable LED lamp with wireless phone charging base.", "price": Decimal("49.99"), "stock": 3},
]

async def seed_data():
    print("Starting database schema creation and seeding...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Seed Users
        user_map = {}
        for user_data in SEED_USERS:
            res = await session.execute(select(User).where(User.email == user_data["email"]))
            user = res.scalar_one_or_none()
            if not user:
                user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"])
                )
                session.add(user)
                await session.flush()
                print(f"Created user: {user_data['email']}")
            user_map[user_data["email"]] = user

        # Seed Products
        prod_map = {}
        for prod_data in SEED_PRODUCTS:
            res = await session.execute(select(Product).where(Product.name == prod_data["name"]))
            product = res.scalar_one_or_none()
            if not product:
                product = Product(
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    stock=prod_data["stock"]
                )
                session.add(product)
                await session.flush()
                print(f"Created product: {prod_data['name']}")
            prod_map[prod_data["name"]] = product

        # Seed Simulated Cart for Alice
        alice = user_map.get("alice@example.com")
        if alice:
            cart_res = await session.execute(select(Cart).where(Cart.user_id == alice.id))
            alice_cart = cart_res.scalar_one_or_none()
            if not alice_cart:
                alice_cart = Cart(user_id=alice.id)
                session.add(alice_cart)
                await session.flush()

                # Add sample items to Alice's cart
                kbd = prod_map.get("Mechanical Keyboard")
                mouse = prod_map.get("Wireless Ergonomic Mouse")
                if kbd and mouse:
                    session.add(CartItem(cart_id=alice_cart.id, product_id=kbd.id, quantity=1))
                    session.add(CartItem(cart_id=alice_cart.id, product_id=mouse.id, quantity=1))
                    print("Seeded simulated cart items for Alice")

        # Seed Simulated Order for Bob
        bob = user_map.get("bob@example.com")
        if bob:
            order_res = await session.execute(select(Order).where(Order.user_id == bob.id))
            bob_order = order_res.scalar_one_or_none()
            if not bob_order:
                monitor = prod_map.get("UltraWide Monitor 34\"")
                if monitor:
                    total_amount = Decimal(str(monitor.price))
                    order = Order(
                        user_id=bob.id,
                        status="CONFIRMED",
                        total_amount=total_amount
                    )
                    session.add(order)
                    await session.flush()

                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=monitor.id,
                        quantity=1,
                        price=monitor.price
                    )
                    session.add(order_item)
                    print(f"Seeded simulated order #{str(order.id)[:8]} for Bob")

        await session.commit()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
