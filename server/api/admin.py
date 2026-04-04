from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses, arguments
from sqlalchemy import func
from datetime import datetime
from api.app import db, cache
from api.auth import token_auth
from api.schemas import StudentSchema, CompanySchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, AdminStatsSchema, PlacementSchema, PositionSchema
from api.models import Student, Position, Application, Placement, Company, User
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
    """Test if cache is working"""
    return { "time": datetime.now() }, 200

@admin.route("/stats", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@response(AdminStatsSchema())
def get_stats():
    """Get overall stats"""
    num_students = db.session.scalar(db.select(func.count()).select_from(Student))
    num_companies = db.session.scalar(db.select(func.count()).select_from(Company))
    num_companies_pending = db.session.scalar(db.select(func.count()).select_from(Company).filter(Company.status == "pending"))
    num_positions_pending = db.session.scalar(db.select(func.count()).select_from(Position).filter(Position.is_approved == False))
    num_positions = db.session.scalar(db.select(func.count()).select_from(Position))
    num_applications = db.session.scalar(db.select(func.count()).select_from(Application))
    num_placements = db.session.scalar(db.select(func.count()).select_from(Placement))
    companies_pending = db.session.scalars(db.select(Company).filter(Company.status == "pending"))
    positions_pending = db.session.scalars(db.select(Position).filter(Position.is_approved == False))
    return {
        "num_students": num_students,
        "num_companies": num_companies,
        "num_companies_pending": num_companies_pending,
        "companies_pending": companies_pending,
        "num_positions": num_positions,
        "num_applications": num_applications,
        "num_placements": num_placements,
        "positions_pending": positions_pending,
        "num_positions_pending": num_positions_pending
    }

@admin.route("/students", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(StudentSchema()))
def get_students(args):
    """Get all students"""
    query = db.session.query(Student).join(User)
    items, pagination = paginate_query(
        query=query,
        model=Student,
        args=args,
        allowed_filters={
            "id": "equals",
            "roll_number": "equals",
            "user.email": "ilike",
            "first_name": "ilike",
            "last_name": "ilike",
            "cgpa": "gt",
            "gender": "equals",
            "status": "equals"
        },
        allowed_sort={"id", "roll_number", "user.email", "first_name", "last_name", "cgpa", "gender", "status"},
        endpoint="admin.get_students"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>/applications", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_student_applications(args, id):
    """Get a student's applications"""
    query = db.session.query(Application).join(Position).join(Company).filter(Application.student_id == id)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "position_id": "equals",
            "position.role": "ilike",
            "position.company.name": "ilike",
            "created_at": "gt",
            "updated_at": "gt",
            "placement_count": "gt",
            "status": "equals"
        },
        allowed_sort={"id", "position_id", "position.role", "position.company.name", "created_at", "updated_at", "placement_count", "status"},
        endpoint="admin.get_student_applications"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["admin"])
@body(StudentSchema(only=("status",), partial=True, load_instance=False))
@response(StudentSchema())
def update_student_status(data, id):
    """Update a student's status"""
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
    """Get all applications"""
    query = db.session.query(Application).join(Position).join(Company)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "student_id": "equals",
            "position_id": "equals",
            "position.role": "ilike",
            "position.company.name": "ilike",
            "created_at": "gt",
            "updated_at": "gt",
            "placement_count": "gt",
            "status": "equals"
        },
        allowed_sort={"id", "student_id", "position_id", "position.role", "position.company.name", "created_at", "updated_at", "placement_count", "status"},
        endpoint="admin.get_applications"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>/placements", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PlacementSchema()))
def get_student_placements(args, id):
    """Get a student's placements"""
    query = db.session.query(Placement).join(Application).join(Position).join(Company).filter(Application.student_id == id)
    items, pagination = paginate_query(
        query=query,
        model=Placement,
        args=args,
        allowed_filters={
            "id": "equals",
            "application_id": "equals",
            "application.position.role": "ilike",
            "application.position.company.name": "ilike",
            "joining_date": "gt",
            "salary": "gt",
            "status": "equals",
            "created_at": "gt"
        },
        allowed_sort={"id", "application_id", "application.position.role", "application.position.company.name", "joining_date", "salary", "status", "created_at"},
        endpoint="admin.get_student_placements"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/placements", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PlacementSchema()))
def get_placements(args):
    """Get all placements"""
    query = db.session.query(Placement).join(Application).join(Position).join(Company)
    items, pagination = paginate_query(
        query=query,
        model=Placement,
        args=args,
        allowed_filters={
            "id": "equals",
            "application_id": "equals",
            "application.student_id": "equals",
            "application.position.role": "ilike",
            "application.position.company.name": "ilike",
            "joining_date": "gt",
            "salary": "gt",
            "status": "equals",
            "created_at": "gt"
        },
        allowed_sort={"id", "application_id", "application.student_id", "application.position.role", "application.position.company.name", "joining_date", "salary", "status", "created_at"},
        endpoint="admin.get_placements"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/positions/<int:id>/whitelist", methods=["POST"])
@authenticate(token_auth, role=["admin"])
@response(PositionSchema())
def change_position_status(id):
    """Whitelist a position"""
    position = db.get_or_404(Position, id)
    if position.is_approved == True:
        abort(403, f"Position #{id} is already approved by an administrator.")
    position.is_approved = True
    db.session.commit()
    return position