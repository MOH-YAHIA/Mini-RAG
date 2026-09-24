import uuid
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Project(BaseModel):
    id: uuid.UUID | None = None
    project_id: str = Field(min_length=1)

    @field_validator('project_id') #additional validation
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed = True
    )