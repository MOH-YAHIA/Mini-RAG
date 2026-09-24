import uuid

from sqlalchemy import (
    Integer,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .alchemy_base import AlchemyBase


class AlchemyChunk(AlchemyBase):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chunk_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    chunk_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )

    chunk_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id"),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_chunks_project_id",
            "chunk_project_id",
        ),

        Index(
            "ix_chunks_asset_id",
            "chunk_asset_id",
        ),
    )