import pytest
from app.tasks.order_tasks import audit_low_stock, record_analytics_event, send_receipt_email


@pytest.mark.asyncio
async def test_send_receipt_email_execution():
    ctx = {}
    result = await send_receipt_email(ctx, "test_order_123", "alice@example.com", "150.00")
    assert result["status"] == "success"
    assert result["order_id"] == "test_order_123"
    assert result["user_email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_audit_low_stock_execution():
    ctx = {}
    items = [
        {"product_id": "prod_1", "name": "Keyboard", "remaining_stock": 2},
        {"product_id": "prod_2", "name": "Mouse", "remaining_stock": 50},
    ]
    result = await audit_low_stock(ctx, items)
    assert result["status"] == "success"
    assert len(result["low_stock_items"]) == 1
    assert result["low_stock_items"][0]["id"] == "prod_1"


@pytest.mark.asyncio
async def test_record_analytics_event_execution():
    ctx = {}
    payload = {"order_id": "ord_1", "total_amount": "199.99"}
    result = await record_analytics_event(ctx, "ORDER_PLACED", payload)
    assert result["status"] == "success"
    assert result["event_type"] == "ORDER_PLACED"
