from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement, Company

student = Blueprint("student", __name__)

@student.route("/students/me", methods=["GET"])
@authenticate(token_auth, role=["student"])
@response(StudentSchema())
def get_student_self():
    """Returns a user's details."""
    return token_auth.current_user().student

@student.route("/students/me", methods=["PUT"])
@authenticate(token_auth, role=["student"])
@body(StudentSchema(load_instance=False))
@response(StudentSchema())
def update_student_self(data):
    student = token_auth.current_user().student
    student.update(data)
    db.session.commit()
    return student

@student.route("/students/me/applications", methods=["GET"])
@authenticate(token_auth, role=["student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications_self(args):
    student = token_auth.current_user().student
    query = db.session.query(Application).filter(Application.student == student)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={"id", "status"},
        allowed_sort={"id"},
        endpoint="student.get_applications_self"
    )
    return { "pagination": pagination, "data": items }, 200