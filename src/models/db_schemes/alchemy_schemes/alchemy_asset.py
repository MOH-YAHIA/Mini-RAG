import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .alchemy_base import AlchemyBase


class AlchemyAsset(AlchemyBase):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    asset_project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    asset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    asset_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    asset_config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    asset_pushed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now().astimezone(),
    )

 
    __table_args__ = (
        Index(
            "ix_assets_project_id_name",
            "asset_project_id",
            "asset_name",
        ),

        Index(
            "ix_assets_project_id",
            "asset_project_id",
        ),
    )