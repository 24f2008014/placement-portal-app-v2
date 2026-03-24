from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement, Company

admin = Blueprint("admin", __name__)

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
        allowed_filters={"id", "roll_number", "email", "first_name", "last_name", "status"},
        allowed_sort={"id"},
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
        allowed_filters={"id"},
        allowed_sort={"id"},
        endpoint="admin.get_student_applications"
    )
    return { "pagination": pagination, "data": items }, 200

@admin.route("/students/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["admin"])
@body(StudentSchema(partial=("status",)))
@response(StudentSchema())
def update_student_status(data, id):
    student = db.get_or_404(Student, id)
    student.update(data)
    db.session.commit()
    return student