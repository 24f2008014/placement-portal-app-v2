from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement

main = Blueprint("main", __name__)
user_schema = UserSchema()
update_user_schema = UpdateUserSchema()
empty_schema = EmptySchema()
register_schema = RegisterSchema()
student_schema = StudentSchema()
company_schema = CompanySchema()
departments_schema = DepartmentSchema(many=True)
branches_schema = BranchSchema(many=True)
industries_schema = IndustrySchema(many=True)
position_schema = PositionSchema()

@main.route("/")
def index():
    return "Hello!"

@main.route("/user", methods=["GET"])
@authenticate(token_auth)
@response(register_schema)
def profile():
    """Returns a user's details."""
    return token_auth.current_user()

@main.route("/users/me", methods=["GET"])
@authenticate(token_auth)
@response(user_schema)
def get_user():
    """Returns a user's details."""
    return token_auth.current_user()

@main.route("/users/me", methods=["PUT"])
@authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def update_user(data):
    """Update a user's email address and password."""
    user = token_auth.current_user()
    user.update(data)
    db.session.commit()
    return user

@main.route("/students/me", methods=["GET"])
@authenticate(token_auth)
@response(student_schema)
def get_student():
    """Returns a user's details."""
    return token_auth.current_user().student

@main.route("/students/me", methods=["PUT"])
@authenticate(token_auth)
@body(StudentSchema(load_instance=False))
@response(student_schema)
def update_student(data):
    student = token_auth.current_user().student
    student.update(data)
    db.session.commit()
    return student

@main.route("/companies/me", methods=["GET"])
@authenticate(token_auth)
@response(company_schema)
def get_company_self():
    """Returns your company's details."""
    return token_auth.current_user().company

@main.route("/companies/me", methods=["PUT"])
@authenticate(token_auth)
@body(CompanySchema(load_instance=False))
@response(company_schema)
def update_company_self(data):
    """Update your company's details."""
    company = token_auth.current_user().company
    company.update(data)
    db.session.commit()
    return company

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
    return user

@main.route("/departments", methods=["GET"])
@response(departments_schema)
def get_departments():
    """Return all departments."""
    return db.session.scalars(db.select(Department))

@main.route("/branches", methods=["GET"])
@response(branches_schema)
def get_branches():
    """Return all branches."""
    return db.session.scalars(db.select(Branch))

@main.route("/industries", methods=["GET"])
@response(industries_schema)
def get_industries():
    """Return all industries."""
    return db.session.scalars(db.select(Industry))

@main.route("/students", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(StudentSchema()))
def get_all_students(args):
    query = db.session.query(Student)
    items, pagination = paginate_query(query, Student, args, {"first_name", "last_name"}, {"id", "user_id"}, "main.get_all_students")
    return { "pagination": pagination, "data": items }, 200