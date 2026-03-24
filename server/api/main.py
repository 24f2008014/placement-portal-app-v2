from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, PlacementSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement, Company

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return "Hello!"

@main.route("/users/me", methods=["GET"])
@authenticate(token_auth)
@response(UserSchema())
def get_user():
    """Returns a user's details."""
    return token_auth.current_user()

@main.route("/users/me", methods=["PUT"])
@authenticate(token_auth)
@body(UpdateUserSchema())
@response(UserSchema())
def update_user(data):
    """Update a user's email address and password."""
    user = token_auth.current_user()
    user.update(data)
    db.session.commit()
    return user

@main.route("/register", methods=["POST"])
@body(RegisterSchema())
@response(UserSchema(), 201)
def register(data):
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
@response(DepartmentSchema(many=True))
def get_departments():
    """Return all departments."""
    return db.session.scalars(db.select(Department))

@main.route("/branches", methods=["GET"])
@response(BranchSchema(many=True))
def get_branches():
    """Return all branches."""
    return db.session.scalars(db.select(Branch))

@main.route("/industries", methods=["GET"])
@response(IndustrySchema(many=True))
def get_industries():
    """Return all industries."""
    return db.session.scalars(db.select(Industry))

@main.route("/positions", methods=["GET"])
@authenticate(token_auth, role=["admin", "student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_positions(args):
    query = db.session.query(Position)
    items, pagination = paginate_query(query, Position, args, {"role"}, {"id"}, "main.get_positions")
    return { "pagination": pagination, "data": items }, 200

@main.route("/positions/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(PositionSchema())
def get_position(id):
    """Get a position by ID."""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    return position

@main.route("/positions/<int:id>/applications", methods=["GET"])
@authenticate(token_auth, role=["company", "admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications(args, id):
    """Get all applications made for a position."""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    query = db.session.query(Application).where(Application.position == position)
    items, pagination = paginate_query(query, Application, args, {"status"}, {"id"}, "company.get_applications")
    return { "pagination": pagination, "data": items }, 200

@main.route("/companies", methods=["GET"])
@authenticate(token_auth, role=["admin", "student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(CompanySchema()))
def get_companies(args):
    query = db.session.query(Company)
    items, pagination = paginate_query(
        query=query,
        model=Company,
        args=args,
        allowed_filters={"id", "status"},
        allowed_sort={"id"},
        endpoint="main.get_companies"
    )
    return { "pagination": pagination, "data": items }, 200

@main.route("/companies/<int:id>", methods=["GET"])
@authenticate(token_auth, role=["admin", "student"])
@response(CompanySchema())
def get_company(id):
    """Get a company by ID."""
    company = db.get_or_404(Company, id)
    return company

@main.route("/students/<int:id>", methods=["GET"])
@authenticate(token_auth, role=["admin", "company"])
@response(StudentSchema())
def get_student(id):
    """Get a student by ID."""
    student = db.get_or_404(Student, id)
    if token_auth.current_user().company:
        application = db.session.execute(
            db.select(Application).filter(
                Application.student_id == id,
                Application.position.company == token_auth.current_user().company
            )
        ).first()
        if application is None:
            abort(403)
    return student

@main.route("/applications/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(ApplicationSchema())
def get_application(id):
    """Get an application by ID."""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company and token_auth.current_user().company != application.position.company:
        abort(403)
    if token_auth.current_user().student and token_auth.current_user().student != application.student:
        abort(403)
    return application

@main.route("/placements/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(PlacementSchema())
def get_placement(id):
    """Get a placement by ID."""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().company and token_auth.current_user().company != placement.application.position.company:
        abort(403)
    if token_auth.current_user().student and token_auth.current_user().student != placement.application.student:
        abort(403)
    return placement
