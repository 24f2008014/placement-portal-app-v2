from flask import current_app
from api.app import db
from sqlalchemy import String, Integer, ForeignKey, Column, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from werkzeug.security import generate_password_hash, check_password_hash
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta

class TimeConversionMixin:
    """
    Mixin for converting naive/UTC datetimes to aware (IST) datetime strings.
    """
    __abstract__ = True
    local_tz = ZoneInfo("Asia/Kolkata")
    dt_format = "%b %d %Y, %I:%M %p"
    
    def to_local(self, dt: datetime):
        if dt.tzinfo is None: # DB will always be naive
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(self.local_tz).strftime(self.dt_format)

class User(TimeConversionMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    # phone_number: Mapped[Optional[str]] = mapped_column(String(32), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column()

    # `password` and its setter are for allowing marshmallow to set the password hash directly
    @property
    def password(self):
        pass

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"

class Role:
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    users: Mapped[List["User"]] = relationship(secondary="user_roles", back_populates="roles")

    def __repr__(self):
        return f"Role(id={self.id}, name={self.name})"

# Bi-directional many-to-many should be defined as an association table, not a separate model
user_roles = db.Table(
    "user_roles",
    Column("user_id", ForeignKey(User.id), primary_key=True),
    Column("role_id", ForeignKey(Role.id), primary_key=True),
)