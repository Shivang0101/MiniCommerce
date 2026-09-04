import sys
import uuid
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from locust import HttpUser, between, task
from app.core.security import create_access_token



class MiniCommerceUser(HttpUser):
    """
    Simulates a realistic, high-concurrency virtual customer executing catalog browsing,
    cart management, and idempotent checkout operations. Supports scaling from 10 local users
    up to 1,000+ unique concurrent virtual users for AWS cloud stress testing.
    """

    wait_time = between(0.1, 1.5)

    def on_start(self):
        """Generates a unique virtual user identity and JWT access token on session start."""
        self.user_id = str(uuid.uuid4())
        self.token = create_access_token(subject=self.user_id)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self.sample_product_ids = [
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
            "33333333-3333-3333-3333-333333333333",
        ]

    @task(4)
    def browse_products_keyset(self):
        """High-frequency catalog browsing using O(1) Keyset (cursor) pagination."""
        with self.client.get(
            "/api/v1/products/keyset?limit=10",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/products/keyset",
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.sample_product_ids = [p["id"] for p in data[:5] if "id" in p]
                except Exception:
                    pass
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(3)
    def browse_products_standard(self):
        """Standard catalog search and filtering query."""
        with self.client.get(
            "/api/v1/products?page=1&page_size=10",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/products",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def view_cart(self):
        """Fetch current shopping cart items."""
        with self.client.get(
            "/api/v1/cart",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/cart",
        ) as response:
            if response.status_code in (200, 401, 404):
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def checkout_idempotent_order(self):
        """Executes idempotent checkout with SHA-256 payload hash header protection."""
        idempotency_key = str(uuid.uuid4())
        checkout_headers = {
            **self.headers,
            "Idempotency-Key": idempotency_key,
        }
        checkout_payload = {
            "shipping_address": "123 Cloud Architecture Way, AWS Region us-east-1",
            "items": [
                {"product_id": self.sample_product_ids[0], "quantity": 1}
            ] if self.sample_product_ids else [],
        }

        with self.client.post(
            "/api/v1/orders",
            headers=checkout_headers,
            json=checkout_payload,
            catch_response=True,
            name="/api/v1/orders",
        ) as response:
            # 201 Created or 400/401/409 expected when cart/stock/auth boundaries are reached
            if response.status_code in (200, 201, 400, 401, 404, 409):
                response.success()
            else:
                response.failure(f"Checkout failed with status: {response.status_code}")
