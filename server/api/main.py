from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema
from api.models import User, Role, Department, Branch, Student

main = Blueprint("main", __name__)
user_schema = UserSchema()
empty_schema = EmptySchema()
register_schema = RegisterSchema()
student_schema = StudentSchema()
departments_schema = DepartmentSchema(many=True)
branches_schema = BranchSchema(many=True)

@main.route("/")
def index():
    return "Hello!"

@main.route("/user", methods=["GET"])
@authenticate(token_auth)
@response(user_schema)
def profile():
    """Returns a user's details."""
    return token_auth.current_user()

@main.route("/register", methods=["POST"])
@body(register_schema)
@response(user_schema, 201)
def new(data):
    """Register a new account."""
    email = data["email"]
    password = data["password"]
    profile_obj = data["profile"]
    role = "student" if isinstance(profile_obj, Student) else "company"

    user = User(email=email)
    user.set_password(password)
    user.roles = [db.session.scalar(db.select(Role).where(Role.name == role))]
    db.session.add(user)
    profile_obj.user = user
    db.session.add(profile_obj)
    db.session.commit()

    # if role == "student":
    #     user.roles = [db.session.scalar(db.select(Role).where(Role.name == "student"))]
    #     try:
    #         student_obj = student_schema.load(profile, session=db.session)
    #         student_obj.user_id = user.id
    #         db.session.add(student_obj)
    #         db.session.commit()
    #     except ValidationError as e:
    #         messages = {"json": e.messages}
    #         abort(400, messages)
    
    return user

@main.route("/departments", methods=["GET"])
@response(departments_schema)
def get_departments():
    return db.session.scalars(db.select(Department))

@main.route("/branches", methods=["GET"])
@response(branches_schema)
def get_branches():
    return db.session.scalars(db.select(Branch))