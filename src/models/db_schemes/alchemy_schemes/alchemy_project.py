import uuid

from sqlalchemy import String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .alchemy_base import AlchemyBase


class AlchemyProject(AlchemyBase):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )