import uuid
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.outbox import Outbox

class OutboxRepository:
    @staticmethod
    async def create_event(db: AsyncSession, event_type: str, payload_json: str) -> Outbox:
        outbox_event = Outbox(
            event_type=event_type,
            payload_json=payload_json,
            status="PENDING"
        )
        db.add(outbox_event)
        return outbox_event

    @staticmethod
    async def get_pending_events(db: AsyncSession, limit: int = 50) -> list[Outbox]:
        result = await db.execute(
            select(Outbox)
            .where(Outbox.status == "PENDING")
            .order_by(Outbox.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def mark_event_processed(db: AsyncSession, event_id: uuid.UUID) -> None:
        await db.execute(
            update(Outbox)
            .where(Outbox.id == event_id)
            .values(status="PROCESSED", processed_at=datetime.now(timezone.utc))
        )
        await db.commit()
