from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    LargeBinary,
    JSON
)
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from datetime import datetime, timezone
from typing import Optional



class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Role(Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Log(Enum):
    NORMAL = "normal"
    LOGIN = "login"
    LOGOUT = "logout"
    ADD_ITEM = "add_item"
    CREATE_PROJECT = "create_project"
    REMOVE_ITEM = "remove_item"
    UPDATE_ITEM = "update_item"
    DELETE_ITEM = "delete_item"
    ADD_ACTIVITY = "add_activity"
    REMOVE_ACTIVITY = "remove_activity"
    UPDATE_ACTIVITY = "update_activity"
    DELETE_ACTIVITY = "delete_activity"
    SIGN_IN = "sign_in"
    DELETE_PROJECT = "delete_project"
class AppMetadata(Base):
    __tablename__ =  "app_metadata"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True, default="Intranet")
    version: Mapped[str] = mapped_column(String, nullable=False)
    download_url: Mapped[str] = mapped_column(String, nullable=False, default="www.google.com")
    mandatory_update: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default = lambda: datetime.now(timezone.utc))
    sha256: Mapped[str] = mapped_column(String, nullable=False)
    release_notes: Mapped[str] = mapped_column(String, nullable=True)






class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    surname: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    picture: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    role: Mapped[str] = mapped_column(String,default=Role.USER.value, nullable=False)

    # Relationship with Logs
    logs: Mapped[list["Logs"]] = relationship(
        "Logs", back_populates="user", cascade="all, delete-orphan"
    )

class Logs(Base):
    __tablename__ = "logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship with Users
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["Users"] = relationship("Users", back_populates="logs")

    # Relationship with Projects
    project_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=True
    )
    project: Mapped[Optional["Projects"]] = relationship(
        "Projects", back_populates="project_logs"
    )


class Projects(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    project_owner: Mapped[str] = mapped_column(
        String, default="unknown", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    beginning: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary_pdf: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # List of Project Items
    project_items: Mapped[list["ProjectItems"]] = relationship(
        "ProjectItems",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    # List of corresponding activities
    project_activities: Mapped[list["ProjectActivities"]] = relationship(
        "ProjectActivities",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    # List of Project todos
    project_todos: Mapped[list["ProjectTodos"]] = relationship(
        "ProjectTodos",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    # relationship with Logs
    project_logs: Mapped[list["Logs"]] = relationship(
        "Logs", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectItems(Base):
    __tablename__ = "project_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


    # relationship
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    project = relationship("Projects", back_populates="project_items")
class ProjectActivities(Base):
    __tablename__ = "project_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=False)
    time: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


    # relationship
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    project = relationship("Projects", back_populates="project_activities")
class ProjectTodos(Base):
    __tablename__ = "project_todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=False)
    time: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationship with Projects table
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    project = relationship("Projects", back_populates="project_todos")


class ServiceProjects(Base):
    __tablename__ = "service_projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String, nullable=False)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=True)
    code: Mapped[str] = mapped_column(String, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    repair_time: Mapped[float] = mapped_column(Float, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tasks: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    service_parts: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    pdf_form: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # tasks scheme -> # [{task_name: name, task_time: time, task_date: date}]

    # service_parts scheme ->[{name:part_name,code: code, quantity:quantity}]



