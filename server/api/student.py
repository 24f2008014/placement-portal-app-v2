from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement, Company
from datetime import datetime, timezone

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
        allowed_filters={"id", "status", "position_id"},
        allowed_sort={"id"},
        endpoint="student.get_applications_self"
    )
    return { "pagination": pagination, "data": items }, 200

@student.route("/positions/<int:id>/applications", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(ApplicationSchema(), 201)
def create_application(id):
    student = token_auth.current_user().student
    position = db.get_or_404(Position, id)
    if position.status == "closed" or position.is_approved == False:
        abort(403)
    existing_application = db.session.scalar(db.select(Application).filter(Application.student == student))
    if existing_application is not None:
        abort(403)
    application = Application(student=student, position=position)
    db.session.add(application)
    db.session.commit()
    return application

@student.route("/applications/<int:id>/withdraw", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(ApplicationSchema())
def withdraw_application(id):
    application = db.get_or_404(Application, id)
    if token_auth.current_user().student != application.student:
        abort(403)
    if application.status == "withdrawn" or application.position.status == "closed" or application.placements:
        abort(403)
    application.status = "withdrawn"
    application.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    return application