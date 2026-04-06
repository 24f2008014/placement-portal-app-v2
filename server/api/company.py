from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, PlacementSchema, CompanyStatsSchema
from api.models import Position, Application, Placement
from datetime import datetime, timezone
from sqlalchemy import func

company = Blueprint("company", __name__)

@company.route("/companies/me/stats", methods=["GET"])
@authenticate(token_auth, role=["company"])
@response(CompanyStatsSchema())
def get_company_stats():
    """Get company dashboard stats"""
    company = token_auth.current_user().company
    num_positions = db.session.scalar(db.select(func.count()).select_from(Position).where(Position.company == company))
    num_applications = db.session.scalar(db.select(func.count()).select_from(Application).join(Position).filter(Position.company == company, Application.status != "withdrawn"))
    num_placements = db.session.scalar(db.select(func.count()).select_from(Placement).join(Application).join(Position).where(Position.company == company))
    upcoming_interviews = db.session.scalars(
        db.select(Application)
        .join(Position)
        .filter(
            Position.company == company,
            Application.status == "shortlisted",
            Application.interview_date > datetime.now()
        )
    )
    return {
        "num_positions": num_positions,
        "num_applications": num_applications,
        "num_placements": num_placements,
        "upcoming_interviews": upcoming_interviews
    }

@company.route("/positions", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(PositionSchema())
@response(PositionSchema())
def new_position(data):
    """Create new position"""
    company = token_auth.current_user().company
    if company.status != "whitelisted":
        abort(403, "Company is blacklisted.")
    position = data
    position.company = company
    position.is_approved = False
    db.session.add(position)
    db.session.commit()
    return position

@company.route("/positions/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["company"])
@body(PositionSchema(only=("status",), partial=True, load_instance=False))
@response(PositionSchema())
def change_position_status(data, id):
    """Change a position's status"""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    if (data["status"] == "open") & (position.status == "closed"):
        if datetime.now() > position.deadline:
            abort(403, "Can't re-open a position after the deadline has passed.")
    position.update(data)
    db.session.commit()
    return position

@company.route("/companies/me/positions", methods=["GET"])
@authenticate(token_auth, role=["company"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_company_positions(args):
    """Get your positions"""
    company = token_auth.current_user().company
    query = db.session.query(Position).filter(Position.company == company)
    items, pagination = paginate_query(
        query=query,
        model=Position,
        args=args,
        allowed_filters={
            "id": "equals",
            "role": "ilike",
            "salary_min": "gt",
            "salary_max": "gt",
            "min_cgpa": "gt",
            "deadline": "gt",
            "is_approved": "equals",
            "status": "equals",
            "created_at": "gt",
            "application_count": "gt"
        },
        allowed_sort={"id", "role", "salary_min", "salary_max", "min_cgpa", "deadline", "is_approved", "status", "created_at", "application_count"},    
        endpoint="company.get_company_positions"
    )
    return { "pagination": pagination, "data": items }, 200

@company.route("/companies/me/applications", methods=["GET"])
@authenticate(token_auth, role=["company"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_company_applications(args):
    """Get applications for your positions"""
    company = token_auth.current_user().company
    query = db.session.query(Application).join(Position).filter(Position.company == company, Application.status != "withdrawn")
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "student_id": "equals",
            "position_id": "equals",
            "position.role": "ilike",
            "created_at": "gt",
            "updated_at": "gt",
            "placement_count": "gt",
            "status": "equals"
        },
        allowed_sort={"id", "student_id", "position_id", "position.role", "created_at", "updated_at", "placement_count", "status"},      
        endpoint="company.get_company_applications"
    )
    return { "pagination": pagination, "data": items }, 200

@company.route("/companies/me/placements", methods=["GET"])
@authenticate(token_auth, role=["company"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PlacementSchema()))
def get_company_placements_self(args):
    """Get your placements"""
    company = token_auth.current_user().company
    query = db.session.query(Placement).join(Application).join(Position).filter(Position.company == company)
    items, pagination = paginate_query(
        query=query,
        model=Placement,
        args=args,
        allowed_filters={
            "id": "equals",
            "application_id": "equals",
            "application.student_id": "equals",
            "application.position.role": "ilike",
            "joining_date": "gt",
            "salary": "gt",
            "created_at": "gt",
            "status": "equals"
        },
        allowed_sort={"id", "application_id", "application.student_id", "application.position.role", "joining_date", "salary", "created_at", "status"},
        endpoint="company.get_company_placements_self"
    )
    return { "pagination": pagination, "data": items }, 200

@company.route("/companies/me", methods=["GET"])
@authenticate(token_auth)
@response(CompanySchema())
def get_company_self():
    """Get your company's details"""
    return token_auth.current_user().company

@company.route("/companies/me", methods=["PUT"])
@authenticate(token_auth)
@body(CompanySchema(load_instance=False))
@response(CompanySchema())
def update_company_self(data):
    """Update your company's details"""
    company = token_auth.current_user().company
    company.update(data)
    db.session.commit()
    return company

@company.route("/applications/<int:id>/shortlist", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(ApplicationSchema(only=("interview_date",), partial=True, load_instance=False))
@response(ApplicationSchema())
def shortlist_application(data, id):
    """Shortlist an application for interview"""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company != application.position.company:
        abort(403)
    if application.status != "pending":
        abort(403, f"Application cannot be shortlisted in its current status: {application.status}")
    application.status = "shortlisted"
    application.update(data)
    application.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return application

@company.route("/applications/<int:id>/select", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(PlacementSchema())
@response(PlacementSchema(), 201)
def select_application(data, id):
    """Select an application and make a placement offer"""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company != application.position.company:
        abort(403)
    if application.status != "shortlisted":
        abort(403, f"Application cannot be shortlisted in its current status: {application.status}")
    min_salary = db.session.scalar(db.select(Position.salary_min).join(Application).filter(Application.id == id))
    if data["salary"] < min_salary:
        abort(400, f"Salary cannot be lower than the associated position's min_salary: {min_salary}.")
    application.status = "selected"
    application.updated_at = datetime.now(timezone.utc)
    placement = Placement(application=application, **data)
    db.session.add(placement)
    db.session.commit()
    return placement

@company.route("/applications/<int:id>/reject", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(ApplicationSchema(only=("feedback",), partial=True, load_instance=False))
@response(ApplicationSchema())
def reject_application(data, id):
    """Reject an application"""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company != application.position.company:
        abort(403)
    if application.status in ["selected", "rejected", "withdrawn"]:
        abort(403, f"Application cannot be rejected in its current status: {application.status}.")
    application.update(data)
    application.status = "rejected"
    application.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return application