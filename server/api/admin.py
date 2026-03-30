from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses, arguments
from sqlalchemy import func
from datetime import datetime
from celery.result import AsyncResult
from api.app import db, cache
from api.auth import token_auth
from api.schemas import StudentSchema, CompanySchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, StatsSchema
from api.models import Student, Position, Application, Placement, Company
from api.tasks import add_together

admin = Blueprint("admin", __name__)

@admin.route("/cache_test", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@cache.cached(timeout=15)
def cache_test():
    """Quickly check whether caching is working properly or not."""
    return { "time": datetime.now() }, 200

@admin.route("/celery_test", methods=["GET"])
@authenticate(token_auth, role=["admin"])
def admin_celery_test():
    result = add_together.delay(5, 10)
    return { "result_id": result.id }, 200

@admin.route("/result/<id>", methods=["GET"])
@authenticate(token_auth, role=["admin"])
def task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "status": result.state,
        "result": result.result if result.ready() else None,
    }

@admin.route("/stats", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@response(StatsSchema())
def get_stats():
    num_students = db.session.scalar(db.select(func.count()).select_from(Student))
    num_companies = db.session.scalar(db.select(func.count()).select_from(Company))
    num_positions = db.session.scalar(db.select(func.count()).select_from(Position))
    num_applications = db.session.scalar(db.select(func.count()).select_from(Application))
    num_placements = db.session.scalar(db.select(func.count()).select_from(Placement))
    return {
        "num_students": num_students,
        "num_companies": num_companies,
        "num_positions": num_positions,
        "num_applications": num_applications,
        "num_placements": num_placements
    }

@admin.route("/students", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(StudentSchema()))
def get_students(args):
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
    print(data)
    student = db.get_or_404(Student, id)
    student.update(data)
    db.session.commit()
    return student

@admin.route("/companies/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["admin"])
@body(CompanySchema(only=("status",), partial=True, load_instance=False))
@response(CompanySchema())
def update_company_status(data, id):
    print(data)
    company = db.get_or_404(Company, id)
    company.update(data)
    db.session.commit()
    return company