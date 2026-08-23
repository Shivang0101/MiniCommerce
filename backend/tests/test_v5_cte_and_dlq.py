import pytest
import uuid
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, ROLE_SCOPES

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.repositories.outbox_repository import OutboxRepository
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_cte_window_functions_revenue_analytics(db_session: AsyncSession):
    """Test CTE and SQL Window Functions revenue aggregation and ranking calculations."""
    # 1. Create test products
    p1 = await ProductRepository.create(
        db_session,
        type("ProductIn", (), {"name": "Laptop Pro", "description": "High end", "price": Decimal("1000.00"), "stock": 10})
    )
    p2 = await ProductRepository.create(
        db_session,
        type("ProductIn", (), {"name": "Wireless Mouse", "description": "Ergonomic", "price": Decimal("50.00"), "stock": 50})
    )

    # 2. Execute CTE & Window Function analytics
    analytics = await ProductRepository.get_revenue_window_analytics(db_session)
    
    assert len(analytics) >= 2
    # Verify key attributes exist in response
    first_item = analytics[0]
    assert "product_id" in first_item
    assert "product_name" in first_item
    assert "revenue_rank" in first_item
    assert "total_catalog_revenue" in first_item
    assert "revenue_percentage" in first_item
    assert first_item["revenue_rank"] == 1


@pytest.mark.asyncio
async def test_outbox_dlq_transition_and_replay(db_session: AsyncSession):
    """Test outbox event failure retries, transition to DEAD_LETTER, and replay back to PENDING."""
    # 1. Create a pending outbox event
    event = await OutboxRepository.create_event(db_session, "TEST_DLQ_EVENT", '{"test": true}')
    await db_session.commit()
    await db_session.refresh(event)

    assert event.status == "PENDING"
    assert event.retry_count == 0

    # 2. Mark event as failed 2 times (should become FAILED)
    ev1 = await OutboxRepository.mark_event_failed(db_session, event.id, "Connection timeout error 1", max_retries=3)
    assert ev1.retry_count == 1
    assert ev1.status == "FAILED"
    assert "Connection timeout" in ev1.last_error

    ev2 = await OutboxRepository.mark_event_failed(db_session, event.id, "Connection timeout error 2", max_retries=3)
    assert ev2.retry_count == 2
    assert ev2.status == "FAILED"

    # 3. Third failure (should transition to DEAD_LETTER)
    ev3 = await OutboxRepository.mark_event_failed(db_session, event.id, "Connection timeout error 3", max_retries=3)
    assert ev3.retry_count == 3
    assert ev3.status == "DEAD_LETTER"

    # 4. Query DLQ list
    dead_letters = await OutboxRepository.get_dead_letter_events(db_session)
    assert any(str(e.id) == str(event.id) for e in dead_letters)

    # 5. Replay dead letter event
    replayed = await OutboxRepository.replay_dead_letter_event(db_session, event.id)
    assert replayed.status == "PENDING"
    assert replayed.retry_count == 0
    assert replayed.last_error is None


@pytest.mark.asyncio
async def test_admin_analytics_and_dlq_endpoints(client: AsyncClient, db_session: AsyncSession):
    """Test Admin API endpoints for CTE revenue analytics and DLQ event replay."""
    # 1. Create admin user & generate token
    admin_user = User(
        email="dlq_admin@example.com",
        password_hash="hashed_pw",
        is_admin=True,
        role="SRE_ADMIN"
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)

    admin_token = create_access_token(subject=admin_user.id, scopes=ROLE_SCOPES["SRE_ADMIN"])
    headers = {"Authorization": f"Bearer {admin_token}"}


    # 2. Test GET /api/v1/admin/analytics/revenue
    res = await client.get("/api/v1/admin/analytics/revenue", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

    # 3. Create a DEAD_LETTER event
    event = await OutboxRepository.create_event(db_session, "ADMIN_DLQ_TEST", '{"foo": "bar"}')
    await db_session.commit()
    await db_session.refresh(event)

    # Force to DEAD_LETTER
    event.status = "DEAD_LETTER"
    event.retry_count = 3
    event.last_error = "Fatal payload corruption"
    await db_session.commit()

    # 4. Test GET /api/v1/admin/outbox/dead-letter
    dl_res = await client.get("/api/v1/admin/outbox/dead-letter", headers=headers)
    assert dl_res.status_code == 200
    dl_data = dl_res.json()
    assert any(item["id"] == str(event.id) for item in dl_data)

    # 5. Test POST /api/v1/admin/outbox/{event_id}/replay
    replay_res = await client.post(f"/api/v1/admin/outbox/{event.id}/replay", headers=headers)
    assert replay_res.status_code == 200
    r_json = replay_res.json()
    assert r_json["status"] == "PENDING"
    assert r_json["retry_count"] == 0
