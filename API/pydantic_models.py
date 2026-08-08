from pydantic import BaseModel,ConfigDict, Base64Bytes
from database.models import Role
from datetime import datetime
from typing import Any, Optional

class AppMetadataSchema(BaseModel):
    id: int
    filename: str | None = None
    version: str
    download_url: str
    mandatory_update: bool
    created_at: datetime
    sha256: str
    release_notes: str | None = None


class UsersSchema(BaseModel):
    id: int
    name: str | None = None
    surname: str | None = None

    email: str
    phone_number: str | None = None
    phone: str | None = None
    password: str
    picture: bytes | None = None
    role: str = Role.USER.value

    # Allows Pydantic to parse directly from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)
class LogSchema(BaseModel):
    id: int
    activity: str
    description: str | None = None
    timestamp: datetime
    user_id: int
    project_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class ProjectSchema(BaseModel):
    id: int
    number: int
    name: str
    description: str
    project_owner: str = "unknown"
    is_active: bool = True
    beginning: datetime
    end: datetime | None = None
    summary_pdf: Base64Bytes | None = None

    model_config = ConfigDict(from_attributes=True)
class ProjectItemSchema(BaseModel):
    id: int | None = None
    name: str
    code: str | None = None
    quantity: float
    unit: str
    description: str | None = None
    project_id: int

    model_config = ConfigDict(from_attributes=True)
class ProjectActivitySchema(BaseModel):
    id: int | None = None
    name: str
    time: float
    description: str | None = None
    project_id: int

    model_config = ConfigDict(from_attributes=True)
class ProjectTodoSchema(BaseModel):
    id: int | None = None
    name: str
    time: float
    description: str | None = None
    project_id: int

class ServiceProjectSchema(BaseModel):
    id: Optional[int] = None
    number: str
    owner: str
    start_date: datetime
    end_date: datetime | None = None
    phone_number: str | None = None
    email: str | None = None
    manufacturer: str
    model: str | None = None
    code: str | None = None
    serial_number: str | None = None
    description: str
    repair_time: float | None = None
    active: bool = True
    tasks: list[dict[str, Any]] | None = None
    service_parts: list[dict[str, Any]] | None = None
    pdf_form: Base64Bytes | None = None

    model_config = ConfigDict(from_attributes=True)