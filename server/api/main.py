import os
from flask import Blueprint, abort, send_from_directory, current_app
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, PlacementSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement, Company
from celery.result import AsyncResult

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return "Hello!"

@main.route("/result/<id>", methods=["GET"])
@authenticate(token_auth)
def task_result(id):
    """Get the status of a task"""
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "status": result.state,
        "result": result.result if result.ready() else None,
    }

@main.route("/temp/<filename>", methods=["GET"])
@authenticate(token_auth, role=["student"])
def get_file(filename):
    """Get a file by name"""
    return send_from_directory(
        os.path.join(os.path.dirname(os.getcwd()), "server", current_app.config["TEMP_FOLDER"]),
        filename
    )

@main.route("/users/me", methods=["GET"])
@authenticate(token_auth)
@response(UserSchema())
def get_user():
    """Get the current user"""
    return token_auth.current_user()

@main.route("/users/me", methods=["PUT"])
@authenticate(token_auth)
@body(UpdateUserSchema())
@response(UserSchema())
def update_user(data):
    """Update a user's account details"""
    user = token_auth.current_user()
    user.update(data)
    db.session.commit()
    return user

@main.route("/register", methods=["POST"])
@body(RegisterSchema())
@response(UserSchema(), 201)
def register(data):
    """Register a new user account"""
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
    """Get all departments"""
    return db.session.scalars(db.select(Department))

@main.route("/branches", methods=["GET"])
@response(BranchSchema(many=True))
def get_branches():
    """Get all branches"""
    return db.session.scalars(db.select(Branch))

@main.route("/industries", methods=["GET"])
@response(IndustrySchema(many=True))
def get_industries():
    """Get all industries"""
    return db.session.scalars(db.select(Industry))

@main.route("/positions", methods=["GET"])
@authenticate(token_auth, role=["admin", "student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_positions(args):
    """Get all positions
    Can be filtered using query arguments. Filters must be in the format `?filters={"key1":"value1","key1":"value2"}`.

    Allowed `filters`: `id` (=), `role` (ILIKE), `salary_min` (>=), `salary_max` (>=), `deadline` (>=), `min_cgpa` (>=), `status` (=).
    
    Allowed `sort_by`: `id`, `role`, `salary_min`, `salary_max`, `deadline`, `min_cgpa`, `status`.
    """
    query = db.session.query(Position)
    if token_auth.current_user().student:
        query = query.filter(Position.is_approved == True, Position.status == "open")
    items, pagination = paginate_query(
        query=query,
        model=Position,
        args=args,
        allowed_filters={
            "id": "equals",
            "company.name": "ilike_relationship",
            "role": "ilike",
            "salary_min": "gt",
            "salary_max": "gt",
            "deadline": "gt",
            "min_cgpa": "gt",
            "is_approved": "equals",
            "status": "equals",
            "created_at": "gt",
            "application_count": "gt"
        },
        allowed_sort={"id", "role", "salary_min", "salary_max", "deadline", "min_cgpa", "status", "created_at"},
        endpoint="main.get_positions"
    )
    return { "pagination": pagination, "data": items }, 200

@main.route("/positions/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(PositionSchema())
def get_position(id):
    """Get a position by ID"""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    return position

@main.route("/positions/<int:id>/applications", methods=["GET"])
@authenticate(token_auth, role=["company", "admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications(args, id):
    """Get all applications made for a position by ID"""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    query = db.session.query(Application).where(Application.position == position)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "status": "equals"
        },
        allowed_sort={"id"},
        endpoint="main.get_applications"
    )
    print(items)
    return { "pagination": pagination, "data": items }, 200

@main.route("/companies/<int:id>/positions", methods=["GET"])
@authenticate(token_auth, role=["student", "admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_company_positions(args, id):
    """Get all positions for a company"""
    company = db.get_or_404(Company, id)
    query = db.session.query(Position).filter(Position.company == company)
    if token_auth.current_user().student:
        query = query.filter(Position.is_approved == True)
    items, pagination = paginate_query(
        query=query,
        model=Position,
        args=args,
        allowed_filters={
            "id": "equals",
            "role": "ilike",
            "salary_min": "gt",
            "salary_max": "gt",
            "deadline": "gt",
            "min_cgpa": "gt",
            "status": "equals"
        },
        allowed_sort={"id", "role", "salary_min", "salary_max", "deadline", "min_cgpa", "status"},
        endpoint="main.get_company_positions"
    )    
    return { "pagination": pagination, "data": items }, 200

@main.route("/companies", methods=["GET"])
@authenticate(token_auth, role=["admin", "student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(CompanySchema()))
def get_companies(args):
    """Get all companies"""
    query = db.session.query(Company)
    items, pagination = paginate_query(
        query=query,
        model=Company,
        args=args,
        allowed_filters={
            "id": "equals",
            "name": "ilike",
            "status": "equals",
            "contact_email": "ilike",
            "location": "ilike",
            "open_position_count": "gt",
            "industry.name": "ilike_relationship"
        },
        allowed_sort={"id", "name", "location", "contact_email", "open_position_count", "status", "industry.name"},
        endpoint="main.get_companies"
    )
    return { "pagination": pagination, "data": items }, 200

@main.route("/companies/<int:id>", methods=["GET"])
@authenticate(token_auth, role=["admin", "student"])
@response(CompanySchema())
def get_company(id):
    """Get a company by ID"""
    company = db.get_or_404(Company, id)
    return company

@main.route("/students/<int:id>", methods=["GET"])
@authenticate(token_auth, role=["admin", "company"])
@response(StudentSchema())
def get_student(id):
    """Get a student by ID"""
    student = db.get_or_404(Student, id)
    if token_auth.current_user().company: # If company, student must have applied to one of their positions
        application = db.session.execute(
            db.select(Application).join(Position).filter(
                Application.student_id == id,
                Position.company_id == token_auth.current_user().company.id
            )
        ).first()
        if application is None:
            abort(403)
    return student

@main.route("/uploads/resumes/<filename>", methods=["GET"])
@authenticate(token_auth)
def get_resume(filename):
    """Get a resume by filename"""
    if token_auth.current_user().student\
        and db.session.scalar(db.select(Student).filter(Student.resume_url == filename)) != token_auth.current_user().student:
        abort(403)
    return send_from_directory(
        os.path.join(os.path.dirname(os.getcwd()), "server", current_app.config["UPLOAD_FOLDER"]),
        filename
    )

@main.route("/applications/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(ApplicationSchema())
def get_application(id):
    """Get an application by ID"""
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
    """Get a placement by ID"""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().company and token_auth.current_user().company != placement.application.position.company:
        abort(403)
    if token_auth.current_user().student and token_auth.current_user().student != placement.application.student:
        abort(403)
    return placement
