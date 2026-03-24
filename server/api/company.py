from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement

company = Blueprint("company", __name__)

@company.route("/positions", methods=["POST"])
@authenticate(token_auth, role=["company"])
@body(PositionSchema())
@response(PositionSchema())
def new_position(data):
    company = token_auth.current_user().company
    if company.status != "whitelisted":
        abort(403)
    position = Position(company=company, **data)
    db.session.add(position)
    db.session.commit()
    return position

@company.route("/positions/<int:id>", methods=["DELETE"])
@authenticate(token_auth, role=["company"])
def delete_position(id):
    """Delete a position by ID."""
    position = db.get_or_404(Position, id)
    if token_auth.current_user().company and token_auth.current_user().company != position.company:
        abort(403)
    db.session.delete(position)
    db.session.commit()
    return "", 204

@company.route("/companies/me/positions", methods=["GET"])
@authenticate(token_auth, role=["company"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_company_positions(args):
    """Get all positions made by your company."""
    query = db.session.query(Position)
    items, pagination = paginate_query(query, Position, args, {"role"}, {"id"}, "company.get_positions_self")
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
