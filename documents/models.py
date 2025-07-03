import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Float, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import table_registry


@table_registry.mapped_as_dataclass
class DocumentRecord:
    __tablename__ = 'document_records'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        init=False
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size_mb: Mapped[float] = mapped_column(Float, nullable=False)
    chunks_ids: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
