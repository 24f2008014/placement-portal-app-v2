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
def post_position(data):
    company = token_auth.current_user().company
    if company.approval_status == False:
        abort(403)
    position = Position(company=company, **data)
    db.session.add(position)
    db.session.commit()
    return position

@company.route("/positions/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(PositionSchema())
def get_position(id):
    """Get a position by ID."""
    position = db.get_or_404(Position, id)
    # if (token_auth.current_user().company) and (token_auth.current_user().company != position.company):
    #     abort(403)
    return position

@company.route("/companies/me/positions", methods=["GET"])
@authenticate(token_auth, role=["company"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_positions_self(args):
    """Get all positions made by your company."""
    query = db.session.query(Position)
    items, pagination = paginate_query(query, Position, args, {"role"}, {"id"}, "company.get_positions_self")
    return { "pagination": pagination, "data": items }, 200

@company.route("/positions/<int:id>/applications", methods=["GET"])
@authenticate(token_auth, role=["company", "admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications(args, id):
    """Get all applications made for a position."""
    position = db.get_or_404(Position, id)
    if (token_auth.current_user().company) and (token_auth.current_user().company != position.company):
        abort(403)
    query = db.session.query(Application).where(Application.position == position)
    items, pagination = paginate_query(query, Application, args, {"status"}, {"id"}, "company.get_applications")
    return { "pagination": pagination, "data": items }, 200