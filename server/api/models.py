from flask import current_app
from api.app import db
from sqlalchemy import String, Integer, ForeignKey, Column, Float, Boolean, CheckConstraint
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

class Industry(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))

class Department(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))

class Branch(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey(Department.id))
    name: Mapped[str] = mapped_column(String(128))

class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    users: Mapped[List["User"]] = relationship(secondary="user_roles", back_populates="roles")

class User(TimeConversionMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    roles: Mapped[List["Role"]] = relationship(secondary="user_roles", back_populates="users")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(back_populates="user")
    student: Mapped["Student"] = relationship(back_populates="user")

    def get_roles(self):
        return [role.name for role in self.roles]
    
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

# Bi-directional many-to-many should be defined as an association table, not a separate model
user_roles = db.Table(
    "user_roles",
    Column("user_id", ForeignKey(User.id), primary_key=True),
    Column("role_id", ForeignKey(Role.id), primary_key=True),
)

class RefreshToken(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), index=True)
    issued_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column()
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    def is_valid(self):
        if self.is_revoked:
            return False
        return datetime.now(timezone.utc) < self.expires_at

class Company(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    name: Mapped[str] = mapped_column(String(128))
    industry_id: Mapped[int] = mapped_column(ForeignKey(Industry.id))
    description: Mapped[str] = mapped_column(String(1024))
    contact_email: Mapped[str] = mapped_column(String(128))
    contact_phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    website: Mapped[str] = mapped_column(String(128))
    location: Mapped[str] = mapped_column(String(128))
    approval_status: Mapped[bool] = mapped_column(Boolean, default=False)
    positions: Mapped[List["Position"]] = relationship(back_populates="company")

class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    roll_number: Mapped[str] = mapped_column(String(128), unique=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str] = mapped_column(String(128))
    bio: Mapped[Optional[str]] = mapped_column(String(1024))
    department_id: Mapped[int] = mapped_column(ForeignKey(Department.id))
    branch_id: Mapped[int] = mapped_column(ForeignKey(Branch.id))
    graduation_year: Mapped[int] = mapped_column()
    cgpa: Mapped[int] = mapped_column(CheckConstraint("cgpa >= 0 AND cgpa <= 10", name="cgpa_check"))
    date_of_birth: Mapped[Optional[datetime]] = mapped_column()
    gender: Mapped[str] = mapped_column(String(128), CheckConstraint("gender IN ('male', 'female', 'other')"))
    resume_url: Mapped[Optional[str]] = mapped_column(String(512))
    approval_status: Mapped[bool] = mapped_column(Boolean, default=True)
    applications: Mapped[List["Application"]] = relationship(back_populates="student")
    user: Mapped["User"] = relationship(back_populates="student")

class Position(TimeConversionMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey(Company.id))
    role: Mapped[str] = mapped_column(String(128))
    salary_min: Mapped[int] = mapped_column(CheckConstraint("salary_min >= 0", name="salary_min_check"))
    salary_max: Mapped[int] = mapped_column(CheckConstraint("salary_max >= 0", name="salary_max_check"))
    description: Mapped[str] = mapped_column()
    deadline: Mapped[datetime] = mapped_column()
    min_cgpa: Mapped[int] = mapped_column(CheckConstraint("min_cgpa >= 0 AND min_cgpa <= 10", name="min_cgpa_check"))
    approval_status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    company: Mapped["Company"] = relationship(back_populates="positions")
    applications: Mapped[List["Application"]] = relationship(back_populates="position")

class Application(TimeConversionMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey(Student.id))
    position_id: Mapped[int] = mapped_column(ForeignKey(Position.id))
    status: Mapped[str] = mapped_column(
        String(128),
        CheckConstraint("status IN ('pending', 'shortlisted', 'offered', 'placed', 'rejected')"),
        default="pending"
    )
    interview_date: Mapped[Optional[datetime]] = mapped_column()
    interview_completed: Mapped[Optional[bool]] = mapped_column()
    interview_feedback: Mapped[Optional[str]] = mapped_column()
    offer_salary: Mapped[Optional[datetime]] = mapped_column()
    offer_joining_date: Mapped[Optional[datetime]] = mapped_column()
    offer_accepted: Mapped[Optional[bool]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    student: Mapped["Student"] = relationship(back_populates="applications")
    position: Mapped["Position"] = relationship(back_populates="applications")

class Placement(TimeConversionMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey(Application.id))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column()