from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, PlacementSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement
from datetime import datetime, timezone

company = Blueprint("company", __name__)

@company.route("/positions", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(PositionSchema())
@response(PositionSchema())
def new_position(data):
    company = token_auth.current_user().company
    if company.status != "whitelisted":
        abort(403)
    # position = Position(company=company, **data)
    position = data
    position.company = company
    db.session.add(position)
    db.session.commit()
    return position

@company.route("/positions/<int:id>", methods=["PATCH"])
@authenticate(token_auth, role=["company"])
@body(PositionSchema(only=("status",), partial=True, load_instance=False))
@response(PositionSchema())
def change_position_status(data, id):
    """Change a position's status."""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    position.update(data)
    db.session.commit()
    return position

@company.route("/companies/me/positions", methods=["GET"])
@authenticate(token_auth, role=["company"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_company_positions(args):
    """Get all positions made by your company."""
    query = db.session.query(Position)
    items, pagination = paginate_query(
        query=query,
        model=Position,
        args=args,
        allowed_filters={
            "id": "equals",
            "role": "ilike"
        },
        allowed_sort={"id"},
        endpoint="company.get_positions_self"
    )
    return { "pagination": pagination, "data": items }, 200

@company.route("/companies/me", methods=["GET"])
@authenticate(token_auth)
@response(CompanySchema())
def get_company_self():
    """Returns your company's details."""
    return token_auth.current_user().company

@company.route("/companies/me", methods=["PUT"])
@authenticate(token_auth)
@body(CompanySchema(load_instance=False))
@response(CompanySchema())
def update_company_self(data):
    """Update your company's details."""
    company = token_auth.current_user().company
    company.update(data)
    db.session.commit()
    return company

@company.route("/applications/<int:id>/shortlist", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(ApplicationSchema(only=("interview_date",), partial=True, load_instance=False))
@response(ApplicationSchema())
def shortlist_application(data, id):
    """Shortlist an applicant for an interview."""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company != application.position.company:
        abort(403)
    if application.status == "withdrawn" or application.position.status == "closed":
        abort(403)
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
    """Select an applicant and make them a placement offer."""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company != application.position.company:
        abort(403)
    if application.status == "withdrawn" or application.position.status == "closed":
        abort(403)
    application.status = "selected"
    application.updated_at = datetime.now(timezone.utc)
    placement = Placement(application=application, **data)
    db.session.add(placement)
    db.session.commit()
    return placement

@company.route("/applications/<int:id>/reject", methods=["POST"])
@authenticate(token_auth, role=["company"])
@response(ApplicationSchema())
def reject_application(id):
    """Reject an application."""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().company != application.position.company:
        abort(403)
    if application.status == "withdrawn" or application.position.status == "closed" or application.placements:
        abort(403)
    application.status = "rejected"
    db.session.commit()
    return application

@company.route("/placements/<int:id>/withdraw", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(PlacementSchema())
def withdraw_placement(id):
    """Withdraw a pending placement offer."""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().company != placement.application.position.company:
        abort(403)
    if placement.status != "pending":
        abort(403)
    placement.status = "withdrawn"
    db.session.commit()
    return placement