from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses, arguments
from sqlalchemy import func
from datetime import datetime
from api.app import db, cache
from api.auth import token_auth
from api.schemas import StudentSchema, CompanySchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, AdminStatsSchema, PlacementSchema, UserSchema
from api.models import Student, Position, Application, Placement, Company, User, Role
from api.tasks import monthly_report

admin = Blueprint("admin", __name__)

@admin.route("/admin/monthly_report", methods=["GET"])
@authenticate(token_auth, role=["admin"])
def monthly_report_manual():
    """Manually trigger the admin monthly report email"""
    monthly_report.delay()
    return "Sent!", 200

@admin.route("/cache_test", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@cache.cached(timeout=15)
def cache_test():
    """Quickly check whether caching is working properly or not."""
    return { "time": datetime.now() }, 200

@admin.route("/stats", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@response(AdminStatsSchema())
def get_stats():
    """Get stats for the admin dashboard."""
    num_students = db.session.scalar(db.select(func.count()).select_from(Student))
    num_companies = db.session.scalar(db.select(func.count()).select_from(Company))
    num_companies_pending = db.session.scalar(db.select(func.count()).select_from(Company).filter(Company.status == "pending"))
    num_positions = db.session.scalar(db.select(func.count()).select_from(Position))
    num_applications = db.session.scalar(db.select(func.count()).select_from(Application))
    num_placements = db.session.scalar(db.select(func.count()).select_from(Placement))
    companies_pending = db.session.scalars(db.select(Company).filter(Company.status == "pending"))    
    return {
        "num_students": num_students,
        "num_companies": num_companies,
        "num_companies_pending": num_companies_pending,
        "companies_pending": companies_pending,
        "num_positions": num_positions,
        "num_applications": num_applications,
        "num_placements": num_placements
    }

@admin.route("/users", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(UserSchema()))
def get_users(args):
    """Get all users"""
    query = db.session.query(User)
    items, pagination = paginate_query(
        query=query,
        model=User,
        args=args,
        allowed_filters={
            "id": "equals",
            "email": "ilike",
            "created_at": "gt"
        },
        allowed_sort={"id", "email", "created_at"},
        endpoint="admin.get_users"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(StudentSchema()))
def get_students(args):
    """Get all students."""
    query = db.session.query(Student)
    items, pagination = paginate_query(
        query=query,
        model=Student,
        args=args,
        allowed_filters={
            "id": "equals",
            "roll_number": "equals",
            "contact_email": "ilike",
            "first_name": "ilike",
            "last_name": "ilike",
            "cgpa": "gt",
            "gender": "equals",
            "status": "equals"
        },
        allowed_sort={"id", "roll_number", "contact_email", "first_name", "last_name", "cgpa", "gender", "status"},
        endpoint="admin.get_students"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>/applications", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_student_applications(args, id):
    """Get a student's applications."""
    query = db.session.query(Application).filter(Application.student_id == id)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals"
        },
        allowed_sort={"id"},
        endpoint="admin.get_student_applications"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["admin"])
@body(StudentSchema(only=("status",), partial=True, load_instance=False))
@response(StudentSchema())
def update_student_status(data, id):
    """Update a student's status."""
    student = db.get_or_404(Student, id)
    student.update(data)
    db.session.commit()
    return student

@admin.route("/companies/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["admin"])
@body(CompanySchema(only=("status",), partial=True, load_instance=False))
@response(CompanySchema())
def update_company_status(data, id):
    """Update a company's status"""
    company = db.get_or_404(Company, id)
    company.update(data)
    db.session.commit()
    return company

@admin.route("/applications", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications(args):
    """Get all applications."""
    query = db.session.query(Application)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "student_id": "equals",
            "status": "equals"
        },
        allowed_sort={"id", "student_id", "created_at", "status"},
        endpoint="admin.get_student_applications"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>/placements", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PlacementSchema()))
def get_student_placements(args, id):
    """Get a student's placements."""
    query = db.session.query(Placement).join(Application).filter(Application.student_id == id)
    items, pagination = paginate_query(
        query=query,
        model=Placement,
        args=args,
        allowed_filters={
            "id": "equals",
            "status": "equals"
        },
        allowed_sort={"id", "application_id", "created_at", "status"},
        endpoint="admin.get_student_placements"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/placements", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PlacementSchema()))
def get_placements(args):
    """Get all placements."""
    query = db.session.query(Placement)
    items, pagination = paginate_query(
        query=query,
        model=Placement,
        args=args,
        allowed_filters={
            "id": "equals",
            "status": "equals"
        },
        allowed_sort={"id", "status"},
        endpoint="admin.get_placements"
    )
    return { "pagination": pagination, "data": items }, 200