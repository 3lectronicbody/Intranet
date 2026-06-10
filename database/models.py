from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    LargeBinary,
)
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from datetime import datetime, timezone
from typing import Optional


class Base(DeclarativeBase):
    pass


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

    def __init__(
        self,
        email: str,
        password: str,
        role: str = Role.USER.value,
        name: str | None = None,
        surname: str | None = None,
        phone: str | None = None,
        picture: bytes | None = None,
    ):

        self.name = name
        self.surname = surname
        self.email = email
        self.phone = phone
        self.password = password
        self.picture = picture
        self.role = role


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
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    project_owner: Mapped[str] = mapped_column(
        String, default="unknown", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    beginning: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationship with Project Details
    project_details: Mapped[list["ProjectDetails"]] = relationship(
        "ProjectDetails",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    # relationship with Logs
    project_logs: Mapped[list["Logs"]] = relationship(
        "Logs", back_populates="project", cascade="all, delete-orphan"
    )

    # For annotations because pycharm can't see Mapped[]
    def __init__(
        self,
        name: str,
        description: str,
        project_owner: str = "unknown",
        is_active: bool | None = True,
        beginning: datetime | None = None,
        end: datetime | None = None,
    ):
        self.name = name
        self.description = description
        self.project_owner = project_owner
        self.is_active = is_active
        self.beginning = beginning
        self.end = end


class ProjectDetails(Base):
    __tablename__ = "project_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity: Mapped[str | None] = mapped_column(String, nullable=True)
    item: Mapped[str | None] = mapped_column(String, nullable=True)
    item_code: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String, nullable=True)
    todo: Mapped[str | None] = mapped_column(String, nullable=True)

    # relationship
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    project = relationship("Projects", back_populates="project_details")