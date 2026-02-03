from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import UserSchema, EmptySchema, RegisterSchema, StudentSchema, DepartmentSchema, BranchSchema, UpdateUserSchema, IndustrySchema, CompanySchema, PositionSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection
from api.models import User, Role, Department, Branch, Student, Industry, Position, Application, Placement, Company

admin = Blueprint("admin", __name__)

@admin.route("/companies", methods=["GET"])
@authenticate(token_auth, role=["admin"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(CompanySchema()))
def get_companies(args):
    query = db.session.query(Company)
    items, pagination = paginate_query(query, Company, args, {"name"}, {"id", "user_id"}, "admin.get_companies")
    return { "pagination": pagination, "data": items }, 200