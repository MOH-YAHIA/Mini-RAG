from .base import SQLAlchemyBase
from sqlalchemy import Column, String , Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class Project(SQLAlchemyBase):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False) # as_uuid=True ensures that the UUID is stored as a native PostgreSQL UUID type not as a string

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) # server_default=func.now() sets the default value to the current timestamp when a new record is created
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True) # onupdate=func.now() automatically updates the timestamp whenever the record is updated

    chunks = relationship("DataChunk", back_populates="project") # for python orm that allows us to access the related DataChunk objects from a Project instance
    assets = relationship("Asset", back_populates="project") # for python orm that allows us to access the related Asset objects from a Project instance