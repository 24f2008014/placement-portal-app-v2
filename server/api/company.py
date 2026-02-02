from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection
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