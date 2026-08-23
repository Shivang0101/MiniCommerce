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

    @staticmethod
    async def mark_event_failed(
        db: AsyncSession,
        event_id: uuid.UUID,
        error_msg: str,
        max_retries: int = 3
    ) -> Outbox | None:
        stmt = select(Outbox).where(Outbox.id == event_id)
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        if not event:
            return None

        event.retry_count += 1
        event.last_error = error_msg[:1000] # Truncate long backtraces
        
        if event.retry_count >= event.max_retries:
            event.status = "DEAD_LETTER"
        else:
            event.status = "FAILED"

        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_dead_letter_events(db: AsyncSession, limit: int = 50) -> list[Outbox]:
        result = await db.execute(
            select(Outbox)
            .where(Outbox.status == "DEAD_LETTER")
            .order_by(Outbox.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def replay_dead_letter_event(db: AsyncSession, event_id: uuid.UUID) -> Outbox | None:
        stmt = select(Outbox).where(Outbox.id == event_id)
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        if not event:
            return None

        event.status = "PENDING"
        event.retry_count = 0
        event.last_error = None
        event.processed_at = None

        await db.commit()
        await db.refresh(event)
        return event

